import json
from collections import defaultdict

import numpy as np
import pytest

from fakes import ROADS_CENTER, fake_roads, write_fake_prepared
from gridsim import legacy
from gridsim.feeders.prepare import load_feeders, prepare_feeders
from gridsim.feeders.roads import TO_LAMBERT
from gridsim.feeders.sizing import SizedGrid
from gridsim.feeders.topology import StationGrid

# Fake-Knoten wie in fakes.write_fake_prepared (Station 0, 0, 0, 0, 1, 1, 1, 1, 2, 2), entlang der Ost-West-Straße
NODE_STATION = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2]
NODE_OFFSET_M = [(40, 15), (80, -15), (120, 15), (160, -15), (-60, 12), (-110, -12), (-160, 12), (-210, -12),
                 (30, 300), (60, 330)]
LEGACY_STATION = [0, 2, 3]   # Legacy-Station 1 hat keine Knoten und fällt beim Verdichten weg


def fake_build_members(inp):
    c = np.array(TO_LAMBERT.transform(*ROADS_CENTER))
    st_xy = np.array([c, c + [0, 2000], c + [-20, 0], c + [0, 250]])
    stations = [{'osm_id': f'way/{i}', 'lon': 0.0, 'lat': 0.0} for i in range(4)]
    hh = [1, 1, 5, 1, 1, 5, 5, 1, 0, 0]
    kwp = [8, 10, 0, 0, 6, 0, 0, 0, 60, 40]
    nodes = [{'xy': tuple(c + off), 'hh': h, 'kwp': float(k), 'pv': defaultdict(float),
              'station': LEGACY_STATION[s]} for off, h, k, s in zip(NODE_OFFSET_M, hh, kwp, NODE_STATION)]
    return stations, st_xy, ['Steyr'] * 4, nodes


@pytest.fixture
def setup(tmp_path, monkeypatch):
    sim = legacy.load('steyr_sim_variant_a')
    monkeypatch.setattr(sim, 'build_members', fake_build_members)
    inp = tmp_path / 'input'
    inp.mkdir()
    fake_roads(inp / 'osm_roads.json')
    prepared = tmp_path / 'prepared'
    write_fake_prepared(prepared, 2012)
    write_fake_prepared(prepared, 2023)
    return inp, prepared


def test_prepare_feeders_writes_all_stations(setup):
    inp, prepared = setup
    out = prepare_feeders(inp, prepared)
    assert out == prepared / 'feeders'
    index = json.loads((out / 'index.json').read_text())
    assert len(index) == 3
    assert isinstance(json.loads((out / 'manifest.json').read_text())['inputs'], dict)
    lines = json.loads((out / 'lines.geojson').read_text())
    assert lines['features'] and {'type', 'parallel', 'feeder', 'overhead', 'service'} <= set(
        lines['features'][0]['properties'])
    lon, lat = lines['features'][0]['geometry']['coordinates'][0]
    assert 14 < lon < 15 and 47.5 < lat < 48.5

    grids = load_feeders(prepared)
    assert sorted(grids) == [0, 1, 2]
    for s, (grid, sized) in grids.items():
        assert isinstance(grid, StationGrid) and isinstance(sized, SizedGrid)
        assert grid.station == s
        assert grid.node_index.tolist() == [i for i, st in enumerate(NODE_STATION) if st == s]
        m = len(grid.parent)
        assert grid.downstream.shape == (m, len(grid.node_index))
        assert len(sized.types) == m and sized.i_max_a.shape == (m,) and len(grid.geometry) == m
        assert (grid.downstream.toarray().sum(axis=0) >= 1).all()   # jeder Knoten hängt am Netz
    report = json.loads((out / 'report.json').read_text())
    assert report['n_stations'] == 3
    assert 0.0 <= report['cable_share']['by_cable_length'] <= 1.0


def test_station_file_roundtrip_exact(setup, tmp_path):
    """CSR, Geometrie und alle Felder kommen bitgleich aus der npz-Datei zurück."""
    from gridsim.feeders.prepare import _load_station, _save_station
    inp, prepared = setup
    prepare_feeders(inp, prepared)
    grid, sized = load_feeders(prepared)[0]
    path = tmp_path / 'x.npz'
    _save_station(path, grid, sized)
    g2, s2 = _load_station(path)
    for f in ('data', 'indices', 'indptr'):
        a, b = getattr(grid.downstream, f), getattr(g2.downstream, f)
        assert a.dtype == b.dtype and np.array_equal(a, b)
    assert g2.downstream.shape == grid.downstream.shape
    for f in ('node_index', 'parent', 'length_m', 'feeder', 'service', 'overhead', 'marked'):
        a, b = getattr(grid, f), getattr(g2, f)
        assert a.dtype == b.dtype and np.array_equal(a, b), f
    assert (g2.station, g2.area) == (grid.station, grid.area)
    assert all(np.array_equal(x, y) for x, y in zip(grid.geometry, g2.geometry))
    assert s2.types == sized.types
    for f in ('parallel', 'i_max_a', 'r_ohm', 'x_ohm', 'du_load_pct', 'du_feed_pct', 'marked'):
        a, b = getattr(sized, f), getattr(s2, f)
        assert a.dtype == b.dtype and np.array_equal(a, b), f


def test_load_feeders_without_directory(tmp_path):
    assert load_feeders(tmp_path) is None


def test_prepare_feeders_rejects_node_mismatch(setup):
    inp, prepared = setup
    path = prepared / '2023' / 'nodes_station.npy'
    st = np.load(path)
    st[0] = 1
    np.save(path, st)
    with pytest.raises(ValueError, match='Knoten'):
        prepare_feeders(inp, prepared)


def test_prepare_feeders_rejects_build_members_mismatch(setup, monkeypatch):
    inp, prepared = setup
    sim = legacy.load('steyr_sim_variant_a')

    def fewer(inp):
        stations, st_xy, uw, nodes = fake_build_members(inp)
        return stations, st_xy, uw, nodes[:-1]

    monkeypatch.setattr(sim, 'build_members', fewer)
    with pytest.raises(ValueError, match='Knoten'):
        prepare_feeders(inp, prepared)


def test_design_loads_heute(tmp_path):
    from gridsim import profiles
    from gridsim.data import load_prepared
    from gridsim.feeders.prepare import design_loads
    from gridsim.run import BASE_SEED
    p = load_prepared(write_fake_prepared(tmp_path, 2012), 2012)
    wp, cars, pv = design_loads(p)
    share = profiles.SCENARIOS['heute']
    hh = np.asarray(p.nodes_hh)
    assert wp[2] == 0.0 and (wp[8:] == 0).all()                    # Fernwärme und Hallen ohne Wärmepumpe
    assert (wp[[0, 1, 3, 4, 5, 6, 7]] > 0).all()
    assert np.allclose(cars, share['ev_share'] * hh)
    assert np.allclose(pv, np.asarray(p.nodes_kwp_bins).sum(axis=1) * float(np.max(p.pv_bins)))
    # Knoten 0 von Hand: p_wp × Leistung in der kältesten Stunde der Zelle 0, Versatz 0
    fw_frac = np.asarray(p.nodes_fw)[hh > 0].mean()
    p_wp = min(1.0, share['wp_share'] / (1 - fw_frac))
    limits, _ = profiles.wpev.spread(len(hh), BASE_SEED)
    t = np.asarray(p.temp_cells[:, 0], dtype=float)
    el = profiles.heat_pump_kw(t, np.array([18000.0]), limits[:1], np.zeros(1, int), np.array([0.15]))
    assert wp[0] == pytest.approx(p_wp * float(el[int(np.argmin(t)), 0]), rel=1e-5)  # float32


def test_cli_prepare_feeders(setup, capsys):
    from gridsim.cli import main
    inp, prepared = setup
    main(['prepare-feeders', '--input', str(inp), '--prepared', str(prepared)])
    assert (prepared / 'feeders' / 'report.json').exists()
    assert 'prepared feeders' in capsys.readouterr().out
