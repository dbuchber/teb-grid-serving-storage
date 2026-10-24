import json

import pytest

from fakes import write_fake_prepared
from gridsim.data import load_prepared
from gridsim.run import RunParams, cached_seeds, run_many, run_seed, seed_of


def params(**kw):
    base = dict(weather_year=2023, scenario='2040', pv_factor=1.0, charging='uncontrolled', storage='base', n_seeds=3)
    return RunParams(**{**base, **kw})


@pytest.mark.parametrize('field,value', [('weather_year', 2020), ('pv_factor', 3.0), ('charging', 'foo'),
                                         ('scenario', '2050'), ('storage', 'x'), ('n_seeds', 0)])
def test_params_validate_rejects_unknown(field, value):
    with pytest.raises(ValueError, match=field):
        params(**{field: value}).validate()


def test_key_stable_and_distinct():
    assert params().key() == params().key() and len(params().key()) == 12
    assert params().key() != params(charging='t3d').key()


def test_seed_of():
    assert seed_of(0) == 20261024 and seed_of(2) == 20263024


@pytest.mark.parametrize('charging', ['uncontrolled', 'winap', 't3d', 'controlled', 'v2g'])
def test_run_seed_fake_deterministic(tmp_path, charging):
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    a = run_seed(p, params(charging=charging), 0)
    b = run_seed(p, params(charging=charging), 0)
    assert a.region == b.region and a.seed == seed_of(0)
    assert len(a.station_load_kw_max) == 3 and len(a.worst_day) == 3
    c = run_seed(p, params(charging=charging), 1)
    assert c.station_load_kw_max != a.station_load_kw_max


def test_run_many_yields_all_seeds(tmp_path):
    root = write_fake_prepared(tmp_path / 'prep')
    cache = tmp_path / 'cache'
    got = list(run_many(root, params(), workers=2, cache_dir=cache))
    assert {r.index for r in got} == {0, 1, 2}
    key = params().key()
    assert sorted(f.name for f in (cache / key).glob('seed_*.json')) == ['seed_0.json', 'seed_1.json', 'seed_2.json']
    manifest = json.loads((cache / key / 'manifest.json').read_text())
    assert manifest['params']['charging'] == 'uncontrolled' and 'legacy_sha256sums' in manifest
    assert [r.index for r in cached_seeds(cache, params())] == [0, 1, 2]
    again = list(run_many(root, params(), workers=2, cache_dir=cache))  # aus dem Cache
    assert [r.region for r in sorted(again, key=lambda r: r.index)] == [r.region for r in sorted(got, key=lambda r: r.index)]


def test_corrupt_seed_file_is_skipped(tmp_path):
    # Review I2: abgeschnittene Cache-Datei darf keinen 500 auslösen
    root = write_fake_prepared(tmp_path / 'prep')
    cache = tmp_path / 'cache'
    list(run_many(root, params(), workers=1, cache_dir=cache))
    (cache / params().key() / 'seed_1.json').write_text('{"index": 1, "se')
    assert [r.index for r in cached_seeds(cache, params())] == [0, 2]
    again = list(run_many(root, params(), workers=1, cache_dir=cache))
    assert sorted(r.index for r in again) == [0, 1, 2]
    assert not list((cache / params().key()).glob('*.tmp'))


def test_key_includes_model_version(monkeypatch):
    # Review I3: Modelländerung darf keinen alten Cache wiederverwenden
    import gridsim.run as runmod
    k1 = params().key()
    monkeypatch.setattr(runmod, 'MODEL_VERSION', 'other')
    assert params().key() != k1
