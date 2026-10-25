"""Zusatzstationen, wo NS-Abgänge zu lang sind (Spec Entscheidung 1, Owner 25.10.2026).

Ergebnis ist eine **neue Variante** der vorbereiteten Daten (z. B. ``prepared-ns/``); die Ausgangsvariante bleibt
unverändert. Ablauf (``prepare_extra_stations``):

1. Netze aller Stationen bauen und bemessen wie ``prepare-feeders``.
2. ``plan_extra``: je Station mit markiertem Abgang (zu lang oder Bemessung scheitert) die Knoten dieser Abgänge
   per k-Means gruppieren; k = kleinste Zahl, bei der kein Cluster mehr als ``MAX_CLUSTER`` Knoten hat (3,5 Abgänge
   × 30; Controller-Entscheidung, Netz OÖ im Mittel ca. 58 Anlagen je Station) und kein Knoten weiter
   als ``max_feeder_m`` / 1,2 (Luftlinie, Umwegfaktor) vom Clusterzentrum liegt. Standort = Wohngebäude nächst
   dem Zentrum (nur Hallen im Cluster: Knoten nächst dem Zentrum), auf den nächsten Straßenknoten gezogen, wenn
   einer höchstens ``SNAP_M`` entfernt ist.
3. ``reassign``: nur Knoten markierter Abgänge (Gebäude und PV-Hallen) wechseln, und zwar zur nächsten Station
   (alt + neu) entlang der Straße (``RoadGraph.nearest_station``); ohne Straßenverbindung nächste Station in
   Luftlinie (≤ 600 m wie ``build_members``; weiter weg trotzdem, gezählt). Alle übrigen Knoten behalten ihre
   Station. Kein Knoten bleibt ohne Station.
4. Stationen ohne Knoten fallen aus der Variante (gezählt).
5. Sind danach mehr als 10 % der Stationen markiert, ein zweiter Durchgang (2.–4.), danach wird berichtet statt
   weiter iteriert.
6. ``write_variant``: alle Dateien aller Wetterjahre kopiert; ``nodes_station.npy`` und ``stations.json``
   ersetzt (gleiches Format; Trafo mit ``sim.trafo_kva`` der neuen Zuordnung, ``uw`` vom Elternknoten), im
   ``manifest.json`` je Jahr ein Verweis auf die Ausgangsvariante, dazu ``variant.json`` (Stationskoordinaten
   EPSG:31287, Elternstation, Bericht).
7. ``prepare_feeders`` auf der Variante; der Bericht bekommt den Block ``extra_stations``.
"""
import hashlib
import json
import math
import shutil
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial import cKDTree

from gridsim import legacy
from gridsim.feeders.area import AREAS
from gridsim.feeders.prepare import (DESIGN_YEAR, TO_WGS84, VARIANT_FILE, build_grids, feeder_context, marked_share,
                                     node_feeder, prepare_feeders)
from gridsim.feeders.topology import LINE_DETOUR, MAX_BUILDINGS

ID_FORMAT = 'demo:steyr:ns-{:03d}'
SNAP_M = 50.0           # Standort auf Straßenknoten ziehen, wenn höchstens so weit entfernt
AIR_MAX_M = 600.0       # Luftlinien-Zuordnung ohne Straße wie build_members (base.MAX_DIST_M)
MAX_PASSES = 2
MARKED_LIMIT = 0.10     # Anteil markierter Stationen, ab dem ein weiterer Durchgang läuft
SEED = 20261025         # k-Means; je Station SEED + Stationsindex
MAX_CLUSTER = int(3.5 * MAX_BUILDINGS)   # 105 Knoten je Zusatzstation (3,5 Abgänge × 30)


def _clusters(pts, radius, seed):
    """Kleinste k-Means-Teilung: ≤ MAX_CLUSTER Punkte je Cluster, alle Punkte ≤ ``radius`` vom Zentrum.

    Gibt Liste von (Indexarray, Zentrum) zurück; leere Cluster entfallen.
    """
    n = len(pts)
    origin = pts.mean(axis=0)
    rel = pts - origin
    for k in range(max(1, math.ceil(n / MAX_CLUSTER)), n + 1):
        if k == n:
            labels = np.arange(n)
        elif k == 1:
            labels = np.zeros(n, int)
        else:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')               # leere Cluster sind hier erlaubt
                _, labels = kmeans2(rel, k, seed=seed, minit='++')
        out = []
        for lab in np.unique(labels):
            idx = np.flatnonzero(labels == lab)
            centre = rel[idx].mean(axis=0)
            if len(idx) > MAX_CLUSTER or np.hypot(*(rel[idx] - centre).T).max() > radius:
                break
            out.append((idx, centre + origin))
        else:
            return out
    raise AssertionError('unerreichbar: Einzelcluster erfüllen immer beide Bedingungen')


def _marked_local(grid, sized):
    """Lokale Knotenindizes (``grid.node_index``-Reihenfolge) auf markierten Abgängen."""
    bad = grid.marked | sized.marked
    if not bad.any() or not len(grid.node_index):
        return np.zeros(0, int)
    return np.flatnonzero(bad[node_feeder(grid)])


def marked_nodes(grids: dict) -> np.ndarray:
    """Globale Knotenindizes auf markierten Abgängen aller Stationen (dürfen die Station wechseln)."""
    parts = [np.asarray(g[0].node_index)[_marked_local(g[0], g[1])] for g in grids.values()]
    return np.sort(np.concatenate(parts)).astype(int) if parts else np.zeros(0, int)


def plan_extra(st_xy, nodes_xy, nodes_hh, nodes_station, grids: dict, roads=None, station_ids=None,
               start=1) -> list[dict]:
    """Neue Stationsstandorte für alle Stationen mit markiertem Abgang (siehe Moduldoku, Schritt 2).

    ``grids``: {s: (StationGrid, SizedGrid, ...)}; Knotenarrays global. ``parent`` ist ``station_ids[s]`` bzw. der
    Stationsindex ohne ``station_ids``. IDs fortlaufend ab ``start``.
    """
    xy = np.asarray(nodes_xy, dtype=float).reshape(-1, 2)
    hh = np.asarray(nodes_hh)
    new = []
    for s in sorted(grids):
        grid, sized = grids[s][0], grids[s][1]
        local = _marked_local(grid, sized)
        if not len(local):
            continue
        idx = np.asarray(grid.node_index)[local]
        radius = AREAS[grid.area].max_feeder_m / LINE_DETOUR
        for members, centre in _clusters(xy[idx], radius, SEED + int(s)):
            cand = idx[members]
            homes = cand[hh[cand] > 0]
            cand = homes if len(homes) else cand
            site = xy[cand[int(np.argmin(np.hypot(*(xy[cand] - centre).T)))]].copy()
            if roads is not None:
                d, t = roads.tree.query(site)
                if d <= SNAP_M:
                    site = roads.xy[int(t)].astype(float)
            lon, lat = TO_WGS84.transform(site[0], site[1])
            new.append({'id': ID_FORMAT.format(start + len(new)), 'x': float(site[0]), 'y': float(site[1]),
                        'lon': float(lon), 'lat': float(lat), 'synthetic': 1,
                        'parent': station_ids[s] if station_ids is not None else int(s)})
    return new


def reassign(st_xy, nodes_xy, roads, current=None, movable=None):
    """Station je Knoten (siehe Moduldoku, Schritt 3) und Zählung {'road', 'air', 'air_far'} der bewegten Knoten.

    ``current``: bisherige Station je Knoten; ``movable``: Indizes der Knoten, die wechseln dürfen. Ohne beides
    werden alle Knoten zugeordnet.
    """
    st_xy = np.asarray(st_xy, dtype=float).reshape(-1, 2)
    xy = np.asarray(nodes_xy, dtype=float).reshape(-1, 2)
    if current is None:
        out, mov = np.full(len(xy), -1, dtype=np.int32), np.arange(len(xy))
    else:
        out = np.asarray(current, dtype=np.int32).copy()
        mov = np.arange(len(xy)) if movable is None else np.asarray(movable, dtype=int)
    pts = xy[mov]
    st_of = np.full(len(pts), -1)
    if roads is not None and len(pts):
        st_of, _, _ = roads.nearest_station(st_xy, pts)
        st_of = np.asarray(st_of).copy()
    d, near = cKDTree(st_xy).query(pts) if len(pts) else (np.zeros(0), np.zeros(0, int))
    miss = st_of < 0
    st_of[miss] = near[miss]
    out[mov] = st_of
    return out, {'road': int((~miss).sum()), 'air': int((miss & (d <= AIR_MAX_M)).sum()),
                 'air_far': int((miss & (d > AIR_MAX_M)).sum())}


def _station_rows(stations, st_of, hh, kwp):
    """stations.json-Zeilen (Format wie gridsim.prepare) aus der neuen Zuordnung."""
    sim = legacy.load('steyr_sim_variant_a')
    rows = []
    for i, s in enumerate(stations):
        m = st_of == i
        n_b, n_hh, k = int((hh[m] > 0).sum()), int(hh[m].sum()), float(kwp[m].sum())
        rows.append({'id': s['id'], 'idx': i, 'kva': sim.trafo_kva(n_b, n_hh, k), 'lon': s['lon'], 'lat': s['lat'],
                     'uw': s['uw'], 'synthetic': int(s['synthetic']), 'n_hh': n_hh, 'n_buildings': n_b,
                     'kwp': round(k, 1)})
    return rows


def write_variant(prepared_root, out_root, stations, nodes_station, meta=None):
    """Variante schreiben (siehe Moduldoku, Schritt 6). ``stations``: Liste mit id, x, y, lon, lat, uw, synthetic,
    parent (Reihenfolge = Stationsindex); jede Station muss Knoten haben."""
    src, out = Path(prepared_root).resolve(), Path(out_root).resolve()
    if out == src or src in out.parents or out in src.parents:
        raise ValueError(f'Variante {out} darf nicht in der Ausgangsvariante {src} liegen (oder umgekehrt)')
    if out.exists():
        if not (out / VARIANT_FILE).exists() and any(out.iterdir()):
            raise ValueError(f'{out} existiert und ist keine Variante; nicht überschrieben')
        shutil.rmtree(out)
    st_of = np.asarray(nodes_station, dtype=np.int32)
    if set(np.unique(st_of).tolist()) != set(range(len(stations))):
        raise ValueError('jede Station der Variante braucht Knoten, jeder Knoten eine Station')
    years = sorted(int(d.name) for d in src.iterdir() if d.is_dir() and d.name.isdigit())
    hh = np.load(src / str(DESIGN_YEAR) / 'nodes_hh.npy').astype(int)
    kwp = np.load(src / str(DESIGN_YEAR) / 'nodes_kwp_bins.npy').astype(float).sum(axis=1)
    rows = _station_rows(stations, st_of, hh, kwp)
    ref = {'source': str(src), 'stations': len(rows)}
    for y in years:
        d_src, d_out = src / str(y), out / str(y)
        d_out.mkdir(parents=True)
        for f in sorted(d_src.iterdir()):
            if f.is_file() and f.name not in ('nodes_station.npy', 'stations.json', 'manifest.json'):
                shutil.copy2(f, d_out / f.name)
        np.save(d_out / 'nodes_station.npy', st_of)
        (d_out / 'stations.json').write_text(json.dumps(rows, ensure_ascii=False))
        manifest = json.loads((d_src / 'manifest.json').read_text())
        manifest['variant'] = {**ref, 'source_manifest_sha256': hashlib.sha256(
            (d_src / 'manifest.json').read_bytes()).hexdigest()}
        (d_out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    variant = {'created': datetime.now(timezone.utc).isoformat(timespec='seconds'), **ref,
               'crs': 'EPSG:31287',
               'stations': [{'id': s['id'], 'x': float(s['x']), 'y': float(s['y']), 'synthetic': int(s['synthetic']),
                             'parent': s.get('parent')} for s in stations],
               **(meta or {})}
    (out / VARIANT_FILE).write_text(json.dumps(variant, ensure_ascii=False, indent=1))
    return out


def prepare_extra_stations(input_dir: Path, prepared_root: Path, out_root: Path, max_passes=MAX_PASSES) -> Path:
    """Zusatzstationen planen, Variante nach ``out_root`` schreiben und dort ``prepare_feeders`` ausführen."""
    inp, src, out = Path(input_dir), Path(prepared_root), Path(out_root)
    if out.resolve() == src.resolve():
        raise ValueError('Ausgabe der Variante darf nicht die Ausgangsvariante sein')
    ctx = feeder_context(inp, src)
    p, roads, xy, hh, kwp, loads = ctx['p'], ctx['roads'], ctx['xy'], ctx['hh'], ctx['kwp'], ctx['loads']
    stations = [{'id': r['id'], 'x': float(x), 'y': float(y), 'lon': r['lon'], 'lat': r['lat'], 'uw': r['uw'],
                 'synthetic': int(r['synthetic']), 'parent': None, 'old': True}
                for r, (x, y) in zip(p.stations, ctx['st_xy'])]
    st_of = ctx['st_of']
    grids = build_grids(ctx['st_xy'], xy, hh, kwp, st_of, loads, roads, len(stations))
    shares = {'source': round(marked_share(grids), 4)}
    passes, added, dropped, next_id = [], 0, {'old': 0, 'new': 0}, 1
    for k in range(1, max_passes + 1):
        if k > 1 and shares[f'pass{k - 1}'] <= MARKED_LIMIT:
            break
        st_xy = np.array([[s['x'], s['y']] for s in stations], dtype=float)
        new = plan_extra(st_xy, xy, hh, st_of, grids, roads=roads, station_ids=[s['id'] for s in stations],
                         start=next_id)
        movable = marked_nodes(grids)
        uw = {s['id']: s['uw'] for s in stations}
        stations += [{**s, 'uw': uw[s['parent']], 'old': False} for s in new]
        next_id += len(new)
        added += len(new)
        st_xy = np.array([[s['x'], s['y']] for s in stations], dtype=float)
        st_of, info = reassign(st_xy, xy, roads, current=st_of, movable=movable)
        info['movable'] = int(len(movable))
        keep = np.unique(st_of)
        gone = [stations[i] for i in sorted(set(range(len(stations))) - set(keep.tolist()))]
        dropped['old'] += sum(s['old'] for s in gone)
        dropped['new'] += sum(not s['old'] for s in gone)
        remap = np.full(len(stations), -1, dtype=np.int32)
        remap[keep] = np.arange(len(keep), dtype=np.int32)
        stations = [stations[i] for i in keep]
        st_of = remap[st_of]
        grids = build_grids(st_xy[keep], xy, hh, kwp, st_of, loads, roads, len(stations))
        shares[f'pass{k}'] = round(marked_share(grids), 4)
        passes.append({'pass': k, 'planned': len(new), 'dropped': len(gone), 'stations': len(stations),
                       'assignment': info, 'marked_share': shares[f'pass{k}']})

    n_old = len(p.stations)
    extra = {'stations_old': n_old, 'stations_added': added, 'stations_dropped': dropped,
             'stations_new_kept': sum(not s['old'] for s in stations), 'stations_total': len(stations),
             'marked_share': shares, 'marked_limit': MARKED_LIMIT, 'passes': passes,
             'buildings_without_road': {'air_le_600m': sum(x['assignment']['air'] for x in passes),
                                        'air_gt_600m': sum(x['assignment']['air_far'] for x in passes),
                                        'definition': 'bewegte Knoten ohne Straßenverbindung, Summe der Durchgänge'},
             'nodes_moved': int(sum(a != b for a, b in zip(
                 [p.stations[i]['id'] for i in ctx['st_of']], [stations[i]['id'] for i in st_of]))),
             'rule': {'max_cluster': MAX_CLUSTER, 'moves': 'nur Knoten markierter Abgänge', 'radius': 'max_feeder_m / 1,2', 'snap_m': SNAP_M,
                      'air_max_m': AIR_MAX_M, 'seed': SEED, 'max_passes': max_passes}}
    write_variant(src, out, stations, st_of, meta={'report': extra})
    feeders = prepare_feeders(inp, out)
    report = json.loads((feeders / 'report.json').read_text())
    report['extra_stations'] = extra
    (feeders / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1))
    return feeders
