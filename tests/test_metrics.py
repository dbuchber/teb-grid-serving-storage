import numpy as np
import pytest

from gridsim import legacy, metrics

need = legacy.load('steyr_storage_need')


def test_station_rows_equal_legacy():
    rng = np.random.default_rng(1)
    flow = rng.normal(250, 90, (8760, 5))
    kva = np.array([250.0, 400, 160, 630, 250])
    cap = np.array([30.0, 0, 10, 80, 5])
    rows = metrics.station_rows(flow, kva, cap)
    for s in range(5):
        old = need.segment_row(flow[:, s], kva[s], np.array([cap[s]]))
        if old is None:
            assert rows[s] is None
            continue
        old['n_speicher'] = max(old['n_speicher_energie'], old['n_speicher_leistung'])
        for k in old:
            if k == 'speicher_im_modell':
                continue
            assert rows[s][k] == old[k], (s, k)


def test_no_congestion_gives_none_and_zero_kpis():
    flow = np.full((8760, 3), 50.0)
    rows = metrics.station_rows(flow, np.full(3, 400.0), np.zeros(3))
    assert rows == [None, None, None]
    k = metrics.region_kpis(rows, rows, None, 3)
    assert k['stations_load_congestion'] == 0 and k['e_net_mwh'] == 0 and k['storage_units'] == 0
    assert k['congestion_h_median'] == 0 and k['ev_unmet_mwh'] == 0


def test_region_kpis_counts():
    flow = np.full((8760, 2), 100.0)
    flow[100:103, 0] = 300.0  # 3 h über 250 kVA
    rows = metrics.station_rows(flow, np.array([250.0, 400.0]), np.zeros(2))
    k = metrics.region_kpis(rows, [None, None], np.ones((2, 365)), 2)
    assert k['stations_load_congestion'] == 1 and k['congestion_h_median'] == 3
    assert k['trafo_plus1'] == 1 and k['ev_unmet_mwh'] == round(730 / 1000, 3)


def test_costs_mark_placeholders():
    k = {'storage_units': 10, 'trafo_plus1': 2, 'trafo_plus2': 1, 'trafo_over_1000': 0, 'e_inst_mwh': 0.1}
    c = metrics.costs(k, dict(metrics.COST_DEFAULTS))
    assert c['storage_eur'] == 10 * 10 * 600
    assert c['trafo_eur'] is None and 'trafo_step_eur' in c['placeholders']
    c2 = metrics.costs(k, dict(metrics.COST_DEFAULTS, trafo_step_eur=30000))
    assert c2['trafo_eur'] == (2 * 1 + 1 * 2) * 30000
    assert 'line_eur_per_m' in c2['placeholders']


# --- Task 7: Leitungskennzahlen -------------------------------------------------------------------------------------

def _line_case():
    """Zwei Abgänge: Abschnitt 0 (100 m) → 1 (50 m) auf Abgang 0, Abschnitt 2 (30 m) auf Abgang 1."""
    from scipy import sparse
    from gridsim.feeders.sizing import SizedGrid
    from gridsim.feeders.topology import StationGrid
    grid = StationGrid(station=0, area='ort', node_index=np.arange(2), parent=np.array([-1, 0, -1], np.int32),
                       length_m=np.array([100.0, 50.0, 30.0], np.float32), feeder=np.array([0, 0, 1], np.int16),
                       service=np.zeros(3, bool), overhead=np.zeros(3, bool),
                       downstream=sparse.csr_matrix(np.array([[1, 0], [1, 0], [0, 1]])),
                       marked=np.array([False, True]), geometry=[np.zeros((2, 2))] * 3,
                       tail=np.array([True, False]))
    sized = SizedGrid(types=['NAYY 4x150'] * 3, parallel=np.ones(3, np.int8), i_max_a=np.full(3, 275.0),
                      r_ohm=np.zeros(3), x_ohm=np.zeros(3), du_load_pct=np.zeros(2), du_feed_pct=np.zeros(2),
                      marked=np.array([True, False]))
    return grid, sized


def test_line_kpis_directions_and_lengths():
    grid, sized = _line_case()
    pct = np.zeros((8760, 3), np.float32)       # vorzeichenbehaftet: + Bezug, − Einspeisung
    pct[10, 0] = 130.0                          # Abschnitt 0 bei Bezug überlastet (1 h)
    pct[11, 0] = -105.0                         # und bei Einspeisung (1 h)
    pct[12:15, 2] = -120.0                      # Abschnitt 2 bei Einspeisung (3 h)
    pct[20, 1] = 100.0                          # genau 100 %: keine Überlast
    k = metrics.line_kpis(pct, sized, grid)
    assert k['max_pct'] == pytest.approx(130.0)
    assert k['load_h'] == 1 and k['feed_h'] == 4
    assert k['over_m'] == pytest.approx(130.0)
    assert k['over_m_load'] == pytest.approx(100.0) and k['over_m_feed'] == pytest.approx(130.0)
    assert k['feeder_load_h'] == [1, 0] and k['feeder_feed_h'] == [1, 3]
    assert k['marked_feeders'] == 2 and k['tail_feeders'] == 1


def test_line_kpis_empty_grid():
    grid, sized = _line_case()
    k = metrics.line_kpis(np.zeros((8760, 3), np.float32), sized, grid)
    assert k['max_pct'] == 0.0 and k['load_h'] == 0 and k['over_m'] == 0.0


@pytest.mark.parametrize('trafo,line,expected', [(140, 90, 'trafo'), (140, 101, 'beide'), (90, 120, 'leitung'),
                                                 (100, 100, 'keiner')])
def test_first_classification(trafo, line, expected):
    """Höchste Auslastung (%) von Trafo und Leitung in einer Richtung; Überlast heißt > 100 %."""
    assert metrics.first_bottleneck(trafo, line) == expected


def test_first_classification_without_line():
    assert metrics.first_bottleneck(140, None) is None


def test_costs_line_eur():
    k = {'storage_units': 0, 'trafo_plus1': 0, 'trafo_plus2': 0, 'trafo_over_1000': 0, 'line_over_m': 250.0}
    c = metrics.costs(k, dict(metrics.COST_DEFAULTS))
    assert c['line_eur'] is None and 'line_eur_per_m' in c['placeholders']
    assert 'not in the live model' not in c['note']
    c2 = metrics.costs(k, dict(metrics.COST_DEFAULTS, line_eur_per_m=200.0))
    assert c2['line_eur'] == 250.0 * 200.0 and 'line_eur_per_m' not in c2['placeholders']
    c3 = metrics.costs(dict(k, line_over_m=None), dict(metrics.COST_DEFAULTS, line_eur_per_m=200.0))
    assert c3['line_eur'] is None


def test_line_limit_from_one_constant():
    """Minor 3 (finales Review): Bewertung und Abnahme leiten die 100-%-Grenze aus sizing.I_LIMIT ab."""
    from gridsim import metrics
    from gridsim.feeders import report, sizing
    assert metrics.LINE_LIMIT_PCT == 100.0 * sizing.I_LIMIT == 100.0
    assert report.LIMIT_PCT == metrics.LINE_LIMIT_PCT
