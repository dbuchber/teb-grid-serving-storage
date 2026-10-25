"""Netzspeicher am Leitungsengpass (Spec 4.6, Task 9)."""
import json
from dataclasses import replace

import numpy as np
import pytest
from scipy import sparse

from gridsim import metrics, netzspeicher
from gridsim.control_lines import limit_kw
from gridsim.feeders.loading import loading_pct
from gridsim.feeders.sizing import SizedGrid
from gridsim.feeders.topology import StationGrid

H = 8760
LOAD, FEED = 40.0, 45.0     # Grenzleistung Bezug / Einspeisung (kW)


def flow_with_peaks(seed=3):
    """Abschnittsfluss: Grundlast, an manchen Abenden Bezugsspitzen, an manchen Mittagen Einspeisespitzen."""
    rng = np.random.default_rng(seed)
    h = np.arange(H)
    flow = 15.0 + 8.0 * np.sin(2 * np.pi * ((h % 24) - 13) / 24) + rng.normal(0, 2, H)
    for d in rng.choice(365, 40, replace=False):
        flow[d * 24 + 18:d * 24 + 21] = LOAD + rng.uniform(1, 9, 3)
    for d in rng.choice(365, 30, replace=False):
        flow[d * 24 + 11:d * 24 + 15] = -FEED - rng.uniform(1, 7, 4)
    return flow


def test_size_both_directions():
    flow = flow_with_peaks()
    kwh, kw = netzspeicher.size(flow, (LOAD, FEED))
    load = metrics.segment_row(flow, LOAD)
    feed = metrics.segment_row(-flow, FEED)
    assert kwh == max(load['e_inst_kwh'], feed['e_inst_kwh'])
    assert kw >= max(load['p_max_kw'], feed['p_max_kw'])
    assert kw <= max(load['p_max_kw'], feed['p_max_kw']) + 0.2
    assert netzspeicher.size(np.full(H, 10.0), (LOAD, FEED)) is None


def test_dispatch_soc_bounds():
    flow = flow_with_peaks()
    kwh, kw = netzspeicher.size(flow, (LOAD, FEED))
    x, soc = netzspeicher.dispatch(flow, (LOAD, FEED), kwh, kw, return_soc=True)
    assert x.shape == (H,) and soc.shape == (H,)
    assert soc.min() >= 0.0 and soc.max() <= kwh + 1e-9
    assert np.abs(x).max() <= kw + 1e-9
    # zu kleiner Speicher: Grenzen halten trotzdem
    x, soc = netzspeicher.dispatch(flow, (LOAD, FEED), kwh / 10, kw / 3, return_soc=True)
    assert soc.min() >= 0.0 and soc.max() <= kwh / 10 + 1e-9 and np.abs(x).max() <= kw / 3 + 1e-9


def test_dispatch_removes_overload_when_sized():
    flow = flow_with_peaks()
    kwh, kw = netzspeicher.size(flow, (LOAD, FEED))
    x = netzspeicher.dispatch(flow, (LOAD, FEED), kwh, kw)
    after = flow + x
    assert after.max() <= LOAD and after.min() >= -FEED
    # entlädt bei Bezugsüberlast, lädt bei Einspeiseüberlast
    assert (x[flow > LOAD] < 0).all() and (x[flow < -FEED] > 0).all()


def test_dispatch_never_pushes_over_limit():
    """Außerhalb der Engpässe (Rückkehr auf 50 %) darf der Speicher keinen Abschnitt über eine Grenze bringen."""
    flow = flow_with_peaks()
    flow[flow > 0] = np.minimum(flow[flow > 0], LOAD - 0.5)   # knapp unter der Grenze: kaum Raum zum Laden
    flow[5000:5004] = -FEED - 10.0                            # einmal laden müssen, danach zurück auf 50 %
    x = netzspeicher.dispatch(flow, (LOAD, FEED), 100.0, 20.0)
    after = flow + x
    ok = (flow <= LOAD) & (flow >= -FEED)
    assert (after[ok] <= LOAD).all() and (after[ok] >= -FEED).all()
    # mehrere Abschnitte (Pfad des Knotens): jeder bleibt in seinen Grenzen
    two = np.column_stack([flow, 0.25 * flow])               # Abschnitt 1 mit 10 kW: ab ±40 kW am Abschnitt 0 eng
    lim2 = (np.array([LOAD, 10.0]), np.array([FEED, 10.0]))
    x2 = netzspeicher.dispatch(two, lim2, 100.0, 20.0)
    after2 = two + x2[:, None]
    ok2 = ((two <= lim2[0]) & (two >= -lim2[1])).all(axis=1)
    assert (after2[ok2] <= lim2[0]).all() and (after2[ok2] >= -lim2[1]).all()
    assert (x2 != x).any()                                    # der engere Abschnitt begrenzt die Rückkehr auf 50 %


def test_dispatch_energy_balance():
    flow = flow_with_peaks()
    kwh, kw = netzspeicher.size(flow, (LOAD, FEED))
    eta = 0.95
    x, soc = netzspeicher.dispatch(flow, (LOAD, FEED), kwh, kw, eta=eta, return_soc=True)
    lhs = np.maximum(x, 0).sum() * eta - np.maximum(-x, 0).sum() / eta
    assert lhs == pytest.approx(soc[-1] - 0.5 * kwh, abs=1e-6)
    assert np.maximum(-x, 0).sum() > 10.0      # er arbeitet wirklich


def test_dispatch_prepares_with_daily_forecast():
    """Perfekte Tagesprognose: vor einem großen Entladeereignis wird über 50 % geladen."""
    flow = np.full(H, 10.0)
    flow[100 * 24 + 17:100 * 24 + 23] = LOAD + 10.0            # 6 h × 10 kW = 60 kWh aus 80 kWh
    x, soc = netzspeicher.dispatch(flow, (LOAD, FEED), 80.0, 12.0, return_soc=True)
    after = flow + x
    assert after.max() <= LOAD
    assert soc[100 * 24 + 16] > 0.5 * 80.0
    assert soc[200 * 24] == pytest.approx(40.0, abs=1e-6)        # danach wieder 50 %


def toy_grid(i_max=(60.0, 30.0, 30.0, 60.0, 40.0)):
    """Abgang 0: Abschnitt 0 (Knoten 0, 1) mit Kindern 1 (Knoten 0) und 2 (Knoten 1); Abgang 1: 3 → 4 (Knoten 2)."""
    down = sparse.csr_matrix(np.array([[1, 1, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, 1]], dtype=np.int8))
    grid = StationGrid(station=0, area='ort', node_index=np.arange(3), parent=np.array([-1, 0, 0, -1, 3], np.int32),
                       length_m=np.array([50, 20, 10, 50, 5], np.float32), feeder=np.array([0, 0, 0, 1, 1], np.int16),
                       service=np.array([False, True, True, False, True]), overhead=np.zeros(5, bool),
                       downstream=down, marked=np.zeros(2, bool), geometry=[np.zeros((2, 2))] * 5)
    sized = SizedGrid(types=['x'] * 5, parallel=np.ones(5, np.int8), i_max_a=np.asarray(i_max, dtype=float),
                      r_ohm=np.zeros(5), x_ohm=np.zeros(5), du_load_pct=np.zeros(2), du_feed_pct=np.zeros(2),
                      marked=np.zeros(2, bool))
    return grid, sized


def test_place_one_per_feeder():
    grid, _ = toy_grid()
    pct = np.full((H, 5), 50.0, np.float32)
    pct[10, 0], pct[11, 1], pct[12, 2] = 130.0, 110.0, 120.0      # Abgang 0: Abschnitt 0 am stärksten
    pct[13, 3], pct[14, 4] = 101.0, 150.0                          # Abgang 1: Hausanschluss 4
    got = netzspeicher.place(grid, pct)
    # Abschnitt 0 endet an einem Abzweig: nächster Knoten dahinter ist Knoten 1 (10 m statt 20 m)
    assert got == [(0, 1), (1, 2)]
    pct[:, 3:] = 99.0                                               # Abgang 1 ohne Überlast
    assert netzspeicher.place(grid, pct) == [(0, 1)]
    assert netzspeicher.place(grid, np.zeros((H, 5), np.float32)) == []


def test_plan_station_sizes_bottleneck():
    grid, sized = toy_grid()
    load_kw, feed_kw = limit_kw(sized)
    seg = np.zeros((H, 5))
    seg[:, 0] = flow_with_peaks() * load_kw[0] / LOAD
    seg[:, 1] = 0.2 * seg[:, 0]          # Kinder schwächer ausgelastet als Abschnitt 0
    seg[:, 2] = 0.3 * seg[:, 0]
    plan = netzspeicher.plan_station(0, grid, sized, seg)
    assert len(plan) == 1
    st = plan[0]
    assert (st['station'], st['feeder'], st['segment'], st['node']) == (0, 0, 0, 1)
    assert (st['kwh'], st['kw']) == netzspeicher.size(seg[:, 0], (load_kw[0], feed_kw[0]))
    json.dumps(plan)
    assert netzspeicher.plan_station(0, grid, replace(sized, i_max_a=sized.i_max_a * 100), seg) == []


def test_path_segments():
    grid, _ = toy_grid()
    assert list(netzspeicher.path_segments(grid, 1)) == [0, 2]
    assert list(netzspeicher.path_segments(grid, 2)) == [3, 4]


# --- Lauf ----------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='module')
def run_case(tmp_path_factory):
    """Fake prepared mit ``feeders/``; Grenzströme auf 15 % gesenkt, damit Leitungen überlastet sind."""
    from fakes import align_station_positions, fake_build_members_factory, fake_roads, write_fake_prepared
    from gridsim import legacy
    from gridsim.data import load_prepared
    from gridsim.feeders.prepare import load_feeders, prepare_feeders
    tmp = tmp_path_factory.mktemp('ns')
    build = fake_build_members_factory()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(legacy.load('steyr_sim_variant_a'), 'build_members', build)
        inp = tmp / 'input'
        inp.mkdir()
        fake_roads(inp / 'osm_roads.json')
        prepared = tmp / 'prepared'
        write_fake_prepared(prepared, 2012)
        write_fake_prepared(prepared, 2023)
        align_station_positions(prepared, build)
        prepare_feeders(inp, prepared)
    p = load_prepared(prepared, 2023)
    weak = {s: (g, replace(z, i_max_a=z.i_max_a * 0.15)) for s, (g, z) in load_feeders(prepared).items()}
    return p, weak, prepared


def lp(**kw):
    from gridsim.run import RunParams
    base = dict(weather_year=2023, scenario='2040', pv_factor=1.0, charging='uncontrolled', storage='base', n_seeds=1)
    return RunParams(**{**base, **kw})


def test_plan_from_sizing_run(run_case):
    from gridsim.run import netzspeicher_plan
    p, weak, _ = run_case
    plan = netzspeicher_plan(p, lp(netzspeicher=True), weak)
    assert plan and [st['station'] for st in plan] == sorted(st['station'] for st in plan)
    for s in {st['station'] for st in plan}:
        feeders = [st['feeder'] for st in plan if st['station'] == s]
        assert len(feeders) == len(set(feeders))                 # höchstens einer je Abgang
    assert all(st['kwh'] > 0 and st['kw'] > 0 for st in plan)


@pytest.mark.parametrize('charging,limits', [('uncontrolled', 'trafo'), ('controlled', 'trafo+leitung'),
                                             ('v2g', 'trafo+leitung')])
def test_run_seed_with_netzspeicher(run_case, charging, limits):
    """Gesteuertes Laden/V2G reagieren auf den Speicher (sieht nur den Grundfluss), daher im Leitungsmodus geprüft."""
    from gridsim.feeders.loading import segment_flow
    from gridsim.nodeflow import station_block
    from gridsim.run import flows, netzspeicher_plan, run_seed
    p, weak, _ = run_case
    on, off = lp(charging=charging, limits=limits, netzspeicher=True), lp(charging=charging, limits=limits)
    plan = netzspeicher_plan(p, on, weak)
    r_off = run_seed(p, off, 0, feeders=weak, feeders_fp='x')
    r_on = run_seed(p, on, 0, feeders=weak, feeders_fp='x', plan=plan)
    assert r_on.extra['netzspeicher_effective'] is True and r_off.extra['netzspeicher_effective'] is False
    assert r_on.region['netzspeicher_n'] == len(plan)
    assert r_on.region['netzspeicher_kwh'] == pytest.approx(sum(st['kwh'] for st in plan), abs=0.05)
    assert r_on.region['netzspeicher_vollzyklen'] > 0
    assert r_on.region['line_over_m_rest'] == r_on.region['line_over_m']
    assert r_on.region['line_over_m_rest'] <= r_off.region['line_over_m']
    assert r_off.region['netzspeicher_n'] is None
    # ohne Plan bemisst run_seed selbst (im Speicher), gleiches Ergebnis
    assert run_seed(p, on, 0, feeders=weak, feeders_fp='x').region == r_on.region
    # Speicher im Knotenfluss: Stationsfluss = Summe der Knoten, Engpass entlastet
    f_on, f_off = flows(p, on, 0, feeders=weak, plan=plan), flows(p, off, 0, feeders=weak)
    tot_on = tot_off = 0.0
    for st in plan:
        s, j = st['station'], st['segment']
        grid, sized = weak[s]
        block = station_block(p, on, f_on, s)
        np.testing.assert_allclose(block.net().sum(axis=1, dtype=np.float64), f_on['flow'][:, s], atol=1e-3)
        all_on = segment_flow(grid, sized, block)
        all_off = segment_flow(grid, sized, station_block(p, off, f_off, s))
        path = netzspeicher.path_segments(grid, st['node'])
        ok = loading_pct(all_off[:, path], replace(sized, i_max_a=sized.i_max_a[path])) <= 100.0
        assert (loading_pct(all_on[:, path], replace(sized, i_max_a=sized.i_max_a[path]))[ok] <= 100.0).all()
        seg_on, seg_off = all_on[:, j], all_off[:, j]
        load_kw, feed_kw = limit_kw(sized)
        over = lambda x: np.maximum(x - load_kw[j], 0).sum() + np.maximum(-x - feed_kw[j], 0).sum()  # noqa: E731
        assert over(seg_on) < over(seg_off)
        tot_on, tot_off = tot_on + over(seg_on), tot_off + over(seg_off)
    # in Summe mehr als halbiert; Rest: tagelange Überlast ohne Stunden zum Nachladen (Bemessung § 7.2 je Ereignis)
    assert tot_on < 0.5 * tot_off


def test_netzspeicher_without_feeders_falls_back(run_case):
    from gridsim.run import run_seed
    p, _, _ = run_case
    r = run_seed(p, lp(netzspeicher=True), 0, feeders=None)
    r0 = run_seed(p, lp(), 0, feeders=None)
    assert r.extra['netzspeicher_effective'] is False
    assert r.region == r0.region and r.region['netzspeicher_kwh'] is None
    assert r.station_load_kw_max == r0.station_load_kw_max


def test_plan_cache_reuse_and_fingerprint(run_case, tmp_path):
    from gridsim.run import netzspeicher_plan_cached
    calls = []

    def compute():
        calls.append(1)
        return [{'station': 0, 'feeder': 0, 'segment': 1, 'node': 0, 'kwh': 5.0, 'kw': 2.0}]

    pr = lp(netzspeicher=True)
    a = netzspeicher_plan_cached(tmp_path, pr, 'fp1', compute)
    data = json.loads((tmp_path / pr.key() / 'netzspeicher.json').read_text())
    assert data['feeders_fp'] == 'fp1' and data['storages'] == a
    assert netzspeicher_plan_cached(tmp_path, pr, 'fp1', compute) == a and len(calls) == 1
    netzspeicher_plan_cached(tmp_path, pr, 'fp2', compute)        # andere Stationsnetze: neu bemessen
    assert len(calls) == 2
    (tmp_path / pr.key() / 'netzspeicher.json').write_text('{"feeders_fp": "fp2", "sto')
    netzspeicher_plan_cached(tmp_path, pr, 'fp2', compute)        # abgebrochen geschrieben: neu bemessen
    assert len(calls) == 3


def test_run_many_writes_plan(run_case, tmp_path):
    from gridsim.run import feeders_fingerprint, run_many
    _, _, prepared = run_case
    pr = lp(netzspeicher=True, pv_factor=2.0)
    got = list(run_many(prepared, pr, workers=1, cache_dir=tmp_path))
    data = json.loads((tmp_path / pr.key() / 'netzspeicher.json').read_text())
    assert data['feeders_fp'] == feeders_fingerprint(prepared)
    assert got[0].extra['netzspeicher_effective'] is True
    assert got[0].region['netzspeicher_n'] == len(data['storages'])


def test_costs_netzspeicher():
    k = {'storage_units': 0, 'trafo_plus1': 0, 'trafo_plus2': 0, 'trafo_over_1000': 0, 'netzspeicher_kwh': 120.0}
    c = metrics.costs(k, dict(metrics.COST_DEFAULTS))
    assert c['netzspeicher_eur'] == 120.0 * metrics.COST_DEFAULTS['storage_eur_per_kwh']
    assert metrics.costs(dict(k, netzspeicher_kwh=None), dict(metrics.COST_DEFAULTS))['netzspeicher_eur'] is None
