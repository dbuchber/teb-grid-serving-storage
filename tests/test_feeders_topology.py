import numpy as np
import pytest

from fakes import ROADS_CENTER, ROADS_HALF, fake_roads
from gridsim.feeders.area import AREAS
from gridsim.feeders.roads import TO_LAMBERT, RoadGraph
from gridsim.feeders.topology import LINE_DETOUR, MAX_BUILDINGS, build_station_grid


@pytest.fixture(scope='module')
def roads(tmp_path_factory):
    return RoadGraph(fake_roads(tmp_path_factory.mktemp('roads') / 'roads.json'))


def arm(direction):
    """Ursprung (Kreuzung) und Einheitsvektor eines Straßenarms in EPSG:31287."""
    lon, lat = ROADS_CENTER
    dlon, dlat = ROADS_HALF
    end = {'ost': (lon + dlon, lat), 'west': (lon - dlon, lat), 'nord': (lon, lat + dlat)}[direction]
    c = np.array(TO_LAMBERT.transform(lon, lat))
    v = np.array(TO_LAMBERT.transform(*end)) - c
    return c, v / np.hypot(*v)


def along(direction, s, offset=10.0):
    """Gebäude ``s`` m entlang des Arms, ``offset`` m neben der Straße."""
    c, v = arm(direction)
    s = np.atleast_1d(np.asarray(s, float))
    return c + s[:, None] * v + offset * np.array([-v[1], v[0]])


def build(xy, hh=None, kwp=None, roads=None, st_xy=None):
    n = len(xy)
    hh = np.ones(n, np.int16) if hh is None else np.asarray(hh)
    kwp = np.zeros(n, np.float32) if kwp is None else np.asarray(kwp, np.float32)
    st_xy = arm('ost')[0] if st_xy is None else np.asarray(st_xy, float)
    node_index = np.arange(100, 100 + n)
    g = build_station_grid(7, st_xy, node_index, np.asarray(xy, float), hh, kwp, roads)
    check_invariants(g, n)
    return g


def check_invariants(g, n):
    m = len(g.parent)
    assert g.station == 7 and len(g.node_index) == n
    for a in (g.length_m, g.feeder, g.service, g.overhead):
        assert a.shape == (m,)
    assert g.downstream.shape == (m, n) and len(g.geometry) == m
    assert g.parent.dtype == np.int32 and g.length_m.dtype == np.float32 and g.feeder.dtype == np.int16
    assert all(g.parent[j] < j for j in range(m))                 # Eltern vor Kindern
    child = g.parent >= 0
    assert (g.feeder[child] == g.feeder[g.parent[child]]).all()   # Kinder bleiben im Abgang
    assert (g.overhead[child] == g.overhead[g.parent[child]]).all()
    assert not g.service[g.parent[child]].any()                   # Hausanschluss ist immer Blatt
    assert len(g.marked) == (g.feeder.max() + 1 if m else 0)
    d = g.downstream.toarray().astype(int)
    assert set(np.unique(d)) <= {0, 1}
    for j in range(m):                                            # Zeile = eigener Endknoten + Kinderzeilen
        kids = np.flatnonzero(g.parent == j)
        own = d[j] - d[kids].sum(axis=0)
        assert own.min() >= 0 and own.sum() == (0 if len(kids) else 1)
    assert (g.length_m >= 0).all()


def per_feeder(g):
    """Gebäude je Abgang aus den Abschnitten ab der Sammelschiene."""
    d = g.downstream.toarray()
    roots = np.flatnonzero(g.parent == -1)
    return np.bincount(g.feeder[roots], weights=d[roots].sum(axis=1), minlength=len(g.marked))


def reach(g):
    """Weglänge Sammelschiene -> Gebäude je Knoten."""
    return g.downstream.T @ g.length_m.astype(float)


def test_downstream_root_rows_cover_all_nodes(roads):
    xy = np.vstack([along('ost', np.arange(30, 400, 35)), along('west', np.arange(30, 300, 35)),
                    along('nord', [50, 120, 200], offset=-15)])
    kwp = np.zeros(len(xy))
    kwp[3] = 45.0
    g = build(xy, kwp=kwp, roads=roads)
    roots = g.parent == -1
    assert (g.downstream[np.flatnonzero(roots)].toarray().sum(axis=0) == 1).all()
    assert g.service.sum() == len(xy) - 1                         # alle außer dem Direktabgang
    assert g.area in AREAS


def test_feeder_split_limits_buildings(roads):
    xy = np.vstack([along('ost', 40.0 * np.arange(1, 36)), along('west', 40.0 * np.arange(1, 36))])
    g = build(xy, roads=roads)
    assert g.area == 'ort'
    counts = per_feeder(g)
    assert counts.sum() == 70 and counts.max() <= MAX_BUILDINGS
    assert len(counts) >= 3


def test_long_feeder_marked(roads):
    xy = np.vstack([along('ost', 10.0 * np.arange(1, 9)), along('ost', [1500.0])])
    g = build(xy, roads=roads)
    assert g.area == 'stadt'
    assert g.marked.any()
    r = reach(g)
    assert r[-1] > AREAS['stadt'].max_feeder_m
    # Teilung trennt das ferne Gebäude ab: nur sein Abgang ist markiert, der nahe nicht
    d = g.downstream.toarray()
    far_feeders = set(g.feeder[d[:, -1] > 0])
    assert far_feeders == set(np.flatnonzero(g.marked))
    assert not set(g.feeder[d[:, 0] > 0]) & far_feeders


def test_direct_feeder_for_large_pv(roads):
    xy = np.vstack([along('ost', 20.0 * np.arange(1, 7)), along('nord', [200.0])])
    hh = np.array([1] * 6 + [0])
    kwp = np.array([5.0] * 6 + [40.0])
    g = build(xy, hh=hh, kwp=kwp, roads=roads)
    d = g.downstream.toarray()
    segs = np.flatnonzero(d[:, -1])
    assert len(segs) == 1                                         # genau ein Abschnitt: der eigene Abgang
    j = segs[0]
    assert g.parent[j] == -1 and not g.service[j]
    assert d[j].sum() == 1
    assert (g.feeder == g.feeder[j]).sum() == 1                   # Abgang gehört der Anlage allein
    assert g.length_m[j] == pytest.approx(reach(g)[-1]) and g.length_m[j] > 200.0


def overhead_share(g):
    trunk = ~g.service
    return g.length_m[trunk & g.overhead].sum() / g.length_m[trunk].sum()


@pytest.mark.parametrize('area, spacing, side', [('ort', 50.0, 15), ('streu', 120.0, 12)])
def test_overhead_share_near_target(area, spacing, side):
    """Freileitungsanteil liegt auf ±10 Prozentpunkte am Ziel (Station mit ≥ 5 Abgängen), ohne Überschießen."""
    st = np.array([600000.0, 380000.0])
    half = (side - 1) / 2 * spacing
    grid = np.array([[x, y] for x in np.linspace(-half, half, side) for y in np.linspace(-half, half, side)])
    g = build(grid + st + [spacing / 3, spacing / 3], st_xy=st)
    assert g.area == area
    assert len(g.marked) >= 5
    target = 1 - AREAS[area].cable_share
    assert abs(overhead_share(g) - target) <= 0.10
    assert g.overhead.any() and not g.overhead.all()


def test_overhead_share_stadt_zero():
    grid = np.array([[x, y] for x in range(-100, 101, 20) for y in range(-100, 101, 20)], float)
    g = build(grid + [600000.0, 380000.0], st_xy=[600000.0, 380000.0])
    assert g.area == 'stadt'
    assert not g.overhead.any()


def test_overhead_feeders_closer_rule():
    """Ein Abgang kommt nur dazu, wenn der Anteil dadurch näher ans Ziel rückt."""
    from gridsim.feeders.topology import _overhead_feeders
    # Ziel 20 % von 1000 m = 200 m: 600 m würde überschießen (|600−200| > 200), 150 + 50 trifft genau
    oh = _overhead_feeders(np.array([600.0, 150.0, 100.0, 50.0, 100.0]), 0.8)
    assert oh.tolist() == [False, True, False, True, False]
    assert not _overhead_feeders(np.array([300.0, 200.0]), 1.0).any()
    assert not _overhead_feeders(np.zeros(3), 0.5).any()


@pytest.mark.parametrize('far_station', [False, True])
def test_no_road_falls_back_to_air_line(roads, far_station):
    """Ohne Straßengraph oder mit Station weit weg von jeder Straße: Netz per Luftlinie × 1,2."""
    st = np.array([600000.0, 380000.0]) if not far_station else arm('ost')[0] + [0.0, 5000.0]
    rng = np.random.default_rng(5)
    xy = st + rng.uniform(-300, 300, size=(60, 2))
    kwp = np.zeros(60)
    kwp[0] = 35.0
    g = build(xy, kwp=kwp, st_xy=st, roads=roads if far_station else None)
    assert len(g.marked) >= 2                                     # Abgänge werden gezählt
    assert per_feeder(g).max() <= MAX_BUILDINGS
    for length, geom in zip(g.length_m, g.geometry):
        air = np.hypot(*np.diff(geom, axis=0).T).sum()
        assert length == pytest.approx(LINE_DETOUR * air, rel=1e-5, abs=1e-3)
    d = g.downstream.toarray()
    assert (d[g.parent == -1].sum(axis=0) == 1).all()
    j = np.flatnonzero(d[:, 0])
    assert len(j) == 1 and g.parent[j[0]] == -1                   # Direktabgang
    assert g.length_m[j[0]] == pytest.approx(LINE_DETOUR * np.hypot(*(xy[0] - st)), rel=1e-5)


def test_empty_station():
    g = build(np.zeros((0, 2)))
    assert len(g.parent) == 0 and len(g.marked) == 0
