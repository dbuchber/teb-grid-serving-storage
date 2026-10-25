import json
from dataclasses import asdict
from pathlib import Path

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
    assert [r.index for r in cached_seeds(cache, params(), 'none')] == [0, 1, 2]
    again = list(run_many(root, params(), workers=2, cache_dir=cache))  # aus dem Cache
    assert [r.region for r in sorted(again, key=lambda r: r.index)] == [r.region for r in sorted(got, key=lambda r: r.index)]


def test_corrupt_seed_file_is_skipped(tmp_path):
    # Review I2: abgeschnittene Cache-Datei darf keinen 500 auslösen
    root = write_fake_prepared(tmp_path / 'prep')
    cache = tmp_path / 'cache'
    list(run_many(root, params(), workers=1, cache_dir=cache))
    (cache / params().key() / 'seed_1.json').write_text('{"index": 1, "se')
    assert [r.index for r in cached_seeds(cache, params(), 'none')] == [0, 2]
    again = list(run_many(root, params(), workers=1, cache_dir=cache))
    assert sorted(r.index for r in again) == [0, 1, 2]
    assert not list((cache / params().key()).glob('*.tmp'))


def test_key_includes_model_version(monkeypatch):
    # Review I3: Modelländerung darf keinen alten Cache wiederverwenden
    import gridsim.run as runmod
    k1 = params().key()
    monkeypatch.setattr(runmod, 'MODEL_VERSION', 'other')
    assert params().key() != k1


def test_params_accept_moderate_scenario():
    RunParams(weather_year=2023, scenario="2040m", n_seeds=1).validate()


# --- Task 7: Leitungskennzahlen im Lauf ---------------------------------------------------------------------------

REFERENCE = json.loads((Path(__file__).parent / 'data' / 'trafo_reference.json').read_text())
LINE_EXTRA = ('station_line_max_pct', 'station_line_load_h', 'station_line_feed_h', 'station_first_load',
              'station_first_feed')
LINE_REGION = ('stations_line_load_congestion', 'stations_line_feed_congestion', 'stations_line_only', 'line_over_m',
               'line_over_m_load', 'line_over_m_feed', 'marked_feeders', 'tail_feeders')
FIRST = {'trafo', 'leitung', 'beide', 'keiner'}


@pytest.fixture(scope='module')
def prepared_with_feeders(tmp_path_factory):
    """Fake prepared (2012, 2023) mit ``feeders/`` aus ``prepare_feeders`` (Fake-Straßen und -Mitglieder)."""
    from fakes import align_station_positions, fake_build_members_factory, fake_roads
    from gridsim import legacy
    from gridsim.feeders.prepare import prepare_feeders
    tmp = tmp_path_factory.mktemp('feeders')
    build = fake_build_members_factory()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(legacy.load('steyr_sim_variant_a'), 'build_members', build)
        inp = tmp / 'input'
        inp.mkdir()
        fake_roads(inp / 'osm_roads.json')
        prepared = tmp / 'prepared'
        write_fake_prepared(prepared, 2012)
        write_fake_prepared(prepared, 2023)
        align_station_positions(prepared, build)
        prepare_feeders(inp, prepared)
    return prepared


def _assert_matches_reference(got, ref):
    assert set(got.region) >= set(ref['region'])
    for k, v in ref['region'].items():
        if isinstance(v, int) and not isinstance(v, bool):
            assert got.region[k] == v, k
        else:
            assert got.region[k] == pytest.approx(v, rel=1e-9, abs=0), k
    for k in ('station_load_kw_max', 'station_congestion_h', 'station_feed_h', 'worst_day'):
        assert getattr(got, k) == ref[k], k


@pytest.mark.parametrize('set_name', ['default', 'stressed'])
@pytest.mark.parametrize('charging', ['uncontrolled', 'winap', 't3d', 'controlled', 'v2g'])
def test_default_params_trafo_kpis_unchanged(tmp_path, prepared_with_feeders, set_name, charging):
    """Default-Params: Trafo-Kennzahlen wie im Stand 98113e5 (tests/data/trafo_reference.json), mit und ohne Feeders."""
    kw = REFERENCE['sets'][set_name]
    plain = load_prepared(write_fake_prepared(tmp_path), 2023)
    with_feeders = load_prepared(prepared_with_feeders, 2023)
    for i in (0, 1):
        ref = REFERENCE['results'][set_name][charging][str(i)]
        _assert_matches_reference(run_seed(plain, RunParams(charging=charging, **kw), i), ref)
        _assert_matches_reference(run_seed(with_feeders, RunParams(charging=charging, **kw), i), ref)


def test_runs_without_feeders(tmp_path):
    """Review Focus 5: ohne ``feeders/`` läuft alles wie bisher, Leitungswerte sind None."""
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    r = run_seed(p, params(), 0)
    for k in LINE_EXTRA:
        assert r.extra[k] is None, k
    for k in LINE_REGION:
        assert r.region[k] is None, k
    got = list(run_many(tmp_path, params(n_seeds=1), workers=1))
    assert got[0].extra['station_line_max_pct'] is None and got[0].region == r.region


def test_runs_with_feeders(prepared_with_feeders):
    p = load_prepared(prepared_with_feeders, 2023)
    r = run_seed(p, params(scenario='2040', pv_factor=2.0), 0)
    n = p.n_stations
    for k in LINE_EXTRA:
        assert len(r.extra[k]) == n, k
    assert all(x >= 0 for x in r.extra['station_line_max_pct'])
    assert set(r.extra['station_first_load']) | set(r.extra['station_first_feed']) <= FIRST
    for k in LINE_REGION:
        assert r.region[k] is not None, k
    assert r.region['line_over_m'] >= max(r.region['line_over_m_load'], r.region['line_over_m_feed'])
    assert r.region['line_over_m'] <= r.region['line_over_m_load'] + r.region['line_over_m_feed'] + 1e-6
    # Station 2 (nur PV-Hallen, 100 kWp an 125 kVA, PV × 2): Trafo bei Einspeisung überlastet
    assert r.extra['station_first_feed'][2] in ('trafo', 'beide')
    json.dumps(asdict(r))   # Cache-tauglich


def test_run_many_workers_load_feeders(prepared_with_feeders):
    a = run_seed(load_prepared(prepared_with_feeders, 2023), params(n_seeds=2), 1)
    got = {r.index: r for r in run_many(prepared_with_feeders, params(n_seeds=2), workers=2)}
    assert got[1].extra == a.extra and got[1].region == a.region


def test_params_validate_limits():
    with pytest.raises(ValueError, match='limits'):
        params(limits='x').validate()
    with pytest.raises(ValueError, match='netzspeicher'):
        params(netzspeicher='ja').validate()
    params(limits='trafo+leitung', netzspeicher=True).validate()
    assert RunParams().limits == 'trafo' and RunParams().netzspeicher is False


def test_key_includes_limits_and_netzspeicher():
    keys = {params().key(), params(limits='trafo+leitung').key(), params(netzspeicher=True).key()}
    assert len(keys) == 3


def test_model_version():
    import gridsim.run as runmod
    assert runmod.MODEL_VERSION == '2026-10-26.2'


def test_line_overload_reaches_region(prepared_with_feeders):
    """Mit auf 30 % gesenkten Grenzströmen: Leitungsüberlast in extra und Region, Trafo-Werte unverändert."""
    from dataclasses import replace
    from gridsim.feeders.prepare import load_feeders
    p = load_prepared(prepared_with_feeders, 2023)
    pr = params(scenario='2040', pv_factor=2.0)
    weak = {s: (g, replace(z, i_max_a=z.i_max_a * 0.3)) for s, (g, z) in load_feeders(prepared_with_feeders).items()}
    base = run_seed(p, pr, 0)
    r = run_seed(p, pr, 0, feeders=weak)
    assert r.region['line_over_m'] > 0 and r.region['stations_line_feed_congestion'] >= 1
    assert r.region['stations_line_only'] >= 1
    assert {'leitung', 'beide'} & set(r.extra['station_first_feed'] + r.extra['station_first_load'])
    assert max(r.extra['station_line_max_pct']) == pytest.approx(max(base.extra['station_line_max_pct']) / 0.3,
                                                                 rel=1e-3)
    for k in REFERENCE['results']['default']['uncontrolled']['0']['region']:
        assert r.region[k] == base.region[k], k


# --- Fix-Runde 1: Netzstand im Cache ---------------------------------------------------------------------------------

def _make_feeders(prepared):
    """``feeders/`` für ein Fake-prepared (2012 und 2023 vorhanden) wie in ``prepared_with_feeders``."""
    from fakes import align_station_positions, fake_build_members_factory, fake_roads
    from gridsim import legacy
    from gridsim.feeders.prepare import prepare_feeders
    build = fake_build_members_factory()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(legacy.load('steyr_sim_variant_a'), 'build_members', build)
        inp = prepared.parent / 'input'
        inp.mkdir(exist_ok=True)
        fake_roads(inp / 'osm_roads.json')
        align_station_positions(prepared, build)
        prepare_feeders(inp, prepared)


def _weaken_feeders(prepared, factor):
    """Grenzströme aller Stationsdateien skalieren und den Index neu schreiben (anderer Inhalt, gleiche Struktur)."""
    import numpy as np
    d = prepared / 'feeders'
    for f in d.glob('*.npz'):
        z = dict(np.load(f))
        z['i_max_a'] = z['i_max_a'] * factor
        np.savez_compressed(f, **z)


def test_feeders_fingerprint(tmp_path):
    from gridsim.run import feeders_fingerprint
    root = tmp_path / 'prep'
    write_fake_prepared(root, 2012)
    write_fake_prepared(root, 2023)
    assert feeders_fingerprint(root) == 'none' and feeders_fingerprint(None) == 'none'
    _make_feeders(root)
    a = feeders_fingerprint(root)
    assert a != 'none' and feeders_fingerprint(root) == a
    _weaken_feeders(root, 0.5)
    assert feeders_fingerprint(root) not in ('none', a)


def test_cache_follows_feeders_state(tmp_path):
    """Review Fix 1: Cache ohne Netze, dann Netze anlegen → neu rechnen; Netze ändern → wieder neu rechnen."""
    root = tmp_path / 'prep'
    write_fake_prepared(root, 2012)
    write_fake_prepared(root, 2023)
    cache = tmp_path / 'cache'
    pr = params(n_seeds=1, scenario='2040', pv_factor=2.0)
    first = list(run_many(root, pr, workers=1, cache_dir=cache))[0]
    assert first.extra['station_line_max_pct'] is None and first.feeders_fp == 'none'
    assert len(cached_seeds(cache, pr, 'none')) == 1

    _make_feeders(root)
    second = list(run_many(root, pr, workers=1, cache_dir=cache))[0]
    assert second.extra['station_line_max_pct'] is not None and second.feeders_fp not in ('none', None)
    assert cached_seeds(cache, pr, 'none') == []
    manifest = json.loads((cache / pr.key() / 'manifest.json').read_text())
    assert manifest['feeders_fingerprint'] == second.feeders_fp

    _weaken_feeders(root, 0.3)
    third = list(run_many(root, pr, workers=1, cache_dir=cache))[0]
    assert third.feeders_fp != second.feeders_fp
    assert max(third.extra['station_line_max_pct']) > max(second.extra['station_line_max_pct']) * 3
    again = list(run_many(root, pr, workers=1, cache_dir=cache))[0]   # jetzt aus dem Cache
    assert again.extra == third.extra and again.runtime_s == third.runtime_s


def test_run_seed_direct_sees_new_feeders(tmp_path):
    """Review Fix 2: der Prozess-Cache der Netze hängt am Fingerabdruck, nicht nur am Pfad."""
    root = tmp_path / 'prep'
    write_fake_prepared(root, 2012)
    write_fake_prepared(root, 2023)
    p = load_prepared(root, 2023)
    assert run_seed(p, params(), 0).extra['station_line_max_pct'] is None
    _make_feeders(root)
    a = run_seed(p, params(), 0)
    assert a.extra['station_line_max_pct'] is not None
    _weaken_feeders(root, 0.5)
    b = run_seed(p, params(), 0)
    assert b.feeders_fp != a.feeders_fp
    assert max(b.extra['station_line_max_pct']) == pytest.approx(2 * max(a.extra['station_line_max_pct']), rel=1e-2)
