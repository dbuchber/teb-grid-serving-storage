"""Abnahmebericht NS-Leitungen (gridsim/feeders/report.py)."""
import json

import numpy as np
import pytest

from gridsim.cli import main
from gridsim.feeders import report
from gridsim.run import SeedResult
from test_run import prepared_with_feeders  # noqa: F401  (Fixture)


def seeds(matrix, first_load=None, first_feed=None):
    """SeedResults mit ``station_line_max_pct`` aus ``matrix`` (Seeds × Stationen)."""
    out = []
    for i, row in enumerate(matrix):
        n = len(row)
        out.append(SeedResult(index=i, seed=i, region={}, station_load_kw_max=[0] * n, station_congestion_h=[0] * n,
                              station_feed_h=[0] * n, worst_day=[0] * n,
                              extra={'station_line_max_pct': list(row),
                                     'station_first_load': (first_load or [['keiner'] * n] * len(matrix))[i],
                                     'station_first_feed': (first_feed or [['keiner'] * n] * len(matrix))[i]}))
    return out


def ten(values):
    """10 Seeds, alle mit denselben Stationswerten."""
    return seeds([values] * 10)


def test_acceptance_passes_with_five_over_100():
    ok = ten([101, 102, 103, 104, 105] + [50] * 252)
    acc = report.acceptance({2012: ok, 2017: ok, 2023: ok})
    assert acc['passed'] and acc['combined']['over_100'] == 5 and acc['combined']['over_120'] == 0


def test_acceptance_fails_on_sixth_station_or_one_over_120():
    six = ten([101] * 6 + [50] * 251)
    assert not report.acceptance({2012: six, 2017: six, 2023: six})['passed']
    hard = ten([121] + [50] * 256)
    acc = report.acceptance({2012: hard, 2017: hard, 2023: hard})
    assert not acc['passed'] and acc['combined']['over_120'] == 1


def test_acceptance_takes_p90_over_seeds_and_max_over_years():
    # Station 0: ein Ausreißer-Seed von 10 liegt über dem P90 (P90 = 9. von 10 Werten interpoliert)
    m = [[50, 50]] * 9 + [[300, 50]]
    p90 = report.station_p90(seeds(m))
    assert p90[0] == pytest.approx(np.percentile([50] * 9 + [300], 90)) and p90[1] == 50
    low, high = ten([50, 50]), ten([50, 130])
    acc = report.acceptance({2012: low, 2017: high, 2023: low})
    assert acc['combined']['over_120'] == 1 and acc['years'][2012]['over_120'] == 0
    assert acc['combined']['stations_over_100'] == [1]


def test_acceptance_missing_year_fails_and_none_stations_ignored():
    r = ten([None, 50])
    acc = report.acceptance({2012: r, 2023: r})
    assert acc['missing_years'] == [2017] and not acc['passed']
    assert acc['combined']['over_100'] == 0


def test_acceptance_limit_is_five_of_all_stations():
    """Fix-Runde 1: höchstens 5 Stationen über 100 %, gleich wie viele Stationen es gibt (5 von 465)."""
    acc = report.acceptance({y: ten([101] * 6 + [50] * 459) for y in report.ACCEPT_YEARS})
    assert not acc['passed'] and acc['n_stations'] == 465 and 'max_over_scaled' not in acc


def test_render_states_five_of_n():
    acc = report.acceptance({y: ten([101] * 5 + [50] * 460) for y in report.ACCEPT_YEARS})
    rep = {'n_stations': 465, 'cable_share': {'by_route_length': 0.75, 'by_cable_length': 0.72, 'target': 0.79,
                                             'band': [0.74, 0.84]},
           'trunk_km_per_station': {'route_length': 2.0, 'cable_length': 3.0, 'target': 2.7},
           'feeders_per_station': {'mean': 4.4, 'median': 3, 'target': [3.4, 3.8]}, 'km_per_type': {},
           'marked': {'feeders_any': 0, 'stations_any': 0, 'stations_any_share': 0.0, 'feeders_long': 0,
                      'feeders_sizing': 0}, 'tails': {'feeders': 0, 'stations': 0}}
    md = report.render(rep, {}, acc, [], {})
    assert 'höchstens 5 von 465 Stationen über 100 %' in md and '**bestanden**' in md and '257' not in md


def test_station_class_majority_and_tie_goes_to_heavier():
    fl = [['trafo', 'keiner', 'leitung'], ['trafo', 'beide', 'trafo'], ['keiner', 'beide', 'leitung'],
          ['keiner', 'keiner', 'trafo']]
    r = seeds([[0, 0, 0]] * 4, first_load=fl)
    assert report.station_class(r) == ['trafo', 'beide', 'leitung']
    assert report.combined_class(['trafo', 'keiner', None], ['leitung', 'keiner', None]) == ['leitung', 'keiner', None]


def test_chain_first_scenario_with_bottleneck():
    cls = {'heute': ['keiner', 'leitung', 'keiner', 'keiner'],
           '2030': ['trafo', 'beide', 'keiner', 'keiner'],
           '2040': ['beide', 'beide', 'leitung', 'keiner']}
    assert report.chain(cls) == {('2030', 'trafo'): 1, ('heute', 'leitung'): 1, ('2040', 'leitung'): 1, 'nie': 1}


def test_plausibility_flags_band():
    rep = {'cable_share': {'by_route_length': 0.75, 'by_cable_length': 0.72, 'target': 0.79, 'band': [0.74, 0.84]},
           'trunk_km_per_station': {'route_length': 2.0, 'cable_length': 3.0, 'target': 2.7},
           'feeders_per_station': {'mean': 4.4, 'median': 3, 'target': [3.4, 3.8]}}
    rows = {r[0]: r for r in report.plausibility(rep)}
    assert rows['Kabelanteil nach Trassenlänge (Abnahmegröße)'][3] is True
    assert rows['Abgänge je Station (Mittel / Median)'][3] is False


def test_lines_report_end_to_end(prepared_with_feeders, tmp_path):  # noqa: F811
    cache = tmp_path / 'cache'
    main(['batch', '--prepared', str(prepared_with_feeders), '--cache', str(cache), '--seeds', '2', '--workers', '1',
          '--years', '2012', '2023', '--scenarios', 'heute', '2030', '2040', '--charging', 'uncontrolled'])
    main(['batch', '--prepared', str(prepared_with_feeders), '--cache', str(cache), '--seeds', '2', '--workers', '1',
          '--years', '2023', '--scenarios', '2040', '--charging', 'controlled', '--limits', 'trafo+leitung',
          '--netzspeicher', 'on'])
    out = tmp_path / 'docs' / 'r.md'
    main(['lines-report', '--prepared', str(prepared_with_feeders), '--cache', str(cache), '--report', str(out)])
    md = out.read_text()
    data = json.loads(out.with_suffix('.json').read_text())
    assert '## Abnahmegrenze „heute“' in md and 'nicht bestanden' in md       # 2017 fehlt
    assert data['acceptance']['missing_years'] == [2017]
    assert len(data['compare']) == 7
    ns = [r for r in data['compare'] if r['netzspeicher']]
    assert ns[0]['limits'] == 'trafo+leitung' and ns[0]['netzspeicher_n'] is not None
    assert set(data['chains']) == {'2012', '2023'}
    n = len(json.loads((prepared_with_feeders / 'feeders' / 'index.json').read_text()))
    assert sum(data['chains']['2023'].values()) == n
    assert '## Reihenfolge heute → 2030 → 2040' in md


def test_segment_table(prepared_with_feeders):  # noqa: F811
    from gridsim.data import load_prepared
    from gridsim.feeders.prepare import load_feeders
    from gridsim.run import RunParams
    p = load_prepared(prepared_with_feeders, 2023)
    fe = load_feeders(prepared_with_feeders)
    t = report.segment_table(p, RunParams(scenario='2040', pv_factor=2.0), 0, fe, [0])
    rows = t[0]
    assert len(rows) == len(fe[0][0].length_m)
    assert rows == sorted(rows, key=lambda r: -r['max_pct'])
    assert {'type', 'max_pct', 'hours_over', 'tail', 'service'} <= set(rows[0])


def test_plausibility_german_decimals():
    rep = {'cable_share': {'by_route_length': 0.7433, 'by_cable_length': 0.72, 'target': 0.79, 'band': [0.74, 0.84]},
           'trunk_km_per_station': {'route_length': 2.057, 'cable_length': 3.1, 'target': 2.7},
           'feeders_per_station': {'mean': 4.36, 'median': 3, 'target': [3.4, 3.8]}}
    rows = {r[0]: r for r in report.plausibility(rep)}
    assert rows['NS-Trasse je Station'][1:3] == ('2,06 km', 'ca. 2,7 km')


def test_render_lists_voltage_only_feeders_separately():
    """Fix-Runde 4: reine Spannungsfälle mit Anzahl, Stationen und Gebietstyp, getrennt von den markierten."""
    rep = {'n_stations': 100, 'cable_share': {'by_route_length': 0.75, 'by_cable_length': 0.72, 'target': 0.79,
                                             'band': [0.74, 0.84]},
           'trunk_km_per_station': {'route_length': 2.0, 'cable_length': 3.0, 'target': 2.7},
           'feeders_per_station': {'mean': 4.4, 'median': 3, 'target': [3.4, 3.8]}, 'km_per_type': {},
           'marked': {'feeders_any': 9, 'stations_any': 8, 'stations_any_share': 0.08, 'feeders_long': 9,
                      'feeders_sizing': 0}, 'tails': {'feeders': 0, 'stations': 0},
           'voltage_only': {'feeders': 71, 'stations': 57, 'stations_share': 0.57,
                            'stations_by_area': {'stadt': 2, 'ort': 26, 'streu': 29}}}
    md = report.render(rep, {}, None, [], {})
    assert 'Nur Spannung (zählt nicht zur 10-%-Grenze): 71 Abgänge an 57 Stationen (57,0 %; stadt 2, ort 26, streu 29)' in md
