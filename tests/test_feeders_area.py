import numpy as np

from gridsim.feeders.area import AREAS, classify
from gridsim.feeders.types import SERVICE, TRUNK_CABLE, TRUNK_OVERHEAD


def test_classify_grid_spacing():
    xy = np.array([[x, y] for x in range(0, 200, 20) for y in range(0, 200, 20)], float)
    assert classify(xy, np.ones(len(xy))) == 'stadt'          # 20 m Raster
    assert classify(xy * 3, np.ones(len(xy))) == 'ort'        # 60 m
    assert classify(xy * 6, np.ones(len(xy))) == 'streu'      # 120 m


def test_classify_ignores_halls_and_few_homes():
    xy = np.array([[0, 0], [10, 0], [20, 0], [5000, 0]], float)
    assert classify(xy, np.array([1, 1, 1, 0])) == 'streu'    # < 5 Wohngebäude


def test_areas_pinned():
    assert [(a.name, a.max_nn_m, a.cable_share, a.max_feeder_m) for a in AREAS.values()] == [
        ('stadt', 35.0, 1.0, 500.0), ('ort', 85.0, 0.8, 700.0), ('streu', float('inf'), 0.5, 1000.0)]
    assert list(AREAS) == ['stadt', 'ort', 'streu']


def test_line_types_pinned():
    assert [t.i_max_a for t in TRUNK_CABLE] == [144, 275, 313]
    assert [t.i_max_a for t in TRUNK_OVERHEAD] == [255, 320]
    assert SERVICE[False].i_max_a == 123 and SERVICE[True].i_max_a == 135
    assert [t.name for t in TRUNK_CABLE] == ['NAYY 4x50', 'NAYY 4x150', 'NAYY 4x240']
    assert [t.name for t in TRUNK_OVERHEAD] == ['Al 4x70', 'Al 4x95']
    assert SERVICE[False].name == 'NAYY 4x35' and SERVICE[True].name == 'Al 4x25'
    assert not any(t.overhead for t in TRUNK_CABLE) and all(t.overhead for t in TRUNK_OVERHEAD)
    assert not SERVICE[False].overhead and SERVICE[True].overhead
