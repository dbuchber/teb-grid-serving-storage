"""Radiale NS-Topologie je Station: Abgänge entlang der Straßen, geteilt und markiert nach Spec 4.2.

Ergebnis sind reine Arrays (kein pandapower): Abschnitte mit Elternabschnitt, Länge, Abgang und der Matrix
``downstream`` (welche Gebäude hinter welchem Abschnitt liegen). Abschnitte stehen topologisch sortiert
(Eltern vor Kindern); rückwärts iteriert läuft man von den Blättern zur Sammelschiene.

Aufbau (wie ``build_net_roads`` in gridsim/legacy/steyr_sim_variant_a.py, ohne pandapower):

- Anlagen über ``DIRECT_KWP`` bekommen einen eigenen Abgang ab der Sammelschiene, der der Straße folgt
  (ohne Straße: Luftlinie × ``LINE_DETOUR``); dieser Abschnitt endet am Gebäude, ohne Hausanschluss.
- Übrige Gebäude mit Straße hängen am Straßenbaum (``RoadGraph.station_tree``/``contract``): Abschnitte
  zwischen Abzweigen bzw. Anschlusspunkten, vom Anschlusspunkt ein Hausanschluss zum Gebäude.
- Gebäude ohne Straße im Umkreis (oder alle, wenn die Station an keiner Straße liegt bzw. ``roads is None``)
  hängen an einem Luftlinien-Baum (minimaler Spannbaum ab der Station, wie das Luftlinien-Netz in
  gridsim/legacy); jede Kante = Luftlinie × ``LINE_DETOUR``. Der Baumknoten liegt am Gebäude selbst, der
  Hausanschluss hat daher die Länge 0.
- Jeder Ast ab der Sammelschiene ist ein Abgang. Abgänge werden geteilt (siehe ``_split``); ein geteilter
  Abgang ist ein eigenes Kabel ab der Sammelschiene im selben Graben (Länge = Weg ab Sammelschiene).
- Reichweite eines Abgangs = Weglänge Sammelschiene → fernstes Gebäude einschließlich Hausanschluss.
"""
from dataclasses import dataclass

import numpy as np
from scipy import sparse

from gridsim.feeders.area import AREAS, classify

DIRECT_KWP = 30.0       # Annahme K1: Anlagen darüber an eigenem Abgang ab der Sammelschiene
MAX_BUILDINGS = 30      # höchstens so viele Gebäude je Abgang
LINE_DETOUR = 1.2       # Umwegfaktor der Luftlinie


@dataclass
class StationGrid:
    station: int                 # Index in prepared stations
    area: str
    node_index: np.ndarray       # (n,) globale Knotenindizes der Station
    parent: np.ndarray           # (m,) int32, Elternabschnitt, -1 = Sammelschiene
    length_m: np.ndarray         # (m,) float32
    feeder: np.ndarray           # (m,) int16, Abgangsnummer ab 0
    service: np.ndarray          # (m,) bool, Hausanschluss
    overhead: np.ndarray         # (m,) bool
    downstream: sparse.csr_matrix  # (m, n), 1 = Knoten liegt hinter dem Abschnitt
    marked: np.ndarray           # (n_feeder,) bool, „bräuchte eigene Station“
    geometry: list               # m Arrays (k,2), EPSG:31287


def _polyline_m(pts):
    return float(np.hypot(*np.diff(pts, axis=0).T).sum()) if len(pts) > 1 else 0.0


class _Tree:
    """Baum der Trunk-Knoten; Knotenindex topologisch (Elternknoten < Kind), -1 = Sammelschiene."""

    def __init__(self):
        self.parent, self.length, self.geom = [], [], []

    def add(self, parent, length, geom):
        self.parent.append(parent)
        self.length.append(float(length))
        self.geom.append(np.asarray(geom, dtype=float))
        return len(self.parent) - 1


def _road_tree(tree, roads, tr, targets):
    """Straßenbaum über die Anschlusspunkte; gibt Baumknoten je Anschlusspunkt zurück.

    Liegt ein Anschlusspunkt auf dem Stationsknoten selbst, bekommt er einen Pseudoknoten mit Länge 0
    ab der Sammelschiene (eigener kurzer Abgang).
    """
    segs, _ = roads.contract(tr, targets)
    kids = {}
    for seg in segs:
        kids.setdefault(seg[0], []).append(seg)
    at = {}
    if tr['s'] in set(targets):
        p = roads.xy[tr['s']]
        at[tr['s']] = tree.add(-1, 0.0, [p, p])
    queue = [(tr['s'], -1)]
    while queue:                                    # Breitensuche ab der Station: Eltern vor Kindern
        node, idx = queue.pop(0)
        for _, k, pts, length in sorted(kids.get(node, []), key=lambda sg: sg[1]):
            at[k] = tree.add(idx, length, pts)
            queue.append((k, at[k]))
    return at


def _air_tree(tree, st_xy, pts):
    """Minimaler Spannbaum (Prim) über Station + Gebäude, Kanten Luftlinie × LINE_DETOUR; Baumknoten je Gebäude."""
    allp = np.vstack([st_xy, pts])
    n = len(allp)
    in_tree = np.zeros(n, bool)
    in_tree[0] = True
    best = np.hypot(*(allp - allp[0]).T)
    via = np.zeros(n, int)
    node_of = {0: -1}
    for _ in range(n - 1):
        k = int(np.argmin(np.where(in_tree, np.inf, best)))
        in_tree[k] = True
        node_of[k] = tree.add(node_of[via[k]], LINE_DETOUR * best[k], [allp[via[k]], allp[k]])
        d = np.hypot(*(allp - allp[k]).T)
        upd = ~in_tree & (d < best)
        best[upd], via[upd] = d[upd], k
    return [node_of[k] for k in range(1, n)]


def _local(tparent, roots, own_cnt, own_min, own_max):
    """Abgang je Baumknoten und Kennzahlen des Teilbaums innerhalb des Abgangs (ohne abgeteilte Teilbäume)."""
    k_n = len(tparent)
    feeder = np.empty(k_n, int)
    for k in range(k_n):
        feeder[k] = k if k in roots else feeder[tparent[k]]
    cnt, mn, mx = own_cnt.copy(), own_min.copy(), own_max.copy()
    for k in range(k_n - 1, -1, -1):
        p = tparent[k]
        if k not in roots and p >= 0:
            cnt[p] += cnt[k]
            mn[p] = min(mn[p], mn[k])
            mx[p] = max(mx[p], mx[k])
    return feeder, cnt, mn, mx


def _split(tparent, dist, own_cnt, own_min, own_max, limit_m):
    """Abgänge an Abzweigen teilen; gibt die Menge der Abgangs-Wurzelknoten zurück.

    Abzweig = jeder Knoten des zusammengefassten Baums (Abzweig oder Anschlusspunkt), damit auch ein Abgang an
    einer einzigen langen Straße teilbar ist. Solange ein Abgang teilbar verletzt, wird ein Teilbaum zum eigenen
    Abgang ab der Sammelschiene:

    - mehr als MAX_BUILDINGS Gebäude: der Teilbaum mit den meisten Gebäuden, die noch ≤ MAX_BUILDINGS sind
      (bei Gleichstand der fernere);
    - sonst Reichweite > ``limit_m`` und der Abgang hat auch Gebäude innerhalb der Grenze: ein größter Teilbaum,
      dessen Gebäude alle jenseits der Grenze liegen (der mit dem fernsten Gebäude). Weiter teilen verkürzt die
      Reichweite nicht (das Kabel folgt demselben Weg ab der Sammelschiene); der abgeteilte Abgang bleibt lang
      und wird später markiert.

    Gibt es keinen solchen Teilbaum (z. B. > 30 Gebäude am selben Anschlusspunkt), bleibt der Abgang wie er ist.
    """
    roots = {k for k, p in enumerate(tparent) if p == -1}
    while True:
        feeder, cnt, mn, mx = _local(tparent, roots, own_cnt, own_min, own_max)
        cut = None
        for r in sorted(roots):
            members = [c for c in np.flatnonzero(feeder == r) if c != r and cnt[c] > 0]
            if cnt[r] > MAX_BUILDINGS:
                cands = [c for c in members if cnt[c] <= MAX_BUILDINGS]
                if cands:
                    cut = max(cands, key=lambda c: (cnt[c], dist[c]))
                    break
            if mx[r] > limit_m and mn[r] <= limit_m:
                cands = [c for c in members if mn[c] > limit_m and mn[tparent[c]] <= limit_m]
                if cands:
                    cut = max(cands, key=lambda c: mx[c])
                    break
        if cut is None:
            return roots
        roots.add(int(cut))


def _root_geometry(tree, k):
    """Weg Sammelschiene → Baumknoten k als eine Polylinie."""
    chain = []
    while k >= 0:
        chain.append(tree.geom[k])
        k = tree.parent[k]
    chain = chain[::-1]
    return np.vstack([chain[0]] + [g[1:] for g in chain[1:]])


def _overhead_feeders(trunk_len, cable_share):
    """Abgänge als Freileitung, sodass der Freileitungsanteil der Trunklänge möglichst nahe an 1 − cable_share liegt.

    Abgänge nach Trunklänge absteigend; ein Abgang wird nur dann Freileitung, wenn der Anteil dadurch näher ans
    Ziel rückt (|Anteil − Ziel| sinkt). So schießt ein langer Abgang nicht über das Ziel hinaus.
    """
    oh = np.zeros(len(trunk_len), bool)
    total = float(trunk_len.sum())
    target = (1.0 - cable_share) * total
    if total <= 0 or target <= 0:
        return oh
    done = 0.0
    for f in np.argsort(-trunk_len, kind='stable'):
        if abs(done + trunk_len[f] - target) < abs(done - target):
            oh[f] = True
            done += float(trunk_len[f])
    return oh


def build_station_grid(station: int, st_xy, node_index, nodes_xy, nodes_hh, nodes_kwp, roads) -> StationGrid:
    """Radiales NS-Netz einer Station (Spec 4.2).

    ``nodes_xy`` (n, 2), ``nodes_hh`` (n,), ``nodes_kwp`` (n,) gehören zu den Knoten ``node_index`` der Station
    (gleiche Reihenfolge, nicht global). ``roads`` ist ein ``RoadGraph`` oder None. Der Gebietstyp wird hier mit
    ``classify`` bestimmt und in ``StationGrid.area`` abgelegt.
    """
    st_xy = np.asarray(st_xy, dtype=float)
    xy = np.asarray(nodes_xy, dtype=float).reshape(-1, 2)
    kwp = np.asarray(nodes_kwp, dtype=float)
    n = len(xy)
    area = classify(xy, nodes_hh)
    a = AREAS[area]
    direct = kwp > DIRECT_KWP

    tr = roads.station_tree(st_xy, xy) if roads is not None and n else None
    ok = tr['ok'] if tr is not None else np.zeros(n, bool)

    # Trunk-Baum: Straßenbaum, dann Luftlinien-Baum für Gebäude ohne Straße
    tree = _Tree()
    att = np.full(n, -1)
    svc_len = np.zeros(n)
    svc_geom = [None] * n
    road_nodes = np.flatnonzero(~direct & ok)
    if len(road_nodes):
        at = _road_tree(tree, roads, tr, [int(tr['t'][i]) for i in road_nodes])
        for i in road_nodes:
            t = int(tr['t'][i])
            att[i], svc_len[i] = at[t], tr['d_t'][i]
            svc_geom[i] = np.array([roads.xy[t], xy[i]])
    air_nodes = np.flatnonzero(~direct & ~ok)
    if len(air_nodes):
        for i, k in zip(air_nodes, _air_tree(tree, st_xy, xy[air_nodes])):
            att[i] = k
            svc_geom[i] = np.array([xy[i], xy[i]])
    tparent = np.array(tree.parent, dtype=int)
    k_n = len(tparent)
    dist = np.zeros(k_n)
    for k in range(k_n):
        dist[k] = tree.length[k] + (dist[tparent[k]] if tparent[k] >= 0 else 0.0)

    rest = np.flatnonzero(~direct)
    reach_b = dist[att[rest]] + svc_len[rest] if len(rest) else np.zeros(0)
    own_cnt = np.zeros(k_n, int)
    own_min, own_max = np.full(k_n, np.inf), np.full(k_n, -np.inf)
    np.add.at(own_cnt, att[rest], 1)
    np.minimum.at(own_min, att[rest], reach_b)
    np.maximum.at(own_max, att[rest], reach_b)
    roots = _split(tparent, dist, own_cnt, own_min, own_max, a.max_feeder_m)
    tfeeder, cnt, _, _ = _local(tparent, roots, own_cnt, own_min, own_max)

    # Abgangsnummern: Baum-Abgänge nach Gebäudezahl absteigend, dann Direktabgänge in Knotenreihenfolge
    live_roots = sorted((r for r in roots if cnt[r] > 0), key=lambda r: (-cnt[r], r))
    number = {r: f for f, r in enumerate(live_roots)}
    n_feeder = len(live_roots) + int(direct.sum())

    parent, length, feeder, service, geometry = [], [], [], [], []

    def seg(p, ln, f, svc, geom):
        parent.append(p), length.append(ln), feeder.append(f), service.append(svc), geometry.append(geom)
        return len(parent) - 1

    seg_of = {}
    for k in range(k_n):                    # Trunk in Baumreihenfolge: Eltern vor Kindern
        if cnt[k] == 0:                     # nach dem Teilen leerer Ast
            continue
        f = number[tfeeder[k]]
        if k in roots:                      # eigenes Kabel ab Sammelschiene, Weg wie im Baum
            seg_of[k] = seg(-1, dist[k], f, False, _root_geometry(tree, k))
        else:
            seg_of[k] = seg(seg_of[tparent[k]], tree.length[k], f, False, tree.geom[k])
    end = np.full(n, -1)
    for f, i in enumerate(np.flatnonzero(direct), start=len(live_roots)):
        if ok[i]:
            t = int(tr['t'][i])
            geom = np.vstack([roads.xy[roads.path(tr, t)], xy[i]])
            end[i] = seg(-1, tr['dist'][t] + tr['d_t'][i], f, False, geom)
        else:
            end[i] = seg(-1, LINE_DETOUR * np.hypot(*(xy[i] - st_xy)), f, False, np.array([st_xy, xy[i]]))
    for i in rest:                          # Hausanschlüsse zuletzt (Blätter)
        k = seg_of[att[i]]
        end[i] = seg(k, svc_len[i], feeder[k], True, svc_geom[i])

    parent = np.array(parent, dtype=np.int32)
    length = np.array(length, dtype=np.float32)
    feeder = np.array(feeder, dtype=np.int16)
    service = np.array(service, dtype=bool)
    m = len(parent)

    rows, cols = [], []
    for i in range(n):
        j = end[i]
        while j >= 0:
            rows.append(j), cols.append(i)
            j = parent[j]
    downstream = sparse.csr_matrix((np.ones(len(rows), np.int8), (rows, cols)), shape=(m, n))

    trunk_len = np.bincount(feeder[~service], weights=length[~service], minlength=n_feeder)
    overhead = _overhead_feeders(trunk_len, a.cable_share)[feeder] if m else np.zeros(0, bool)

    node_reach = downstream.T @ length.astype(float)
    marked = np.zeros(n_feeder, bool)
    if n:
        np.logical_or.at(marked, feeder[end], node_reach > a.max_feeder_m)
    return StationGrid(station=station, area=area, node_index=np.asarray(node_index), parent=parent,
                       length_m=length, feeder=feeder, service=service, overhead=overhead,
                       downstream=downstream, marked=marked, geometry=geometry)
