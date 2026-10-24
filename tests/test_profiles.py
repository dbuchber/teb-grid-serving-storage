import time

import numpy as np
import pytest

from fakes import big_prepared, write_fake_prepared
from gridsim import legacy, profiles
from gridsim.data import load_prepared

wpev = legacy.load('steyr_wp_ev')


def test_assign_shares_and_fw():
    p = big_prepared(n_homes=4000)
    heat, cars = profiles.assign(p, '2040', np.random.default_rng(3))
    homes = p.nodes_hh > 0
    assert abs((heat[homes] > 0).mean() - 0.70) < 0.05   # Anteil über alle Wohngebäude bleibt
    assert not (heat[p.nodes_fw] > 0).any()              # Fernwärme: keine Wärmepumpe
    assert np.allclose(heat[heat > 0], p.nodes_heat_kwh[heat > 0])
    share_ev = cars.sum() / p.nodes_hh.sum()
    assert abs(share_ev - 0.60) < 0.03


def test_assign_pauschal_without_lod1():
    p = big_prepared(n_homes=200)
    p.nodes_heat_kwh[:] = np.nan
    heat, _ = profiles.assign(p, '2040', np.random.default_rng(3))
    efh = (heat > 0) & (p.nodes_hh == 1)
    assert np.all(heat[efh] == wpev.HEAT_KWH_EFH)


def _ev_setup(n_cars):
    p = big_prepared(n_homes=n_cars)
    cars = np.ones(n_cars, dtype=int)
    return p, cars


def test_ev_energy_conserved():
    p, cars = _ev_setup(300)
    ev = profiles.ev_events(p, cars, np.random.default_rng(5))
    t_day = p.temp_cells.mean(axis=1).reshape(365, 24).mean(axis=1)
    kwh_day = wpev.KM_PER_YEAR / 365 * wpev.KWH_PER_KM * (1 + wpev.COLD_PER_K * np.maximum(15 - t_day, 0))
    charged = ev.kwh_grid.sum() * wpev.EV_ETA
    demand = kwh_day.sum() * cars.sum()  # Erwartungswert (Faktor 0,5–1,5 im Mittel 1)
    assert demand * 0.9 < charged < demand * 1.1 + wpev.EV_CHARGE_KWH * cars.sum()
    assert np.all(np.isclose(ev.kw, wpev.EV_KW_FAST) | np.isclose(ev.kw, wpev.EV_KW_SLOW))
    assert (ev.deadline_h > ev.arrive_h).all()


def test_ev_arrivals_evening():
    p, cars = _ev_setup(500)
    ev = profiles.ev_events(p, cars, np.random.default_rng(6))
    day = ev.arrive_h // 24
    weekday = (day + p.first_weekday) % 7 < 5
    hour = ev.arrive_h[weekday] % 24
    assert ((hour >= 15) & (hour <= 21)).mean() > 0.9


def test_ev_events_match_legacy_stats():
    p, cars = _ev_setup(500)
    temp = np.asarray(p.temp_cells.mean(axis=1), dtype=float)
    old = wpev.ev_kw(cars, temp, np.random.default_rng(7), p.first_weekday).sum(axis=1)
    ev = profiles.ev_events(p, cars, np.random.default_rng(8))
    new = np.zeros(8760)
    for a, e, k in zip(ev.arrive_h, ev.kwh_grid, ev.kw):  # einfache Referenz-Darstellung
        h = a
        while e > 1e-9 and h < 8760:
            step = min(k, e); new[h] += step; e -= step; h += 1
    assert new.sum() == pytest.approx(old.sum(), rel=0.05)
    peak_old = old.reshape(365, 24).mean(axis=0).argmax()
    peak_new = new.reshape(365, 24).mean(axis=0).argmax()
    assert abs(int(peak_old) - int(peak_new)) <= 1


def test_ev_events_speed():
    p, cars = _ev_setup(20000)
    t = time.perf_counter()
    profiles.ev_events(p, cars, np.random.default_rng(9))
    assert time.perf_counter() - t < 2.0


def test_heat_pump_matches_legacy():
    p = big_prepared(n_homes=300, n_stations=5)
    heat, _ = profiles.assign(p, '2030', np.random.default_rng(2))
    st_sum, storage_nodes = profiles.heat_pump(p, heat, seed=11)
    limits, shifts = wpev.spread(len(heat), 11)
    dhw = np.where(np.isnan(p.nodes_dhw), wpev.DHW_SHARE, p.nodes_dhw)
    old = wpev.heat_pump_kw_cells(np.asarray(p.temp_cells, float), heat, np.asarray(p.nodes_cell), limits, shifts, dhw)
    old_st = np.column_stack([old[:, p.nodes_station == s].sum(axis=1) for s in range(5)])
    assert st_sum.shape == (8760, 5)
    assert np.allclose(st_sum, old_st, rtol=1e-4, atol=1e-3)
    idx = np.flatnonzero(p.nodes_kwh > 0)
    assert storage_nodes.shape == (8760, len(idx))
    assert np.allclose(storage_nodes, old[:, idx], rtol=1e-4, atol=1e-4)


def test_station_without_homes_has_zero_load(tmp_path):
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    heat, cars = profiles.assign(p, '2040', np.random.default_rng(1))
    st_sum, _ = profiles.heat_pump(p, heat, seed=1)
    ev = profiles.ev_events(p, cars, np.random.default_rng(1))
    assert not st_sum[:, 2].any()
    assert not (ev.station == 2).any()


def test_station_sum():
    p = big_prepared(n_homes=40, n_stations=4)
    vals = np.ones((8760, 40), dtype=np.float32)
    out = profiles.station_sum(vals, p)
    assert out.shape == (8760, 4) and np.allclose(out[0], 10)
