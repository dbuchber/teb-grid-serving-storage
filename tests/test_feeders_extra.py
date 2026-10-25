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
from gridsim.feeders.prepare import TO_WGS84, build_grids, marked_share, node_feeder
from gridsim.feeders.sizing import DesignRule


def no_loads(zeros):
    """Auslegung nur aus Haushalten nach P_HH · g(n): keine Geräte, keine H0-Untergrenze."""
    return {'wp_kw': zeros, 'kwp_peak': zeros, 'rule': DesignRule(wp_share=0.0, ev_share=0.0, h0_peak_kw=0.0)}
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
    return build_grids(np.asarray(st_xy, float), xy, hh, zeros, np.asarray(st_of), no_loads(zeros), roads,
                       len(st_xy))


def test_extra_station_splits_long_feeder(roads):
    """Stadtstation mit 8 Gebäuden 1 500 m entfernt: eine Zusatzstation, danach nichts mehr markiert."""
    xy = np.vstack([east(10.0 * np.arange(1, 9)), east(1500.0 + 20.0 * np.arange(8))])
    st_xy = C[None, :]
    st_of = np.zeros(len(xy), int)
    grids = grids_for(st_xy, xy, st_of, roads)
    assert grids[0][0].area == 'stadt' and marked_share(grids) == 1.0

    new = plan_extra(st_xy, xy, np.ones(len(xy), int), st_of, grids, roads=roads, station_ids=['way/1'])
    assert len(new) == 1
    site = np.array([new[0]['x'], new[0]['y']])
    assert np.hypot(*(xy[8:] - site).T).min() <= SNAP_M          # an einem Gebäude, auf die Straße gezogen
    assert np.min(np.hypot(*(roads.xy - site).T)) < 1e-6
    assert sorted(new[0]['members'].tolist()) == list(range(8, 16)) and new[0]['n_homes'] == 8

    all_xy = np.vstack([st_xy, site])
    st_of2, info = reassign(all_xy, xy, roads, current=st_of, movable=new[0]['members'])
    assert st_of2.tolist() == [0] * 8 + [1] * 8
    assert info['air'] == info['air_far'] == 0
    assert marked_share(grids_for(all_xy, xy, st_of2, roads)) == 0.0


def test_new_station_ids_and_flags(roads):
    xy = np.vstack([east(10.0 * np.arange(1, 9)), east(1500.0 + 20.0 * np.arange(6)),
                    east(-1600.0 - 20.0 * np.arange(6))])
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


def ort_station(tail):
    """Ortsstation (16 Gebäude, 40 m Abstand beidseits der Kreuzung) plus ``tail`` Gebäude ab 1 500 m."""
    near = np.vstack([east(40.0 * np.arange(1, 9)), east(-40.0 * np.arange(1, 9))])
    return np.vstack([near, east(1500.0 + 40.0 * np.arange(tail))])


def test_tail_of_three_gets_no_station(roads):
    """3 Gebäude 1 500 m draußen an einer Ortsstation: Ausläufer, nicht markiert, keine Zusatzstation."""
    xy = ort_station(3)
    st_of = np.zeros(len(xy), int)
    grids = grids_for(C[None, :], xy, st_of, roads)
    grid, sized = grids[0][0], grids[0][1]
    assert grid.area == 'ort'
    assert grid.tail.sum() >= 1 and not grid.marked.any() and not sized.marked.any()
    assert marked_share(grids) == 0.0
    skipped = []
    assert plan_extra(C[None, :], xy, np.ones(len(xy), int), st_of, grids, roads=roads, skipped=skipped) == []


def test_tail_of_eight_gets_station(roads):
    xy = ort_station(8)
    st_of = np.zeros(len(xy), int)
    grids = grids_for(C[None, :], xy, st_of, roads)
    assert grids[0][0].area == 'ort' and grids[0][0].marked.any()
    new = plan_extra(C[None, :], xy, np.ones(len(xy), int), st_of, grids, roads=roads)
    assert len(new) == 1 and sorted(new[0]['members'].tolist()) == list(range(16, 24))


def test_small_cluster_skipped(roads):
    """Cluster unter 6 Wohngebäuden entsteht nicht, auch wenn der Abgang markiert ist (PV-Hallen zählen nicht)."""
    xy = ort_station(8)
    hh = np.ones(len(xy), int)
    hh[18:] = 0                                                   # nur 2 Wohngebäude draußen, 6 Hallen
    st_of = np.zeros(len(xy), int)
    zeros = np.zeros(len(xy))
    grids = build_grids(C[None, :], xy, hh, zeros, st_of, no_loads(zeros), roads, 1)
    assert not grids[0][0].marked.any()                           # nach Wohngebäuden: Ausläufer
    grids[0][0].marked[:] = grids[0][0].tail                      # erzwungen markiert: Cluster trotzdem zu klein
    skipped = []
    assert plan_extra(C[None, :], xy, hh, st_of, grids, roads=roads, skipped=skipped) == []
    assert skipped == [8]


def hamlet_roads(path, s_xy, j_xy, ends):
    """Straße Station → Abzweig J und drei Straßen ab J (Koordinaten EPSG:31287) als Overpass-JSON."""
    pts = [s_xy, j_xy] + list(ends)
    lon, lat = TO_WGS84.transform(*np.array(pts).T)
    elements = [{'type': 'node', 'id': i + 1, 'lon': float(x), 'lat': float(y)} for i, (x, y) in enumerate(zip(lon, lat))]
    elements += [{'type': 'way', 'id': 100, 'nodes': [1, 2], 'tags': {'highway': 'residential'}}]
    elements += [{'type': 'way', 'id': 101 + k, 'nodes': [2, 3 + k], 'tags': {'highway': 'residential'}}
                 for k in range(len(ends))]
    path.write_text(json.dumps({'elements': elements}), encoding='utf-8')
    return RoadGraph(path)


def test_hamlet_beyond_junction_is_marked(tmp_path):
    """Abzweig innerhalb der Grenze, drei Straßen mit je 3–4 Wohngebäuden dahinter: markiert, eine Zusatzstation.

    ``_split`` teilt jede Straße zum eigenen Abgang (< 6 ferne Wohngebäude je Abgang); die Gruppierung je Station
    erkennt den Weiler (11 ferne Wohngebäude) und markiert die Abgänge.
    """
    from gridsim.feeders.topology import TAIL_MIN_HOMES
    s = np.array([600000.0, 380000.0])
    j = s + [600.0, 0.0]
    dirs = [np.array([0.83, 0.55]), np.array([1.0, 0.0]), np.array([0.83, -0.55])]
    roads = hamlet_roads(tmp_path / 'r.json', s, j, [j + 300.0 * d for d in dirs])
    normal = lambda d: np.array([-d[1], d[0]])                    # noqa: E731
    near = [s + [x, 10.0] for x in 40.0 * np.arange(1, 9)]        # Ortskern an der Zufahrt
    near.append(j + 20.0 * dirs[0] + 10.0 * normal(dirs[0]))      # ein Gebäude knapp hinter dem Abzweig
    far = [j + t * d + 10.0 * normal(d) for d, ts in zip(dirs, ([110, 150, 190], [110, 150, 190, 230],
                                                               [110, 150, 190, 230])) for t in ts]
    xy = np.array(near + far)
    st_of = np.zeros(len(xy), int)
    grids = grids_for(s[None, :], xy, st_of, roads)
    grid = grids[0][0]
    assert grid.area == 'ort'
    nf = node_feeder(grid)
    far_feeders = set(nf[len(near):].tolist())
    assert len(far_feeders) == 3                                  # jede Straße ein eigener Abgang
    assert all((nf[len(near):] == f).sum() < TAIL_MIN_HOMES for f in far_feeders)
    assert set(np.flatnonzero(grid.marked)) == far_feeders and not grid.tail.any()
    new = plan_extra(s[None, :], xy, np.ones(len(xy), int), st_of, grids, roads=roads)
    assert len(new) == 1 and sorted(new[0]['members'].tolist()) == list(range(len(near), len(xy)))


def test_revert_small_new_station():
    """Neue Station mit < 6 Wohngebäuden nach der Zuordnung: Knoten zurück an die vorherige Station."""
    from gridsim.feeders.extra_stations import revert_small
    previous = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    st_of = np.array([0, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 1])     # Station 2: 6 Gebäude, Station 3: 5
    hh = np.ones(13, int)
    out, small = revert_small(st_of, previous, hh, first_new=2)
    assert small == [3]
    assert out.tolist() == [0, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]
    hh[1] = 0                                                     # Halle zählt nicht: Station 2 hat nur 5
    out, small = revert_small(st_of, previous, hh, first_new=2)
    assert small == [2, 3] and out.tolist() == previous.tolist()


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
FAR_OFFSETS[3] = (1500, -15)            # Station 0 bekommt 7 ferne Wohngebäude (Knoten 3 und 10–15)
EXTRA = [((1500 + 30 * k, 15 * (-1) ** k), 1, 0.0, 0) for k in range(1, 7)]


def extend_prepared(prepared):
    """Fake-Prepared um die Knoten aus EXTRA erweitern (Kopien von Knoten 3, Station 0)."""
    for d in sorted(p for p in prepared.iterdir() if p.name.isdigit()):
        for name in ('nodes_station', 'nodes_hh', 'nodes_kwp_bins', 'nodes_kwh', 'nodes_fw', 'nodes_cell',
                     'nodes_heat_kwh', 'nodes_dhw'):
            a = np.load(d / f'{name}.npy')
            np.save(d / f'{name}.npy', np.concatenate([a, np.repeat(a[3:4], len(EXTRA), axis=0)]))


@pytest.fixture
def setup(tmp_path, monkeypatch):
    sim = legacy.load('steyr_sim_variant_a')
    fbm = fake_build_members_factory(FAR_OFFSETS, extra=EXTRA)
    monkeypatch.setattr(sim, 'build_members', fbm)
    inp = tmp_path / 'input'
    inp.mkdir()
    fake_roads(inp / 'osm_roads.json')
    prepared = tmp_path / 'prepared'
    for y in (2012, 2023):
        write_fake_prepared(prepared, y)
    extend_prepared(prepared)
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
    assert pb['buildings'] == 14 and pb['buildings_per_station']['n'] == report['n_stations']
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
    far = np.array([3] + list(range(10, 16)))
    assert set(st[far]) == {rows.index(new[0])}
    keep = ~np.isin(np.arange(len(st)), far)                      # nicht markierte Knoten behalten ihre Station
    assert [rows[i]['id'] for i in st[keep]] == [src[i]['id'] for i in src_st[keep]]
    v = json.loads((out / 'variant.json').read_text())
    assert [s['id'] for s in v['stations']] == [r['id'] for r in rows]
    assert v['stations'][rows.index(new[0])]['parent'] == 'way/1'


def test_trafo_kva_rule(setup):
    """kva geänderter Stationen = sim.trafo_kva der neuen Zuordnung; unveränderte Stationen: Zeile der Quelle."""
    inp, prepared, out = setup
    prepare_extra_stations(inp, prepared, out)
    sim = legacy.load('steyr_sim_variant_a')
    rows = json.loads((out / '2012' / 'stations.json').read_text())
    src = {r['id']: r for r in json.loads((prepared / '2012' / 'stations.json').read_text())}
    st = np.load(out / '2012' / 'nodes_station.npy')
    src_st = np.load(prepared / '2012' / 'nodes_station.npy')
    hh = np.load(out / '2012' / 'nodes_hh.npy').astype(int)
    kwp = np.load(out / '2012' / 'nodes_kwp_bins.npy').astype(float).sum(axis=1)
    unchanged = 0
    for i, r in enumerate(rows):
        m = st == i
        assert m.any()
        s = src.get(r['id'])
        if s is not None and np.array_equal(np.flatnonzero(m), np.flatnonzero(src_st == s['idx'])):
            assert r == {**s, 'idx': i}                           # bitgleich bis auf idx (Fake-kva ≠ Regel)
            unchanged += 1
            continue
        n_b, n_hh, k = int((hh[m] > 0).sum()), int(hh[m].sum()), float(kwp[m].sum())
        assert (r['n_buildings'], r['n_hh'], r['kwp']) == (n_b, n_hh, round(k, 1))
        assert r['kva'] == sim.trafo_kva(n_b, n_hh, k)
    assert unchanged == 2                                         # Stationen 1 und 2 unberührt


def test_cli_extra_stations(setup, capsys):
    from gridsim.cli import main
    inp, prepared, out = setup
    main(['prepare-feeders', '--input', str(inp), '--prepared', str(prepared), '--extra-stations', '--out', str(out)])
    assert (out / 'feeders' / 'report.json').exists() and not (prepared / 'feeders').exists()
    assert 'extra_stations' in capsys.readouterr().out



def test_voltage_only_feeders_do_not_count_toward_marked_share():
    """Fix-Runde 4: Abgänge, die nur am Spannungsfall scheitern, zählen nicht zur 10-%-Grenze und lösen keine
    Zusatzstation aus; zu lange Abgänge und Stromüberschreitung zählen weiter."""
    from dataclasses import replace
    from gridsim.feeders.extra_stations import _marked_local
    from gridsim.feeders.sizing import SizedGrid
    from test_feeders_sizing import make_grid
    grid = make_grid([-1, -1], [50, 80], [False, False], [0, 1], [0, 1])
    nf = len(grid.marked)
    base = SizedGrid(types=['NAYY 4x50'] * len(grid.parent), parallel=np.ones(len(grid.parent), np.int8),
                     i_max_a=np.ones(len(grid.parent)), r_ohm=np.zeros(len(grid.parent)), x_ohm=np.zeros(len(grid.parent)),
                     du_load_pct=np.zeros(nf), du_feed_pct=np.zeros(nf), marked=np.zeros(nf, bool),
                     marked_voltage=np.zeros(nf, bool))
    volt = replace(base, marked_voltage=np.ones(nf, bool))
    assert marked_share({0: (grid, volt)}) == 0.0 and len(_marked_local(grid, volt)) == 0
    assert marked_share({0: (grid, replace(base, marked=np.ones(nf, bool)))}) == 1.0
    long = replace(grid, marked=np.ones(nf, bool))
    assert marked_share({0: (long, volt)}) == 1.0
