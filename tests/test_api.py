import json
import threading
import time

import pytest
from fastapi.testclient import TestClient

from fakes import write_fake_prepared
from gridsim.run import SeedResult, seed_of

from api.app import create_app


def fake_result(i):
    return SeedResult(index=i, seed=seed_of(i), region={'stations_load_congestion': i, 'e_net_mwh': float(i),
                      'storage_units': i, 'trafo_plus1': 0, 'trafo_plus2': 0, 'trafo_over_1000': 0},
                      station_load_kw_max=[1.0, 2.0, 3.0], station_congestion_h=[i, 0, 0], station_feed_h=[0, 0, 0],
                      worst_day=[1, 2, 3], feeders_fp='none')


class FakeRunner:
    def __init__(self, delay=0.0, gate=None):
        self.calls, self.delay, self.gate = [], delay, gate

    def __call__(self, root, params, workers=4, cache_dir=None):
        self.calls.append(params)
        for i in range(params.n_seeds):
            if self.gate is not None:
                self.gate.wait(5)
            time.sleep(self.delay)
            yield fake_result(i)


@pytest.fixture
def make(tmp_path):
    root = write_fake_prepared(tmp_path / 'prep')

    def _make(runner=None, **kw):
        app = create_app(prepared_root=root, cache_dir=tmp_path / 'cache', runner=runner or FakeRunner(), **kw)
        return TestClient(app), app
    return _make


BODY = {'weather_year': 2023, 'scenario': '2030', 'pv_factor': 1.0, 'charging': 'uncontrolled', 'storage': 'base', 'n_seeds': 3}


def wait_done(client, run_id, timeout=5):
    t = time.time()
    while time.time() - t < timeout:
        r = client.get(f'/api/runs/{run_id}').json()
        if r['status'] in ('done', 'cached', 'error'):
            return r
        time.sleep(0.02)
    raise AssertionError('timeout')


def test_health_and_options(make):
    client, _ = make()
    assert client.get('/api/health').json() == {'ok': True}
    opt = client.get('/api/options').json()
    assert 't3d' in opt['charging'] and opt['cost_defaults']['storage_eur_per_kwh'] == 600
    assert 'trafo_step_eur' in opt['placeholders']
    st = client.get('/api/stations').json()
    assert [s['id'] for s in st] == ['way/1', 'node/2', 'demo:steyr:station-003']
    assert [s['idx'] for s in st] == [0, 1, 2]   # Stationsindex explizit (Zuordnung zu lines.geojson)


@pytest.mark.parametrize('field,value', [('weather_year', 2020), ('pv_factor', 3.0), ('charging', 'foo'), ('n_seeds', 'x')])
def test_invalid_params_400(make, field, value):
    client, _ = make()
    r = client.post('/api/runs', json={**BODY, field: value})
    assert r.status_code == 400 and field in r.json()['error']


def test_same_params_run_once(make):
    runner = FakeRunner(delay=0.05)
    client, _ = make(runner)
    a = client.post('/api/runs', json=BODY).json()
    b = client.post('/api/runs', json=BODY).json()
    assert a['run_id'] == b['run_id']
    wait_done(client, a['run_id'])
    assert len(runner.calls) == 1


def test_max_jobs_queue(make):
    gate = threading.Event()
    client, _ = make(FakeRunner(gate=gate), max_jobs=2)
    ids = [client.post('/api/runs', json={**BODY, 'charging': c}).json() for c in ('uncontrolled', 'winap', 't3d')]
    assert [i['status'] for i in ids].count('queued') == 1
    gate.set()
    for i in ids:
        assert wait_done(client, i['run_id'])['status'] == 'done'


def test_resume_after_disconnect(make):
    gate = threading.Event()
    client, _ = make(FakeRunner(gate=gate))
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    gate.set()
    with client.stream('GET', f'/api/runs/{run_id}/events') as s:
        for line in s.iter_lines():
            if line.startswith('data:') and '"index"' in line:
                break  # Verbindung nach dem ersten Seed abbrechen
    r = wait_done(client, run_id)
    assert sorted(x['index'] for x in r['seeds']) == [0, 1, 2]


def test_sse_replay_cached(make, tmp_path):
    client, app = make(replay_delay=0.01)
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    client2, _ = make(replay_delay=0.01)  # neue App, gleicher Cache auf Platte → Replay
    from gridsim.run import RunParams
    from dataclasses import asdict
    cache = tmp_path / 'cache' / RunParams(**BODY).key()
    cache.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        (cache / f'seed_{i}.json').write_text(json.dumps(asdict(fake_result(i))))
    r = client2.post('/api/runs', json=BODY).json()
    assert r['status'] == 'cached'
    events = []
    with client2.stream('GET', f'/api/runs/{r["run_id"]}/events') as s:
        for line in s.iter_lines():
            if line.startswith('event:'):
                events.append(line.split(':', 1)[1].strip())
    assert events == ['seed', 'seed', 'seed', 'done']


def test_cached_seeds_with_other_feeders_state_are_recomputed(make, tmp_path):
    """Fix-Runde 1 Task 7: Cache aus einem anderen Netzstand gilt nicht als fertig."""
    runner = FakeRunner()
    client, _ = make(runner=runner)
    from dataclasses import asdict, replace
    from gridsim.run import RunParams
    cache = tmp_path / 'cache' / RunParams(**BODY).key()
    cache.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        (cache / f'seed_{i}.json').write_text(json.dumps(asdict(replace(fake_result(i), feeders_fp='abc'))))
    r = client.post('/api/runs', json=BODY).json()
    assert r['status'] != 'cached'
    wait_done(client, r['run_id'])
    assert len(runner.calls) == 1


def test_day_unknown_station_404(make):
    client, _ = make()
    r = client.get('/api/stations/way%2F999/day', params={'weather_year': 2023})
    assert r.status_code == 404 and 'no model data' in r.json()['error']


def test_day_known_station(make):
    client, _ = make()
    r = client.get('/api/stations/way%2F1/day', params={'weather_year': 2023, 'scenario': '2040'})
    assert r.status_code == 200 and len(r.json()['trafo_kw']) == 96


def test_costs(make):
    client, _ = make()
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    r = client.post('/api/costs', json={'run_id': run_id, 'cost': {'trafo_step_eur': 30000}}).json()
    assert r['storage_eur'] == 1 * 10 * 600 and r['trafo_eur'] == 0 and 'line_eur_per_m' in r['placeholders']


def test_sse_disconnect_before_first_seed_does_not_block_run(make):
    # Review C1: Keepalive darf nicht unter dem Lock gesendet werden
    gate = threading.Event()
    client, app = make(FakeRunner(gate=gate), keepalive_s=0.1)
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    with client.stream('GET', f'/api/runs/{run_id}/events') as s:
        for line in s.iter_lines():
            if line.startswith(':'):
                break  # Keepalive erhalten, Client geht
    import gc; gc.collect()
    gate.set()
    r = wait_done(client, run_id)
    assert r['status'] == 'done' and len(r['seeds']) == 3


def test_costs_invalid_value_400(make):
    client, _ = make()
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    r = client.post('/api/costs', json={'run_id': run_id, 'cost': {'storage_eur_per_kwh': 'x'}})
    assert r.status_code == 400


def test_done_run_is_replayed_with_delay(make):
    # Review M6: auch ein im selben Prozess fertig gerechneter Lauf wächst sichtbar
    client, _ = make(replay_delay=0.05)
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    t = time.time()
    with client.stream('GET', f'/api/runs/{run_id}/events') as s:
        n = sum(1 for line in s.iter_lines() if line.startswith('event: seed'))
    assert n == 3 and time.time() - t >= 0.14


# --- Leitungen (Task 10) ---

def write_fake_feeders(root):
    """Minimaler feeders/-Ordner: index.json je Stationsindex, lines.geojson mit einem Abschnitt."""
    d = root / 'feeders'
    d.mkdir()
    (d / 'index.json').write_text(json.dumps({
        '0': {'area': 'stadt', 'n_feeders': 4, 'marked': 1}, '1': {'area': 'ort', 'n_feeders': 3, 'marked': 0, 'marked_voltage': 3},
        '2': {'area': 'streu', 'n_feeders': 1, 'marked': 2}}))
    (d / 'lines.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'geometry': {'type': 'LineString', 'coordinates': [[14.4, 48.0], [14.41, 48.0]]},
         'properties': {'station': 0, 'type': 'NAYY 4x150', 'parallel': 1, 'feeder': 0, 'overhead': False,
                        'service': False, 'length_m': 80.0}}]}))


def test_limits_and_netzspeicher_in_run_body(make):
    runner = FakeRunner()
    client, _ = make(runner)
    r = client.post('/api/runs', json={**BODY, 'limits': 'trafo+leitung', 'netzspeicher': True}).json()
    wait_done(client, r['run_id'])
    assert runner.calls[0].limits == 'trafo+leitung' and runner.calls[0].netzspeicher is True
    plain = client.post('/api/runs', json=BODY).json()   # Standard: trafo, ohne Netzspeicher, eigener Lauf
    assert plain['run_id'] != r['run_id']
    wait_done(client, plain['run_id'])
    assert runner.calls[1].limits == 'trafo' and runner.calls[1].netzspeicher is False


@pytest.mark.parametrize('field,value', [('limits', 'x'), ('netzspeicher', 'maybe')])
def test_invalid_limits_400(make, field, value):
    client, _ = make()
    r = client.post('/api/runs', json={**BODY, field: value})
    assert r.status_code == 400 and field in r.json()['error']


def test_options_list_limits(make):
    client, _ = make()
    opt = client.get('/api/options').json()
    assert opt['limits'] == ['trafo', 'trafo+leitung'] and opt['netzspeicher'] == [False, True]


def test_stations_area_marked_none_without_feeders(make):
    client, _ = make()
    assert all(s['area'] is None and s['marked'] is None for s in client.get('/api/stations').json())


def test_stations_area_and_marked_with_feeders(tmp_path):
    root = write_fake_prepared(tmp_path / 'prep')
    write_fake_feeders(root)
    client = TestClient(create_app(prepared_root=root, cache_dir=tmp_path / 'cache', runner=FakeRunner()))
    st = client.get('/api/stations').json()
    assert [(s['area'], s['marked']) for s in st] == [('stadt', 1), ('ort', 0), ('streu', 2)]
    assert [s['marked_voltage'] for s in st] == [None, 3, None]   # Fix-Runde 4: reine Spannungsfälle getrennt


def test_lines_404_without_feeders(make):
    client, _ = make()
    assert client.get('/api/lines').status_code == 404


def test_lines_geojson_with_feeders(tmp_path):
    root = write_fake_prepared(tmp_path / 'prep')
    write_fake_feeders(root)
    client = TestClient(create_app(prepared_root=root, cache_dir=tmp_path / 'cache', runner=FakeRunner()))
    r = client.get('/api/lines', params={'weather_year': 2023})
    assert r.status_code == 200 and r.json()['features'][0]['properties']['station'] == 0
    assert client.get('/api/lines', params={'weather_year': 2020}).status_code == 400


def test_costs_pass_line_and_netzspeicher_medians(make, monkeypatch):
    """Task 7/9 Review: line_over_m und netzspeicher_kwh (Median, None-sicher) gehen in metrics.costs."""
    def runner(root, params, workers=4, cache_dir=None):
        for i in range(3):
            r = fake_result(i)
            r.region.update({'line_over_m': 100.0 * (i + 1), 'netzspeicher_kwh': 50.0 * (i + 1)})
            yield r
    client, _ = make(runner)
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    c = client.post('/api/costs', json={'run_id': run_id, 'cost': {'line_eur_per_m': 10}}).json()
    assert c['line_eur'] == 200.0 * 10 and c['netzspeicher_eur'] == 100.0 * 600


def test_costs_without_line_values_are_none(make):
    client, _ = make()   # fake_result ohne Leitungskennzahlen (Lauf ohne feeders/)
    run_id = client.post('/api/runs', json=BODY).json()['run_id']
    wait_done(client, run_id)
    c = client.post('/api/costs', json={'run_id': run_id, 'cost': {'line_eur_per_m': 10}}).json()
    assert c['line_eur'] is None and c['netzspeicher_eur'] is None
