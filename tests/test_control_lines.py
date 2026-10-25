"""Gesteuertes Laden, V2G und T3d gegen Leitungsgrenzen (Spec 4.5, Task 8)."""
from dataclasses import replace

import numpy as np
import pytest
from scipy import sparse

from fakes import FEEDER_NODE_OFFSET_M, write_fake_prepared
from gridsim import control
from gridsim.control_lines import controlled_lines, limit_kw, room, signal_lines, v2g_lines
from gridsim.data import load_prepared
from gridsim.feeders.loading import loading_pct, segment_flow
from gridsim.feeders.sizing import SizedGrid, design_flows, size
from gridsim.feeders.topology import StationGrid, build_station_grid
from gridsim.nodeflow import NodeBlock, base_block
from gridsim.run import RunParams, flows

H = 8760
HH_PEAK = 1.0


def toy_grid(i_max=(40.0, 15.0, 60.0, 40.0)):
    """Zwei Abgänge: A = Abschnitt 0 (Knoten 0, 1) mit Kind 1 (Knoten 1); B = Abschnitt 2 (Knoten 2, 3) mit Kind 3."""
    down = sparse.csr_matrix(np.array([[1, 1, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1]], dtype=np.int8))
    grid = StationGrid(station=0, area='ort', node_index=np.arange(4), parent=np.array([-1, 0, -1, 2], np.int32),
                       length_m=np.full(4, 50, np.float32), feeder=np.array([0, 0, 1, 1], np.int16),
                       service=np.array([False, True, False, True]), overhead=np.zeros(4, bool), downstream=down,
                       marked=np.zeros(2, bool), geometry=[np.zeros((2, 2))] * 4)
    sized = SizedGrid(types=['x'] * 4, parallel=np.ones(4, np.int8), i_max_a=np.asarray(i_max, dtype=float),
                      r_ohm=np.zeros(4), x_ohm=np.zeros(4), du_load_pct=np.zeros(2), du_feed_pct=np.zeros(2),
                      marked=np.zeros(2, bool))
    return grid, sized


def toy_block(base, hh=(1, 2, 1, 0)):
    """Knotenblock mit Grundlast ``base`` (8760, 4) als Haushaltslast, sonst null."""
    z = np.zeros((H, 4), np.float32)
    return NodeBlock(hh_kw=np.asarray(base, np.float32), pv_kw=z.copy(), wp_kw=z.copy(), storage_kw=z.copy(),
                     ev_kw=z.copy(), v2g_kw=z.copy(), nodes=np.arange(4), hh=np.asarray(hh, float),
                     hh_peak_kw=HH_PEAK)


def ev_demand(rng, p=0.15):
    """Ladewunsch je Knoten: zufällige Abende mit 11 kW über einige Stunden."""
    ev = np.zeros((H, 4))
    for n in range(4):
        for d in range(365):
            if rng.random() < 0.7:
                t0 = d * 24 + int(rng.integers(16, 22))
                ev[t0:t0 + int(rng.integers(1, 5)), n] = 11.0
    return ev


def with_ev(block, ev):
    return replace(block, ev_kw=np.asarray(ev, np.float32))


@pytest.fixture(scope='module')
def toy():
    rng = np.random.default_rng(7)
    grid, sized = toy_grid()
    base = rng.uniform(0.0, 8.0, (H, 4))
    return grid, sized, toy_block(base), ev_demand(rng)


def test_room_matches_loading_pct(toy):
    grid, sized, block, _ = toy
    seg0 = segment_flow(grid, sized, block)
    st0 = block.net().sum(axis=1)
    seg_room, trafo_room = room(seg0, sized, 30.0, st0)
    assert seg_room.shape == (H, 4) and trafo_room.shape == (H,)
    assert (seg_room >= 0).all() and (trafo_room >= 0).all()
    # Fluss + Raum liegt genau auf 100 % (wo Raum > 0)
    pct = loading_pct(seg0 + seg_room, sized)
    np.testing.assert_allclose(pct[seg_room > 0], 100.0, rtol=1e-4)
    np.testing.assert_allclose(limit_kw(sized)[0], sized.i_max_a * np.sqrt(3) * 0.4 * 0.97)


def test_controlled_lines_respects_every_segment(toy):
    grid, sized, block, ev = toy
    kva = 45.0
    out, unmet = controlled_lines(block, ev, grid, sized, kva)
    assert out.shape == (H, 4) and unmet.shape == (4, 365)
    seg0 = segment_flow(grid, sized, block)
    seg = segment_flow(grid, sized, with_ev(block, out))
    pct0, pct = loading_pct(seg0, sized), loading_pct(seg, sized)
    ok = pct0 <= 100.0
    assert (pct[ok] <= 100.0).all()   # streng: keine Scheinüberlast aus float32-Rundung
    st0 = block.net().sum(axis=1)
    under = st0 <= kva
    assert (st0[under] + out.sum(axis=1)[under] <= kva + 1e-4).all()
    # Steuerung greift wirklich ein: ohne sie lägen Abschnitte drüber
    raw = loading_pct(segment_flow(grid, sized, with_ev(block, ev)), sized)
    assert (raw[ok] > 100.5).any()
    # Abschnitt 1 (eng, nur Knoten 1) begrenzt Knoten 1 stärker als Knoten 0
    assert unmet[1].sum() > unmet[0].sum()


def test_controlled_lines_never_negative():
    """Review Focus 3: Grundfluss schon über der Grenze → Laden 0 (nie negativ), Bedarf in ``unmet``."""
    grid, sized = toy_grid()
    base = np.full((H, 4), 1.0)
    base[:, 1] = 50.0          # Abschnitte 0 und 1 dauerhaft über der Grenze
    block = toy_block(base, hh=(0, 0, 0, 0))
    ev = np.zeros((H, 4))
    ev[18:21, :] = 11.0        # Tag 0, 18–20 Uhr; Frist Tag 1 7 Uhr
    seg_room, trafo_room = room(segment_flow(grid, sized, block), sized, 40.0, block.net().sum(axis=1))
    assert seg_room[:, :2].max() == 0.0 and trafo_room.max() == 0.0 and seg_room.min() >= 0.0
    out, unmet = controlled_lines(block, ev, grid, sized, 1000.0)
    assert out.min() >= 0.0
    assert out[:, :2].max() == 0.0
    np.testing.assert_allclose(unmet[:2, 1], 33.0)
    np.testing.assert_allclose(out[:, 2:].sum(axis=0), 33.0)   # Abgang B unbeeinflusst
    assert unmet[2:].sum() == 0.0
    # auch der Trafo schon über der Grenze → nirgends Laden
    out, unmet = controlled_lines(block, ev, toy_grid((1e6,) * 4)[0], toy_grid((1e6,) * 4)[1], 10.0)
    assert out.max() == 0.0 and unmet[:, 1].sum() == pytest.approx(132.0)


def test_energy_conserved(toy):
    """Geladen + ungeladen = Bedarf je Knoten und Tag (Tag d = Stunden nach der Frist d−1 bis zur Frist d)."""
    grid, sized, block, ev = toy
    out, unmet = controlled_lines(block, ev, grid, sized, 45.0)
    edges = np.r_[0, np.arange(365) * 24 + control.DEADLINE_H + 1]
    want = np.add.reduceat(ev, edges[:-1], axis=0)[:365]
    got = np.add.reduceat(out, edges[:-1], axis=0)[:365]
    np.testing.assert_allclose(got + unmet.T, want, atol=1e-6)
    assert unmet.sum() > 1.0


@pytest.fixture(scope='module')
def fake_case(tmp_path_factory):
    p = load_prepared(write_fake_prepared(tmp_path_factory.mktemp('p'), kva=(6, 9, 10)), 2023)
    pr = RunParams(weather_year=2023, scenario='2040', charging='uncontrolled', n_seeds=1)
    return p, pr, flows(p, pr, 0)


def fake_feeder(p, s, scale=1.0):
    nodes = np.flatnonzero(np.asarray(p.nodes_station) == s)
    xy = np.asarray(FEEDER_NODE_OFFSET_M, dtype=float)[nodes]
    hh = np.asarray(p.nodes_hh)[nodes]
    kwp = np.asarray(p.nodes_kwp_bins, dtype=float)[nodes].sum(axis=1)
    grid = build_station_grid(s, (0.0, 0.0), nodes, xy, hh, kwp, None)
    load, feed = design_flows(grid, hh, np.ones(len(nodes)), 0.5 * hh, kwp)
    sized = size(grid, load, feed)
    return grid, replace(sized, i_max_a=sized.i_max_a * scale)


@pytest.mark.parametrize('s', [0, 1])
def test_trafo_only_equals_old_controlled(fake_case, s):
    """Alle Abschnitte sehr stark → Stationssumme wie ``control.controlled``."""
    p, pr, f = fake_case
    grid, sized = fake_feeder(p, s, scale=1e6)
    block0 = base_block(p, pr, f, s)
    from gridsim.nodeflow import _ev_nodes
    ev_n = _ev_nodes(f['ev'], f['start'], s, block0.nodes)
    kva = float(p.kva[s])
    out, unmet = controlled_lines(block0, ev_n, grid, sized, kva, station_flow0=f['base'][:, s])
    ref, ref_unmet = control.controlled(f['base'][:, [s]], ev_n.sum(axis=1, dtype=np.float64)[:, None], [kva])
    assert np.abs(ref[:, 0] - ev_n.sum(axis=1)).max() > 1.0     # Trafo greift ein
    np.testing.assert_allclose(out.sum(axis=1), ref[:, 0], atol=1e-6)
    np.testing.assert_allclose(unmet.sum(axis=0), ref_unmet[0], atol=1e-6)


def test_v2g_lines_relieves_downstream_only():
    """Überlast auf Abgang A wird nur von Autos hinter A gedeckt."""
    grid, sized = toy_grid((30.0, 30.0, 60.0, 40.0))
    lim = limit_kw(sized)[0]
    base = np.zeros((H, 4))
    base[:, 1] = 0.5 * lim[1]
    base[18, 1] = lim[1] + 5.0          # 18 Uhr: Abschnitte 0 und 1 je 5 kW über der Grenze (A)
    block = toy_block(base, hh=(0, 0, 0, 0))
    kva = 1000.0
    # nur Autos auf Abgang B: keine Entlastung von A möglich
    out, rech, unmet = v2g_lines(block, np.array([0, 0, 1, 1.0]), grid, sized, kva)
    assert out.max() == 0.0 and rech.max() == 0.0 and unmet.sum() == 0.0
    # Auto an Knoten 0 (hinter Abschnitt 0, nicht hinter 1): deckt nur Abschnitt 0, nicht den engen Abschnitt 1
    out, rech, unmet = v2g_lines(block, np.array([1.0, 0, 1, 1]), grid, sized, kva)
    assert out[18, 0] == pytest.approx(5.0, abs=1e-3) and out[:, 2:].max() == 0.0
    seg = segment_flow(grid, sized, replace(block, v2g_kw=(out - rech).astype(np.float32)))
    assert loading_pct(seg, sized)[18, 0] <= 100.0 and seg[18, 1] > lim[1]
    # Auto an Knoten 1: deckt beide Abschnitte
    out, rech, unmet = v2g_lines(block, np.array([0, 1.0, 1, 1]), grid, sized, kva)
    assert out[18, 1] == pytest.approx(5.0, abs=1e-3) and out.sum() == pytest.approx(5.0, abs=1e-3)
    # Nachladen bis 7 Uhr im Raum des Pfads, Energie erhalten
    assert rech.sum() + unmet.sum() == pytest.approx(out.sum())
    seg = segment_flow(grid, sized, replace(block, v2g_kw=(out - rech).astype(np.float32)))
    assert (loading_pct(seg, sized)[19:32] <= 100.0).all()
    assert rech[19:32, 1].sum() == pytest.approx(out.sum())


def test_v2g_lines_trafo_overload_uses_all_cars():
    grid, sized = toy_grid((1e6,) * 4)
    base = np.zeros((H, 4))
    base[18] = [10, 10, 10, 10]
    block = toy_block(base, hh=(0, 0, 0, 0))
    out, rech, unmet = v2g_lines(block, np.array([0, 1.0, 0, 1]), grid, sized, 36.0)
    assert out[18].sum() == pytest.approx(4.0) and out[18, 0] == 0 and out[18, 2] == 0
    ref = control.v2g_with_recharge(base.sum(axis=1)[:, None], np.zeros((H, 1)), [36.0], [2.0])
    np.testing.assert_allclose(out.sum(axis=1), ref[0][:, 0], atol=1e-9)
    np.testing.assert_allclose(rech.sum(axis=1), ref[1][:, 0], atol=1e-9)


def test_signal_lines_trafo_or_segment():
    grid, sized = toy_grid()
    lim = limit_kw(sized)[0]
    seg = np.zeros((H, 4))
    st = np.zeros(H)
    assert not signal_lines(seg, sized, st, 10.0).any()
    seg[5 * 24 + 20, 3] = lim[3] + 0.1          # Tag 5, 20 Uhr: Abschnitt 3 über der Grenze
    st[9 * 24 + 17] = 11.0                      # Tag 9, 17 Uhr: Trafo über der Grenze
    sig = signal_lines(seg, sized, st, 10.0)
    assert sig.shape == (365,) and sig.dtype == bool
    assert set(np.flatnonzero(sig)) == {5, 9}
    seg[:, 2] = -lim[2] * 1.5                   # Einspeisung über der Grenze zählt nicht (Ladesignal)
    assert set(np.flatnonzero(signal_lines(seg, sized, st, 10.0))) == {5, 9}


# --- Lauf im Grenzmodus trafo+leitung ------------------------------------------------------------------------------

@pytest.fixture(scope='module')
def run_case(tmp_path_factory):
    """Fake prepared mit ``feeders/`` und kleinen Trafos; Grenzströme auf 15 % gesenkt, damit Leitungen greifen."""
    from fakes import align_station_positions, fake_build_members_factory, fake_roads
    from gridsim import legacy
    from gridsim.feeders.prepare import load_feeders, prepare_feeders
    tmp = tmp_path_factory.mktemp('feeders')
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
    return p, weak


def lp(**kw):
    base = dict(weather_year=2023, scenario='2040', pv_factor=1.0, charging='controlled', storage='base', n_seeds=1)
    return RunParams(**{**base, **kw})


@pytest.mark.parametrize('charging', ['uncontrolled', 'winap'])
def test_uncontrolled_and_winap_same_in_both_modes(run_case, charging):
    p, weak = run_case
    a = flows(p, lp(charging=charging), 0, feeders=weak)
    b = flows(p, lp(charging=charging, limits='trafo+leitung'), 0, feeders=weak)
    np.testing.assert_array_equal(a['flow'], b['flow'])
    assert b['limits_effective'] == 'trafo+leitung' and a['limits_effective'] == 'trafo'


def test_line_mode_without_feeders_falls_back(run_case):
    p, _ = run_case
    a = flows(p, lp(), 0)
    b = flows(p, lp(limits='trafo+leitung'), 0, feeders=None)
    np.testing.assert_array_equal(a['flow'], b['flow'])
    assert b['limits_effective'] == 'trafo'


@pytest.mark.parametrize('charging', ['controlled', 'v2g'])
def test_line_mode_station_flow_is_node_sum(run_case, charging):
    from gridsim.nodeflow import station_block
    p, weak = run_case
    pr = lp(charging=charging, limits='trafo+leitung')
    f = flows(p, pr, 0, feeders=weak)
    t = flows(p, lp(charging=charging), 0, feeders=weak)
    assert f['unmet'].sum() > t['unmet'].sum() + 1.0          # Leitungen sperren zusätzlich Energie
    for s, (grid, sized) in weak.items():
        block = station_block(p, pr, f, s)
        np.testing.assert_allclose(block.net().sum(axis=1, dtype=np.float64), f['flow'][:, s], atol=1e-3)
        assert block.ev_kw.min() >= 0.0
        pct0 = loading_pct(segment_flow(grid, sized, base_block(p, pr, f, s)), sized)
        pct = loading_pct(segment_flow(grid, sized, replace(block, v2g_kw=block.v2g_kw * 0)), sized)
        if charging == 'controlled':   # bei V2G kommt das Nachladen dazu, ebenfalls im Raum (eigener Test)
            assert (pct[pct0 <= 100.0] <= 100.0).all()
            assert (f['flow'][:, s] <= np.maximum(f['base'][:, s], p.kva[s]) + 1e-3).all()


def test_line_mode_t3d_uses_line_signal(run_case):
    p, weak = run_case
    a = flows(p, lp(charging='t3d'), 0, feeders=weak)
    b = flows(p, lp(charging='t3d', limits='trafo+leitung'), 0, feeders=weak)
    assert b['limits_effective'] == 'trafo+leitung'
    assert (b['start'] != a['start']).any()
    # nur verschoben: gleiche Energie bis auf Ladungen, die über das Jahresende rutschen
    np.testing.assert_allclose(b['ev_load'][:-48].sum(), a['ev_load'][:-48].sum(), rtol=2e-3)


def test_run_seed_records_limits_effective(run_case):
    from gridsim.run import run_seed
    p, weak = run_case
    r = run_seed(p, lp(limits='trafo+leitung'), 0, feeders=weak, feeders_fp='x')
    assert r.extra['limits_effective'] == 'trafo+leitung'
    r0 = run_seed(p, lp(limits='trafo+leitung'), 0, feeders=None)
    assert r0.extra['limits_effective'] == 'trafo'


@pytest.mark.parametrize('i_parent', [47.7, 123.0])   # Werte, bei denen ohne Abstand 100,00001 % herauskamen
def test_v2g_lines_feed_cap_keeps_margin(i_parent):
    """Task-8-Review: Rückspeisung an Kind-Abschnitt darf den Eltern-Abschnitt (PV-Einspeisung) nicht über 100 % drücken."""
    grid, sized = toy_grid((i_parent, 15.0, 60.0, 40.0))
    load_kw, feed_kw = limit_kw(sized)
    base = np.zeros((H, 4))
    base[18, 1] = load_kw[1] + 5.0                        # Kind-Abschnitt 1 in Bezugsrichtung überlastet
    base[18, 0] = -feed_kw[0] - base[18, 1] + 2.0         # PV an Knoten 0: Eltern-Abschnitt 0 knapp unter der Grenze
    block = toy_block(base, hh=(0, 0, 0, 0))
    out, rech, _ = v2g_lines(block, np.array([0, 3.0, 0, 0]), grid, sized, 1000.0)
    assert out[18, 1] > 1.0                               # V2G greift, wird aber am Eltern-Abschnitt gekappt
    seg = segment_flow(grid, sized, replace(block, v2g_kw=(out - rech).astype(np.float32)))
    pct = loading_pct(seg, sized)
    assert seg[18, 0] < 0 and pct[18, 0] <= 100.0


def test_trafo_never_above_kva_by_rounding():
    """Task 11: Laden/V2G füllen den Trafo-Raum genau; der Stationsfluss darf durch Rundung nicht über ``kva`` liegen
    (sonst zählt die Trafo-Kennzahl Scheinüberlast)."""
    rng = np.random.default_rng(11)
    grid, sized = toy_grid((1e6,) * 4)
    base = rng.uniform(0.0, 9.7, (H, 4)) + 1e-7 * rng.random((H, 4))
    block = toy_block(base, hh=(0, 0, 0, 0))
    st0 = block.net().sum(axis=1, dtype=np.float64)
    kva = 23.456789
    ev = rng.uniform(0.0, 11.0, (H, 4))
    out, _ = controlled_lines(block, ev, grid, sized, kva, station_flow0=st0)
    flow = st0 + out.sum(axis=1)
    ok = st0 <= kva                      # Grundfluss schon über kva: dort lädt niemand, Überlast bleibt echt
    assert out.sum(axis=1)[~ok].max() == 0.0
    assert out.sum() > 0 and (flow[ok] > kva).sum() == 0
    # V2G: Überlast am Trafo wird genau bis kva gedeckt, nicht knapp darüber
    st = st0 + ev.sum(axis=1)
    vb = replace(block, ev_kw=ev.astype(np.float32))
    out, rech, _ = v2g_lines(vb, np.full(4, 3.0), grid, sized, kva, station_flow=st)
    flow = st - out.sum(axis=1) + rech.sum(axis=1)
    assert out.sum() > 0
    assert ((flow > kva) & (flow < kva + 1e-6)).sum() == 0     # Scheinüberlast; echte Restüberlast bleibt erlaubt
