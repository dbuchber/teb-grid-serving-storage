import numpy as np
import pytest

from fakes import FEEDER_NODE_OFFSET_M, write_fake_prepared
from gridsim.data import load_prepared
from gridsim.feeders.loading import loading_pct, segment_flow, surcharge_factor
from gridsim.feeders.sizing import DesignRule, SizedGrid, design_flows, size
from gridsim.feeders.topology import build_station_grid
from gridsim.nodeflow import station_block
from gridsim.run import RunParams, flows

KWH_PER_HH = 3000


def fake_feeder(p, s):
    """Netz einer Fake-Station per Luftlinie (roads=None) und Bemessung mit einfachen Auslegungslasten."""
    nodes = np.flatnonzero(np.asarray(p.nodes_station) == s)
    xy = np.asarray(FEEDER_NODE_OFFSET_M, dtype=float)[nodes]
    hh = np.asarray(p.nodes_hh)[nodes]
    kwp = np.asarray(p.nodes_kwp_bins, dtype=float)[nodes].sum(axis=1)
    grid = build_station_grid(s, (0.0, 0.0), nodes, xy, hh, kwp, None)
    load, feed = design_flows(grid, hh, np.ones(len(nodes)), kwp, DesignRule(wp_share=1.0, ev_share=0.5, h0_peak_kw=0.0))
    return grid, size(grid, load, feed)


@pytest.fixture(scope='module')
def case(tmp_path_factory):
    p = load_prepared(write_fake_prepared(tmp_path_factory.mktemp('p')), 2023)
    pr = RunParams(weather_year=2023, scenario='2040', charging='uncontrolled', n_seeds=1)
    return p, pr, flows(p, pr, 0)


@pytest.mark.parametrize('s', [0, 1, 2])
def test_root_segments_sum_without_surcharge(case, s):
    p, pr, f = case
    grid, sized = fake_feeder(p, s)
    block = station_block(p, pr, f, s)
    seg = segment_flow(grid, sized, block, surcharge=False)
    assert seg.shape == (8760, len(grid.parent))
    root = grid.parent == -1
    np.testing.assert_allclose(seg[:, root].sum(axis=1, dtype=np.float64), f['flow'][:, s], atol=1e-3)


def test_segment_flow_adds_surcharge_on_household_part(case):
    p, pr, f = case
    grid, sized = fake_feeder(p, 0)
    block = station_block(p, pr, f, 0)
    plain = segment_flow(grid, sized, block, surcharge=False)
    with_s = segment_flow(grid, sized, block)
    d = grid.downstream.astype(np.float32)
    n_hh = d @ np.asarray(p.nodes_hh, dtype=float)[grid.node_index]
    fac = surcharge_factor(n_hh, float(np.max(p.h0)) * KWH_PER_HH)
    hh_seg = (d @ block.hh_kw.T.astype(np.float64)).T
    np.testing.assert_allclose(with_s, plain + (fac - 1)[None, :] * hh_seg, atol=1e-3)
    assert (with_s >= plain - 1e-4).all() and (with_s > plain + 0.1).any()


def test_segment_flow_station_without_households_unchanged(case):
    """Station 2 hat nur PV-Hallen (hh = 0): kein Zuschlag, keine Division durch null."""
    p, pr, f = case
    grid, sized = fake_feeder(p, 2)
    block = station_block(p, pr, f, 2)
    a, b = segment_flow(grid, sized, block), segment_flow(grid, sized, block, surcharge=False)
    assert np.isfinite(a).all()
    np.testing.assert_array_equal(a, b)


def test_surcharge_only_small_groups(case):
    p = case[0]
    peak = float(np.max(p.h0)) * KWH_PER_HH
    f = surcharge_factor(np.array([0, 1, 500]), peak)
    assert f[0] == 1.0
    assert f[1] > 1.0
    assert f[2] == pytest.approx(1.0)


def test_loading_direction_pf():
    sized = SizedGrid(types=['NAYY 4x150'], parallel=np.array([1], np.int8), i_max_a=np.array([275.0]),
                      r_ohm=np.zeros(1), x_ohm=np.zeros(1), du_load_pct=np.zeros(1), du_feed_pct=np.zeros(1),
                      marked=np.zeros(1, bool))
    pct = loading_pct(np.array([[100.0], [-100.0], [0.0]]), sized)
    feed = 100.0 * 100e3 / (np.sqrt(3) * 400.0) / 275.0
    assert pct[1, 0] == pytest.approx(feed, rel=1e-5)
    assert pct[0, 0] == pytest.approx(feed / 0.97, rel=1e-5)
    assert pct[2, 0] == 0.0


def test_loading_uses_effective_limit_with_parallel():
    """``i_max_a`` enthält die Parallelführung schon: nicht noch einmal mit ``parallel`` multiplizieren."""
    sized = SizedGrid(types=['NAYY 4x240'], parallel=np.array([2], np.int8), i_max_a=np.array([626.0]),
                      r_ohm=np.zeros(1), x_ohm=np.zeros(1), du_load_pct=np.zeros(1), du_feed_pct=np.zeros(1),
                      marked=np.zeros(1, bool))
    pct = loading_pct(np.array([[-100.0]]), sized)
    assert pct[0, 0] == pytest.approx(100.0 * 100e3 / (np.sqrt(3) * 400.0) / 626.0, rel=1e-5)
