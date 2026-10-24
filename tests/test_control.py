import numpy as np
import pytest

from fakes import big_prepared, write_fake_prepared
from gridsim import control, legacy, profiles
from gridsim.data import load_prepared
from gridsim.profiles import EvEvents

sim = legacy.load('steyr_sim_variant_a')
v2g_legacy = legacy.load('steyr_v2g_demo')
wpev = legacy.load('steyr_wp_ev')


def events(arrive, kwh, kw, station=None):
    arrive = np.asarray(arrive, dtype=np.int32)
    n = len(arrive)
    station = np.zeros(n, dtype=np.int32) if station is None else np.asarray(station, dtype=np.int32)
    return EvEvents(node=np.arange(n, dtype=np.int32), station=station, arrive_h=arrive,
                    kwh_grid=np.asarray(kwh, dtype=np.float32), kw=np.asarray(kw, dtype=np.float32),
                    deadline_h=((arrive // 24 + 1) * 24 + 7).astype(np.int32))


def test_render_energy_and_power():
    ev = events([18, 40], [10.0, 25.0], [11.0, 3.7])
    hourly = control.render(ev, ev.arrive_h, 1)
    assert hourly.sum() == pytest.approx(35.0, rel=1e-5)
    assert hourly.max() <= 11.0 + 1e-6
    assert hourly[18, 0] == pytest.approx(10.0)  # 10 kWh in der ersten Stunde mit 11 kW
    q = control.render(ev, ev.arrive_h, 1, step_h=0.25, hours=8760)
    assert q.shape == (35040, 1) and q.sum() * 0.25 == pytest.approx(35.0, rel=1e-5)


def test_winap_starts_at_23_in_winter():
    jan, jul = 10 * 24 + 18, 190 * 24 + 18
    ev = events([jan, jul], [10.0, 10.0], [11.0, 11.0])
    start = control.start_winap(ev, 2023)
    assert start[0] == 10 * 24 + 23 and start[1] == jul


def test_winap_keeps_arrival_if_not_done_by_7():
    ev = events([10 * 24 + 18], [40.0], [3.7])  # 10,8 h Ladedauer > 8 h
    assert control.start_winap(ev, 2023)[0] == 10 * 24 + 18


def test_winap_creates_synchronous_peak():
    p = big_prepared(n_homes=200, n_stations=1)
    ev = profiles.ev_events(p, np.ones(200, dtype=int), np.random.default_rng(1))
    unc = control.render(ev, control.start_uncontrolled(ev), 1)
    win = control.render(ev, control.start_winap(ev, 2023), 1)
    assert win.max() > unc.max()


def test_t3d_staggers_within_station():
    d = 15
    ev = events([d * 24 + 18] * 30, [5.0] * 30, [11.0] * 30)  # 30 Autos an einer Station
    signal = np.zeros((1, 365), dtype=bool)
    signal[0, d] = True
    start = control.start_t3d(ev, signal, 2023)
    assert set(start) == {d * 24 + 22, (d + 1) * 24, (d + 1) * 24 + 2}
    assert np.bincount(control.node_group(ev.node), minlength=3).min() >= 5  # Gruppen etwa gleich groß


def test_t3d_without_signal_is_winap():
    ev = events([15 * 24 + 18], [5.0], [11.0])
    start = control.start_t3d(ev, np.zeros((1, 365), dtype=bool), 2023)
    assert start[0] == control.start_winap(ev, 2023)[0]


def test_t3d_peak_below_winap():
    p = big_prepared(n_homes=300, n_stations=1)
    ev = profiles.ev_events(p, np.ones(300, dtype=int), np.random.default_rng(2))
    signal = np.ones((1, 365), dtype=bool)
    win = control.render(ev, control.start_winap(ev, 2023), 1)[:, 0]
    t3d = control.render(ev, control.start_t3d(ev, signal, 2023), 1)[:, 0]
    assert t3d.max() < win.max()   # an derselben Station: keine neue Spitze
    assert t3d.sum() == pytest.approx(win.sum(), rel=2e-3)  # Jahresende: Ladung nach 31.12. entfällt (wie legacy)


def test_node_group_is_stable():
    g = control.node_group(np.arange(100))
    assert list(g) == list(control.node_group(np.arange(100))) and set(g) == {0, 1, 2}


def test_engpass_signal_evening_window():
    flow = np.zeros((8760, 2))
    flow[5 * 24 + 19, 0] = 500
    flow[6 * 24 + 12, 1] = 500  # mittags: kein Abendsignal
    s = control.engpass_signal(flow, np.array([400.0, 400.0]))
    assert s.shape == (2, 365) and s[0, 5] and s.sum() == 1


def test_controlled_never_exceeds_kva():
    rng = np.random.default_rng(3)
    f0 = rng.uniform(100, 380, (8760, 4))
    ev = rng.uniform(0, 80, (8760, 4))
    kva = np.full(4, 400.0)
    out, unmet = control.controlled(f0, ev, kva)
    assert (f0 + out <= kva + 1e-6).all()
    assert unmet.shape == (4, 365)


def test_controlled_matches_legacy_single_station():
    rng = np.random.default_rng(4)
    f0 = rng.uniform(100, 390, 8760)
    ev = rng.uniform(0, 60, 8760)
    old, old_unmet = v2g_legacy.controlled(f0, ev, 400.0)
    new, unmet = control.controlled(f0[:, None], ev[:, None], np.array([400.0]))
    assert np.allclose(new[:, 0], old)
    assert np.isclose(unmet.sum(), old_unmet.sum())


def test_v2g_caps():
    residual = np.zeros((8760, 1))
    residual[10 * 24 + 18: 10 * 24 + 22, 0] = 50.0
    out = control.v2g(residual, np.array([2]))
    assert (out <= residual + 1e-9).all()
    assert out.max() <= 11 * 0.7 * 2 + 1e-9
    assert out[10 * 24 + 12: 11 * 24 + 12].sum() <= 15 * 0.7 * 2 + 1e-9


def test_storage_flow_matches_legacy_base(tmp_path):
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    heat, _ = profiles.assign(p, '2040', np.random.default_rng(5))
    wp_st, wp_sto = profiles.heat_pump(p, heat, seed=5)
    flow = control.storage_flow(p, 1.5, 'base', wp_st, wp_sto)
    limits, shifts = wpev.spread(len(heat), 5)
    dhw = np.where(np.isnan(p.nodes_dhw), wpev.DHW_SHARE, p.nodes_dhw)
    wp_node = wpev.heat_pump_kw_cells(np.asarray(p.temp_cells, float), heat, np.asarray(p.nodes_cell), limits, shifts, dhw)
    pv = (np.asarray(p.pv_bins) @ np.asarray(p.nodes_kwp_bins).T) * 1.5
    load = np.asarray(p.h0)[:, None] * sim.KWH_PER_HH * np.asarray(p.nodes_hh)[None, :] + wp_node
    net = sim.simulate(pv, load, np.asarray(p.nodes_kwh, float), 'base')
    ref = np.column_stack([net[:, p.nodes_station == s].sum(axis=1) for s in range(3)])
    assert np.allclose(flow, ref, rtol=1e-4, atol=1e-3)


def test_t3d_signal_forecasts_winap_peak():
    d = 20  # Jänner
    arrive = [d * 24 + h for h in (16, 16, 17, 17, 18, 18, 19, 19, 20, 20)]
    ev = events(arrive, [8.0] * 10, [11.0] * 10)  # gemeinsam 80 kW ab 23 Uhr
    base = np.zeros((8760, 1))
    kva = np.array([50.0])
    assert control.render(ev, ev.arrive_h, 1).max() < 50          # ungesteuert kein Engpass
    assert control.render(ev, control.start_winap(ev, 2023), 1).max() > 50  # WiNAP erzeugt ihn
    start = control.start_t3d_forecast(ev, base, kva, 2023)
    assert len(set(start)) > 1                                     # Signal erkannt → gestaffelt
    assert control.render(ev, start, 1).max() < control.render(ev, control.start_winap(ev, 2023), 1).max()
