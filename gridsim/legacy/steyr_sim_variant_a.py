#!/usr/bin/env python3
"""Variante A (ex ante): Speicher im Eigenverbrauch gegen netzdienliche Steuerung, alle
Ortsnetzstationen im Raum Steyr, Wetterjahr 2023 (PVGIS), Haushaltslast APCS H0.

Strategien je Heimspeicher (stündlich, gleiche Eingänge):
  base      Eigenverbrauch: laden bei Überschuss, entladen bei Bezug (heutiges Verhalten)
  fixcap    ohne Prognose: bis 15 Uhr nur Überschuss über FIXCAP_SHARE x kWp laden
  forecast  Tagesprognose (perfekt, obere Schranke): Ladeschwelle je Tag so, dass der
            Speicher genau mit der Spitze voll wird
  room      wie forecast, zusätzlich nachts (0-6 Uhr) bis auf BACKUP_SOC ins Netz entladen,
            damit am Tag Platz ist (setzt erlaubte Speichereinspeisung voraus, UC3)

Netz je Station: synthetisch aus realen Gebäudelagen (3-11 Sektoren um die Station, je
Sektor ein Minimum Spanning Tree), in der Stadt Kabel NAYY 4x150, am Land Bündelleiter
Al 95 mm²; Anlagen über 30 kWp an eigenem Abgang ab der Sammelschiene. Trafo 30/0,4 kV
nach Wohngebäuden (ca. 3 kVA je Gebäude) und angeschlossener PV (70-%-Regel) bemessen.
Belege: docs/research/2026-10-24-netzmodell-belege.md (K1-K6).
Trafo-KPIs aus der Leistungsbilanz aller 8 760 Stunden, Spannung per pandapower in den
LF_HOURS stärksten Rückspeisestunden des Basisfalls. Alle Zahlen sind Modellwerte.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial import cKDTree, distance_matrix

import steyr_pv_per_station as base

SEED = 20261024
HH_PER_MFH = 5             # Annahme: Haushalte je Mehrparteienhaus
KWH_PER_HH = 3000          # Annahme: Jahresverbrauch je Haushalt
STORAGE_SHARE = 0.5        # Annahme: Anteil der Haushalts-PV (<= 30 kWp) mit Speicher
STORAGE_KWH_PER_KWP = 1.0  # Speichergröße 1 kWh/kWp, begrenzt auf 5-15 kWh
STORAGE_SHARE_LARGE = 0.0  # Annahme: Anteil Gewerbe/Landwirtschaft (30-250 kWp) mit Speicher
STORAGE_KWH_PER_KWP_LARGE = 0.5
C_RATE = 0.5
ETA = 0.95                 # Wirkungsgrad je Richtung
FIXCAP_SHARE = 0.5
FIXCAP_UNTIL_H = 15
KVA_PER_BUILDING = 3.0     # Beleg A1: real ca. 2,8-4,6 kVA je Gebäude (DG DemoNet)
KVA_PER_HH = 2.0           # Beleg A6: real ca. 2,0-3,6 kVA je Kunde (DG DemoNet), MFH-Gebiete
KVA_PER_KWP = 0.7          # Annahme: Trafo deckt 70 % der angeschlossenen PV
BACKUP_SOC = 0.2
NIGHT_HOURS = 6
TRAFO_SIZES = (125, 160, 250, 400, 630, 800, 1000)
LOADING_LIMIT = 0.8
PV_ATTACH_M = 40
LINE_DETOUR = 1.2
BUILDINGS_PER_FEEDER = 18   # Beleg K2: 3-11 Abgänge, Eberstalzell 165 Gebäude / 11 Abgänge
MIN_FEEDERS, MAX_FEEDERS = 3, 11
RURAL_MEDIAN_M = 200         # Annahme: Station gilt als ländlich ab 200 m mittlerer Gebäudedistanz
# Annahme: typische Herstellerwerte Bündelleiter Al 4x95 mm² (Beleg B5 nennt nur die Kennung „95 B“)
RURAL_LINE = {'r_ohm_per_km': 0.320, 'x_ohm_per_km': 0.083, 'c_nf_per_km': 0.0, 'max_i_ka': 0.245, 'type': 'ol'}
DIRECT_KWP = 30              # Annahme K1: ab hier eigener Abgang ab der Sammelschiene
LF_HOURS = 24
STRATEGIES = ('base', 'fixcap', 'forecast', 'room')
CLASSES = ((0, 50, 'bis 50 kWp'), (50, 250, '50-250 kWp'), (250, 1e9, 'über 250 kWp'))
PVGIS_BINS = ('S35', 'E30', 'W30', 'F10')


def pv_bin(aspect, slope):
    if aspect is None or slope is None or slope < 15:
        return 'F10'
    if 135 <= aspect < 225:
        return 'S35'
    if 45 <= aspect < 135:
        return 'E30'
    if 225 <= aspect < 315:
        return 'W30'
    return 'F10'


def drop_leap_day(vals):
    """8 784 Stundenwerte eines Schaltjahres auf 8 760 kürzen (29.2. entfällt)."""
    vals = np.asarray(vals)
    if len(vals) == 8784:
        vals = np.concatenate([vals[:59 * 24], vals[60 * 24:]])
    assert len(vals) == 8760, len(vals)
    return vals


def read_pvgis(path):
    """Stündliche Leistung je kWp (kW), 8 760 Werte (Standard: 2023)."""
    vals = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line[:4].isdigit() and ':' in line[:14]:
                vals.append(float(line.split(',')[1]) / 1000)
    return drop_leap_day(vals)


def read_h0(path, year=2023):
    """APCS H0 (kWh je Viertelstunde, Summe 1 000 kWh/a) für 2026 auf ``year`` gelegt.

    Wochentage werden ausgerichtet, z. B. 1.1.2023 ist ein Sonntag, der erste Sonntag 2026 der 4.1.
    Feiertage werden nicht verschoben.
    """
    q = []
    with open(path, encoding='latin-1') as fh:
        next(fh)
        for line in fh:
            typ, _, val = line.rstrip('\n').split(';')
            if typ == '1':
                q.append(float(val.replace(',', '.')))
    q = np.array(q)
    assert len(q) == 35040, len(q)
    hourly = q.reshape(-1, 4).sum(axis=1)  # kWh je Stunde = mittlere kW
    hourly = hourly / hourly.sum()          # Anteil am Jahresverbrauch
    shift = (date(year, 1, 1).weekday() - date(2026, 1, 1).weekday()) % 7 * 24
    return np.roll(hourly, -shift)


def build_members(inp):
    """Stationen, Haushaltsknoten und PV wie in der Stationsanalyse, plus Speicherzuteilung."""
    stations = base.local_stations(json.loads((inp / 'osm_power.json').read_text())['elements'])
    uws = base.substations(json.loads((inp / 'powerstations.json').read_text()))
    pv = [p for p in base.pv_points(json.loads((inp / 'pv_steyr_bbox.geojson').read_text())) if p['kwp'] <= base.MV_KWP]
    geb = base.buildings(inp / 'gebaeude_bbox.csv')
    st_xy = np.array([base.TO_LAMBERT.transform(s['lon'], s['lat']) for s in stations])
    stations, st_xy = base.add_synthetic(stations, st_xy, geb)
    uw_xy = np.array([base.TO_LAMBERT.transform(u['lon'], u['lat']) for u in uws])

    homes = [b for b in geb if b['kind'] in ('01', '02')]
    nodes = [{'xy': b['xy'], 'hh': 1 if b['kind'] == '01' else HH_PER_MFH, 'pv': defaultdict(float), 'kwp': 0.0}
             for b in homes]
    tree = cKDTree(np.array([n['xy'] for n in nodes]))
    for p in pv:  # PV an das nächste Wohngebäude hängen, sonst eigener Knoten (Stall, Halle)
        d, i = tree.query(p['xy'])
        target = nodes[i] if d <= PV_ATTACH_M else None
        if target is None:
            target = {'xy': p['xy'], 'hh': 0, 'pv': defaultdict(float), 'kwp': 0.0}
            nodes.append(target)
        target['pv'][pv_bin(p['aspect'], p['slope'])] += p['kwp']
        target['kwp'] += p['kwp']
    d, idx = cKDTree(st_xy).query(np.array([n['xy'] for n in nodes]))
    rng = np.random.default_rng(SEED)
    rng_large = np.random.default_rng(SEED + 1)  # eigener Strom: Haushaltszuteilung bleibt gleich
    for n, dist, si in zip(nodes, d, idx):
        n['station'] = int(si) if dist <= base.MAX_DIST_M else -1
        small = 0 < n['kwp'] <= base.SMALL_KWP and n['hh'] > 0
        n['kwh'] = float(np.clip(n['kwp'] * STORAGE_KWH_PER_KWP, 5, 15)) if small and rng.random() < STORAGE_SHARE else 0.0
        if base.SMALL_KWP < n['kwp'] <= base.MV_KWP and rng_large.random() < STORAGE_SHARE_LARGE:
            n['kwh'] = n['kwp'] * STORAGE_KWH_PER_KWP_LARGE
    nodes = [n for n in nodes if n['station'] >= 0]
    st_uw = cKDTree(uw_xy).query(st_xy)[1]
    return stations, st_xy, [uws[i]['name'] for i in st_uw], nodes


def simulate(pv_kw, load_kw, cap, strategy):
    """Netto-Leistung je Knoten und Stunde (positiv = Bezug) und Speicherenergien."""
    n_h, n = pv_kw.shape
    pmax = cap * C_RATE
    soc = np.zeros(n)
    net = np.empty((n_h, n), dtype=np.float32)
    kwp = np.maximum(pv_kw.max(axis=0), 1e-9)
    surplus_all = pv_kw - load_kw
    for day in range(n_h // 24):
        sl = slice(day * 24, day * 24 + 24)
        surplus = surplus_all[sl]
        night_out = np.zeros(n)
        if strategy == 'room':  # vor dem Tag Platz schaffen, gleichmäßig über die Nacht
            night_out = np.maximum(soc - BACKUP_SOC * cap, 0) * ETA / NIGHT_HOURS
            th = forecast_threshold(surplus, (cap - np.minimum(soc, BACKUP_SOC * cap)) / ETA, pmax)
        elif strategy == 'forecast':
            th = forecast_threshold(surplus, (cap - soc) / ETA, pmax)
        for h in range(24):
            s = surplus[h]
            if strategy == 'base' or (strategy != 'base' and h >= FIXCAP_UNTIL_H):
                chargeable = np.maximum(s, 0)
            elif strategy == 'fixcap':
                chargeable = np.maximum(s - FIXCAP_SHARE * kwp, 0)
            else:
                chargeable = np.maximum(s - th, 0)
            charge = np.minimum(np.minimum(chargeable, pmax), (cap - soc) / ETA)
            own = np.maximum(-s, 0)
            if h < NIGHT_HOURS:
                own = np.maximum(own, night_out)
            discharge = np.minimum(np.minimum(own, pmax), soc * ETA)
            soc = soc + charge * ETA - discharge / ETA
            net[day * 24 + h] = -s + charge - discharge
    return net


def forecast_threshold(surplus, room, pmax, iters=30):
    """Schwelle je Knoten: Laden nur über der Schwelle füllt genau den freien Speicher."""
    lo = np.zeros(surplus.shape[1])
    hi = np.maximum(surplus.max(axis=0), 0)
    for _ in range(iters):
        mid = (lo + hi) / 2
        energy = np.minimum(np.maximum(surplus - mid, 0), pmax).sum(axis=0)
        too_little = energy < room
        hi = np.where(too_little, mid, hi)
        lo = np.where(too_little, lo, mid)
    return lo


def trafo_kva(n_buildings, n_hh, kwp):
    need = max(n_buildings * KVA_PER_BUILDING, n_hh * KVA_PER_HH, kwp * KVA_PER_KWP, TRAFO_SIZES[0])
    return next((s for s in TRAFO_SIZES if s >= need), TRAFO_SIZES[-1])


def build_net(st_xy, members, kva, roads=None):
    """Radiales NS-Netz aus realen Knotenlagen: Sektoren um die Station, je Sektor ein MST;
    große Anlagen an eigenem Abgang. Gibt auch Kennwerte des Netzes zurück. Mit ``roads``
    (steyr_lv_roads.RoadGraph) folgen die Stränge dem Straßennetz (build_net_roads).
    ``net['line_coords']`` hält je Leitung die Geometrie (EPSG:31287)."""
    import pandapower as pp
    if roads is not None:
        built = build_net_roads(st_xy, members, kva, roads)
        if built is not None:
            return built

    net = pp.create_empty_network()
    mv = pp.create_bus(net, vn_kv=30)
    lv = pp.create_bus(net, vn_kv=0.4)
    pp.create_ext_grid(net, mv, vm_pu=1.0)
    pp.create_transformer_from_parameters(net, mv, lv, sn_mva=kva / 1000, vn_hv_kv=30, vn_lv_kv=0.4,
                                          vk_percent=4 if kva <= 630 else 6, vkr_percent=1.0,
                                          pfe_kw=0.4, i0_percent=0.3)
    xy = np.array([m['xy'] for m in members]) - st_xy
    dist = np.hypot(xy[:, 0], xy[:, 1])
    rural = float(np.median(dist)) > RURAL_MEDIAN_M
    pp.create_std_type(net, RURAL_LINE, name='Al 95 Buendel', element='line')
    line_type = 'Al 95 Buendel' if rural else 'NAYY 4x150 SE'
    buses = [pp.create_bus(net, vn_kv=0.4) for _ in members]
    direct = np.array([m['kwp'] > DIRECT_KWP for m in members])
    for k, i in enumerate(np.flatnonzero(direct)):  # eigener Abgang: Kabel, ab 100 kWp zweifach parallel
        pp.create_line(net, lv, buses[i], length_km=max(dist[i], 5) * LINE_DETOUR / 1000, name=f'D{k + 1}',
                       std_type='NAYY 4x150 SE', parallel=2 if members[i]['kwp'] > 100 else 1)
    rest = np.flatnonzero(~direct)
    n_feeders = 0
    feeder_len = [dist[i] * LINE_DETOUR for i in np.flatnonzero(direct)]
    if len(rest):
        n_buildings = sum(members[i]['hh'] > 0 for i in rest)
        n_feeders = int(min(len(rest), np.clip(math.ceil(n_buildings / BUILDINGS_PER_FEEDER), MIN_FEEDERS, MAX_FEEDERS)))
        angle = np.arctan2(xy[rest, 1], xy[rest, 0])
        sector = np.empty(len(rest), dtype=int)
        sector[np.argsort(angle)] = np.arange(len(rest)) * n_feeders // len(rest)
        for f in range(n_feeders):
            idx = rest[sector == f]
            pts = np.vstack([[0, 0], xy[idx]])
            mst = minimum_spanning_tree(distance_matrix(pts, pts)).tocoo()
            ids = [lv] + [buses[i] for i in idx]
            for a, b, length in zip(mst.row, mst.col, mst.data):
                pp.create_line(net, ids[a], ids[b], length_km=max(length, 5) * LINE_DETOUR / 1000, std_type=line_type,
                               name=f'A{f + 1}')
            feeder_len.append(float(dist[idx].max()) * LINE_DETOUR)
    net.bus['x'], net.bus['y'] = np.nan, np.nan  # Lage relativ zur Station (für Kartenexport)
    net.bus.loc[lv, ['x', 'y']] = 0.0, 0.0
    net.bus.loc[buses, 'x'], net.bus.loc[buses, 'y'] = xy[:, 0], xy[:, 1]
    loads = [pp.create_load(net, b, p_mw=0) for b in buses]
    sgens = [pp.create_sgen(net, b, p_mw=0) for b in buses]
    absx = net.bus[['x', 'y']].to_numpy() + st_xy
    net['line_coords'] = {li: absx[[ln.from_bus, ln.to_bus]] for li, ln in net.line.iterrows()}
    meta = {'netzart': 'land' if rural else 'stadt', 'abgaenge': n_feeders, 'direktabgaenge': int(direct.sum()),
            'abgang_max_m': round(max(feeder_len), 0) if feeder_len else 0, 'strassennetz': 0, 'ohne_strasse': 0}
    return net, lv, loads, sgens, meta


def _split_feeders(s, segs, building_nodes):
    """Abgang je Knoten des Straßenbaums (Wurzelknoten des Abgangs).

    Jeder Ast ab der Station ist ein Abgang; Abgänge mit mehr als 1,5 x BUILDINGS_PER_FEEDER
    Gebäuden werden an ihren Abzweigen geteilt (weitere Kabel im selben Graben), bis höchstens
    MAX_FEEDERS Abgänge bestehen.
    """
    up = {k: p for p, k, _, _ in segs}
    kids = defaultdict(list)
    for k, p in up.items():
        kids[p].append(k)
    own = defaultdict(int)
    for n in building_nodes:
        own[n] += 1
    roots = set(kids[s])

    def root_of(n):
        while n not in roots and up.get(n, s) != s:
            n = up[n]
        return n

    def load(r):  # Gebäude im Abgang r (ohne Teilbäume, die selbst Abgänge sind)
        total, stack = own[r], list(kids[r])
        while stack:
            n = stack.pop()
            if n in roots:
                continue
            total += own[n]
            stack.extend(kids[n])
        return total

    limit = 1.5 * BUILDINGS_PER_FEEDER
    while len(roots) < MAX_FEEDERS:
        r = max(roots, key=load, default=None)
        new = [c for c in kids.get(r, []) if c not in roots] if r is not None else []
        if r is None or load(r) <= limit or not new or len(roots) + len(new) > MAX_FEEDERS:
            break
        roots.update(new)
    return {n: root_of(n) for n in set(up) | {s}}


def build_net_roads(st_xy, members, kva, roads):
    """NS-Netz entlang der Straßen (steyr_lv_roads); None, wenn die Station an keiner Straße liegt."""
    import pandapower as pp
    import steyr_lv_roads as lr

    pts = np.array([m['xy'] for m in members])
    tr = roads.station_tree(st_xy, pts)
    if tr is None:
        return None
    net = pp.create_empty_network()
    mv = pp.create_bus(net, vn_kv=30)
    lv = pp.create_bus(net, vn_kv=0.4)
    pp.create_ext_grid(net, mv, vm_pu=1.0)
    pp.create_transformer_from_parameters(net, mv, lv, sn_mva=kva / 1000, vn_hv_kv=30, vn_lv_kv=0.4,
                                          vk_percent=4 if kva <= 630 else 6, vkr_percent=1.0,
                                          pfe_kw=0.4, i0_percent=0.3)
    dist = np.hypot(*(pts - st_xy).T)
    rural = float(np.median(dist)) > RURAL_MEDIAN_M
    pp.create_std_type(net, RURAL_LINE, name='Al 95 Buendel', element='line')
    trunk = 'Al 95 Buendel' if rural else 'NAYY 4x150 SE'
    coords = {}
    buses = [pp.create_bus(net, vn_kv=0.4) for _ in members]
    direct = np.array([m['kwp'] > DIRECT_KWP for m in members])
    ok, t, d_t = tr['ok'], tr['t'], tr['d_t']

    def line(a, b, length_m, std, name, geom, parallel=1):
        li = pp.create_line(net, a, b, length_km=max(length_m, 5) / 1000, std_type=std, name=name, parallel=parallel)
        coords[li] = np.asarray(geom)

    for k, i in enumerate(np.flatnonzero(direct)):  # eigenes Kabel ab Sammelschiene, entlang der Straße
        name, par = f'D{k + 1}', 2 if members[i]['kwp'] > 100 else 1
        if ok[i]:
            geom = np.vstack([roads.xy[roads.path(tr, int(t[i]))], pts[i]])
            line(lv, buses[i], tr['dist'][t[i]] + d_t[i], 'NAYY 4x150 SE', name, geom, par)
        else:
            line(lv, buses[i], dist[i] * LINE_DETOUR, 'NAYY 4x150 SE', name, [st_xy, pts[i]], par)
    rest = np.flatnonzero(~direct & ok)
    segs, _ = roads.contract(tr, [int(t[i]) for i in rest]) if len(rest) else ([], {})
    feeder = _split_feeders(tr['s'], segs, [int(t[i]) for i in rest if members[i]['hh'] > 0])
    sizes = {}
    for i in rest:
        sizes[feeder[int(t[i])]] = sizes.get(feeder[int(t[i])], 0) + 1
    order = {r: n + 1 for n, (r, _) in enumerate(sorted(sizes.items(), key=lambda kv: -kv[1]))}
    node_bus = {tr['s']: lv}
    for p_node, k, geom, length in sorted(segs, key=lambda sg: tr['dist'][sg[1]]):  # Eltern vor Kindern
        if feeder[k] not in order:  # Abgang ohne Gebäude (nach dem Teilen leer)
            continue
        node_bus.setdefault(k, pp.create_bus(net, vn_kv=0.4))
        name = f'A{order[feeder[k]]}'
        if feeder[k] == k:  # Anfang eines Abgangs: eigenes Kabel ab Sammelschiene entlang der Straße
            line(lv, node_bus[k], tr['dist'][k], trunk, name, roads.xy[roads.path(tr, k)])
        else:
            line(node_bus[p_node], node_bus[k], length, trunk, name, geom)
    for i in rest:  # Hausanschluss vom Straßenpunkt zum Gebäude
        tn = int(t[i])
        line(node_bus[tn], buses[i], d_t[i], lr.SERVICE_TYPE, f'A{order.get(feeder[tn], 0)}',
             [roads.xy[tn], pts[i]])
    for k, i in enumerate(np.flatnonzero(~direct & ~ok)):  # ohne Straße: Luftlinie ab Sammelschiene
        line(lv, buses[i], dist[i] * LINE_DETOUR, trunk, 'X', [st_xy, pts[i]])
    loads = [pp.create_load(net, b, p_mw=0) for b in buses]
    sgens = [pp.create_sgen(net, b, p_mw=0) for b in buses]
    net['line_coords'] = coords
    reach = [tr['dist'][t[i]] + d_t[i] for i in rest]
    meta = {'netzart': 'land' if rural else 'stadt', 'abgaenge': len(order), 'direktabgaenge': int(direct.sum()),
            'abgang_max_m': round(float(max(reach)), 0) if reach else 0, 'strassennetz': 1,
            'ohne_strasse': int((~direct & ~ok).sum())}
    return net, lv, loads, sgens, meta


def station_kpis(p_station, kva, base_peak):
    """Trafo-Kennzahlen; die *_basis-Werte beziehen sich auf 80 % der Basisfall-Spitze (unabhängig vom Trafo)."""
    feed = -p_station
    limit = LOADING_LIMIT * kva
    ref = LOADING_LIMIT * max(base_peak, 1e-9)
    return {'rueckspeisung_max_kw': round(float(feed.max()), 1), 'bezug_max_kw': round(float(p_station.max()), 1),
            'spitze_vs_basis_pct': round(100 * (feed.max() / base_peak - 1), 1) if base_peak > 0 else None,
            'h_ueber_80pct_basis': int((feed > ref).sum()), 'kwh_ueber_80pct_basis': round(float(np.maximum(feed - ref, 0).sum()), 1),
            'h_ueber_80pct_trafo': int((feed > limit).sum()),
            'rueckspeisung_kwh': round(float(np.maximum(feed, 0).sum()), 0)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--no-loadflow', action='store_true')
    ap.add_argument('--large-share', type=float, default=STORAGE_SHARE_LARGE,
                    help='Anteil der Anlagen 30-250 kWp (Gewerbe, Landwirtschaft) mit Speicher')
    ap.add_argument('--roads', type=Path, help='OSM-Straßen (Overpass-JSON): Stränge entlang der Straßen')
    args = ap.parse_args()
    globals()['STORAGE_SHARE_LARGE'] = args.large_share
    args.output.mkdir(parents=True, exist_ok=True)
    import pandapower as pp

    stations, st_xy, st_uw, nodes = build_members(args.input)
    roads = None
    if args.roads:
        import steyr_lv_roads
        roads = steyr_lv_roads.RoadGraph(args.roads)
    profiles = {b: read_pvgis(args.input / f'pvgis_{b}.csv') for b in PVGIS_BINS}
    h0 = read_h0(args.input / 'apcs' / 'synthload2026.csv')
    pv_kw = np.column_stack([sum(profiles[b] * k for b, k in n['pv'].items()) if n['pv'] else np.zeros(8760)
                             for n in nodes])
    load_kw = np.column_stack([h0 * KWH_PER_HH * n['hh'] for n in nodes])
    cap = np.array([n['kwh'] for n in nodes])
    st_of = np.array([n['station'] for n in nodes])
    nets = {s: simulate(pv_kw, load_kw, cap, s) for s in STRATEGIES}

    rows, samples = [], defaultdict(list)
    for si in sorted(set(st_of)):
        members_idx = np.flatnonzero(st_of == si)
        members = [nodes[i] for i in members_idx]
        n_hh = sum(m['hh'] for m in members)
        n_buildings = sum(m['hh'] > 0 for m in members)
        kwp = sum(m['kwp'] for m in members)
        kva = trafo_kva(n_buildings, n_hh, kwp)
        cls = next(c for lo, hi, c in CLASSES if lo <= kwp < hi)
        p_st = {s: nets[s][:, members_idx].sum(axis=1) for s in STRATEGIES}
        hours = np.argsort(p_st['base'])[:LF_HOURS]  # stärkste Rückspeisung im Basisfall
        lf, meta = {}, {}
        if not args.no_loadflow:
            net, lv, loads, sgens, meta = build_net(st_xy[si], members, kva, roads)
            for s in STRATEGIES:
                du, vmax, line = [], [], []
                for h in hours:
                    net.load.loc[loads, 'p_mw'] = np.maximum(nets[s][h, members_idx], 0) / 1000
                    net.sgen.loc[sgens, 'p_mw'] = np.maximum(-nets[s][h, members_idx], 0) / 1000
                    pp.runpp(net, numba=False)
                    vm = net.res_bus.vm_pu
                    du.append(float(vm.max() - vm[lv]))
                    vmax.append(float(vm.max()))
                    line.append(float(net.res_line.loading_percent.max()))
                lf[s] = {'du_max_pct': round(100 * max(du), 2), 'vm_max_pu': round(max(vmax), 4),
                         'h_du_ueber_3pct': int(sum(d > 0.03 for d in du)), 'kabel_max_pct': round(max(line), 1)}
        for s in STRATEGIES:
            row = {'station': stations[si]['osm_id'], 'synthetic': stations[si].get('synthetic', 0), 'uw': st_uw[si],
                   'klasse': cls, 'strategie': s, 'kwp_ns': round(kwp, 1), 'haushalte': n_hh, 'wohngebaeude': n_buildings,
                   'trafo_kva': kva, **meta,
                   'speicher': int((cap[members_idx] > 0).sum()),
                   **station_kpis(p_st[s], kva, float(-p_st['base'].min())), **lf.get(s, {})}
            rows.append(row)
        samples[cls].append((kwp, si, p_st))

    with open(args.output / 'variante_a_stationen.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';')
        w.writeheader()
        w.writerows(rows)

    # Kundensicht: Eigenverbrauch der Speicherhaushalte je Strategie
    m = cap > 0
    gen = pv_kw[:, m].sum()
    customer = {}
    for s in STRATEGIES:
        export = np.maximum(-nets[s][:, m], 0).sum()
        customer[s] = {'eigenverbrauch_pct': round(100 * (1 - export / gen), 1),
                       'bezug_mwh': round(float(np.maximum(nets[s][:, m], 0).sum()) / 1000, 1)}

    # Zeitreihen der Stichprobe: je Klasse fünf Stationen an Quantilen, klarster Tag
    day = int(np.argmax(profiles['S35'].reshape(-1, 24).sum(axis=1)))
    with open(args.output / 'stichprobe_tag.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['klasse', 'station', 'stunde'] + list(STRATEGIES))
        for cls, items in samples.items():
            items.sort(key=lambda t: t[0])
            for q in (0.1, 0.3, 0.5, 0.7, 0.9):
                kwp, si, p_st = items[min(int(q * len(items)), len(items) - 1)]
                for h in range(24):
                    w.writerow([cls, stations[si]['osm_id'], h] + [round(float(p_st[s][day * 24 + h]), 1) for s in STRATEGIES])

    summary = {'stationen': len(rows) // len(STRATEGIES), 'knoten': len(nodes), 'speicher': int(m.sum()),
               'speicher_mwh': round(float(cap.sum()) / 1000, 2), 'klarster_tag_2023': str(date(2023, 1, 1) + timedelta(days=day)),
               'kunden': customer,
               'annahmen': {'hh_je_mfh': HH_PER_MFH, 'kwh_je_hh': KWH_PER_HH, 'speicher_anteil': STORAGE_SHARE, 'speicher_anteil_gross': STORAGE_SHARE_LARGE,
                            'speicher_kwh_je_kwp_gross': STORAGE_KWH_PER_KWP_LARGE,
                            'speicher_kwh_je_kwp': STORAGE_KWH_PER_KWP, 'c_rate': C_RATE, 'eta': ETA,
                            'fixcap_anteil_kwp': FIXCAP_SHARE, 'kva_je_wohngebaeude': KVA_PER_BUILDING, 'kva_je_haushalt': KVA_PER_HH, 'direktabgang_ab_kwp': DIRECT_KWP,
                            'gebaeude_je_abgang': BUILDINGS_PER_FEEDER, 'land_ab_median_m': RURAL_MEDIAN_M, 'kva_je_kwp': KVA_PER_KWP, 'backup_soc': BACKUP_SOC, 'auslastungsgrenze': LOADING_LIMIT,
                            'lastfluss_stunden': LF_HOURS, 'seed': SEED, 'wetterjahr': 2023,
                            'netz': 'entlang OSM-Straßen' if args.roads else 'Luftlinie (Sektor-MST)'}}
    by_class = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_class[(r['klasse'], r['strategie'])]['rueckspeisung_max_kw'].append(r['rueckspeisung_max_kw'])
        by_class[(r['klasse'], r['strategie'])]['h_ueber_80pct_basis'].append(r['h_ueber_80pct_basis'])
        by_class[(r['klasse'], r['strategie'])]['kwh_ueber_80pct_basis'].append(r['kwh_ueber_80pct_basis'])
        if r['spitze_vs_basis_pct'] is not None:
            by_class[(r['klasse'], r['strategie'])]['spitze_vs_basis_pct'].append(r['spitze_vs_basis_pct'])
        if 'du_max_pct' in r:
            by_class[(r['klasse'], r['strategie'])]['du_max_pct'].append(r['du_max_pct'])
    summary['klassen'] = {f'{k[0]} | {k[1]}': {key: {'n': len(v), 'median': float(np.median(v)), 'p90': float(np.percentile(v, 90)),
                                                    'summe': float(np.sum(v))} for key, v in d.items()}
                          for k, d in sorted(by_class.items())}
    (args.output / 'variante_a_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps({k: summary[k] for k in ('stationen', 'knoten', 'speicher', 'speicher_mwh', 'klarster_tag_2023', 'kunden')},
                     ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
