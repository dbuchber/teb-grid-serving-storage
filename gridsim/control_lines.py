"""Gesteuertes Laden, V2G und T3d gegen Trafo **und** Leitungsgrenzen (Spec 4.5, Grenzmodus ``trafo+leitung``).

Grenze je Abschnitt in kW: i_max · √3 · 0,4 kV · cos φ, cos φ 0,97 in Bezugsrichtung und 1,0 in
Einspeiserichtung (wie ``loading.loading_pct``). Grundlage ist der Abschnittsfluss mit Spitzenzuschlag der
Haushaltslast (``loading.segment_flow``), also genau die Auslastung, die die Leitungskennzahlen zeigen; der Trafo
wird wie in ``control`` ohne Zuschlag gegen ``kva`` bewertet.

- **Gesteuertes Laden** (``controlled_lines``): je Stunde Bedarf je Knoten = eigener Ladewunsch + eigener Rückstau.
  Die Abschnitte werden von den Blättern zur Sammelschiene abgearbeitet (Tiefenstufe für Tiefenstufe; Abschnitte
  einer Stufe liegen disjunkt und werden zusammen gerechnet): Faktor = min(1, Raum / Summe des bisher
  zugeteilten Bedarfs dahinter), angewandt auf alle Knoten dahinter; zuletzt derselbe Schritt am Trafo. Raum =
  max(Grenze − ungesteuerter Fluss, 0), daher nie negatives Laden; liegt der Grundfluss schon über einer Grenze,
  laden die Knoten dahinter nicht. Rückstau verfällt um 7 Uhr in ``unmet`` wie in ``control.controlled``.
  Sind alle Abschnitte weit, ergibt die Stationssumme genau ``control.controlled``.
- **V2G** (``v2g_lines``): je Stunde mit Überlast wird die Überlast jedes Abschnitts von den Blättern zur Wurzel
  nur mit Rückspeisung der Autos dahinter gedeckt (anteilig nach noch verfügbarer Leistung), zuletzt die des
  Trafos mit allen Autos. Leistung ``V2G_KW·V2G_AVAIL`` je Auto, Energie ``V2G_KWH·V2G_AVAIL`` je Auto und Abend
  (Fenster ab 12 Uhr wie ``control.v2g``). Die Rückspeisung darf keinen Abschnitt und nicht den Trafo über die
  Grenze in Einspeiserichtung drücken. Nachladen bis 7 Uhr je Knoten höchstens mit ``V2G_KW·V2G_AVAIL`` je Auto und
  nur im Raum aller Abschnitte des Pfads und des Trafos; Rest in ``unmet``.
- **T3d** (``signal_lines``): Signaltag, wenn im Fenster ``control.SIGNAL_WINDOW`` der Trafo **oder** ein Abschnitt
  in Bezugsrichtung über der Grenze liegt; Prognose wie ``control.start_t3d_forecast`` (Grundfluss + WiNAP).
- ``uncontrolled`` und ``winap`` folgen keinem Netzsignal und sind in beiden Grenzmodi gleich.
- Heimspeicher (Strategien ``base``/``forecast``/``room``) bleiben in beiden Modi unverändert: gridsim hat keine
  Abruflogik für Heimspeicher; Abrufe je Abgang setzt der Netzspeicher um (Task 9).

Laufzeit: Die Stundenschleife ist wegen des Rückstaus nötig, läuft aber nur über Stunden, in denen eine Grenze
greift oder Rückstau besteht; alle übrigen Stunden werden vektoriert über das ganze Jahr geprüft. Innerhalb einer
Stunde ist über die Abschnitte einer Tiefenstufe vektoriert (CSR-Matrix ``downstream``).
"""
from dataclasses import replace

import numpy as np
from scipy import sparse

from gridsim import control
from gridsim.feeders.loading import _K_KW_PER_A, _columns, segment_flow
from gridsim.feeders.sizing import COS_LOAD
from gridsim.nodeflow import _ev_nodes, base_block

DAYS = control.DAYS
_EPS_KW = 1e-3   # Trafo-Überlast darunter (1 W) ist Rundung: gesteuertes Laden füllt den Raum genau bis ``kva``
# Abstand zur Abschnittsgrenze (relativ): Laden/Nachladen füllen bis 99,999 %, V2G deckt bis dorthin. Die
# Kennzahlen rechnen den Abschnittsfluss in float32; ohne Abstand ergäbe ein genau gefüllter Raum Rundungswerte
# knapp über 100 % und damit Scheinüberlast, die erst die Steuerung erzeugt.
_MARGIN = 1e-5


def limit_kw(sized):
    """Grenzleistung je Abschnitt in kW: (Bezug mit cos φ 0,97, Einspeisung mit cos φ 1,0)."""
    i_a = np.asarray(sized.i_max_a, dtype=float)
    return i_a * _K_KW_PER_A * COS_LOAD, i_a * _K_KW_PER_A


def room(seg_flow0, sized, kva, station_flow0):
    """Freier Raum (kW, ≥ 0) für zusätzlichen Bezug: je Abschnitt (8760, m) und am Trafo (8760,).

    Raum = max(Grenze in Bezugsrichtung · (1 − 10⁻⁵) − ungesteuerter Fluss, 0) (Abstand siehe ``_MARGIN``); bei
    Einspeisung (Fluss < 0) ist der Raum größer als die Grenze, weil zusätzlicher Bezug die Einspeisung erst
    aufzehrt. Am Trafo ohne Abstand wie ``control.controlled``.
    """
    load_kw, _ = limit_kw(sized)
    seg_room = np.maximum(load_kw[None, :] * (1.0 - _MARGIN) - np.asarray(seg_flow0, dtype=float), 0.0)
    trafo_room = np.maximum(float(kva) - np.asarray(station_flow0, dtype=float), 0.0)
    return seg_room, trafo_room


class _Tree:
    """``downstream`` in Spaltenreihenfolge des Knotenblocks, gruppiert nach Tiefenstufen (Blätter zuerst)."""

    def __init__(self, grid, block):
        d = grid.downstream.tocsr().astype(np.float64)
        pos = _columns(grid, block)
        n = len(block.nodes)
        if pos is not None or d.shape[1] != n:
            cols = d.indices if pos is None else pos[d.indices]
            d = sparse.csr_matrix((d.data, cols, d.indptr), shape=(d.shape[0], n))
        self.d = d
        parent = np.asarray(grid.parent)
        depth = np.zeros(len(parent), dtype=int)
        for j, q in enumerate(parent):          # Eltern stehen vor den Kindern
            if q >= 0:
                depth[j] = depth[q] + 1
        self.levels = []
        for k in range(int(depth.max()) if len(depth) else -1, -1, -1):
            rows = np.flatnonzero(depth == k)
            dl = d[rows]
            self.levels.append((rows, dl, dl.T.tocsr()))

    def flows(self, x):
        """Abschnittssummen (8760, m) einer Knotenmatrix (8760, n)."""
        return np.asarray((self.d @ np.asarray(x, dtype=float).T).T)

    def cap(self, alloc, seg_room, trafo_room):
        """Kürzt ``alloc`` (≥ 0) von den Blättern zur Wurzel, bis kein Abschnitt und nicht der Trafo über dem Raum liegt."""
        for rows, dl, dlt in self.levels:
            s = dl @ alloc
            r = seg_room[rows]
            over = s > r
            if over.any():
                fac = np.zeros(len(rows))
                fac[over] = r[over] / s[over] - 1.0
                alloc = alloc * np.maximum(1.0 + dlt @ fac, 0.0)
        tot = alloc.sum()
        if tot > trafo_room:
            alloc = alloc * (trafo_room / tot)
        return alloc

    def cover(self, need_seg, need_trafo, avail):
        """Rückspeisung je Knoten (≤ ``avail``), die die Überlast jedes Abschnitts nur mit Knoten dahinter deckt."""
        d = np.zeros_like(avail)
        for rows, dl, dlt in self.levels:
            need = need_seg[rows] - dl @ d
            pos = need > 0
            if pos.any():
                free = avail - d
                extra = dl @ free
                ok = pos & (extra > 0)
                take = np.zeros(len(rows))
                take[ok] = np.minimum(need[ok], extra[ok]) / extra[ok]
                d = d + free * (dlt @ take)
        need = need_trafo - d.sum()
        if need > 0:
            free = avail - d
            extra = free.sum()
            if extra > 0:
                d = d + free * (min(need, extra) / extra)
        return d


def _next(hours, h):
    """Nächste Stunde aus ``hours`` (sortiert) nach ``h``; ``len`` = keine mehr."""
    i = np.searchsorted(hours, h, side='right')
    return int(hours[i]) if i < len(hours) else control.HOURS


def _serve(tree, ev, seg_room, trafo_room):
    """Laden je Knoten und Stunde unter dem Raum, Rückstau bis 7 Uhr; (Laden, ungeladen je Knoten und Tag)."""
    n_h, n = ev.shape
    out = ev.copy()
    unmet = np.zeros((n, DAYS + 1))
    fits = (tree.flows(ev) <= seg_room).all(axis=1) & (ev.sum(axis=1) <= trafo_room)
    bad = np.flatnonzero(~fits)
    backlog = np.zeros(n)
    h = int(bad[0]) if len(bad) else n_h
    while h < n_h:
        want = ev[h] + backlog
        serve = tree.cap(want, seg_room[h], trafo_room[h])
        out[h] = serve
        backlog = want - serve
        if h % 24 == control.DEADLINE_H:
            unmet[:, h // 24] = backlog
            backlog = np.zeros(n)
        h = h + 1 if backlog.any() else _next(bad, h)
    return out, unmet[:, :DAYS]


def controlled_lines(block0, ev_want, grid, sized, kva, station_flow0=None):
    """Gesteuertes Laden je Knoten gegen alle Abschnitte und den Trafo (Moduldoku).

    ``block0``: Knotenblock ohne E-Auto (``nodeflow.base_block``); ``ev_want`` (8760, n) ungesteuerte Ladelast in
    dessen Spaltenreihenfolge; ``station_flow0``: Stationsfluss ohne E-Auto (Default: Summe der Knoten).
    Gibt (Laden (8760, n), ungeladene Energie (n, 365)) zurück.
    """
    ev = np.asarray(ev_want, dtype=float)
    tree = _Tree(grid, block0)
    seg0 = segment_flow(grid, sized, block0).astype(float)
    st0 = block0.net().sum(axis=1, dtype=np.float64) if station_flow0 is None else station_flow0
    seg_room, trafo_room = room(seg0, sized, kva, st0)
    return _serve(tree, ev, seg_room, trafo_room)


def v2g_lines(block, cars_node, grid, sized, kva, station_flow=None):
    """V2G je Knoten gegen Überlast der Abschnitte und des Trafos, mit Nachladen bis 7 Uhr (Moduldoku).

    ``block``: Knotenblock mit gesteuertem Laden; ``cars_node`` (n,) Autos je Knoten in dessen Spaltenreihenfolge;
    ``station_flow``: Stationsfluss mit Laden (Default: Summe der Knoten).
    Gibt (Rückspeisung, Nachladen, nicht nachgeladene Energie je Knoten und Tag (n, 365)) zurück.
    """
    tree = _Tree(grid, block)
    seg = segment_flow(grid, sized, block).astype(float)
    st = block.net().sum(axis=1, dtype=np.float64) if station_flow is None else np.asarray(station_flow, float)
    load_kw, feed_kw = limit_kw(sized)
    kva = float(kva)
    target = load_kw * (1.0 - _MARGIN)
    over_seg = np.where(seg > load_kw[None, :], seg - target[None, :], 0.0)   # nur echte Überlast, Deckung bis target
    over_tr = st - kva
    over_tr[over_tr < _EPS_KW] = 0.0
    cars = np.asarray(cars_node, dtype=float)
    p_cap = control.V2G_KW * control.V2G_AVAIL * cars
    e_cap = control.V2G_KWH * control.V2G_AVAIL * cars
    n_h, n = seg.shape[0], len(cars)
    out = np.zeros((n_h, n))
    hours = np.flatnonzero(over_seg.any(axis=1) | (over_tr > 0)) if cars.sum() > 0 else []
    left, window = e_cap.copy(), None
    for h in hours:
        w = (h - control.V2G_WINDOW_START_H) // 24
        if w != window:
            left, window = e_cap.copy(), w
        d = tree.cover(over_seg[h], over_tr[h], np.minimum(p_cap, left))
        d = tree.cap(d, np.maximum(seg[h] + feed_kw * (1.0 - _MARGIN), 0.0), max(st[h] + kva, 0.0))
        out[h] = d
        left = left - d

    recharge = np.zeros_like(out)
    unmet = np.zeros((n, DAYS + 1))
    seg_room = np.maximum(target[None, :] - seg + tree.flows(out), 0.0)
    trafo_room = np.maximum(kva - st + out.sum(axis=1), 0.0)
    dis = np.flatnonzero(out.sum(axis=1) > 0)
    backlog = np.zeros(n)
    h = int(dis[0]) if len(dis) else n_h
    while h < n_h:
        want = np.minimum(backlog, p_cap)
        if want.any():
            recharge[h] = tree.cap(want, seg_room[h], trafo_room[h])
        backlog = backlog - recharge[h] + out[h]
        if h % 24 == control.DEADLINE_H:
            unmet[:, h // 24] = backlog
            backlog = np.zeros(n)
        h = h + 1 if backlog.any() else _next(dis, h)
    return out, recharge, unmet[:, :DAYS]


def signal_lines(seg_flow, sized, station_flow, kva):
    """T3d-Signal (365,) bool: Tag d, wenn zwischen d 16 Uhr und d+1 8 Uhr Trafo oder ein Abschnitt (Bezug) über der Grenze."""
    load_kw, _ = limit_kw(sized)
    over = (np.asarray(seg_flow) > load_kw[None, :]).any(axis=1) | (np.asarray(station_flow) > float(kva))
    return control.engpass_signal(over[:, None].astype(float), [0.5])[0]   # 1 > 0,5 ⇔ über der Grenze


# --- Anwendung im Lauf (run.flows) ------------------------------------------------------------------------------------

def start_t3d(p, params, part, ev, base, feeders):
    """T3d-Startzeiten mit Signal je Station aus Trafo und Abschnitten (Stationen ohne Netz: nur Trafo)."""
    win = control.start_winap(ev, p.year)
    forecast = np.asarray(base, dtype=float) + control.render(ev, win, p.n_stations)
    signal = control.engpass_signal(forecast, p.kva)
    for s, (grid, sized) in feeders.items():
        block0 = base_block(p, params, part, s)
        ev_n = _ev_nodes(ev, win, s, block0.nodes)
        seg = segment_flow(grid, sized, replace(block0, ev_kw=ev_n))
        signal[s] = signal_lines(seg, sized, forecast[:, s], p.kva[s])
    return control.start_t3d(ev, signal, p.year)


def apply(p, params, part, ev, start, base, feeders):
    """Gesteuertes Laden/V2G aller Stationen im Grenzmodus ``trafo+leitung``.

    Stationen ohne Netz rechnen wie im Modus ``trafo``. Gibt (Laden je Station, V2G netto je Station, ungeladene
    Energie je Station und Tag, Knotenentscheidungen {s: (Laden, V2G netto) als csr float32}) zurück.
    """
    kva = np.asarray(p.kva, dtype=float)
    ev_load, unmet = control.controlled(base, control.render(ev, start, p.n_stations), kva)
    v2g = np.zeros_like(ev_load)
    if params.charging == 'v2g':
        cars_st = np.bincount(np.asarray(p.nodes_station), weights=part['cars'], minlength=p.n_stations)
        out, recharge, unmet_v2g = control.v2g_with_recharge(base, ev_load, kva, cars_st)
        v2g, unmet = out - recharge, unmet + unmet_v2g
    base = np.asarray(base, dtype=float)
    decisions = {}
    for s, (grid, sized) in feeders.items():
        block0 = base_block(p, params, part, s)
        ev_n = _ev_nodes(ev, start, s, block0.nodes)
        charge, unmet_n = controlled_lines(block0, ev_n, grid, sized, kva[s], station_flow0=base[:, s])
        ev_load[:, s], unmet[s] = charge.sum(axis=1), unmet_n.sum(axis=0)
        net = np.zeros_like(charge)
        if params.charging == 'v2g':
            block = replace(block0, ev_kw=charge.astype(np.float32))
            cars = np.asarray(part['cars'], dtype=float)[block0.nodes]
            out, recharge, unmet_v = v2g_lines(block, cars, grid, sized, kva[s], station_flow=base[:, s] + ev_load[:, s])
            net = out - recharge
            v2g[:, s] = net.sum(axis=1)
            unmet[s] += unmet_v.sum(axis=0)
        decisions[s] = (sparse.csr_matrix(charge.astype(np.float32)), sparse.csr_matrix(net.astype(np.float32)))
    return ev_load, v2g, unmet, decisions
