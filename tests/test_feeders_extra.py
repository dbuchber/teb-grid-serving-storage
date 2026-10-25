import hashlib
import json
import re

import numpy as np
import pytest

from fakes import (FEEDER_NODE_OFFSET_M, ROADS_CENTER, ROADS_HALF, align_station_positions, fake_build_members_factory,
                   fake_roads, write_fake_prepared)
from gridsim import legacy
from gridsim.data import ARRAYS
from gridsim.feeders.extra_stations import SNAP_M, plan_extra, prepare_extra_stations, reassign
from gridsim.feeders.prepare import TO_WGS84, build_grids, marked_share
from gridsim.feeders.roads import TO_LAMBERT, RoadGraph

C = np.array(TO_LAMBERT.transform(*ROADS_CENTER))      # Kreuzung der Fake-Straßen
_E = np.array(TO_LAMBERT.transform(ROADS_CENTER[0] + ROADS_HALF[0], ROADS_CENTER[1])) - C
V = _E / np.hypot(*_E)                                   # Richtung des Ostarms in EPSG:31287


@pytest.fixture(scope='module')
def roads(tmp_path_factory):
    return RoadGraph(fake_roads(tmp_path_factory.mktemp('roads') / 'roads.json'))


def east(s, offset=10.0):
    """Gebäude ``s`` m entlang der Ost-West-Straße ab der Kreuzung (negativ: Westarm), ``offset`` m daneben."""
    s = np.atleast_1d(np.asarray(s, float))
    return C + s[:, None] * V + offset * np.array([-V[1], V[0]])


def grids_for(st_xy, xy, st_of, roads, hh=None):
    n = len(xy)
    hh = np.ones(n, int) if hh is None else np.asarray(hh)
    zeros = np.zeros(n)
    return build_grids(np.asarray(st_xy, float), xy, hh, zeros, np.asarray(st_of), (zeros, zeros, zeros), roads,
                       len(st_xy))


def test_extra_station_splits_long_feeder(roads):
    """Stadtstation mit einem Gebäude 1 500 m entfernt: eine Zusatzstation, danach nichts mehr markiert."""
    xy = np.vstack([east(10.0 * np.arange(1, 9)), east([1500.0])])
    st_xy = C[None, :]
    st_of = np.zeros(len(xy), int)
    grids = grids_for(st_xy, xy, st_of, roads)
    assert grids[0][0].area == 'stadt' and marked_share(grids) == 1.0

    new = plan_extra(st_xy, xy, np.ones(len(xy), int), st_of, grids, roads=roads, station_ids=['way/1'])
    assert len(new) == 1
    site = np.array([new[0]['x'], new[0]['y']])
    assert np.hypot(*(site - xy[-1])) <= SNAP_M                  # am Gebäude, auf die Straße gezogen
    assert np.min(np.hypot(*(roads.xy - site).T)) < 1e-6

    all_xy = np.vstack([st_xy, site])
    st_of2, info = reassign(all_xy, xy, roads)
    assert st_of2.tolist() == [0] * 8 + [1]
    assert info['air'] == info['air_far'] == 0
    assert marked_share(grids_for(all_xy, xy, st_of2, roads)) == 0.0


def test_new_station_ids_and_flags(roads):
    xy = np.vstack([east(10.0 * np.arange(1, 9)), east([1500.0, 1520.0]), east([-1600.0, -1620.0])])
    st_xy = C[None, :]
    st_of = np.zeros(len(xy), int)
    grids = grids_for(st_xy, xy, st_of, roads)
    new = plan_extra(st_xy, xy, np.ones(len(xy), int), st_of, grids, roads=roads, station_ids=['way/1'], start=7)
    assert len(new) == 2
    assert [s['id'] for s in new] == ['demo:steyr:ns-007', 'demo:steyr:ns-008']
    for s in new:
        assert re.fullmatch(r'demo:steyr:ns-\d{3}', s['id'])
        assert s['synthetic'] == 1 and s['parent'] == 'way/1'
        lon, lat = TO_WGS84.transform(s['x'], s['y'])
        assert (s['lon'], s['lat']) == pytest.approx((lon, lat), abs=1e-9)


def test_cluster_limits_buildings_and_radius():
    """k-Means: kein Cluster über 105 Knoten, keiner weiter als der Radius vom Zentrum; k minimal."""
    from gridsim.feeders.extra_stations import MAX_CLUSTER, _clusters
    assert MAX_CLUSTER == 105
    pts = east(1200.0 + 8.0 * np.arange(250))                     # 250 Gebäude auf 2 km Straße
    parts = _clusters(pts, 500.0 / 1.2, 1)
    assert sorted(np.concatenate([i for i, _ in parts]).tolist()) == list(range(250))
    assert all(len(i) <= 105 and np.hypot(*(pts[i] - c).T).max() <= 500.0 / 1.2 for i, c in parts)
    assert len(parts) >= 3
    tight = _clusters(pts, 60.0, 1)                               # Radius bestimmt k, nicht die Gebäudezahl
    assert len(tight) > len(parts)
    assert all(np.hypot(*(pts[i] - c).T).max() <= 60.0 for i, c in tight)


def test_compact_cluster_of_100_gives_one_station(roads):
    """100 dicht stehende ferne Gebäude: eine Zusatzstation, nicht vier."""
    block = np.array([[u, v] for u in range(10) for v in range(10)], float) * 15.0
    far = east([1300.0])[0] + block @ np.array([V, [-V[1], V[0]]]) + 10.0 * np.array([-V[1], V[0]])
    xy = np.vstack([east(10.0 * np.arange(1, 5)), far])
    st_xy = C[None, :]
    st_of = np.zeros(len(xy), int)
    grids = grids_for(st_xy, xy, st_of, roads)
    assert grids[0][0].marked.any()
    new = plan_extra(st_xy, xy, np.ones(len(xy), int), st_of, grids, roads=roads)
    assert len(new) == 1
    assert all(s['parent'] == 0 for s in new)                     # ohne station_ids: Index der Elternstation


def test_reassign_moves_only_marked_nodes(roads):
    """Nicht markierte Knoten behalten ihre Station, auch wenn eine neue Station näher liegt."""
    st_xy = np.vstack([C, east([1000.0])[0]])
    xy = east([900.0, 950.0, 1100.0])
    current = np.array([0, 0, 0])
    st_of, info = reassign(st_xy, xy, roads, current=current, movable=np.array([1, 2]))
    assert st_of.tolist() == [0, 1, 1]
    assert info == {'road': 2, 'air': 0, 'air_far': 0}


def test_reassign_air_fallbacks(roads):
    """Ohne Straßenverbindung: Luftlinie ≤ 600 m; weiter weg trotzdem zuordnen und zählen."""
    st_xy = np.vstack([C, C + [0.0, 3000.0]])                     # Station 1 weit weg von jeder Straße
    xy = np.vstack([east([50.0]), C + [400.0, 3000.0], C + [1500.0, 3800.0]])
    st_of, info = reassign(st_xy, xy, roads)
    assert st_of.tolist() == [0, 1, 1]
    assert info == {'road': 1, 'air': 1, 'air_far': 1}
    st_of, info = reassign(st_xy, xy, None)                       # ohne Straßennetz: alles per Luftlinie
    assert st_of.tolist() == [0, 1, 1] and info['road'] == 0


# ---------------------------------------------------------------- Ende-zu-Ende mit Fake-Prepared

FAR_OFFSETS = list(FEEDER_NODE_OFFSET_M)
FAR_OFFSETS[3] = (1500, -15)            # Station 0 (Typ streu, Grenze 1 000 m) bekommt ein fernes Gebäude


@pytest.fixture
def setup(tmp_path, monkeypatch):
    sim = legacy.load('steyr_sim_variant_a')
    fbm = fake_build_members_factory(FAR_OFFSETS)
    monkeypatch.setattr(sim, 'build_members', fbm)
    inp = tmp_path / 'input'
    inp.mkdir()
    fake_roads(inp / 'osm_roads.json')
    prepared = tmp_path / 'prepared'
    for y in (2012, 2023):
        write_fake_prepared(prepared, y)
    align_station_positions(prepared, fbm)
    return inp, prepared, tmp_path / 'prepared-ns'


def tree_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def test_variant_leaves_source_untouched(setup):
    inp, prepared, out = setup
    before = tree_hashes(prepared)
    feeders = prepare_extra_stations(inp, prepared, out)
    assert tree_hashes(prepared) == before
    assert feeders == out / 'feeders' and (feeders / 'report.json').exists()
    variant = json.loads((out / 'variant.json').read_text())
    assert variant['source'] == str(prepared.resolve())
    for y in (2012, 2023):
        for name in ARRAYS:
            if name == 'nodes_station':
                continue
            assert (out / str(y) / f'{name}.npy').read_bytes() == (prepared / str(y) / f'{name}.npy').read_bytes()
        assert json.loads((out / str(y) / 'manifest.json').read_text())['variant']['source'] == str(prepared.resolve())
    assert (out / '2012' / 'nodes_station.npy').read_bytes() == (out / '2023' / 'nodes_station.npy').read_bytes()
    assert (out / '2012' / 'stations.json').read_text() == (out / '2023' / 'stations.json').read_text()
    report = json.loads((feeders / 'report.json').read_text())
    extra = report['extra_stations']
    assert extra['stations_old'] == 3 and extra['stations_added'] >= 1
    assert report['n_stations'] == 3 + extra['stations_added'] - extra['stations_dropped']['old'] \
        - extra['stations_dropped']['new']
    assert extra['marked_share']['source'] > 0.0 and extra['marked_share']['pass1'] == 0.0
    assert 'pass2' not in extra['marked_share']                   # erster Durchgang reicht
    assert report['marked']['stations_any'] == 0
    assert report['cable_share']['acceptance'] == 'by_route_length'
    pb = report['per_building']
    assert pb['buildings'] == 8 and pb['buildings_per_station']['n'] == report['n_stations']
    assert pb['route_m_per_building'] > 0
    with pytest.raises(ValueError):
        prepare_extra_stations(inp, prepared, prepared)           # nie in die Quelle schreiben


def test_new_station_in_variant(setup):
    inp, prepared, out = setup
    prepare_extra_stations(inp, prepared, out)
    rows = json.loads((out / '2012' / 'stations.json').read_text())
    src = json.loads((prepared / '2012' / 'stations.json').read_text())
    assert set(rows[0]) == set(src[0])                            # gleiches Format
    assert [r['idx'] for r in rows] == list(range(len(rows)))
    new = [r for r in rows if r['id'].startswith('demo:steyr:ns-')]
    assert new and all(r['synthetic'] == 1 and r['uw'] == 'Steyr' for r in new)
    st = np.load(out / '2012' / 'nodes_station.npy')
    assert st.dtype == np.int32 and st[3] == rows.index(new[0])   # fernes Gebäude an der Zusatzstation
    src_st = np.load(prepared / '2012' / 'nodes_station.npy')
    keep = np.arange(len(st)) != 3                                # nicht markierte Knoten behalten ihre Station
    assert [rows[i]['id'] for i in st[keep]] == [src[i]['id'] for i in src_st[keep]]
    v = json.loads((out / 'variant.json').read_text())
    assert [s['id'] for s in v['stations']] == [r['id'] for r in rows]
    assert v['stations'][rows.index(new[0])]['parent'] == 'way/1'


def test_trafo_kva_rule(setup):
    """kva jeder Station der Variante = sim.trafo_kva der neuen Zuordnung."""
    inp, prepared, out = setup
    prepare_extra_stations(inp, prepared, out)
    sim = legacy.load('steyr_sim_variant_a')
    rows = json.loads((out / '2012' / 'stations.json').read_text())
    st = np.load(out / '2012' / 'nodes_station.npy')
    hh = np.load(out / '2012' / 'nodes_hh.npy').astype(int)
    kwp = np.load(out / '2012' / 'nodes_kwp_bins.npy').astype(float).sum(axis=1)
    for i, r in enumerate(rows):
        m = st == i
        assert m.any()
        n_b, n_hh, k = int((hh[m] > 0).sum()), int(hh[m].sum()), float(kwp[m].sum())
        assert (r['n_buildings'], r['n_hh'], r['kwp']) == (n_b, n_hh, round(k, 1))
        assert r['kva'] == sim.trafo_kva(n_b, n_hh, k)


def test_cli_extra_stations(setup, capsys):
    from gridsim.cli import main
    inp, prepared, out = setup
    main(['prepare-feeders', '--input', str(inp), '--prepared', str(prepared), '--extra-stations', '--out', str(out)])
    assert (out / 'feeders' / 'report.json').exists() and not (prepared / 'feeders').exists()
    assert 'extra_stations' in capsys.readouterr().out
