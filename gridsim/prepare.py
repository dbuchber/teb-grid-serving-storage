"""Vorbereitung je Wetterjahr: Knoten, Stationen und Profile aus den eingefrorenen Skripten als Arrays.

Referenzkonfiguration wie die Läufe von Session 18 (``steyr_storage_need.py --heat lod1
--district-heating``, ``large_share`` 0,0): Fernwärme-MFH markiert, Wärmebedarf aus LoD1, Temperatur
je Station aus INCA. Ausgabe nach ``out_dir/<year>/``, Format siehe data.py.
"""
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

from gridsim import legacy

INPUTS = ('osm_power.json', 'powerstations.json', 'pv_steyr_bbox.geojson', 'gebaeude_bbox.csv', 'lod1_steyr.csv',
          'osm_places_steyr.json', 'apcs/synthload2026.csv', 'inca/stationen.csv')


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def read_h0_quarter(path, year):
    """APCS H0 je Viertelstunde (Anteil am Jahr), Wochentage wie ``sim.read_h0`` auf ``year`` gelegt."""
    q = []
    with open(path, encoding='latin-1') as fh:
        next(fh)
        for line in fh:
            typ, _, val = line.rstrip('\n').split(';')
            if typ == '1':
                q.append(float(val.replace(',', '.')))
    q = np.array(q)
    assert len(q) == 35040, len(q)
    shift = (date(year, 1, 1).weekday() - date(2026, 1, 1).weekday()) % 7 * 24 * 4
    return np.roll(q / q.sum(), -shift)


def prepare(input_dir, year, out_dir):
    inp, out = Path(input_dir), Path(out_dir) / str(year)
    sim = legacy.load('steyr_sim_variant_a')
    need = legacy.load('steyr_storage_need')
    dh = legacy.load('steyr_district_heating')
    hd = legacy.load('steyr_heat_demand')
    wpev = legacy.load('steyr_wp_ev')
    sim.STORAGE_SHARE_LARGE = 0.0

    stations, _, st_uw, nodes = sim.build_members(inp)
    dh.mark(nodes, dh.places(inp / 'osm_places_steyr.json'))
    temp, cell_of = need.read_inca(inp, year, stations, nodes)
    heat_kwh, dhw, _ = hd.node_heat(nodes, inp / 'lod1_steyr.csv', hd.heating_degree_days(temp.mean(axis=1)), wpev.SEED)

    used = sorted({n['station'] for n in nodes})  # nur Stationen mit Knoten (257)
    compact = {si: i for i, si in enumerate(used)}
    st_of = np.array([compact[n['station']] for n in nodes], dtype=np.int32)
    out.mkdir(parents=True, exist_ok=True)
    arrays = {
        'nodes_station': st_of,
        'nodes_hh': np.array([n['hh'] for n in nodes], dtype=np.int16),
        'nodes_kwp_bins': np.array([[n['pv'].get(b, 0.0) for b in sim.PVGIS_BINS] for n in nodes], dtype=np.float32),
        'nodes_kwh': np.array([n['kwh'] for n in nodes], dtype=np.float32),
        'nodes_fw': np.array([bool(n.get('fw')) for n in nodes]),
        'nodes_cell': np.asarray(cell_of, dtype=np.int16),
        'nodes_heat_kwh': np.asarray(heat_kwh, dtype=np.float32),
        'nodes_dhw': np.asarray(dhw, dtype=np.float32),
        'pv_bins': np.column_stack([sim.read_pvgis(inp / f'pvgis_{b}_{year}.csv') for b in sim.PVGIS_BINS]).astype(np.float32),
        'h0': sim.read_h0(inp / 'apcs' / 'synthload2026.csv', year).astype(np.float32),
        'h0_q': read_h0_quarter(inp / 'apcs' / 'synthload2026.csv', year).astype(np.float32),
        'temp_cells': np.asarray(temp, dtype=np.float32),
    }
    for name, a in arrays.items():
        np.save(out / f'{name}.npy', a)

    rows = []
    for si in used:
        members = [n for n in nodes if n['station'] == si]
        n_b, n_hh, kwp = sum(m['hh'] > 0 for m in members), sum(m['hh'] for m in members), sum(m['kwp'] for m in members)
        s = stations[si]
        rows.append({'id': s['osm_id'], 'idx': compact[si], 'kva': sim.trafo_kva(n_b, n_hh, kwp), 'lon': s['lon'],
                     'lat': s['lat'], 'uw': st_uw[si], 'synthetic': int(s.get('synthetic', 0)), 'n_hh': int(n_hh),
                     'n_buildings': int(n_b), 'kwp': round(float(kwp), 1)})
    (out / 'stations.json').write_text(json.dumps(rows, ensure_ascii=False))
    files = list(INPUTS) + [f'pvgis_{b}_{year}.csv' for b in sim.PVGIS_BINS] + [f'inca/t2m_{year}.csv']
    manifest = {'year': year, 'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'legacy_frozen_at': legacy.FROZEN_AT,
                'legacy_sha256sums': hashlib.sha256((legacy.DIR / 'SHA256SUMS').read_bytes()).hexdigest(),
                'config': {'heat': 'lod1', 'district_heating': True, 'large_share': 0.0},
                'inputs': {f: _sha256(inp / f) for f in files}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    return Path(out_dir)
