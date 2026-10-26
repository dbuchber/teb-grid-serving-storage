"""Zuteilung von Wärmepumpen und E-Autos, Wärmepumpenlast je Station, E-Auto-Ladeereignisse.

Modellannahmen wie ``steyr_wp_ev.py`` (eingefroren), aber vektorisiert: E-Autos als Ladeereignisse
(Ankunft, Energie, Leistung), damit die Ladesteuerung (control.py) nur die Startzeit verschiebt.
"""
from dataclasses import dataclass

import numpy as np
from scipy import sparse

from gridsim import legacy

wpev = legacy.load('steyr_wp_ev')
HOURS = 8760
DAYS = HOURS // 24
DEADLINE_H = 7  # Ladeende spätestens am Folgetag 7 Uhr (gesteuertes Laden, WiNAP)
# Szenarien der eingefrorenen Skripte plus ein mittleres 2040: Wärmepumpen wie 2030 (35 %), E-Autos wie 2040.
# 2040 (70 %) ist der Stressfall für Klimaneutralität; 35 % liegt näher an UBA-WAM und TU-Wien-Szenarien.
# heute aus dem Ist-Abgleich (Owner, Fix-Runde 2, 25.10.2026; Quellen in docs/gridsim-leitungen-abnahme.md):
# E-Autos 0,076 je Haushalt = Elektro-Pkw OÖ 51 343 (31.12.2025) / 672 647 Privathaushalte OÖ 2025;
# Wärmepumpen: OÖ 2023/24 21,4 % der Hauptwohnsitze („Solar, Wärmepumpen“ 142 397 von 666 900). Im Modell zieht
# assign je Wohngebäude; wp_share 0,23 ergibt 21,4 % der Haushalte (Steyr: weniger Fernwärme, mehr Haushalte in
# Mehrfamilienhäusern). Die eingefrorenen Werte in legacy (0,15 / 0,08) bleiben unverändert.
SCENARIOS = {**wpev.SCENARIOS, 'heute': {'wp_share': 0.23, 'ev_share': 0.076},
             '2040m': {'wp_share': 0.35, 'ev_share': 0.60},
             # 2040r (Owner, 25.10.2026): Hauptergebnis 2040; WP 50 % (AIT-Szenarien 48–57 %), E-Autos wie 2040.
             # 2040 (70 %) bleibt als Stresstest (docs/research/2026-10-25-szenarioanteile-wp-ev.md im Hauptrepo).
             '2040r': {'wp_share': 0.50, 'ev_share': 0.60}}


@dataclass
class EvEvents:
    node: np.ndarray        # (M,) Knoten des Autos
    station: np.ndarray     # (M,) Station des Knotens
    arrive_h: np.ndarray    # (M,) Stunde im Jahr, ab der geladen werden kann
    kwh_grid: np.ndarray    # (M,) Energie aus dem Netz inkl. Ladeverlust
    kw: np.ndarray          # (M,) Ladeleistung der Wallbox
    deadline_h: np.ndarray  # (M,) Folgetag 7 Uhr

    def __len__(self):
        return len(self.node)


def assign(p, scenario, rng):
    """Jahreswärme (kWh_th) und Anzahl E-Autos je Knoten wie ``steyr_wp_ev.assign``, LoD1-Wärme wo vorhanden."""
    share = SCENARIOS[scenario]
    hh = np.asarray(p.nodes_hh, dtype=int)
    fw = np.asarray(p.nodes_fw, dtype=bool)
    homes = hh > 0
    fw_frac = fw[homes].mean() if homes.any() else 0.0
    # dieselbe Formel steht in feeders/prepare.design_loads (Bemessung, DesignRule.wp_share); bei Änderung dort
    # nachziehen, Test: tests/test_feeders_prepare.py::test_design_rule_uses_same_p_wp_as_assign
    p_wp = min(1.0, share['wp_share'] / max(1 - fw_frac, 1e-9))
    has_wp = homes & ~fw & (rng.random(len(hh)) < p_wp)
    pauschal = np.where(hh == 1, wpev.HEAT_KWH_EFH, wpev.HEAT_KWH_MFH_HH * hh).astype(float)
    lod1 = np.asarray(p.nodes_heat_kwh, dtype=float)
    heat = np.where(has_wp, np.where(np.isnan(lod1), pauschal, lod1), 0.0)
    cars = np.where(homes, rng.binomial(np.maximum(hh, 0), share['ev_share']), 0)
    return heat, cars


def _onehot(p, columns=None):
    st = np.asarray(p.nodes_station)
    if columns is not None:
        st = st[columns]
    return sparse.csr_matrix((np.ones(len(st), dtype=np.float32), (np.arange(len(st)), st)),
                             shape=(len(st), p.n_stations))


def station_sum(values_by_node, p):
    """(8760, N) je Knoten → (8760, S) je Station."""
    return np.asarray(sparse.csr_matrix(values_by_node) @ _onehot(p) if sparse.issparse(values_by_node)
                      else values_by_node @ _onehot(p), dtype=np.float32)


def heat_pump_kw(temp_c, e, limits, shifts, share):
    """Wie ``steyr_wp_ev.heat_pump_kw`` (gleiche Formeln), in float32 und mit Zeitversatz je Versatzgruppe.

    Die Schleife je Station ist speicherbandbreitengebunden; float32 und ``np.roll`` statt Fancy-Indexing
    halbieren die bewegten Daten.
    """
    f = np.float32
    e, limits, share = e.astype(f), limits.astype(f), share.astype(f)
    t_eff = wpev.effective_temp(np.asarray(temp_c, dtype=float)).astype(f)
    degree = np.maximum(limits[None, :] - t_eff[:, None], f(0))
    dsum = np.maximum(degree.sum(axis=0), f(1e-9))
    dhw = (np.tile(wpev.DHW_PROFILE, HOURS // 24) / (HOURS // 24)).astype(f)
    space = degree * ((1 - share) * e / dsum)[None, :]
    water = dhw[:, None] * (share * e)[None, :]
    q_max = ((1 - share) * np.maximum(limits - f(wpev.BIVALENT_C), 0) / dsum + share * f(dhw.max())) * e
    heat = space + water
    hp_share = np.minimum(heat, q_max[None, :])
    np.divide(hp_share, heat, out=hp_share, where=heat > 0)
    hp_share[heat <= 0] = 1
    cop_s = wpev.cop(t_eff.astype(float)).astype(f)
    cop_w = wpev.cop(t_eff.astype(float), wpev.COP_DHW).astype(f)
    el = hp_share * (space / cop_s[:, None] + water / cop_w[:, None]) + (1 - hp_share) * heat
    shifts = np.asarray(shifts)
    for s in np.unique(shifts):
        if s:
            cols = np.flatnonzero(shifts == s)
            el[:, cols] = np.roll(el[:, cols], int(s), axis=0)
    return el


def heat_pump(p, heat_kwh, seed):
    """Wärmepumpenlast (kW): Stationssumme (8760, S) und Matrix der Speicherknoten (8760, K).

    Zellenweise wie ``heat_pump_kw_cells`` mit Streuung ``spread(N, seed)``; jede Zelle wird sofort auf
    Stationen verdichtet, damit keine volle Knotenmatrix im Speicher liegt.
    """
    heat = np.asarray(heat_kwh, dtype=float)
    limits, shifts = wpev.spread(len(heat), seed)
    dhw = np.asarray(p.nodes_dhw, dtype=float)
    dhw = np.where(np.isnan(dhw), wpev.DHW_SHARE, dhw)
    cells = np.asarray(p.nodes_cell)
    temp = np.asarray(p.temp_cells, dtype=float)
    storage_idx = np.flatnonzero(np.asarray(p.nodes_kwh) > 0)
    pos = {n: k for k, n in enumerate(storage_idx)}
    st_sum = np.zeros((HOURS, p.n_stations), dtype=np.float32)
    storage = np.zeros((HOURS, len(storage_idx)), dtype=np.float32)
    for c in np.unique(cells[heat > 0]):
        idx = np.flatnonzero((cells == c) & (heat > 0))
        el = heat_pump_kw(temp[:, c], heat[idx], limits[idx], shifts[idx], dhw[idx])
        st_sum += np.asarray(el @ _onehot(p, idx), dtype=np.float32)
        for j, n in enumerate(idx):
            if n in pos:
                storage[:, pos[n]] = el[:, j]
    return st_sum, storage


def ev_events(p, cars, rng):
    """Ladeereignisse aller E-Autos; Schleife über Tage, vektorisiert über Autos."""
    cars = np.asarray(cars, dtype=int)
    node = np.repeat(np.arange(len(cars)), cars).astype(np.int32)
    m = len(node)
    t_day = np.asarray(p.temp_cells, dtype=float).mean(axis=1)[:DAYS * 24].reshape(DAYS, 24).mean(axis=1)
    kwh_day = wpev.KM_PER_YEAR / 365 * wpev.KWH_PER_KM * (1 + wpev.COLD_PER_K * np.maximum(15 - t_day, 0))
    weekend = (np.arange(DAYS) + p.first_weekday) % 7 >= 5
    kw = np.where(rng.random(m) < wpev.EV_FAST_SHARE, wpev.EV_KW_FAST, wpev.EV_KW_SLOW).astype(np.float32)
    need = rng.uniform(0, wpev.EV_CHARGE_KWH, m)  # Startzustand streuen
    out_car, out_h, out_kwh = [], [], []
    for d in range(DAYS):
        need += kwh_day[d] * rng.uniform(0.5, 1.5, m)
        go = np.flatnonzero(need >= wpev.EV_CHARGE_KWH)
        if not len(go):
            continue
        mu, sd = wpev.ARRIVAL_WEEKEND if weekend[d] else wpev.ARRIVAL_WEEKDAY
        hour = np.clip(rng.normal(mu, sd, len(go)), 12, 23).astype(int)
        out_car.append(go)
        out_h.append(d * 24 + hour)
        out_kwh.append(need[go] / wpev.EV_ETA)
        need[go] = 0.0
    car = np.concatenate(out_car) if out_car else np.zeros(0, dtype=int)
    arrive = np.concatenate(out_h).astype(np.int32) if out_h else np.zeros(0, dtype=np.int32)
    kwh = np.concatenate(out_kwh).astype(np.float32) if out_kwh else np.zeros(0, dtype=np.float32)
    n = node[car]
    return EvEvents(node=n, station=np.asarray(p.nodes_station)[n].astype(np.int32), arrive_h=arrive, kwh_grid=kwh,
                    kw=kw[car], deadline_h=((arrive // 24 + 1) * 24 + DEADLINE_H).astype(np.int32))
