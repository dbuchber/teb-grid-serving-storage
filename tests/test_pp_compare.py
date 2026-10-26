"""tools/pp_compare.py: Teile ohne pandapower (Knotenzuordnung, Kennzahlen, Export)."""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import sparse

from test_run import prepared_with_feeders  # noqa: F401  (Fixture)

_spec = importlib.util.spec_from_file_location('pp_compare', Path(__file__).parents[1] / 'tools' / 'pp_compare.py')
ppc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ppc)


def test_attach_segment_takes_deepest():
    # 0 → 1 → 2, 0 → 3; Knoten a hinter 0,1,2; b hinter 0,3; c hinter 0,1
    parent = np.array([-1, 0, 1, 0])
    ds = sparse.csr_matrix(np.array([[1, 1, 1], [1, 0, 1], [1, 0, 0], [0, 1, 0]]))
    assert ppc.attach_segment(parent, ds).tolist() == [2, 3, 1]


def test_stats_floor_and_disagreement():
    gs = np.array([[5.0, 50.0, 99.0], [5.0, 50.0, 101.0]])
    pp = np.array([[6.0, 52.0, 101.0], [np.nan, np.nan, np.nan]])
    st = ppc.stats(pp, gs)
    assert st['n'] == 2                       # 5 % liegt unter der Schwelle, NaN (nicht konvergiert) zählt nicht
    assert st['diff_pp_mean'] == 2.0 and st['over100_disagree'] == 1


def test_export_writes_station_files(prepared_with_feeders, tmp_path):  # noqa: F811
    ppc.export(prepared_with_feeders, 2023, '2040', 'uncontrolled', 0, [0, 1], tmp_path / 'x', tmp_path / 'svg')
    z = np.load(tmp_path / 'x' / '0.npz')
    assert z['node_p_kw'].shape[0] == 24 and z['gs_pct'].shape == (24, len(z['parent']))
    # Summe der Knoten hinter den Wurzelabschnitten = Summe der Wurzelflüsse (ohne Zuschlag)
    roots = z['parent'] < 0
    assert np.allclose(z['gs_flow_kw'][:, roots].sum(1), z['node_p_kw'].sum(1), atol=1e-3)
    assert list((tmp_path / 'svg').glob('stichprobe-*-0.svg'))
    assert (tmp_path / 'x' / 'sample.json').exists()
