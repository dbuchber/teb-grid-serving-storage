#!/usr/bin/env python3
"""PV je Umspannwerk und je Ortsnetzstation im Raum Steyr (Analyse, keine Lastflussrechnung).

Eingänge (ein Verzeichnis, Dateinamen fest):
  pv_steyr_bbox.geojson  BOKU-PV-Polygone, Steyr-Zuschnitt (WGS84; PV_type, Wp)
  osm_power.json         Overpass: power=substation|transformer (out tags center)
  powerstations.json     ebUtilities-Netzanschlusskapazitäten je UW (Stand 1.7.2026)
  gebaeude_bbox.csv      BEV-Adressregister GEBAEUDE, Bbox-Filter (EPSG:31255)

Zuordnung: jede PV-Anlage und jedes Gebäude zur nächstgelegenen Station (Voronoi,
euklidisch in EPSG:31287). Das ist eine Näherung: die echten Abgänge folgen den
Leitungen, nicht der Luftlinie. Wohngebäude über MAX_DIST_M von jeder OSM-Station
(OSM ist lückenhaft) bekommen synthetische Stationen per k-means (``synthetic=1``).
Anlagen über MV_KWP gelten als eigener Mittelspannungsanschluss und zählen nicht
zur Ortsnetzstation, nur zum Umspannwerk.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from pyproj import Transformer
from scipy.cluster.vq import kmeans2
from scipy.spatial import cKDTree
from shapely.geometry import shape

MAX_DIST_M = 600
DEDUP_TRANSFORMER_M = 40
# Analyse-Box (PV und Gebäude); UW-Kandidaten auch knapp außerhalb, damit Randanlagen
# nicht dem falschen UW zufallen.
BBOX = (14.28, 47.97, 14.56, 48.12)
UW_BBOX = (14.05, 47.85, 14.80, 48.25)
LOCAL_SUBSTATION = {None, 'minor_distribution'}
HIGH_VOLTAGE_V = 60000
SIMULTANEITY_PV = 0.75  # Annahme für einen klaren Sommertag (siehe Positionspapier)
SMALL_KWP = 30          # Haushaltsanlagen
MV_KWP = 250            # darüber: vermutlich eigener MS-Anschluss
HOMES_PER_SYNTHETIC = 60
SEED = 20261024

TO_LAMBERT = Transformer.from_crs(4326, 31287, always_xy=True)
GK31_TO_LAMBERT = Transformer.from_crs(31255, 31287, always_xy=True)


def max_voltage(tags):
    values = []
    for part in (tags.get('voltage') or '').split(';'):
        try:
            values.append(int(float(part)))
        except ValueError:
            pass
    return max(values) if values else None


def local_stations(elements):
    """Ortsnetzstationen: Mittelspannung oder ohne Spannungsangabe, ohne Sonderanlagen."""
    subs, trafos = [], []
    for e in elements:
        tags = e.get('tags', {})
        lon, lat = (e['lon'], e['lat']) if e['type'] == 'node' else (e['center']['lon'], e['center']['lat'])
        v = max_voltage(tags)
        if v is not None and v >= HIGH_VOLTAGE_V:
            continue
        row = {'osm_id': f"{e['type']}/{e['id']}", 'lon': lon, 'lat': lat, 'name': tags.get('name') or tags.get('ref') or '',
               'operator': tags.get('operator', ''), 'tag': f"{tags.get('power')}:{tags.get('substation') or '-'}:{tags.get('voltage') or '-'}"}
        if tags.get('power') == 'substation' and tags.get('substation') in LOCAL_SUBSTATION:
            subs.append(row)
        elif tags.get('power') == 'transformer':
            trafos.append(row)
    xy = np.array([TO_LAMBERT.transform(s['lon'], s['lat']) for s in subs])
    tree = cKDTree(xy)
    for t in trafos:  # Masttrafos ergänzen, Trafos innerhalb einer Station nicht doppelt zählen
        d, _ = tree.query(TO_LAMBERT.transform(t['lon'], t['lat']))
        if d > DEDUP_TRANSFORMER_M:
            subs.append(t)
    return subs


def substations(powerstations):
    out = []
    for p in powerstations['powerstations']:
        if UW_BBOX[0] <= p['longitude'] <= UW_BBOX[2] and UW_BBOX[1] <= p['latitude'] <= UW_BBOX[3]:
            out.append({'name': p['substationName'], 'operator': p['networkOperator'], 'lon': p['longitude'],
                        'lat': p['latitude'], 'booked': to_float(p['bookedCapacity']),
                        'available': to_float(p['availableCapacity'])})
    return out


def to_float(value):
    return float(str(value).replace(',', '.')) if value not in (None, '') else None


def pv_points(geojson):
    out = []
    for f in geojson['features']:
        geom = shape(f['geometry'])
        c = geom.representative_point()
        p = f['properties']
        out.append({'xy': TO_LAMBERT.transform(c.x, c.y), 'type': p.get('PV_type'), 'kwp': (p.get('Wp') or 0) / 1000,
                    'aspect': p.get('aspect_deg'), 'slope': p.get('slope_deg')})
    return out


def buildings(path):
    out = []
    with open(path, encoding='utf-8-sig', newline='') as fh:
        for r in csv.DictReader(fh, delimiter=';'):
            out.append({'xy': GK31_TO_LAMBERT.transform(float(r['RW']), float(r['HW'])), 'kind': r['EIGENSCHAFT']})
    return out


def add_synthetic(stations, st_xy, geb):
    """Synthetische Stationen für Wohngebäude ohne OSM-Station in Reichweite."""
    homes = np.array([b['xy'] for b in geb if b['kind'] in ('01', '02')])
    d, _ = cKDTree(st_xy).query(homes)
    far = homes[d > MAX_DIST_M]
    if not len(far):
        return stations, st_xy
    k = max(1, math.ceil(len(far) / HOMES_PER_SYNTHETIC))
    centers, _ = kmeans2(far, k, seed=SEED, minit='++')
    back = Transformer.from_crs(31287, 4326, always_xy=True)
    for n, (x, y) in enumerate(centers):
        lon, lat = back.transform(x, y)
        stations.append({'osm_id': f'demo:steyr:station-{n:03d}', 'lon': lon, 'lat': lat, 'name': '',
                         'operator': '', 'tag': 'synthetic', 'synthetic': 1})
    return stations, np.vstack([st_xy, centers])


def assign(points, stations_xy):
    tree = cKDTree(stations_xy)
    d, i = tree.query(np.array([p['xy'] for p in points]))
    return d, i


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    stations = local_stations(json.loads((args.input / 'osm_power.json').read_text())['elements'])
    uws = substations(json.loads((args.input / 'powerstations.json').read_text()))
    pv = pv_points(json.loads((args.input / 'pv_steyr_bbox.geojson').read_text()))
    geb = buildings(args.input / 'gebaeude_bbox.csv')

    st_xy = np.array([TO_LAMBERT.transform(s['lon'], s['lat']) for s in stations])
    n_osm = len(stations)
    stations, st_xy = add_synthetic(stations, st_xy, geb)
    uw_xy = np.array([TO_LAMBERT.transform(u['lon'], u['lat']) for u in uws])

    st = defaultdict(lambda: defaultdict(float))
    uw = defaultdict(lambda: defaultdict(float))
    gap = defaultdict(float)
    d_st, i_st = assign(pv, st_xy)
    _, i_uw = assign(pv, uw_xy)
    for p, d, si, ui in zip(pv, d_st, i_st, i_uw):
        key = 'roof' if p['type'] == 'Rooftop PV' else 'ground'
        uw[ui][f'kwp_{key}'] += p['kwp']
        uw[ui][f'n_{key}'] += 1
        if p['kwp'] > MV_KWP:
            uw[ui]['kwp_mv'] += p['kwp']
            continue
        if p['kwp'] <= SMALL_KWP:
            st[si]['kwp_small'] += p['kwp']
        if d > MAX_DIST_M:
            gap['kwp'] += p['kwp']
            gap['n'] += 1
            continue
        st[si][f'kwp_{key}'] += p['kwp']
        st[si][f'n_{key}'] += 1
    d_b, i_b = assign(geb, st_xy)
    _, i_bu = assign(geb, uw_xy)
    for b, d, si, ui in zip(geb, d_b, i_b, i_bu):
        kind = {'01': 'efh', '02': 'mfh'}.get(b['kind'], 'other')
        uw[ui][f'geb_{kind}'] += 1
        if d <= MAX_DIST_M:
            st[si][f'geb_{kind}'] += 1
            st[si]['dist_sum'] += d
        else:
            gap[f'geb_{kind}'] += 1

    st_rows = []
    for si, s in enumerate(stations):
        a = st[si]
        kwp = a['kwp_roof'] + a['kwp_ground']
        homes = a['geb_efh'] + a['geb_mfh']
        if kwp == 0 and homes == 0:
            continue
        st_rows.append({
            'osm_id': s['osm_id'], 'synthetic': s.get('synthetic', 0), 'name': s['name'], 'tag': s['tag'], 'lon': round(s['lon'], 6), 'lat': round(s['lat'], 6),
            'uw': uws[int(cKDTree(uw_xy).query(st_xy[si])[1])]['name'],
            'n_pv_dach': int(a['n_roof']), 'kwp_dach': round(a['kwp_roof'], 1),
            'n_pv_frei': int(a['n_ground']), 'kwp_frei': round(a['kwp_ground'], 1), 'kwp_ns': round(kwp, 1),
            'kwp_bis_30': round(a['kwp_small'], 1),
            'geb_efh': int(a['geb_efh']), 'geb_mfh': int(a['geb_mfh']), 'geb_sonst': int(a['geb_other']),
            'kwp_je_wohngebaeude': round(kwp / homes, 1) if homes else None,
            'rueckspeisung_kw_schaetzung': round(kwp * SIMULTANEITY_PV, 0),
        })
    st_rows.sort(key=lambda r: r['kwp_ns'], reverse=True)

    uw_rows = []
    for ui, u in enumerate(uws):
        a = uw[ui]
        kwp = a['kwp_roof'] + a['kwp_ground']
        if kwp == 0 and not a['geb_efh']:
            continue
        uw_rows.append({'uw': u['name'], 'betreiber': u['operator'], 'gebucht_ebutilities': u['booked'],
                        'verfuegbar_ebutilities': u['available'], 'pv_mwp_boku_in_box': round(kwp / 1000, 2),
                        'davon_ms_anschluss_mwp': round(a['kwp_mv'] / 1000, 2),
                        'n_pv': int(a['n_roof'] + a['n_ground']), 'geb_efh': int(a['geb_efh']), 'geb_mfh': int(a['geb_mfh'])})
    uw_rows.sort(key=lambda r: r['pv_mwp_boku_in_box'], reverse=True)

    for name, rows in (('pv_je_ortsnetzstation.csv', st_rows), ('pv_je_umspannwerk.csv', uw_rows)):
        with open(args.output / name, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';')
            w.writeheader()
            w.writerows(rows)

    kwps = np.array([r['kwp_ns'] for r in st_rows])
    summary = {
        'stationen_osm_lokal': n_osm, 'stationen_synthetisch': len(stations) - n_osm, 'stationen_mit_zuordnung': len(st_rows), 'uw_kandidaten': len(uws),
        'pv_anlagen': len(pv), 'pv_mwp': round(sum(p['kwp'] for p in pv) / 1000, 2), 'gebaeude': len(geb),
        'pv_ms_anschluss_mwp': round(sum(p['kwp'] for p in pv if p['kwp'] > MV_KWP) / 1000, 2),
        'luecke_pv_n': int(gap['n']), 'luecke_pv_mwp': round(gap['kwp'] / 1000, 2),
        'luecke_geb_efh': int(gap['geb_efh']), 'luecke_geb_mfh': int(gap['geb_mfh']),
        'kwp_je_station_median': float(np.median(kwps)), 'kwp_je_station_p90': float(np.percentile(kwps, 90)),
        'stationen_ueber_250kwp': int((kwps > 250).sum()), 'stationen_ueber_400kwp': int((kwps > 400).sum()),
        'annahmen': {'max_dist_m': MAX_DIST_M, 'gleichzeitigkeit_pv': SIMULTANEITY_PV, 'ms_ab_kwp': MV_KWP,
                     'wohngebaeude_je_synthetischer_station': HOMES_PER_SYNTHETIC, 'seed': SEED,
                     'zuordnung': 'nächste Station, euklidisch EPSG:31287'},
    }
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
