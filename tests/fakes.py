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


ROADS_CENTER = (14.42, 48.04)      # Kreuzung der beiden Fake-Straßen (lon, lat)
ROADS_HALF = (0.03, 0.02)          # halbe Armlänge in Grad: etwa 2,2 km je Richtung


def fake_roads(path):
    """Kleines Overpass-JSON: Kreuz aus zwei geraden Straßen (West–Ost, Süd–Nord) um ROADS_CENTER."""
    lon, lat = ROADS_CENTER
    dlon, dlat = ROADS_HALF
    nodes = {1: (lon, lat), 2: (lon - dlon, lat), 3: (lon + dlon, lat), 4: (lon, lat - dlat), 5: (lon, lat + dlat)}
    elements = [{'type': 'node', 'id': i, 'lon': x, 'lat': y} for i, (x, y) in nodes.items()]
    elements += [{'type': 'way', 'id': 10, 'nodes': [2, 1, 3], 'tags': {'highway': 'residential'}},
                 {'type': 'way', 'id': 11, 'nodes': [4, 1, 5], 'tags': {'highway': 'residential'}}]
    path.write_text(json.dumps({'elements': elements}), encoding='utf-8')
    return path


# Fake-Knoten wie in write_fake_prepared (Station 0, 0, 0, 0, 1, 1, 1, 1, 2, 2), entlang der Ost-West-Straße
FEEDER_NODE_STATION = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2]
FEEDER_NODE_OFFSET_M = [(40, 15), (80, -15), (120, 15), (160, -15), (-60, 12), (-110, -12), (-160, 12), (-210, -12),
                        (30, 300), (60, 330)]
FEEDER_LEGACY_STATION = [0, 2, 3]   # Legacy-Station 1 hat keine Knoten und fällt beim Verdichten weg


def fake_build_members_factory(offsets=FEEDER_NODE_OFFSET_M, extra=()):
    """``build_members``-Ersatz mit Stationen und Knoten um ROADS_CENTER (EPSG:31287).

    ``extra``: weitere Knoten (Versatz, hh, kWp, Station 0–2) hinter den zehn Standardknoten.
    """
    from gridsim.feeders.roads import TO_LAMBERT

    def fake_build_members(inp):
        from collections import defaultdict
        c = np.array(TO_LAMBERT.transform(*ROADS_CENTER))
        st_xy = np.array([c, c + [0, 2000], c + [-20, 0], c + [0, 250]])
        stations = [{'osm_id': f'way/{i}', 'lon': 0.0, 'lat': 0.0} for i in range(4)]
        hh = [1, 1, 5, 1, 1, 5, 5, 1, 0, 0]
        kwp = [8, 10, 0, 0, 6, 0, 0, 0, 60, 40]
        nodes = [{'xy': tuple(c + off), 'hh': h, 'kwp': float(k), 'pv': defaultdict(float),
                  'station': FEEDER_LEGACY_STATION[s]} for off, h, k, s in zip(offsets, hh, kwp, FEEDER_NODE_STATION)]
        nodes += [{'xy': tuple(c + off), 'hh': h, 'kwp': float(k), 'pv': defaultdict(float),
                   'station': FEEDER_LEGACY_STATION[s]} for off, h, k, s in extra]
        return stations, st_xy, ['Steyr'] * 4, nodes

    return fake_build_members


def align_station_positions(prepared, build_members):
    """stations.json-Koordinaten aller Jahre auf die (verdichteten) Stationen von ``build_members`` setzen."""
    from pyproj import Transformer
    back = Transformer.from_crs(31287, 4326, always_xy=True)
    _, st_xy, _, _ = build_members(None)
    lon, lat = back.transform(*np.asarray(st_xy)[FEEDER_LEGACY_STATION].T)
    for d in sorted(p for p in prepared.iterdir() if p.name.isdigit()):
        rows = json.loads((d / 'stations.json').read_text())
        for r, x, y in zip(rows, lon, lat):
            r['lon'], r['lat'] = float(x), float(y)
        (d / 'stations.json').write_text(json.dumps(rows))
