import json

import numpy as np
import pytest

from fakes import write_fake_prepared
from gridsim.data import load_prepared
from gridsim.playback import busiest_week, export_week, week_pct
from gridsim.run import RunParams, flows


@pytest.fixture
def p(tmp_path):
    return load_prepared(write_fake_prepared(tmp_path), 2023)


def test_week_pct_is_flow_over_rating_for_168_hours(p):
    params = RunParams(weather_year=2023, scenario='2040')
    flow = flows(p, params, 0)['flow']
    pct = week_pct(flow, p.kva, start_day=14)
    assert pct.shape == (p.n_stations, 168)
    assert pct[1, 5] == round(100 * flow[14 * 24 + 5, 1] / p.kva[1])


def test_busiest_week_starts_on_monday_and_has_most_overload_hours():
    flow = np.zeros((8760, 2))
    flow[40 * 24:40 * 24 + 30, 0] = 200  # 30 h über 100 kVA ab Tag 40
    start = busiest_week(flow, np.array([100.0, 100.0]), first_weekday=6)  # 1.1. ist Sonntag
    assert (start + 6) % 7 == 0  # Montag
    assert start <= 40 < start + 7


def test_busiest_week_feed_in_counts_negative_flow():
    flow = np.zeros((8760, 1))
    flow[180 * 24 + 12, 0] = -150
    start = busiest_week(flow, np.array([100.0]), first_weekday=0, direction='feed')
    assert start <= 180 < start + 7


def test_export_week_writes_ids_dates_and_series(p, tmp_path):
    out = tmp_path / 'w.json'
    params = RunParams(weather_year=2023, scenario='2040', charging='controlled')
    export_week(p, params, start_day=14, path=out, seed_index=0)
    d = json.loads(out.read_text())
    assert d['start'] == '2023-01-15' and d['hours'] == 168
    assert d['stations'] == p.station_ids
    assert len(d['pct']) == p.n_stations and len(d['pct'][0]) == 168
    assert d['params']['charging'] == 'controlled' and d['seed_index'] == 0
