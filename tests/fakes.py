"""Synthetisches Mini-Verzeichnis im Format von gridsim.prepare (3 Stationen, 10 Knoten)."""
import json

import numpy as np

HOURS = 8760
STATION_IDS = ['way/1', 'node/2', 'demo:steyr:station-003']


def winter_summer(offset=0.0):
    """−5 °C im Jänner bis +20 °C im Juli, Tagesgang ± 4 K."""
    h = np.arange(HOURS)
    return 7.5 - 12.5 * np.cos(2 * np.pi * h / HOURS) + 4 * np.sin(2 * np.pi * (h % 24 - 9) / 24) + offset


def write_fake_prepared(root, year=2023, kva=(160, 250, 125)):
    d = root / str(year)
    d.mkdir(parents=True)
    rng = np.random.default_rng(0)
    station = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2], dtype=np.int32)
    hh = np.array([1, 1, 5, 1, 1, 5, 5, 1, 0, 0], dtype=np.int16)  # Station 2: nur PV-Hallen
    kwp_bins = np.zeros((10, 4), dtype=np.float32)
    kwp_bins[[0, 1, 4, 8, 9], 0] = [8, 10, 6, 60, 40]
    kwh = np.where(np.isin(np.arange(10), [0, 4]), 8.0, 0.0).astype(np.float32)
    arrays = {
        'nodes_station': station, 'nodes_hh': hh, 'nodes_kwp_bins': kwp_bins, 'nodes_kwh': kwh,
        'nodes_fw': np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0], dtype=bool),
        'nodes_cell': np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1], dtype=np.int16),
        'nodes_heat_kwh': np.where(hh > 0, np.where(hh == 1, 18000.0, 7000.0 * hh), np.nan).astype(np.float32),
        'nodes_dhw': np.where(hh > 0, 0.15, np.nan).astype(np.float32),
    }
    h = np.arange(HOURS)
    sun = np.clip(np.sin(np.pi * ((h % 24) - 6) / 12), 0, None) * (0.6 + 0.4 * np.sin(np.pi * (h / HOURS)))
    arrays['pv_bins'] = np.repeat(sun[:, None], 4, axis=1).astype(np.float32) * 0.8
    h0 = 1 + 0.5 * np.sin(2 * np.pi * ((h % 24) - 13) / 24) + 0.3 * rng.random(HOURS)
    arrays['h0'] = (h0 / h0.sum()).astype(np.float32)
    arrays['h0_q'] = (np.repeat(arrays['h0'], 4) / 4).astype(np.float32)
    arrays['temp_cells'] = np.column_stack([winter_summer(), winter_summer(-2)]).astype(np.float32)
    for name, a in arrays.items():
        np.save(d / f'{name}.npy', a)
    stations = [{'id': sid, 'idx': i, 'kva': kva[i], 'lon': 14.4 + i / 100, 'lat': 48.04, 'uw': 'Steyr',
                 'synthetic': int(sid.startswith('demo:')), 'n_hh': int(hh[station == i].sum()),
                 'n_buildings': int((hh[station == i] > 0).sum()), 'kwp': float(kwp_bins[station == i].sum())}
                for i, sid in enumerate(STATION_IDS)]
    (d / 'stations.json').write_text(json.dumps(stations))
    (d / 'manifest.json').write_text(json.dumps({'year': year, 'inputs': {}, 'legacy_frozen_at': 'fake'}))
    return root


def big_prepared(n_homes=2000, n_stations=20, year=2023, seed=1):
    """Prepared im Speicher mit vielen Wohnknoten (für Anteils- und Laufzeittests)."""
    from gridsim.data import Prepared
    rng = np.random.default_rng(seed)
    hh = np.where(rng.random(n_homes) < 0.8, 1, 5).astype(np.int16)
    station = (np.arange(n_homes) % n_stations).astype(np.int32)
    kwp_bins = np.zeros((n_homes, 4), dtype=np.float32)
    kwp_bins[:, 0] = np.where(rng.random(n_homes) < 0.3, 8.0, 0.0)
    temp = np.column_stack([winter_summer(), winter_summer(-2)]).astype(np.float32)
    h0 = np.full(HOURS, 1 / HOURS, dtype=np.float32)
    stations = [{'id': f'way/{i}', 'idx': i, 'kva': 400, 'lon': 14.4, 'lat': 48.0, 'uw': 'Steyr', 'synthetic': 0,
                 'n_hh': int(hh[station == i].sum()), 'n_buildings': int((station == i).sum()), 'kwp': 0.0}
                for i in range(n_stations)]
    return Prepared(year=year, root=None, nodes_station=station, nodes_hh=hh, nodes_kwp_bins=kwp_bins,
                    nodes_kwh=np.where(kwp_bins[:, 0] > 0, 8.0, 0.0).astype(np.float32),
                    nodes_fw=(hh > 1) & (rng.random(n_homes) < 0.3), nodes_cell=(np.arange(n_homes) % 2).astype(np.int16),
                    nodes_heat_kwh=np.where(hh == 1, 18000.0, 7000.0 * hh).astype(np.float32),
                    nodes_dhw=np.full(n_homes, np.nan, dtype=np.float32),
                    pv_bins=np.zeros((HOURS, 4), dtype=np.float32), h0=h0, h0_q=np.repeat(h0, 4) / 4,
                    temp_cells=temp, stations=stations)
