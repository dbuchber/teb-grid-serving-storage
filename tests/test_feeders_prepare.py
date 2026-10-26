import json
import numpy as np
import pytest

from fakes import (FEEDER_NODE_STATION, align_station_positions, fake_build_members_factory, fake_roads,
                   write_fake_prepared)
from gridsim import legacy
from gridsim.feeders.prepare import load_feeders, prepare_feeders
from gridsim.feeders.sizing import SizedGrid
from gridsim.feeders.topology import StationGrid

NODE_STATION = FEEDER_NODE_STATION
fake_build_members = fake_build_members_factory()


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
    align_station_positions(prepared, fake_build_members)
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


def test_manifest_records_model_version_and_current_rule(setup):
    from gridsim import run
    inp, prepared = setup
    out = prepare_feeders(inp, prepared)
    m = json.loads((out / 'manifest.json').read_text())
    assert m['model_version'] == run.MODEL_VERSION
    assert m['design']['rule'] != 'fix1-binom-p90-h0peak'
    assert all(w in m['design']['rule'] for w in ('groesste', 'Mindestquerschnitt', 'Spannungsfaelle'))


def test_load_feeders_warns_on_missing_or_other_model_version(setup):
    import warnings
    inp, prepared = setup
    out = prepare_feeders(inp, prepared)
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        load_feeders(prepared)                                  # aktueller Stand: keine Warnung
    mf = json.loads((out / 'manifest.json').read_text())
    mf['model_version'] = 'alt'
    (out / 'manifest.json').write_text(json.dumps(mf))
    with pytest.warns(RuntimeWarning, match='alt'):
        assert load_feeders(prepared)
    del mf['model_version']
    (out / 'manifest.json').write_text(json.dumps(mf))
    with pytest.warns(RuntimeWarning, match='ohne model_version'):
        assert load_feeders(prepared)


def test_load_feeders_warns_when_prepared_changed_after_build(setup):
    """``gridsim prepare`` lief nach ``prepare-feeders`` erneut: Warnung mit Hinweis auf prepare-feeders."""
    import warnings
    inp, prepared = setup
    prepare_feeders(inp, prepared)
    with warnings.catch_warnings():
        warnings.simplefilter('error')
        load_feeders(prepared)                                  # passender Stand: keine Warnung
    mf = prepared / '2023' / 'manifest.json'
    m = json.loads(mf.read_text())
    m['rebuilt'] = True
    mf.write_text(json.dumps(m))
    with pytest.warns(RuntimeWarning, match=r'prepared/2023 .*prepare-feeders'):
        assert load_feeders(prepared)


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
    for f in ('parallel', 'i_max_a', 'r_ohm', 'x_ohm', 'du_load_pct', 'du_feed_pct', 'marked', 'marked_voltage'):
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
    """Fix-Runde 1: volle WP-Leistung je berechtigtem Knoten, Anteile wie profiles.assign, H0-Spitze aus h0."""
    from gridsim import legacy, profiles
    from gridsim.data import load_prepared
    from gridsim.feeders.prepare import design_loads
    from gridsim.run import BASE_SEED
    p = load_prepared(write_fake_prepared(tmp_path, 2012), 2012)
    loads = design_loads(p)
    wp, pv, rule = loads['wp_kw'], loads['kwp_peak'], loads['rule']
    share = profiles.SCENARIOS['heute']
    hh = np.asarray(p.nodes_hh)
    assert wp[2] == 0.0 and (wp[8:] == 0).all()                    # Fernwärme und Hallen ohne Wärmepumpe
    assert (wp[[0, 1, 3, 4, 5, 6, 7]] > 0).all()
    assert np.allclose(pv, np.asarray(p.nodes_kwp_bins).sum(axis=1) * float(np.max(p.pv_bins)))
    fw_frac = np.asarray(p.nodes_fw)[hh > 0].mean()
    assert rule.wp_share == pytest.approx(min(1.0, share['wp_share'] / (1 - fw_frac)))
    assert rule.ev_share == share['ev_share']
    h0 = np.asarray(p.h0, dtype=float) * legacy.load('steyr_sim_variant_a').KWH_PER_HH
    cold = int(np.argmin(np.asarray(p.temp_cells, dtype=float).mean(axis=1)))
    assert rule.h0_peak_kw == pytest.approx(max(h0[cold], h0.max()))
    # Knoten 0 von Hand: volle Leistung (ohne Anteil) in der kältesten Stunde der Zelle 0, Versatz 0
    limits, _ = profiles.wpev.spread(len(hh), BASE_SEED)
    t = np.asarray(p.temp_cells[:, 0], dtype=float)
    el = profiles.heat_pump_kw(t, np.array([18000.0]), limits[:1], np.zeros(1, int), np.array([0.15]))
    assert wp[0] == pytest.approx(float(el[int(np.argmin(t)), 0]), rel=1e-5)  # float32


def test_cli_prepare_feeders(setup, capsys):
    from gridsim.cli import main
    inp, prepared = setup
    main(['prepare-feeders', '--input', str(inp), '--prepared', str(prepared)])
    assert (prepared / 'feeders' / 'report.json').exists()
    assert 'prepared feeders' in capsys.readouterr().out


def test_prepare_feeders_rejects_station_position_mismatch(setup):
    """Stationsposition aus build_members und stations.json müssen auf 1e-6 Grad übereinstimmen."""
    inp, prepared = setup
    path = prepared / '2023' / 'stations.json'
    rows = json.loads(path.read_text())
    rows[1]['lon'] += 2e-6
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match='Stationsposition'):
        prepare_feeders(inp, prepared)


def test_station_summary_skips_feeders_without_nodes():
    """Abgang ohne Knoten geht nicht als Reichweite 0 in die Statistik ein."""
    from scipy import sparse
    from gridsim.feeders.prepare import _station_summary
    pts = np.array([[0.0, 0.0], [100.0, 0.0]])
    grid = StationGrid(station=0, area='ort', node_index=np.array([5]), parent=np.array([-1, -1, 0], np.int32),
                       length_m=np.array([100.0, 50.0, 10.0], np.float32), feeder=np.array([0, 1, 0], np.int16),
                       service=np.array([False, False, True]), overhead=np.zeros(3, bool),
                       downstream=sparse.csr_matrix(np.array([[1], [0], [1]], np.int8)),
                       marked=np.zeros(2, bool), geometry=[pts, pts * 0.5, pts * 0.1])
    sized = SizedGrid(types=['NAYY 4x50'] * 3, parallel=np.ones(3, np.int8), i_max_a=np.ones(3),
                      r_ohm=np.zeros(3), x_ohm=np.zeros(3), du_load_pct=np.zeros(2), du_feed_pct=np.zeros(2),
                      marked=np.zeros(2, bool))
    s = _station_summary(grid, sized)
    assert s['reach_m'] == [110.0]



def test_report_counts_voltage_only_separately():
    """Fix-Runde 4: reine Spannungsfälle stehen getrennt im Bericht (Abgänge, Stationen, Gebietstyp) und zählen
    nicht in ``marked.stations_any``."""
    from dataclasses import replace
    from scipy import sparse
    from gridsim.feeders.prepare import _report, _station_summary
    pts = np.array([[0.0, 0.0], [100.0, 0.0]])

    def grid(area):
        return StationGrid(station=0, area=area, node_index=np.array([0, 1]), parent=np.array([-1, -1], np.int32),
                           length_m=np.array([100.0, 50.0], np.float32), feeder=np.array([0, 1], np.int16),
                           service=np.zeros(2, bool), overhead=np.zeros(2, bool),
                           downstream=sparse.csr_matrix(np.eye(2, dtype=np.int8)), marked=np.zeros(2, bool),
                           geometry=[pts, pts])
    sized = SizedGrid(types=['NAYY 4x240'] * 2, parallel=np.ones(2, np.int8), i_max_a=np.ones(2), r_ohm=np.zeros(2),
                      x_ohm=np.zeros(2), du_load_pct=np.zeros(2), du_feed_pct=np.zeros(2), marked=np.zeros(2, bool),
                      marked_voltage=np.zeros(2, bool))
    volt = replace(sized, marked_voltage=np.array([True, True]))
    therm = replace(sized, marked=np.array([True, False]))
    grids = {0: (grid('streu'), volt), 1: (grid('ort'), therm), 2: (grid('ort'), sized)}
    summ = {s: _station_summary(g, z, 2) for s, (g, z) in grids.items()}
    assert summ[0]['marked_voltage'] == 2 and summ[0]['marked'] == 0
    rep = _report(summ, grids)
    assert rep['marked']['stations_any'] == 1 and rep['marked']['stations_any_share'] == round(1 / 3, 4)
    v = rep['voltage_only']
    assert v['feeders'] == 2 and v['stations'] == 1 and v['stations_share'] == round(1 / 3, 4)
    assert v['stations_by_area'] == {'stadt': 0, 'ort': 0, 'streu': 1}


class _FixedRng:
    """Liefert für ``random`` überall denselben Wert (Schwelle für has_wp in profiles.assign), Binomial = 0."""

    def __init__(self, u):
        self.u = u

    def random(self, n):
        return np.full(n, self.u)

    def binomial(self, n, p):
        return np.zeros_like(np.asarray(n))


def test_design_rule_uses_same_p_wp_as_assign(tmp_path):
    """Minor 2 (finales Review): Bemessung (DesignRule.wp_share) und Lauf (profiles.assign) nutzen dasselbe p_wp,
    und die Knoten mit Auslegungs-WP sind genau die, an denen assign eine WP ziehen kann."""
    from fakes import write_fake_prepared
    from gridsim import profiles
    from gridsim.data import load_prepared
    from gridsim.feeders.prepare import DESIGN_SCENARIO, DESIGN_YEAR, design_loads
    p = load_prepared(write_fake_prepared(tmp_path / 'p', DESIGN_YEAR), DESIGN_YEAR)
    loads = design_loads(p)
    p_wp = loads['rule'].wp_share
    assert 0 < p_wp <= 1
    below, _ = profiles.assign(p, DESIGN_SCENARIO, _FixedRng(np.nextafter(p_wp, 0.0)))   # knapp unter p_wp: WP
    at, _ = profiles.assign(p, DESIGN_SCENARIO, _FixedRng(p_wp))                       # genau p_wp: keine WP
    assert (below > 0).any() and not (at > 0).any()
    np.testing.assert_array_equal(below > 0, loads['wp_kw'] > 0)


def test_prepare_feeders_warns_without_roads(setup):
    """Ohne osm_roads.json entsteht ein Luftliniennetz: Warnung statt nur Manifesteintrag."""
    inp, prepared = setup
    (inp / 'osm_roads.json').unlink()
    with pytest.warns(RuntimeWarning, match='Luftlinie'):
        out = prepare_feeders(inp, prepared)
    assert json.loads((out / 'manifest.json').read_text())['roads'] is False
