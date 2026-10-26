"""CLI: batch mit Grenzmodus und Netzspeicher (Task 11)."""
import json

import pytest

from fakes import write_fake_prepared
from gridsim import run as runmod
from gridsim.cli import combos, main, run_batch
from test_run import prepared_with_feeders  # noqa: F401  (Fixture)


def test_combos_skip_identical_line_mode():
    got = list(combos((2023,), ('2030',), ('uncontrolled', 'controlled'), ('base',), (1.0,),
                      ('trafo', 'trafo+leitung'), (False, True)))
    # ungesteuert: trafo+leitung identisch zu trafo, wird übersprungen
    assert (2023, '2030', 'uncontrolled', 'base', 1.0, 'trafo+leitung', False) not in got
    assert (2023, '2030', 'uncontrolled', 'base', 1.0, 'trafo', True) in got
    assert (2023, '2030', 'controlled', 'base', 1.0, 'trafo+leitung', True) in got
    assert len(got) == 6


def test_batch_limits_and_netzspeicher(prepared_with_feeders, tmp_path, capsys):  # noqa: F811
    cache = tmp_path / 'cache'
    main(['batch', '--prepared', str(prepared_with_feeders), '--cache', str(cache), '--seeds', '1', '--workers', '1',
          '--years', '2023', '--scenarios', '2040', '--charging', 'controlled', '--limits', 'trafo', 'trafo+leitung',
          '--netzspeicher', 'off', 'on'])
    rows = [json.loads(x) for x in capsys.readouterr().out.splitlines() if x.startswith('{')]
    assert {(r['limits'], r['netzspeicher']) for r in rows} == {('trafo', False), ('trafo', True),
                                                                ('trafo+leitung', False), ('trafo+leitung', True)}
    for r in rows:
        params = runmod.RunParams(weather_year=2023, scenario='2040', charging='controlled', n_seeds=1,
                                  limits=r['limits'], netzspeicher=r['netzspeicher'])
        assert r['key'] == params.key()
        region = (cache / params.key() / 'region.csv').read_text()
        assert 'stations_line_load_congestion' in region and 'nan' not in region
        assert r['stations_line_load_congestion'] is not None


def test_batch_defaults_unchanged(tmp_path):
    prepared = write_fake_prepared(tmp_path / 'p')
    out = run_batch(prepared, tmp_path / 'c', (2023,), ('2030',), ('uncontrolled',), ('base',), (1.0,), n_seeds=1,
                    workers=1)
    (key, bands), = out.items()
    assert key == (2023, '2030', 'uncontrolled', 'base', 1.0, 'trafo', False)
    assert bands['stations_line_load_congestion'] is None   # ohne Netze keine Leitungsbänder
    region = (tmp_path / 'c' / runmod.RunParams(n_seeds=1).key() / 'region.csv').read_text()
    assert 'stations_line_load_congestion' not in region


def test_batch_rejects_bad_netzspeicher(tmp_path):
    with pytest.raises(SystemExit):
        main(['batch', '--prepared', str(tmp_path), '--cache', str(tmp_path), '--netzspeicher', 'maybe'])


def test_prepare_feeders_out_without_extra_stations_is_an_error(tmp_path, capsys):
    """--out ohne --extra-stations wurde früher still ignoriert (Netze landeten in <prepared>/feeders/)."""
    with pytest.raises(SystemExit) as e:
        main(['prepare-feeders', '--input', str(tmp_path), '--prepared', str(tmp_path), '--out', str(tmp_path / 'v')])
    assert e.value.code == 2 and '--extra-stations' in capsys.readouterr().err
    assert not (tmp_path / 'feeders').exists()


def test_help_texts_for_line_options(capsys):
    with pytest.raises(SystemExit):
        main(['batch', '--help'])
    out = capsys.readouterr().out
    assert 'trafo+leitung' in out and 'Netzspeicher' in out
