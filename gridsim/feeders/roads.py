# Kopie von infra-kg-austria/scripts/steyr_lv_roads.py
# (/Users/dbuchber/Desktop/tmp.nosync/vscode/infra-kg-austria/scripts/steyr_lv_roads.py),
# SHA256 der Quelle: b6f28db79614288c58ace5a96289766debde240c91780525a8b60488b0a41468
# Einzige Änderung: `import steyr_pv_per_station as base` ersetzt durch eigenes TO_LAMBERT
# (dort identisch definiert: Transformer.from_crs(4326, 31287, always_xy=True)); Shebang entfernt, Importe sortiert.
"""Synthetische Niederspannungsnetze entlang des Straßennetzes (OSM) für die Steyr-Simulation.

Statt Luftlinien-MST folgt der Strang den Straßen: Von der Station läuft der kürzeste Weg im
Straßengraphen zu jedem Hausanschlusspunkt (nächster Straßenpunkt des Gebäudes); die Vereinigung
dieser Wege ist ein Baum. Jeder Ast, der die Station verlässt, ist ein Abgang. Vom Straßenpunkt
führt ein Hausanschluss (NAYY 4x50) zum Gebäude. Anlagen über DIRECT_KWP bekommen ein eigenes Kabel
ab der Sammelschiene, das ebenfalls der Straße folgt. Gebäude ohne Straße im Umkreis von
SERVICE_MAX_M hängen wie bisher per Luftlinie (mit Umwegfaktor) an der Sammelschiene.

Straßen: OpenStreetMap (ODbL), highway = primary … service/track, ohne Autobahn und Fußwege.
Ketten von Straßenknoten ohne Abzweig werden zu einer Leitung zusammengefasst (Geometrie bleibt).
"""
import json

import numpy as np
from pyproj import Transformer
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

TO_LAMBERT = Transformer.from_crs(4326, 31287, always_xy=True)  # statt steyr_pv_per_station.TO_LAMBERT

SEG_M = 25.0               # lange Straßenabschnitte so fein unterteilen (Anschlusspunkte)
SERVICE_MAX_M = 150.0      # Annahme: weiter weg von jeder Straße -> Luftlinie zur Station
STATION_SNAP_M = 300.0     # Station weiter weg von jeder Straße -> kein Straßennetz
SEARCH_M = 4000.0          # Dijkstra-Grenze ab der Station
SERVICE_TYPE = 'NAYY 4x50 SE'


class RoadGraph:
    def __init__(self, path):
        data = json.loads(path.read_text(encoding='utf-8'))['elements']
        pos = {e['id']: TO_LAMBERT.transform(e['lon'], e['lat']) for e in data if e['type'] == 'node'}
        ids = {nid: k for k, nid in enumerate(pos)}
        xy = [pos[nid] for nid in pos]
        rows, cols, w = [], [], []

        def add(a, b, length):
            rows.extend((a, b)), cols.extend((b, a)), w.extend((length, length))

        for e in data:
            if e['type'] != 'way':
                continue
            nds = [ids[n] for n in e['nodes'] if n in ids]
            for a, b in zip(nds, nds[1:]):
                pa, pb = np.array(xy[a]), np.array(xy[b])
                length = float(np.hypot(*(pb - pa)))
                n = int(length // SEG_M)
                prev = a
                for k in range(1, n + 1):  # Zwischenpunkte für Anschlüsse an langen Abschnitten
                    xy.append(tuple(pa + (pb - pa) * k / (n + 1)))
                    add(prev, len(xy) - 1, length / (n + 1))
                    prev = len(xy) - 1
                add(prev, b, length / (n + 1))
        self.xy = np.array(xy)
        self.adj = coo_matrix((w, (rows, cols)), shape=(len(xy), len(xy))).tocsr()
        self.tree = cKDTree(self.xy)

    def station_tree(self, st_xy, targets_xy, limit=SEARCH_M, snap=STATION_SNAP_M):
        """Kürzeste-Wege-Baum von der Station zu den Anschlusspunkten; None ohne Straße an der Station."""
        d_st, s = self.tree.query(st_xy)
        if d_st > snap:
            return None
        dist, pred = dijkstra(self.adj, indices=s, limit=limit, return_predecessors=True)
        d_t, t = self.tree.query(np.asarray(targets_xy))
        ok = (d_t <= SERVICE_MAX_M) & np.isfinite(dist[t])
        return {'s': int(s), 'dist': dist, 'pred': pred, 't': t, 'd_t': d_t, 'ok': ok}

    def nearest_station(self, st_xy, pts, limit=SEARCH_M):
        """Nächste Station je Punkt entlang der Straßen (Index in ``st_xy``, -1 ohne Straßenverbindung) und Weglänge (m).

        Stationen weiter als STATION_SNAP_M und Punkte weiter als SERVICE_MAX_M von jeder Straße zählen nicht.
        Zusätzlich: ob jede Station am Straßennetz hängt.
        """
        d_st, s = self.tree.query(np.asarray(st_xy))
        st_of_node = {}
        for i in np.flatnonzero(d_st <= STATION_SNAP_M):  # mehrere Stationen am selben Straßenpunkt: die erste
            st_of_node.setdefault(int(s[i]), int(i))
        out = np.full(len(pts), -1)
        length = np.full(len(pts), np.inf)
        snapped = d_st <= STATION_SNAP_M
        if not st_of_node:
            return out, length, snapped
        src = np.array(list(st_of_node))
        dist, _, sources = dijkstra(self.adj, indices=src, limit=limit, min_only=True, return_predecessors=True)
        d_t, t = self.tree.query(np.asarray(pts))
        ok = (d_t <= SERVICE_MAX_M) & np.isfinite(dist[t])
        out[ok] = [st_of_node[int(x)] for x in sources[t[ok]]]
        length[ok] = dist[t[ok]] + d_t[ok]
        return out, length, snapped

    def path(self, tr, node):
        """Knotenfolge Station -> node."""
        out = [node]
        while out[-1] != tr['s']:
            out.append(int(tr['pred'][out[-1]]))
        return out[::-1]

    def contract(self, tr, targets):
        """Baum über die Zielknoten, Ketten ohne Abzweig zusammengefasst.

        Gibt (Segmente, Ast je Knoten) zurück; Segment = (Elternknoten, Knoten, Koordinaten, Länge).
        """
        parent = {}
        for t in set(targets):
            node = t
            while node != tr['s'] and node not in parent:
                parent[node] = int(tr['pred'][node])
                node = parent[node]
        children = {}
        for c, p in parent.items():
            children.setdefault(p, []).append(c)
        keep = {tr['s']} | set(targets) | {n for n, ch in children.items() if len(ch) > 1}
        segs, branch = [], {}
        for k in keep - {tr['s']}:
            chain = [k]
            while chain[-1] not in keep or chain[-1] == k:
                chain.append(parent[chain[-1]])
                if chain[-1] in keep:
                    break
            chain = chain[::-1]
            pts = self.xy[chain]
            segs.append((chain[0], k, pts, float(np.hypot(*np.diff(pts, axis=0).T).sum())))
        up = {k: p for p, k, _, _ in segs}
        for k in up:
            node = k
            while up[node] != tr['s']:
                node = up[node]
            branch[k] = node
        return segs, branch
