"""Netzspeicher am Leitungsengpass (Spec 4.6): Speicher des Netzbetreibers, nicht des Kunden.

- **Ort** (``place``): je Abgang mit Überlast (> 100 % Grenzstrom) der Abschnitt mit der höchsten Auslastung;
  der Speicher sitzt am Knoten direkt dahinter. Endet der Abschnitt an einem Abzweig, ist das der Knoten mit dem
  kürzesten Weg ab dem Abschnitt (Knoten = Gebäude, das Modell kennt keine Speicher an Abzweigen). Höchstens ein
  Speicher je Abgang. Sein Fluss wirkt auf alle Abschnitte des Pfads Knoten → Sammelschiene und auf den Trafo.
- **Bemessung** (``size``): ems-konzept § 7.2 (``metrics.segment_row``) auf den Abschnittsfluss in beiden
  Richtungen; Energie = größte installierte Energie der beiden Richtungen, Leistung = größte Überlast, auf 0,1 kW
  aufgerundet und um den Abstand ``_MARGIN`` erhöht, damit der Einsatz die Überlast ganz abbaut.
- **Einsatz** (``dispatch``, + = Laden): tageweise mit perfekter Prognose wie die Strategie ``forecast``.
  Je Stunde ergibt sich aus allen Abschnitten des Pfads ein Band [lo, hi] für die Speicherleistung, in dem kein
  Abschnitt über die Grenze (mit Abstand ``control_lines._MARGIN``) kommt. hi < 0: Bezugsüberlast, Entladen um −hi
  ist Pflicht; lo > 0: Einspeiseüberlast, Laden um lo ist Pflicht (beides begrenzt durch Leistung und
  Ladezustand). In allen anderen Stunden fährt der Speicher innerhalb des Bands auf einen Ziel-Ladezustand:
  vor dem ersten Engpass des Tages auf den Startwert des Tages, zwischen den Engpässen hält er, nach dem letzten
  (und an Tagen ohne Engpass) auf den Startwert des Folgetags. Startwert = 50 % der Kapazität, verschoben so weit
  nötig, dass die Pflichtstunden des Tages (Prognose ohne Grenzen der Kapazität) nicht an 0 oder an der Kapazität
  anstoßen. Ladezustand zu Jahresbeginn 50 %, Wirkungsgrad 0,95 je Richtung wie die Heimspeicher.
- ``plan_station``/``apply`` verbinden das mit dem Lauf (run.py): Bemessung im Auslegungslauf, Einsatz je Seed.
"""
from dataclasses import replace

import numpy as np

from gridsim import metrics
from gridsim.control_lines import _MARGIN, limit_kw
from gridsim.feeders.loading import loading_pct, segment_flow
from gridsim.nodeflow import _ev_nodes, base_block

ETA = 0.95
SOC_START = 0.5
HOURS = 8760


def bottlenecks(grid, loading_pct):
    """(Abgang, Abschnitt) je Abgang mit Überlast: der Abschnitt mit der höchsten Auslastung (``loading_pct`` in %)."""
    mx = np.asarray(loading_pct, dtype=float).max(axis=0)
    feeder = np.asarray(grid.feeder)
    out = []
    for k in np.unique(feeder[mx > metrics.LINE_LIMIT_PCT]):
        segs = np.flatnonzero((feeder == k) & (mx > metrics.LINE_LIMIT_PCT))
        out.append((int(k), int(segs[np.argmax(mx[segs])])))
    return out


def node_behind(grid, j):
    """Lokaler Knoten direkt hinter Abschnitt ``j``: unter den Knoten dahinter der mit dem kürzesten Leitungsweg."""
    d = grid.downstream.tocsr()
    nodes = d[j].indices
    reach = d.T.tocsr()[nodes] @ np.asarray(grid.length_m, dtype=float)
    return int(nodes[np.argmin(reach)])


def path_segments(grid, node):
    """Abschnitte zwischen dem lokalen Knoten ``node`` und der Sammelschiene (aufsteigend)."""
    return np.sort(grid.downstream.tocsc()[:, node].indices)


def place(grid, loading_pct):
    """(Abgang, lokaler Knoten) je Abgang mit Überlast, höchstens einer je Abgang (Moduldoku)."""
    return [(k, node_behind(grid, j)) for k, j in bottlenecks(grid, loading_pct)]


def size(seg_flow_at, limit_kw):
    """(kWh, kW) aus dem Abschnittsfluss (8760,) gegen ``limit_kw`` = (Bezug, Einspeisung); None ohne Überlast."""
    flow = np.asarray(seg_flow_at, dtype=float)
    load_kw, feed_kw = (float(x) for x in limit_kw)
    rows = [r for r in (metrics.segment_row(flow, load_kw), metrics.segment_row(-flow, feed_kw)) if r]
    if not rows:
        return None
    kwh = max(r['e_inst_kwh'] for r in rows)
    need = max(float((flow - load_kw * (1.0 - _MARGIN)).max()), float((-flow - feed_kw * (1.0 - _MARGIN)).max()))
    kw = max(max(r['p_max_kw'] for r in rows), np.ceil(need * 10.0) / 10.0)
    return float(kwh), float(kw)


def _band(seg, limit_kw):
    """Je Stunde (lo, hi): Speicherleistung, mit der kein Abschnitt (Spalten von ``seg``) über seine Grenze kommt."""
    seg = np.asarray(seg, dtype=float)
    if seg.ndim == 1:
        seg = seg[:, None]
    load_kw, feed_kw = (np.broadcast_to(np.asarray(x, dtype=float), seg.shape[1:]) for x in limit_kw)
    hi = (load_kw[None, :] * (1.0 - _MARGIN) - seg).min(axis=1)
    lo = (-feed_kw[None, :] * (1.0 - _MARGIN) - seg).max(axis=1)
    return lo, hi


def _soc_step(x, eta):
    return x * eta if x >= 0 else x / eta


def _day_start(req, kwh, kw, eta):
    """Startwert des Ladezustands je Tag aus den Pflichtstunden ``req`` (8760,) (Moduldoku)."""
    days = len(req) // 24
    x = np.clip(req[:days * 24], -kw, kw).reshape(days, 24)
    step = np.where(x >= 0, x * eta, x / eta)
    cum = np.cumsum(step, axis=1)
    low = np.maximum(0.0, -cum.min(axis=1))
    high = np.minimum(kwh, kwh - cum.max(axis=1))
    s0 = np.where(low <= high, np.clip(SOC_START * kwh, low, high), 0.5 * (low + high))
    return np.clip(s0, 0.0, kwh)


def dispatch(seg_flow_at, limit_kw, kwh, kw, eta=ETA, return_soc=False):
    """Speicherleistung (8760,), + = Laden, gegen den Abschnittsfluss ``seg_flow_at`` (Moduldoku).

    ``seg_flow_at``: (8760,) eines Abschnitts oder (8760, k) aller Abschnitte des Pfads, + = Bezug;
    ``limit_kw`` = (Bezug, Einspeisung) als Zahl oder (k,). ``return_soc``: zusätzlich der Ladezustand (kWh) am
    Ende jeder Stunde.
    """
    lo, hi = _band(seg_flow_at, limit_kw)
    n = len(lo)
    kwh, kw = float(kwh), float(kw)
    must = (hi < 0) | (lo > 0)
    req = np.where(lo > hi, 0.0, np.where(hi < 0, hi, np.where(lo > 0, lo, 0.0)))   # lo > hi: kein Ausweg, nichts tun
    s0 = _day_start(np.where(must, req, 0.0), kwh, kw, eta)
    days = len(s0)
    ev_hours = must.copy()
    ev_hours[lo > hi] = False
    first = np.full(days + 1, 24)
    last = np.full(days + 1, -1)
    hit = np.flatnonzero(ev_hours[:days * 24])
    if len(hit):
        d, hr = hit // 24, hit % 24
        np.minimum.at(first, d, hr)
        np.maximum.at(last, d, hr)
    s0 = np.r_[s0, SOC_START * kwh]
    x = np.zeros(n)
    soc = np.zeros(n)
    s = SOC_START * kwh
    for h in range(n):
        d, hr = divmod(h, 24)
        d = min(d, days)
        if must[h]:
            v = float(np.clip(req[h], -kw, kw))
        else:
            if hr < first[d]:
                target = s0[d]
            elif hr <= last[d]:
                target = s                       # zwischen den Engpässen des Tages halten
            else:
                target = s0[min(d + 1, days)]
            gap = target - s
            v = min(gap / eta, kw, hi[h]) if gap > 0 else max(gap * eta, -kw, lo[h]) if gap < 0 else 0.0
            v = max(v, 0.0) if gap > 0 else min(v, 0.0)
        v = min(v, (kwh - s) / eta) if v > 0 else max(v, -s * eta)
        s = min(max(s + _soc_step(v, eta), 0.0), kwh)
        x[h], soc[h] = v, s
    return (x, soc) if return_soc else x


def plan_station(s, grid, sized, seg):
    """Netzspeicher einer Station aus dem Abschnittsfluss ``seg`` (8760, m) des Auslegungslaufs.

    Liste von {station, feeder, segment, node (lokal), kwh, kw}; Abgänge, deren Überlast die Bemessung nicht als
    Ereignis sieht (Rundung), bekommen keinen Speicher.
    """
    seg = np.asarray(seg, dtype=float)
    load_kw, feed_kw = limit_kw(sized)
    out = []
    for k, j in bottlenecks(grid, loading_pct(seg, sized)):
        sz = size(seg[:, j], (load_kw[j], feed_kw[j]))
        if sz is None:
            continue
        out.append({'station': int(s), 'feeder': int(k), 'segment': int(j), 'node': node_behind(grid, j),
                    'kwh': sz[0], 'kw': sz[1]})
    return out


def apply(p, params, part, plan, feeders, ev=None, start=None):
    """Einsatz aller Netzspeicher eines Seeds: (Leistung (8760, k) float32 je Speicher, globale Knoten (k,)).

    Spalten in Reihenfolge von ``plan`` (nach Station sortiert). Grundlage je Station: Knotenflüsse ohne E-Auto
    (``base_block`` aus ``part``), mit ``ev``/``start`` dazu die E-Auto-Last mit festen Startzeiten. Speicher
    verschiedener Abgänge teilen keine Abschnitte, daher genügt ein Abschnittsfluss je Station.
    """
    kw_out = np.zeros((HOURS, len(plan)), dtype=np.float32)
    idx = np.zeros(len(plan), dtype=np.int64)
    seg_of = {}
    for col, st in enumerate(plan):
        s = st['station']
        grid, sized = feeders[s]
        if s not in seg_of:
            block = base_block(p, params, part, s)
            if start is not None:
                block = replace(block, ev_kw=_ev_nodes(ev, start, s, block.nodes))
            seg_of = {s: segment_flow(grid, sized, block).astype(float)}   # Plan ist nach Station sortiert
        load_kw, feed_kw = limit_kw(sized)
        path = path_segments(grid, st['node'])
        kw_out[:, col] = dispatch(seg_of[s][:, path], (load_kw[path], feed_kw[path]), st['kwh'], st['kw'])
        idx[col] = int(np.asarray(grid.node_index)[st['node']])
    return kw_out, idx
