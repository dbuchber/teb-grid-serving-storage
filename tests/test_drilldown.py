import numpy as np
import pytest

from fakes import write_fake_prepared
from gridsim.data import load_prepared
from gridsim.drilldown import day_curve
from gridsim.run import RunParams, flows

KEYS = ('household_kw', 'heat_pump_kw', 'ev_kw', 'pv_kw', 'storage_kw', 'v2g_kw', 'trafo_kw')


@pytest.fixture
def p(tmp_path):
    return load_prepared(write_fake_prepared(tmp_path), 2023)


@pytest.mark.parametrize('charging', ['uncontrolled', 't3d', 'v2g'])
def test_day_curve_shape_and_balance(p, charging):
    c = day_curve(p, RunParams(weather_year=2023, scenario='2040', charging=charging), 'way/1')
    assert c['step_min'] == 15 and c['station'] == 'way/1' and c['kva'] == 160
    for k in KEYS:
        assert len(c[k]) == 96
    a = {k: np.array(c[k]) for k in KEYS}
    bal = a['household_kw'] + a['heat_pump_kw'] + a['ev_kw'] - a['pv_kw'] - a['storage_kw'] - a['v2g_kw']
    assert np.allclose(a['trafo_kw'], bal, atol=0.05)  # 7 Werte je auf 0,01 gerundet


def test_day_curve_energy_matches_hourly(p):
    params = RunParams(weather_year=2023, scenario='2040')
    c = day_curve(p, params, 'way/1', day=20)
    hourly = flows(p, params, 0)['flow'][20 * 24:21 * 24, 0]
    assert sum(c['trafo_kw']) / 4 == pytest.approx(hourly.sum(), rel=0.02)


def test_worst_day_default(p):
    params = RunParams(weather_year=2023, scenario='2040')
    flow = flows(p, params, 0)['flow'][:, 0]
    worst = int(flow.reshape(365, 24).max(axis=1).argmax())
    c = day_curve(p, params, 'way/1')
    assert c['day'] == worst and c['date'].startswith('2023-')


def test_unknown_station_raises(p):
    with pytest.raises(KeyError):
        day_curve(p, RunParams(weather_year=2023), 'way/999')


def test_station_without_ev_wp(p):
    c = day_curve(p, RunParams(weather_year=2023, scenario='2040'), 'demo:steyr:station-003')
    assert not any(c['ev_kw']) and not any(c['heat_pump_kw']) and not any(c['household_kw'])
