"""Querschnittswahl nach Planungsregel (Spec 4.3): Grenzstrom und Spannungsfall im Auslegungsfall „heute“.

Hausanschlüsse sind fest (``SERVICE``). Jeder Trunk-Abschnitt bekommt zuerst den kleinsten Typ der Liste (Kabel
oder Freileitung nach ``overhead``), der den Auslegungsstrom trägt. Danach wird je Abgang der Spannungsfall vom
Trafo bis zum entferntesten Knoten geprüft (Σ (R·P + X·Q) / U² auf dem Pfad, Bezug ≤ 5 %, Einspeisung ≤ 3 %); bei
Verletzung wird der Abschnitt des schlechtesten Pfads mit dem größten Beitrag eine Typstufe hochgesetzt, über dem
größten Typ ``parallel = 2``. Hilft auch das nicht, wird der Abgang in ``SizedGrid.marked`` vermerkt.

Alle Leistungen in kW, Spannungsfälle in Prozent der Nennspannung, R/X je Abschnitt in Ω (Länge und
Parallelführung eingerechnet).
"""
from dataclasses import dataclass

import numpy as np

from gridsim.feeders.topology import StationGrid
from gridsim.feeders.types import SERVICE, TRUNK_CABLE, TRUNK_OVERHEAD

P_HH_KW = 2.0                   # Spitzenleistung je Haushalt (Arnold 2019 / Weisenstein 2022, Startwert)
G_INF = 0.07                    # Gleichzeitigkeit für große Kollektive
U_V = 400.0                     # Nennspannung
COS_LOAD = 0.97                 # Verschiebungsfaktor bei Bezug (bei Einspeisung 1,0)
TAN_LOAD = float(np.tan(np.arccos(COS_LOAD)))
DU_LOAD_MAX_PCT = 5.0           # Planungsgrenze Spannungsfall bei Bezug
DU_FEED_MAX_PCT = 3.0           # Planungsgrenze Spannungsanhebung bei Einspeisung
I_LIMIT = 1.0                   # Anteil des thermischen Grenzstroms
MAX_PARALLEL = 2


def g(n: np.ndarray) -> np.ndarray:
    """Gleichzeitigkeitsfaktor g(n) = 0,07 + 0,93·n^(−3/4); n = 0 → 0."""
    n = np.asarray(n, dtype=float)
    safe = np.where(n > 0, n, 1.0)
    return np.where(n > 0, G_INF + (1.0 - G_INF) * safe ** -0.75, 0.0)


def p_ev(n_cars: np.ndarray) -> np.ndarray:
    """Gleichzeitige Ladeleistung je Auto in kW (Maier/Groiß 2026): 0,53 + 10,47·n^(−1,264); n = 0 → 0.

    Ergibt 11 kW bei n = 1, 1,1 kW bei n = 10 und etwa 0,54 kW bei n = 224. ``n_cars`` darf Gleitkomma sein.
    """
    n = np.asarray(n_cars, dtype=float)
    safe = np.where(n > 0, n, 1.0)
    return np.where(n > 0, 0.53 + 10.47 * safe ** -1.264, 0.0)


def design_flows(grid: StationGrid, hh, wp_kw_exp, cars_exp, kwp_peak_kw) -> tuple[np.ndarray, np.ndarray]:
    """Auslegungsbezug und -einspeisung je Abschnitt in kW.

    Die vier Eingaben liegen je Station in ``grid.node_index``-Reihenfolge (Länge n) vor. Bezug eines
    Abschnitts = P_HH·g(n_hh)·n_hh + Σ Wärmepumpen (Erwartungswert) + n_cars·p_ev(n_cars) über die Knoten hinter
    dem Abschnitt. Ein erwartetes Auto unter 1 wird mit p_ev(1) gerechnet, damit es nie über 11 kW kommt.
    Einspeisung = Σ Spitzenleistung der Anlagen hinter dem Abschnitt.
    """
    d = grid.downstream.astype(float)
    n_hh = d @ np.asarray(hh, dtype=float)
    n_cars = d @ np.asarray(cars_exp, dtype=float)
    p_wp = d @ np.asarray(wp_kw_exp, dtype=float)
    p_feed = d @ np.asarray(kwp_peak_kw, dtype=float)
    p_load = P_HH_KW * g(n_hh) * n_hh + p_wp + n_cars * p_ev(np.maximum(n_cars, 1.0))
    return p_load, p_feed


@dataclass
class SizedGrid:
    types: list           # Typname je Abschnitt
    parallel: np.ndarray  # (m,) int8, parallele Systeme je Abschnitt (1 oder 2)
    i_max_a: np.ndarray   # (m,) Grenzstrom des Abschnitts einschließlich Parallelführung
    r_ohm: np.ndarray     # (m,) Widerstand des Abschnitts in Ω
    x_ohm: np.ndarray     # (m,) Reaktanz des Abschnitts in Ω
    du_load_pct: np.ndarray  # (n_feeder,) größter Spannungsfall je Abgang bei Auslegungsbezug
    du_feed_pct: np.ndarray  # (n_feeder,) größte Spannungsanhebung je Abgang bei Auslegungseinspeisung
    marked: np.ndarray    # (n_feeder,) bool, Abgang hält die Planungsregel auch ausgereizt nicht ein


def _current_a(p_load_kw, p_feed_kw):
    """Auslegungsstrom: Bezug mit cos φ 0,97, Einspeisung mit 1,0; maßgebend ist der größere."""
    k = np.sqrt(3.0) * U_V / 1000.0
    return np.maximum(p_load_kw / (k * COS_LOAD), p_feed_kw / k)


def _drop_pct(r_ohm, x_ohm, p_load_kw, p_feed_kw):
    """Spannungsfall je Abschnitt in Prozent (Bezug, Einspeisung): 100·(R·P + X·Q)/U²."""
    p_l = np.asarray(p_load_kw, dtype=float) * 1000.0
    p_f = np.asarray(p_feed_kw, dtype=float) * 1000.0
    du_l = 100.0 * (r_ohm * p_l + x_ohm * p_l * TAN_LOAD) / U_V ** 2
    du_f = 100.0 * (r_ohm * p_f) / U_V ** 2
    return du_l, du_f


def size(grid: StationGrid, p_load, p_feed) -> SizedGrid:
    """Querschnitte je Abschnitt nach Grenzstrom und Spannungsfall (siehe Moduldoku).

    ``p_load``/``p_feed`` in kW je Abschnitt (aus ``design_flows``). ``marked`` enthält nur Abgänge, für die die
    Bemessung scheitert; die Topologie-Markierung bleibt in ``grid.marked``.
    """
    p_load = np.asarray(p_load, dtype=float)
    p_feed = np.asarray(p_feed, dtype=float)
    m = len(grid.parent)
    n_feeder = len(grid.marked)
    marked = np.zeros(n_feeder, bool)
    feeder = grid.feeder.astype(int)
    trunk = ~grid.service
    lists = [TRUNK_OVERHEAD if o else TRUNK_CABLE for o in grid.overhead]

    # Typstufe je Abschnitt (-1 = Hausanschluss), Parallelführung
    step = np.full(m, -1, int)
    parallel = np.ones(m, int)
    cur = _current_a(p_load, p_feed)
    for j in np.flatnonzero(trunk):
        lst = lists[j]
        ok = [k for k, t in enumerate(lst) if t.i_max_a * I_LIMIT >= cur[j]]
        if ok:
            step[j] = ok[0]
        else:
            step[j], parallel[j] = len(lst) - 1, MAX_PARALLEL
            if lst[-1].i_max_a * MAX_PARALLEL * I_LIMIT < cur[j]:
                marked[feeder[j]] = True

    def line_type(j):
        return SERVICE[bool(grid.overhead[j])] if step[j] < 0 else lists[j][step[j]]

    def impedance():
        r, x = np.zeros(m), np.zeros(m)
        for j in range(m):
            t = line_type(j)
            km = float(grid.length_m[j]) / 1000.0
            r[j], x[j] = t.r_ohm_km * km / parallel[j], t.x_ohm_km * km / parallel[j]
        return r, x

    d = grid.downstream.tocsr()
    n = d.shape[1]
    node_feeder = np.full(n, -1)
    path = [d[j].indices for j in range(m)]          # Knoten hinter Abschnitt j
    for j in range(m):
        node_feeder[path[j]] = feeder[j]
    dt = d.T.astype(float).tocsr()                   # (n, m): Abschnitte auf dem Pfad des Knotens

    def node_drops(du_seg_l, du_seg_f):
        return dt @ du_seg_l, dt @ du_seg_f

    # Spannungsfall: je Abgang den schlechtesten Pfad verbessern, bis Grenze erfüllt oder nichts mehr hochsetzbar
    done = marked.copy()
    for _ in range(4 * m + 1):
        r_ohm, x_ohm = impedance()
        du_l, du_f = _drop_pct(r_ohm, x_ohm, p_load, p_feed)
        nd_l, nd_f = node_drops(du_l, du_f)
        changed = False
        for f in range(n_feeder):
            if done[f]:
                continue
            nodes = np.flatnonzero(node_feeder == f)
            if not len(nodes):
                continue
            ratio_l, ratio_f = nd_l[nodes] / DU_LOAD_MAX_PCT, nd_f[nodes] / DU_FEED_MAX_PCT
            k = int(np.argmax(np.maximum(ratio_l, ratio_f)))
            if max(ratio_l[k], ratio_f[k]) <= 1.0 + 1e-9:
                done[f] = True
                continue
            seg_du = du_l if ratio_l[k] >= ratio_f[k] else du_f
            on_path = dt[nodes[k]].indices
            cand = [j for j in on_path if trunk[j] and not (step[j] == len(lists[j]) - 1 and parallel[j] == MAX_PARALLEL)]
            if not cand:
                marked[f] = done[f] = True
                continue
            j = max(cand, key=lambda c: (seg_du[c], -c))
            if step[j] < len(lists[j]) - 1:
                step[j] += 1
            else:
                parallel[j] = MAX_PARALLEL
            changed = True
        if not changed:
            break

    r_ohm, x_ohm = impedance()
    du_l, du_f = _drop_pct(r_ohm, x_ohm, p_load, p_feed)
    nd_l, nd_f = node_drops(du_l, du_f)
    du_load = np.zeros(n_feeder)
    du_feed = np.zeros(n_feeder)
    if n:
        np.maximum.at(du_load, node_feeder[node_feeder >= 0], nd_l[node_feeder >= 0])
        np.maximum.at(du_feed, node_feeder[node_feeder >= 0], nd_f[node_feeder >= 0])
    types = [line_type(j).name for j in range(m)]
    i_max = np.array([line_type(j).i_max_a * parallel[j] for j in range(m)], dtype=float)
    return SizedGrid(types=types, parallel=parallel.astype(np.int8), i_max_a=i_max, r_ohm=r_ohm, x_ohm=x_ohm,
                     du_load_pct=du_load, du_feed_pct=du_feed, marked=marked)
