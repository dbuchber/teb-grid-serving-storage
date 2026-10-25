import numpy as np
import pytest
from scipy import sparse

from scipy.stats import binom

from gridsim.feeders.sizing import DesignRule, design_flows, g, p_ev, size
from gridsim.feeders.topology import StationGrid


def make_grid(parent, length, service, feeder, ends, overhead=None, area='stadt'):
    """Handgebautes StationGrid; ``ends[i]`` = Endabschnitt des Knotens i (Pfad = Kette der Eltern)."""
    parent = np.asarray(parent, np.int32)
    m, n = len(parent), len(ends)
    rows, cols = [], []
    for i, j in enumerate(ends):
        while j >= 0:
            rows.append(j), cols.append(i)
            j = parent[j]
    down = sparse.csr_matrix((np.ones(len(rows), np.int8), (rows, cols)), shape=(m, n))
    feeder = np.asarray(feeder, np.int16)
    return StationGrid(
        station=0, area=area, node_index=np.arange(n), parent=parent,
        length_m=np.asarray(length, np.float32), feeder=feeder,
        service=np.asarray(service, bool),
        overhead=np.zeros(m, bool) if overhead is None else np.asarray(overhead, bool),
        downstream=down, marked=np.zeros(feeder.max() + 1, bool), geometry=[None] * m)


def one_section(length_m, overhead=False):
    return make_grid([-1], [length_m], [False], [0], [0], overhead=[overhead])


def test_g_values():
    assert g(np.array([1]))[0] == pytest.approx(1.0)
    assert g(np.array([0]))[0] == 0.0
    assert g(np.array([100]))[0] == pytest.approx(0.07 + 0.93 * 100 ** -0.75)


def test_p_ev_anchor_points():
    assert p_ev(np.array([1, 10]))[:].round(2).tolist() == [11.0, 1.1]
    assert p_ev(np.array([0]))[0] == 0.0
    assert p_ev(np.array([224.0]))[0] == pytest.approx(0.54, abs=0.01)
    assert p_ev(np.array([2.5]))[0] > 0                              # Gleitkomma erlaubt


NO_DEVICES = DesignRule(wp_share=0.0, ev_share=0.0, h0_peak_kw=0.0)


def star(n_nodes):
    """Trunk 0 mit ``n_nodes`` Hausanschlüssen (Knoten i an Abschnitt i + 1)."""
    return make_grid([-1] + [0] * n_nodes, [50] + [10] * n_nodes, [False] + [True] * n_nodes, [0] * (n_nodes + 1),
                     list(range(1, n_nodes + 1)))


def test_household_term_at_least_h0_peak():
    """Fix-Runde 1: Haushaltslast je Abschnitt = n · max(P_HH · g(n), H0-Spitze), nie unter n · H0-Spitze."""
    gr = star(10)
    hh = np.full(10, 5)                                  # 50 Haushalte am Trunk, 5 je Hausanschluss
    rule = DesignRule(wp_share=0.0, ev_share=0.0, h0_peak_kw=0.79)
    load, _ = design_flows(gr, hh, np.zeros(10), np.zeros(10), rule)
    assert 2.0 * g(np.array([50]))[0] < 0.79              # ohne Fix läge die Auslegung darunter
    assert load[0] == pytest.approx(50 * 0.79)
    assert (load >= 0.79 * np.r_[50, hh] - 1e-9).all()
    # kleine Kollektive: P_HH · g(n) bleibt maßgebend
    load, _ = design_flows(one_section(50), np.array([1]), np.zeros(1), np.zeros(1), rule)
    assert load[0] == pytest.approx(2.0)


def test_devices_binomial_p90():
    """Fix-Runde 1: k = P90 der Binomialverteilung ganzer Geräte; WP mit voller Leistung, E-Autos k · p_ev(k)."""
    gr = star(20)
    hh = np.ones(20, int)
    wp_kw = np.full(20, 10.0)
    wp_kw[0] = 0.0                                       # Knoten 0 kann keine WP haben (z. B. Fernwärme)
    rule = DesignRule(wp_share=0.15, ev_share=0.08, h0_peak_kw=0.0)
    load, _ = design_flows(gr, hh, wp_kw, np.zeros(20), rule)
    k_wp = binom.ppf(0.9, 19, 0.15)
    k_ev = binom.ppf(0.9, 20, 0.08)
    assert k_wp == 5 and k_ev == 3
    hh_part = 2.0 * g(np.array([20]))[0] * 20
    assert load[0] == pytest.approx(hh_part + k_wp * 10.0 + k_ev * p_ev(np.array([k_ev]))[0])
    # ein Haushalt: P(keine WP) = 0,85 < 0,9 → eine ganze WP; P(kein Auto) = 0,92 ≥ 0,9 → kein Auto
    assert load[2] == pytest.approx(2.0 + 10.0)


def test_design_flows_without_homes_or_devices():
    gr = one_section(50)
    load, _ = design_flows(gr, np.array([0]), np.array([0.0]), np.array([0.0]),
                           DesignRule(wp_share=0.15, ev_share=0.08, h0_peak_kw=0.79))
    assert load[0] == 0.0 and np.isfinite(load).all()


def test_design_flows_feed_sums_downstream():
    gr = make_grid([-1, 0, 0], [50, 10, 10], [False, True, True], [0, 0, 0], [1, 2])
    _, feed = design_flows(gr, np.array([1, 3]), np.zeros(2), np.array([0.0, 8.0]), NO_DEVICES)
    assert feed.tolist() == [8.0, 0.0, 8.0]


def test_size_picks_smallest_thermal():
    s = size(one_section(50), np.array([60.0]), np.array([0.0]))
    assert s.types == ['NAYY 4x50']
    assert s.i_max_a[0] == 144 and s.parallel[0] == 1
    s = size(one_section(50), np.array([150.0]), np.array([0.0]))
    assert s.types == ['NAYY 4x150']
    assert not s.marked.any()


def test_size_feed_in_uses_cos_phi_one():
    # 100 kW Einspeisung = 144,3 A > 144 A (4x50); als Bezug mit cos 0,97 wären es 148,8 A, hier zählt 1,0
    s = size(one_section(10), np.array([0.0]), np.array([100.0]))
    assert s.types == ['NAYY 4x150']
    s = size(one_section(10), np.array([0.0]), np.array([99.0]))
    assert s.types == ['NAYY 4x50']


def test_size_overhead_uses_overhead_list():
    s = size(one_section(50, overhead=True), np.array([60.0]), np.array([0.0]))
    assert s.types == ['Al 4x70']
    assert s.i_max_a[0] == 255


def test_size_voltage_drop_upgrades():
    s = size(one_section(600), np.array([60.0]), np.array([0.0]))
    assert s.types[0] != 'NAYY 4x50'
    assert s.du_load_pct.max() <= 5.0
    assert not s.marked.any()


def test_size_upgrades_segment_with_largest_contribution():
    # Kette A (100 m) -> B (500 m); B trägt weniger Strom, aber den größeren Spannungsfall
    gr = make_grid([-1, 0], [100, 500], [False, False], [0, 0], [1])
    s = size(gr, np.array([60.0, 60.0]), np.array([0.0, 0.0]))
    assert s.du_load_pct.max() <= 5.0
    assert s.types[1] != 'NAYY 4x50'
    assert s.types[0] == 'NAYY 4x50' or s.types[0] == s.types[1]


def test_size_parallel_after_largest_type():
    # 1 000 m, 100 kW: mit 4x240 9,1 %, mit 2 x 4x240 4,5 %
    s = size(one_section(1000), np.array([100.0]), np.array([0.0]))
    assert s.types == ['NAYY 4x240'] and s.parallel[0] == 2
    assert s.du_load_pct.max() <= 5.0 and not s.marked.any()
    assert s.i_max_a[0] == 2 * 313


def test_size_marks_impossible():
    s = size(one_section(2000), np.array([200.0]), np.array([0.0]))
    assert s.marked.tolist() == [True]
    assert s.types == ['NAYY 4x240'] and s.parallel[0] == 2


def test_size_marks_only_failing_feeder():
    gr = make_grid([-1, -1], [50, 2000], [False, False], [0, 1], [0, 1])
    s = size(gr, np.array([60.0, 200.0]), np.array([0.0, 0.0]))
    assert s.marked.tolist() == [False, True]
    assert gr.marked.tolist() == [False, False]                      # Topologie-Markierung unberührt


def test_size_feed_in_limit_three_percent():
    s = size(one_section(400), np.array([0.0]), np.array([60.0]))
    assert s.du_feed_pct.max() <= 3.0
    assert s.types[0] != 'NAYY 4x50'


def test_size_service_fixed_and_zero_length():
    gr = make_grid([-1, 0, 0], [50, 0, 30], [False, True, True], [0, 0, 0], [1, 2], overhead=[False, False, True])
    s = size(gr, np.array([20.0, 5.0, 5.0]), np.array([0.0, 0.0, 0.0]))
    assert s.types[1] == 'NAYY 4x35' and s.types[2] == 'Al 4x25'
    assert s.i_max_a[1] == 123 and s.i_max_a[2] == 135
    assert s.r_ohm[1] == 0.0 and s.x_ohm[1] == 0.0
    assert (s.parallel == 1).all()


def test_halls_only_station():
    # alle hh == 0: kein Fehler, Auslegung nur aus Einspeisung
    gr = make_grid([-1, -1], [80, 120], [False, False], [0, 1], [0, 1])
    load, feed = design_flows(gr, np.zeros(2, int), np.zeros(2), np.array([200.0, 0.0]), NO_DEVICES)
    assert np.isfinite(load).all() and (load == 0).all()
    assert feed.tolist() == [200.0, 0.0]
    s = size(gr, load, feed)
    assert s.types[0] == 'NAYY 4x240'                                # 289 A Einspeisung > 275 A (4x150)
    assert s.types[1] == 'NAYY 4x50'
    assert np.isfinite(s.du_load_pct).all() and (s.du_load_pct == 0).all()
