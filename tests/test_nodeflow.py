import numpy as np
import pytest

from fakes import write_fake_prepared
from gridsim import control
from gridsim.data import load_prepared
from gridsim.nodeflow import NodeBlock, station_block
from gridsim.run import CHARGING, RunParams, flows


def params(**kw):
    base = dict(weather_year=2023, scenario='2040', pv_factor=1.0, charging='uncontrolled', storage='base', n_seeds=1)
    return RunParams(**{**base, **kw})


@pytest.fixture(scope='module')
def tight(tmp_path_factory):
    """Fake prepared mit kleinen Trafos, damit gesteuertes Laden und V2G wirklich eingreifen."""
    return load_prepared(write_fake_prepared(tmp_path_factory.mktemp('p'), kva=(6, 9, 10)), 2023)


@pytest.mark.parametrize('charging', CHARGING)
def test_block_sums_to_station_flow(tight, charging):
    pr = params(charging=charging)
    f = flows(tight, pr, 0)
    for s in range(tight.n_stations):
        block = station_block(tight, pr, f, s)
        assert isinstance(block, NodeBlock)
        n_s = int((np.asarray(tight.nodes_station) == s).sum())
        for a in (block.hh_kw, block.pv_kw, block.wp_kw, block.storage_kw, block.ev_kw, block.v2g_kw):
            assert a.shape == (8760, n_s) and a.dtype == np.float32
        assert block.nodes.tolist() == np.flatnonzero(np.asarray(tight.nodes_station) == s).tolist()
        np.testing.assert_allclose(block.net().sum(axis=1, dtype=np.float64), np.asarray(f['flow'][:, s], float),
                                   atol=1e-3)
        np.testing.assert_allclose(block.ev_kw.sum(axis=1, dtype=np.float64), f['ev_load'][:, s], atol=1e-3)
        np.testing.assert_allclose(block.v2g_kw.sum(axis=1, dtype=np.float64), f['v2g'][:, s], atol=1e-3)
        assert block.ev_kw.min() >= -1e-6


def test_tight_fixture_exercises_control(tight):
    """Die Summentests oben prüfen die Verteilung nur, wenn die Steuerung tatsächlich eingreift."""
    for charging in ('controlled', 'v2g'):
        f = flows(tight, params(charging=charging), 0)
        raw = control.render(f['ev'], f['start'], tight.n_stations)
        assert np.abs(f['ev_load'] - raw).max() > 1.0
    assert np.abs(flows(tight, params(charging='v2g'), 0)['v2g']).max() > 0.5


def test_flows_exposes_storage_delta(tight):
    f = flows(tight, params(), 0)
    idx = np.flatnonzero(np.asarray(tight.nodes_kwh) > 0)
    assert f['storage_idx'].tolist() == idx.tolist()
    assert f['storage_delta'].shape == (8760, len(idx))
    assert np.abs(f['storage_delta']).max() > 0.1


def test_controlled_nodes_keep_own_energy(tight):
    """Gesteuert verschiebt jeder Knoten nur eigene Ladeenergie: nie mehr als ungesteuert."""
    pr = params(charging='controlled')
    f = flows(tight, pr, 0)
    unc = station_block(tight, params(charging='uncontrolled'), flows(tight, params(), 0), 0)
    ctl = station_block(tight, pr, f, 0)
    assert (ctl.ev_kw.sum(axis=0) <= unc.ev_kw.sum(axis=0) + 1e-3).all()
