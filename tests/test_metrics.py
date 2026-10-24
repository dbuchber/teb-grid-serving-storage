import numpy as np

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
