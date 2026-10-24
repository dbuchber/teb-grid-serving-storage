"""Integrationstest mit den echten Eingaben (nur auf hetzner, GRIDSIM_INPUT gesetzt)."""
import os
from pathlib import Path

import pytest

from gridsim.data import load_prepared

pytestmark = pytest.mark.skipif('GRIDSIM_INPUT' not in os.environ, reason='nur auf hetzner mit GRIDSIM_INPUT')


def test_prepare_real(tmp_path):
    from gridsim.prepare import prepare
    p = load_prepared(prepare(Path(os.environ['GRIDSIM_INPUT']), 2012, tmp_path), 2012)
    assert len(p.stations) == 257
    assert int(p.nodes_fw.sum()) == 1043  # Fernwärme-MFH laut Session 18
    assert abs(float(p.pv_bins.sum(axis=0).mean()) - 1000) < 300  # kWh je kWp und Jahr
    assert p.h0_q.shape == (35040,) and abs(float(p.h0_q.sum()) - 1) < 1e-3
    assert p.temp_cells.shape[0] == 8760 and int(p.nodes_cell.max()) < p.temp_cells.shape[1]
    assert set(p.nodes_station) == set(range(257))
