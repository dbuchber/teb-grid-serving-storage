"""Vorbereitungsschritt ``prepare-feeders``: je Station ein NS-Netz bauen, nach „heute“ bemessen und speichern.

Eingaben: Knoten- und Stationskoordinaten aus ``build_members`` (eingefroren, wie gridsim.prepare), die
vorbereiteten Arrays in ``prepared/<jahr>/`` und das Straßennetz ``osm_roads.json`` im Eingabeverzeichnis
(fehlt es, entstehen alle Netze per Luftlinie). Ausgabe nach ``prepared/feeders/``:

- ``<station>.npz``: Felder von ``StationGrid`` (einschließlich ``tail``, Ausläufer) und ``SizedGrid``; ``downstream`` als CSR-Arrays
  (``ds_data``, ``ds_indices``, ``ds_indptr``, ``ds_shape``), Geometrie als Punktliste mit Versatz je Abschnitt;
  dazu die Auslegungsflüsse ``p_load_kw``/``p_feed_kw`` (nur zur Nachvollziehbarkeit).
- ``index.json``: je Station Gebietstyp, Abgänge, Markierungen, Ausläufer (``tail``), Trunk- und Freileitungslänge.
- ``lines.geojson``: alle Abschnitte in WGS84.
- ``report.json``: Regionswerte (Prüfziele Spec 4.2, Kabelanteil 4.1).
- ``manifest.json``: SHA256 der Eingaben und Schwellen.

Auslegung (Spec 4.3, Entscheidung 5, Fix-Runde 1 vom 25.10.2026), Szenario „heute“, Wetterjahr 2012: je Knoten
die volle Wärmepumpenleistung in der Stunde mit der tiefsten Temperatur der Knotenzelle (``profiles.heat_pump_kw``,
Wärme wie ``profiles.assign``, Heizgrenze aus ``wpev.spread(N, BASE_SEED)``, Versatz 0; Fernwärme 0) und die
PV-Spitze = kWp × max(pv_bins); je Abschnitt ganze Geräte als P90 der Binomialverteilung und Haushaltslast nicht
unter der H0-Spitze (``sizing.design_flows``, ``design_loads``).
"""
import hashlib
from dataclasses import asdict
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from pyproj import Transformer
from scipy import sparse

from gridsim import legacy
from gridsim.data import load_prepared
from gridsim.feeders.area import AREAS
from gridsim.feeders.roads import RoadGraph
from gridsim.feeders.sizing import DesignRule, SizedGrid, design_flows, size
from gridsim.feeders.topology import TAIL_MIN_HOMES, StationGrid, build_station_grid

DESIGN_YEAR = 2012
DESIGN_SCENARIO = 'heute'
ROADS_FILE = 'osm_roads.json'
MEMBER_INPUTS = ('osm_power.json', 'powerstations.json', 'pv_steyr_bbox.geojson', 'gebaeude_bbox.csv')
TO_WGS84 = Transformer.from_crs(31287, 4326, always_xy=True)
CHUNK = 2000            # Knoten je Wärmepumpenblock (8760 × CHUNK float32)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def _years(prepared_root):
    return sorted(int(d.name) for d in Path(prepared_root).iterdir() if d.is_dir() and d.name.isdigit())


VARIANT_FILE = 'variant.json'
POS_TOL_DEG = 1e-6      # Stationsposition: build_members bzw. Variante gegen stations.json


def _members(inp, root, n_stations):
    """Knoten- und Stationskoordinaten (EPSG:31287) und Station je Knoten.

    Knoten (Lage, Haushalte) kommen immer aus ``build_members``. Ohne ``variant.json`` im Prepared-Ordner sind
    Stationen und Zuordnung die von ``build_members``, Stationen verdichtet wie gridsim.prepare. Mit
    ``variant.json`` (Zusatzstationen, siehe extra_stations.py) kommen die Stationskoordinaten aus der Variante und
    die Zuordnung aus ``nodes_station.npy`` des Auslegungsjahrs.
    """
    sim = legacy.load('steyr_sim_variant_a')
    _, st_xy, _, nodes = sim.build_members(inp)
    xy = np.array([n['xy'] for n in nodes], dtype=float).reshape(-1, 2)
    hh = np.array([n['hh'] for n in nodes], dtype=int)
    vf = Path(root) / VARIANT_FILE
    if vf.exists():
        v = json.loads(vf.read_text())
        st = np.array([[r['x'], r['y']] for r in v['stations']], dtype=float).reshape(-1, 2)
        st_of = np.asarray(np.load(Path(root) / str(DESIGN_YEAR) / 'nodes_station.npy'), dtype=np.int32)
        if len(st_of) != len(nodes):
            raise ValueError(f'Knotenzahl weicht ab: Variante hat {len(st_of)} Knoten, build_members {len(nodes)}')
        if len(st) != n_stations or len(np.unique(st_of)) != n_stations:
            raise ValueError(f'Variante: {len(st)} Stationen in {VARIANT_FILE}, {len(np.unique(st_of))} mit Knoten, '
                             f'prepared hat {n_stations}')
        return st_of, xy, hh, st
    used = sorted({n['station'] for n in nodes})
    compact = {si: i for i, si in enumerate(used)}
    st_of = np.array([compact[n['station']] for n in nodes], dtype=np.int32)
    if len(used) != n_stations:
        raise ValueError(f'build_members liefert {len(used)} Stationen mit Knoten, prepared hat {n_stations}')
    return st_of, xy, hh, np.asarray(st_xy, dtype=float)[used]


def _check_positions(prepared_root, years, st_xy):
    """Stationskoordinaten (build_members bzw. Variante) müssen zu stations.json aller Jahre passen (1e-6 Grad)."""
    lon, lat = TO_WGS84.transform(st_xy[:, 0], st_xy[:, 1]) if len(st_xy) else (np.zeros(0), np.zeros(0))
    for y in years:
        rows = json.loads((Path(prepared_root) / str(y) / 'stations.json').read_text())
        if len(rows) != len(st_xy):
            raise ValueError(f'Stationsposition: prepared/{y} hat {len(rows)} Stationen, erwartet {len(st_xy)}')
        dev = np.maximum(np.abs(np.array([r['lon'] for r in rows]) - lon),
                         np.abs(np.array([r['lat'] for r in rows]) - lat))
        bad = np.flatnonzero(dev > POS_TOL_DEG)
        if len(bad):
            i = int(bad[0])
            raise ValueError(f'Stationsposition weicht ab: prepared/{y}/stations.json und Stationskoordinaten '
                             f'unterscheiden sich bei {len(bad)} Stationen (erste: {rows[i]["id"]}, '
                             f'{dev[i]:.2e} Grad)')


def _check_nodes(prepared_root, years, st_of, hh):
    """Knotenliste aller Jahre und von ``build_members`` muss übereinstimmen (Station und Haushalte je Knoten)."""
    for y in years:
        d = Path(prepared_root) / str(y)
        ps = np.load(d / 'nodes_station.npy')
        ph = np.load(d / 'nodes_hh.npy')
        if len(ps) != len(st_of):
            raise ValueError(f'Knotenzahl weicht ab: prepared/{y} hat {len(ps)} Knoten, build_members {len(st_of)}')
        bad = np.flatnonzero((ps != st_of) | (ph != hh))
        if len(bad):
            raise ValueError(f'Knoten weichen ab: prepared/{y} und build_members unterscheiden sich in {len(bad)} '
                             f'Knoten (erster: {int(bad[0])}); prepared neu erzeugen')


def design_loads(p):
    """Auslegungseingaben je Knoten (global) und Regel (Fix-Runde 1, siehe ``sizing.design_flows``).

    ``wp_kw``: elektrische Leistung einer Wärmepumpe am Knoten in der kältesten Stunde seiner Zelle (Wärme wie
    ``profiles.assign``, Versatz 0), 0 für Knoten ohne mögliche WP (Hallen, Fernwärme); ``kwp_peak``: PV-Spitze;
    ``rule``: Anteile wie ``profiles.assign`` (``p_wp`` je berechtigtem Gebäude, ``ev_share`` je Haushalt) und
    H0-Spitze je Haushalt = max(H0 in der kältesten Stunde des Auslegungsjahrs, Jahresspitze des H0-Profils).
    """
    from gridsim import profiles
    from gridsim.run import BASE_SEED
    share = profiles.SCENARIOS[DESIGN_SCENARIO]
    hh = np.asarray(p.nodes_hh, dtype=int)
    fw = np.asarray(p.nodes_fw, dtype=bool)
    homes = hh > 0
    fw_frac = fw[homes].mean() if homes.any() else 0.0
    p_wp = min(1.0, share['wp_share'] / max(1 - fw_frac, 1e-9))           # wie profiles.assign
    wpev = profiles.wpev
    pauschal = np.where(hh == 1, wpev.HEAT_KWH_EFH, wpev.HEAT_KWH_MFH_HH * hh).astype(float)
    lod1 = np.asarray(p.nodes_heat_kwh, dtype=float)
    heat = np.where(homes & ~fw, np.where(np.isnan(lod1), pauschal, lod1), 0.0)
    limits, _ = wpev.spread(len(hh), BASE_SEED)
    dhw = np.asarray(p.nodes_dhw, dtype=float)
    dhw = np.where(np.isnan(dhw), wpev.DHW_SHARE, dhw)
    cells = np.asarray(p.nodes_cell)
    temp = np.asarray(p.temp_cells, dtype=float)
    wp_kw = np.zeros(len(hh))
    for c in np.unique(cells[heat > 0]):
        idx = np.flatnonzero((cells == c) & (heat > 0))
        cold = int(np.argmin(temp[:, c]))
        for k in range(0, len(idx), CHUNK):
            part = idx[k:k + CHUNK]
            el = profiles.heat_pump_kw(temp[:, c], heat[part], limits[part], np.zeros(len(part), int), dhw[part])
            wp_kw[part] = el[cold]
    kwp = np.asarray(p.nodes_kwp_bins, dtype=float).sum(axis=1)
    h0 = np.asarray(p.h0, dtype=float) * legacy.load('steyr_sim_variant_a').KWH_PER_HH   # wie nodeflow
    cold = int(np.argmin(temp.mean(axis=1)))
    rule = DesignRule(wp_share=float(p_wp), ev_share=float(share['ev_share']),
                      h0_peak_kw=float(max(h0[cold], h0.max())))
    return {'wp_kw': wp_kw, 'kwp_peak': kwp * float(np.max(p.pv_bins)), 'rule': rule}


def _save_station(path, grid: StationGrid, sized: SizedGrid, p_load=None, p_feed=None):
    ds = grid.downstream.tocsr()
    lens = np.array([len(gm) for gm in grid.geometry], dtype=np.int64)
    coords = np.vstack(grid.geometry) if len(grid.geometry) else np.zeros((0, 2))
    extra = {} if p_load is None else {'p_load_kw': np.asarray(p_load), 'p_feed_kw': np.asarray(p_feed)}
    np.savez_compressed(
        path, station=np.int64(grid.station), area=np.str_(grid.area), node_index=grid.node_index,
        parent=grid.parent, length_m=grid.length_m, feeder=grid.feeder, service=grid.service,
        overhead=grid.overhead, marked=grid.marked, tail=grid.tail, ds_data=ds.data, ds_indices=ds.indices, ds_indptr=ds.indptr,
        ds_shape=np.array(ds.shape, dtype=np.int64), geom_coords=coords, geom_offsets=np.concatenate([[0], np.cumsum(lens)]),
        types=np.array(sized.types, dtype=str), parallel=sized.parallel, i_max_a=sized.i_max_a, r_ohm=sized.r_ohm,
        x_ohm=sized.x_ohm, du_load_pct=sized.du_load_pct, du_feed_pct=sized.du_feed_pct, sized_marked=sized.marked,
        sized_marked_voltage=_voltage(sized),
        **extra)


def _voltage(sized):
    """``SizedGrid.marked_voltage`` als bool-Array (ältere Objekte ohne Feld: keine reinen Spannungsfälle)."""
    v = getattr(sized, 'marked_voltage', None)
    return np.zeros(len(sized.marked), bool) if v is None else np.asarray(v, bool)


def _load_station(path):
    z = np.load(path, allow_pickle=False)
    ds = sparse.csr_matrix((z['ds_data'], z['ds_indices'], z['ds_indptr']), shape=tuple(z['ds_shape']))
    off = z['geom_offsets']
    coords = z['geom_coords']
    geometry = [coords[off[j]:off[j + 1]] for j in range(len(off) - 1)]
    grid = StationGrid(station=int(z['station']), area=str(z['area']), node_index=z['node_index'],
                       parent=z['parent'], length_m=z['length_m'], feeder=z['feeder'], service=z['service'],
                       overhead=z['overhead'], downstream=ds, marked=z['marked'], geometry=geometry,
                       tail=z['tail'] if 'tail' in z.files else None)
    sized = SizedGrid(types=[str(t) for t in z['types']], parallel=z['parallel'], i_max_a=z['i_max_a'],
                      r_ohm=z['r_ohm'], x_ohm=z['x_ohm'], du_load_pct=z['du_load_pct'],
                      du_feed_pct=z['du_feed_pct'], marked=z['sized_marked'],
                      marked_voltage=(z['sized_marked_voltage'] if 'sized_marked_voltage' in z.files
                                      else np.zeros(len(z['sized_marked']), bool)))
    return grid, sized


def load_feeders(prepared_root):
    """Alle Stationsnetze aus ``prepared_root/feeders/``; None, wenn das Verzeichnis fehlt."""
    d = Path(prepared_root) / 'feeders'
    if not (d / 'index.json').exists():
        return None
    index = json.loads((d / 'index.json').read_text())
    return {int(s): _load_station(d / f'{int(s)}.npz') for s in index}


def _route(grid):
    """Trassenlänge (m) eines Netzes ohne Hausanschlüsse, aufgeteilt in (Kabel, Freileitung).

    Geteilte Abgänge und Direktabgänge liegen im selben Graben wie der Baum; ihre Geometrie wird in
    Punktpaare zerlegt und gleiche Paare nur einmal gezählt. Längen werden mit Länge/Polylinienlänge des
    Abschnitts skaliert (Luftlinien-Umwegfaktor). Ein Paar mit Kabel und Freileitung zählt anteilig nach Systemen.
    """
    edges = {}
    for j in np.flatnonzero(~grid.service):
        pts = np.asarray(grid.geometry[j], dtype=float)
        if len(pts) < 2:
            continue
        d = np.hypot(*np.diff(pts, axis=0).T)
        poly = d.sum()
        scale = float(grid.length_m[j]) / poly if poly > 0 else 0.0
        key_pts = np.round(pts, 2)
        for a, b, ln in zip(map(tuple, key_pts[:-1]), map(tuple, key_pts[1:]), d):
            if ln <= 0:
                continue
            e = edges.setdefault((min(a, b), max(a, b)), [ln * scale, 0, 0])
            e[2 if grid.overhead[j] else 1] += 1
    cable = sum(ln * c / (c + o) for ln, c, o in edges.values())
    over = sum(ln * o / (c + o) for ln, c, o in edges.values())
    return cable, over


def node_feeder(grid):
    """Abgang je Knoten (in ``grid.node_index``-Reihenfolge)."""
    d = grid.downstream.tocsc()
    return np.array([grid.feeder[d.indices[d.indptr[i]]] for i in range(d.shape[1])], dtype=int)


def _station_summary(grid, sized, n_buildings=None):
    trunk = ~grid.service
    sys_len = grid.length_m.astype(float) * sized.parallel
    route_c, route_o = _route(grid)
    node_reach = grid.downstream.T @ grid.length_m.astype(float)
    n_feeder = len(grid.marked)
    reach = np.zeros(n_feeder)
    has_nodes = np.zeros(n_feeder, bool)          # Abgänge ohne Knoten zählen nicht in die Reichweite
    if len(node_reach):
        end_feeder = node_feeder(grid)
        np.maximum.at(reach, end_feeder, node_reach)
        has_nodes[end_feeder] = True
    return {
        'area': grid.area, 'n_nodes': int(len(grid.node_index)), 'n_feeders': int(n_feeder),
        'n_buildings': None if n_buildings is None else int(n_buildings),
        'marked_long': int(grid.marked.sum()), 'marked_sizing': int(sized.marked.sum()),
        'marked': int((grid.marked | sized.marked).sum()),
        'marked_voltage': int((_voltage(sized) & ~grid.marked & ~sized.marked).sum()),
        'tail': int((grid.tail & ~sized.marked).sum()),
        'trunk_m': round(float(sys_len[trunk].sum()), 1),
        'overhead_m': round(float(sys_len[trunk & grid.overhead].sum()), 1),
        'route_m': round(route_c + route_o, 1), 'route_overhead_m': round(route_o, 1),
        'service_m': round(float(sys_len[grid.service].sum()), 1),
        'reach_m': [round(float(r), 1) for r in reach[has_nodes]],
        'tail_reach_m': [round(float(r), 1) for r in reach[has_nodes & grid.tail & ~sized.marked]],
        'du_load_max_pct': round(float(sized.du_load_pct.max()), 2) if n_feeder else 0.0,
    }


def _stats(values):
    v = np.asarray(values, dtype=float)
    if not len(v):
        return {'n': 0, 'mean': None, 'median': None, 'p90': None}
    return {'n': int(len(v)), 'mean': round(float(v.mean()), 2), 'median': round(float(np.median(v)), 2),
            'p90': round(float(np.percentile(v, 90)), 2)}


def _per_building(s, route):
    """Plausibilität je Gebäude (Wohngebäude, hh > 0): Gebäude je Station und Trassenmeter je Gebäude.

    Orientierung (Netz OÖ): ca. 58 Kundenanlagen je Station, ca. 46 m NS-Leitung je Anlage.
    """
    nb = [x['n_buildings'] for x in s if x.get('n_buildings') is not None]
    if len(nb) != len(s) or not nb:
        return None
    total = sum(nb)
    return {'buildings_per_station': _stats(nb), 'buildings': int(total),
            'route_m_per_building': round(route / total, 1) if total else None,
            'target': {'buildings_per_station': 58, 'route_m_per_building': 46},
            'definition': 'Gebäude = Wohngebäude (hh > 0); Trasse ohne Hausanschlüsse; nur zur Orientierung'}


def _report(summaries, grids):
    n = len(summaries)
    s = list(summaries.values())
    trunk = sum(x['trunk_m'] for x in s)
    over = sum(x['overhead_m'] for x in s)
    route = sum(x['route_m'] for x in s)
    route_o = sum(x['route_overhead_m'] for x in s)
    svc = sum(x['service_m'] for x in s)
    svc_o = sum(float((g.length_m * z.parallel)[g.service & g.overhead].sum()) for g, z in grids.values())
    st_long = sum(x['marked_long'] > 0 for x in s)
    st_size = sum(x['marked_sizing'] > 0 for x in s)
    st_any = sum(x['marked'] > 0 for x in s)
    st_volt = [x for x in s if x.get('marked_voltage', 0) > 0]
    km_type = {}
    for g, z in grids.values():
        for t, ln, par, svc_flag in zip(z.types, g.length_m, z.parallel, g.service):
            key = t + (' (Hausanschluss)' if svc_flag else '')
            km_type[key] = km_type.get(key, 0.0) + float(ln) * int(par) / 1000.0
    areas = {}
    for a in AREAS:
        sub = [x for x in s if x['area'] == a]
        areas[a] = {'stations': len(sub), 'feeders': sum(x['n_feeders'] for x in sub),
                    'feeder_reach_m': _stats([r for x in sub for r in x['reach_m']]),
                    'trunk_km': round(sum(x['trunk_m'] for x in sub) / 1000, 2)}
    return {
        'n_stations': n,
        'marked': {'stations_long': int(st_long), 'stations_sizing': int(st_size), 'stations_any': int(st_any),
                   'stations_any_share': round(st_any / n, 4) if n else 0.0,
                   'feeders_long': sum(x['marked_long'] for x in s),
                   'feeders_sizing': sum(x['marked_sizing'] for x in s), 'feeders_any': sum(x['marked'] for x in s),
                   'definition': 'Station mit mindestens einem Abgang in StationGrid.marked (zu lang, ab '
                                 f'{TAIL_MIN_HOMES} Wohngebäuden jenseits der Grenze) oder SizedGrid.marked '
                                 '(Strom auch mit 2 × größtem Typ über der Grenze); Ausläufer und reine Spannungsfälle zählen nicht'},
        'voltage_only': {
            'stations': len(st_volt), 'stations_share': round(len(st_volt) / n, 4) if n else 0.0,
            'feeders': int(sum(x.get('marked_voltage', 0) for x in s)),
            'stations_by_area': {a: sum(x['area'] == a for x in st_volt) for a in AREAS},
            'definition': 'Abgang thermisch ausreichend, aber Spannungsfall (5 %) bzw. -anhebung (3 %) auch mit dem '
                          'stärksten Typ über der Planungsgrenze (SizedGrid.marked_voltage); zählt nicht zur '
                          '10-%-Grenze (Owner, Fix-Runde 4)'},
        'tails': {'stations': int(sum(x['tail'] > 0 for x in s)), 'feeders': int(sum(x['tail'] for x in s)),
                  'reach_m': _stats([r for x in s for r in x['tail_reach_m']]),
                  'definition': f'Abgang zu lang, aber weniger als {TAIL_MIN_HOMES} Wohngebäude jenseits der '
                                'Grenze und Bemessung erfolgreich (StationGrid.tail); wie jeder Abgang bemessen, '
                                'nicht markiert'},
        'cable_share': {
            'by_cable_length': round(1 - over / trunk, 4) if trunk else None,
            'by_route_length': round(1 - route_o / route, 4) if route else None,
            'by_cable_length_incl_service': round(1 - (over + svc_o) / (trunk + svc), 4) if trunk + svc else None,
            'acceptance': 'by_route_length',
            'definition': 'ohne Hausanschlüsse; Kabellänge zählt parallele Systeme einzeln, Trassenlänge zählt '
                          'gemeinsame Gräben und Parallelsysteme einmal (Abnahmegröße: by_route_length)',
            'target': 0.79, 'band': [0.74, 0.84]},
        'trunk_km_per_station': {'cable_length': round(trunk / n / 1000, 3) if n else None,
                                 'route_length': round(route / n / 1000, 3) if n else None,
                                 'target': 2.7},
        'total_km': {'trunk_cable': round(trunk / 1000, 2), 'trunk_route': round(route / 1000, 2),
                     'service': round(svc / 1000, 2)},
        'feeders_per_station': {**_stats([x['n_feeders'] for x in s]), 'target': [3.4, 3.8]},
        'per_building': _per_building(s, route),
        'areas': areas,
        'km_per_type': {k: round(v, 2) for k, v in sorted(km_type.items())},
        'thresholds': {a.name: {'max_nn_m': a.max_nn_m if np.isfinite(a.max_nn_m) else None,
                                'cable_share': a.cable_share, 'max_feeder_m': a.max_feeder_m}
                       for a in AREAS.values()},
    }


def _geojson(grids):
    feats = []
    for s, (g, z) in grids.items():
        for j, pts in enumerate(g.geometry):
            if pts is None or len(pts) < 2:
                continue
            lon, lat = TO_WGS84.transform(pts[:, 0], pts[:, 1])
            feats.append({'type': 'Feature', 'geometry': {
                'type': 'LineString', 'coordinates': [[round(float(x), 6), round(float(y), 6)] for x, y in zip(lon, lat)]},
                'properties': {'station': int(s), 'type': z.types[j], 'parallel': int(z.parallel[j]),
                               'feeder': int(g.feeder[j]), 'overhead': bool(g.overhead[j]),
                               'service': bool(g.service[j]), 'length_m': round(float(g.length_m[j]), 1)}})
    return {'type': 'FeatureCollection', 'features': feats}


def marked_share(grids):
    """Anteil der Stationen mit markiertem Abgang (zu lang oder Strom zu hoch; reine Spannungsfälle zählen nicht)."""
    if not grids:
        return 0.0
    return sum(bool((g.marked | z.marked).any()) for g, z, *_ in grids.values()) / len(grids)


def build_grids(st_xy, xy, hh, kwp, st_of, loads, roads, n_stations):
    """Netz und Bemessung je Station: {s: (StationGrid, SizedGrid, p_load, p_feed)}.

    ``xy``/``hh``/``kwp``/``st_of`` sind global je Knoten, ``loads`` aus ``design_loads``.
    """
    wp_kw, kwp_peak, rule = loads['wp_kw'], loads['kwp_peak'], loads['rule']
    grids = {}
    for s in range(n_stations):
        idx = np.flatnonzero(st_of == s)
        grid = build_station_grid(s, st_xy[s], idx, xy[idx], hh[idx], kwp[idx], roads)
        p_load, p_feed = design_flows(grid, hh[idx], wp_kw[idx], kwp_peak[idx], rule)
        grids[s] = (grid, size(grid, p_load, p_feed), p_load, p_feed)
    return grids


def feeder_context(input_dir, prepared_root):
    """Gemeinsame Eingaben für ``prepare_feeders`` und Zusatzstationen, mit allen Prüfungen."""
    inp, root = Path(input_dir), Path(prepared_root)
    years = _years(root)
    if DESIGN_YEAR not in years:
        raise ValueError(f'prepared/{DESIGN_YEAR} fehlt (Auslegungsjahr)')
    p = load_prepared(root, DESIGN_YEAR)
    st_of, xy, hh, st_xy = _members(inp, root, p.n_stations)
    _check_nodes(root, years, st_of, hh)
    _check_positions(root, years, st_xy)
    return {'p': p, 'years': years, 'st_of': st_of, 'xy': xy, 'hh': hh, 'st_xy': st_xy,
            'kwp': np.asarray(p.nodes_kwp_bins, dtype=float).sum(axis=1), 'loads': design_loads(p),
            'roads': RoadGraph(inp / ROADS_FILE) if (inp / ROADS_FILE).exists() else None}


def prepare_feeders(input_dir: Path, prepared_root: Path) -> Path:
    inp, root = Path(input_dir), Path(prepared_root)
    ctx = feeder_context(inp, root)
    p, years, roads = ctx['p'], ctx['years'], ctx['roads']
    built = build_grids(ctx['st_xy'], ctx['xy'], ctx['hh'], ctx['kwp'], ctx['st_of'], ctx['loads'], roads,
                        p.n_stations)

    out = root / 'feeders'
    out.mkdir(parents=True, exist_ok=True)
    grids, summaries = {}, {}
    for s, (grid, sized, p_load, p_feed) in built.items():
        _save_station(out / f'{s}.npz', grid, sized, p_load, p_feed)
        grids[s] = (grid, sized)
        summaries[s] = _station_summary(grid, sized, int((ctx['hh'][grid.node_index] > 0).sum()))

    index = {str(s): {k: v for k, v in x.items() if k not in ('reach_m', 'tail_reach_m')}
             for s, x in summaries.items()}
    (out / 'index.json').write_text(json.dumps(index, ensure_ascii=False))
    (out / 'lines.geojson').write_text(json.dumps(_geojson(grids), ensure_ascii=False))
    (out / 'report.json').write_text(json.dumps(_report(summaries, grids), ensure_ascii=False, indent=1))
    files = [f for f in (*MEMBER_INPUTS, ROADS_FILE) if (inp / f).exists()]
    manifest = {'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'design': {'year': DESIGN_YEAR, 'scenario': DESIGN_SCENARIO, 'rule': 'fix1-binom-p90-h0peak',
                           **asdict(ctx['loads']['rule'])},
                'legacy_frozen_at': legacy.FROZEN_AT,
                'legacy_sha256sums': hashlib.sha256((legacy.DIR / 'SHA256SUMS').read_bytes()).hexdigest(),
                'roads': roads is not None,
                'variant': (root / VARIANT_FILE).exists(),
                'inputs': {f: _sha256(inp / f) for f in files},
                'prepared': {str(y): _sha256(root / str(y) / 'manifest.json') for y in years},
                'thresholds': {a.name: [a.max_nn_m if np.isfinite(a.max_nn_m) else None, a.cable_share,
                                        a.max_feeder_m] for a in AREAS.values()}}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    return out
