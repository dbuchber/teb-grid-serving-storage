from gridsim.validate import HEUTE_LEGACY, REFERENCE, compare, trend_ok


def ref_results(scale=1.0):
    return {k: {'stations_load_congestion': v[0] * scale, 'e_net_mwh': v[1] * scale} for k, v in {**REFERENCE['load'], **HEUTE_LEGACY}.items()}


def test_compare_flags_outside_tolerance():
    rows = compare(ref_results(1.5))
    big = [r for r in rows if r['key'] == (2012, '2040') and r['kpi'] == 'e_net_mwh'][0]
    assert not big['ok'] and abs(big['ratio'] - 1.5) < 1e-9
    assert all(r['ok'] for r in compare(ref_results(1.0)))


def test_small_reference_uses_absolute_floor():
    ref = {'load': {(2023, '2030'): (2, 0.2)}}
    res = {(2023, '2030'): {'stations_load_congestion': 4, 'e_net_mwh': 0.9}}
    assert all(r['ok'] for r in compare(res, ref))
    res[(2023, '2030')]['stations_load_congestion'] = 6
    assert [r['ok'] for r in compare(res, ref)] == [False, True]


def test_heute_is_not_checked_against_legacy_reference():
    assert not any(k[1] == 'heute' for k in REFERENCE['load'])
    assert not any(r['key'][1] == 'heute' for r in compare(ref_results(1.0)))


def test_trend_check():
    assert trend_ok(ref_results(1.0))
    bad = ref_results(1.0)
    bad[(2012, '2040')]['e_net_mwh'] = 1.0  # Kältewelle 2040 kleiner als 2030
    assert not trend_ok(bad)
