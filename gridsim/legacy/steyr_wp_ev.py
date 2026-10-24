#!/usr/bin/env python3
"""Stündliche Zusatzlast aus Wärmepumpen und E-Autos je Knoten für die Steyr-Simulation.

Ergänzt steyr_sim_variant_a.py um Lastengpässe (Winterabend). Temperatur aus derselben
PVGIS-Datei wie die PV (Spalte T2m, Wetterjahr 2023), damit PV, Wärmepumpe und E-Auto
dasselbe Wetter sehen. Alternativ je Station aus GeoSphere INCA (1 km, stündlich) für
mehrere Wetterjahre (steyr_weather_fetch.py); dann ist ``temp_c`` eine Matrix (Stunden x
Rasterzellen) und ``cell_of`` ordnet jedem Knoten seine Zelle zu.

Wärmepumpe (Luft/Wasser): Jahreswärmebedarf je Haushalt, Raumwärme proportional zu den
Heizgradstunden unter HEAT_LIMIT_C (Gebäudeträgheit über die gleitende Tagesmitteltemperatur),
Warmwasser mit festem Tagesgang; elektrische Leistung = Wärme / COP(T). Unter BIVALENT_C
deckt die Wärmepumpe nur ihre Leistung am Bivalenzpunkt, den Rest ein Heizstab (COP 1).
Gleichzeitigkeit: je Gebäude streuen Heizgrenze (HEAT_LIMIT_SPREAD) und Zeitversatz
(SHIFT_H); Taktung innerhalb der Stunde ist nicht modelliert.

E-Auto: ungesteuertes Laden zu Hause ab der Ankunft, geladen wird, sobald der Energiebedarf
seit dem letzten Laden EV_CHARGE_KWH übersteigt; Mehrverbrauch bei Kälte.

Alle Anteile und Kennwerte sind Annahmen (Platzhalter), keine Messwerte.
"""
import numpy as np

HOURS = 8760
SEED = 20261024

# Szenarien: Anteil der Wohngebäude mit Wärmepumpe, Anteil der Haushalte mit E-Auto (Annahmen)
SCENARIOS = {
    'heute': {'wp_share': 0.15, 'ev_share': 0.08},
    '2030': {'wp_share': 0.35, 'ev_share': 0.25},
    '2040': {'wp_share': 0.70, 'ev_share': 0.60},
}

HEAT_KWH_EFH = 12000       # Annahme: Jahreswärme Einfamilienhaus inkl. Warmwasser (kWh_th)
HEAT_KWH_MFH_HH = 5000     # Annahme: je Wohnung im Mehrparteienhaus
DHW_SHARE = 0.15           # Anteil Warmwasser an der Jahreswärme
HEAT_LIMIT_C = 15.0        # Heizgrenztemperatur
# COP Luft/Wasser linear in der Temperatur, kalibriert auf when2heat AT 2012/2017 (Ruhnau u. a.
# 2019, OPSD 2023-07-27): Raumwärme = Mittel aus Fußboden- und Radiatorheizung, Warmwasser eigen
COP_SPACE = (2.79, 0.079)  # COP = a + b * T
COP_DHW = (2.14, 0.042)
COP_MIN, COP_MAX = 1.5, 5.0
BIVALENT_C = -7.0          # Annahme: Bivalenzpunkt (effektive Temperatur), darunter Heizstab
HEAT_LIMIT_SPREAD = (14.0, 17.0)  # Annahme: Heizgrenze je Gebäude gleichverteilt
SHIFT_H = 2                # Annahme: Zeitversatz je Gebäude, ganzzahlig in [-2, +2] h
# Warmwasser-Tagesgang (Anteil je Stunde, Summe 1): Spitzen morgens und abends
DHW_PROFILE = np.array([1, 1, 1, 1, 1, 2, 5, 7, 6, 4, 3, 3, 3, 3, 3, 3, 4, 5, 7, 8, 7, 5, 3, 2], dtype=float)
DHW_PROFILE /= DHW_PROFILE.sum()

KM_PER_YEAR = 12000        # Annahme: Fahrleistung je E-Auto
KWH_PER_KM = 0.17
COLD_PER_K = 0.015         # Mehrverbrauch je Kelvin unter 15 °C Tagesmittel
EV_ETA = 0.9               # Ladeverluste
EV_KW_FAST, EV_KW_SLOW = 11.0, 3.7
EV_FAST_SHARE = 0.7        # Anteil 11-kW-Wallboxen
EV_CHARGE_KWH = 12.0       # geladen wird, sobald so viel Energie fehlt
ARRIVAL_WEEKDAY = (18.0, 1.5)   # Mittel, Streuung in Stunden
ARRIVAL_WEEKEND = (15.0, 3.0)


def read_t2m(path):
    """Stündliche Lufttemperatur 2 m (°C) aus einer PVGIS-Stundendatei, 8 760 Werte."""
    vals = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            if line[:4].isdigit() and ':' in line[:14]:
                vals.append(float(line.split(',')[4]))
    assert len(vals) == HOURS, len(vals)
    return np.array(vals)


def cop(temp_c, coef=COP_SPACE):
    """Leistungszahl einer Luft/Wasser-Wärmepumpe, linear in der Außentemperatur."""
    return np.clip(coef[0] + coef[1] * temp_c, COP_MIN, COP_MAX)


def effective_temp(temp_c):
    """Halb aktuelle, halb gleitende 24-h-Mitteltemperatur (Gebäudeträgheit)."""
    padded = np.concatenate([np.full(23, temp_c[0]), temp_c])
    daily = np.convolve(padded, np.ones(24) / 24, mode='valid')
    return 0.5 * temp_c + 0.5 * daily


def heat_pump_kw(temp_c, heat_kwh_year, limits=None, shifts=None, dhw_share=None):
    """Elektrische Leistung (kW) je Stunde und Knoten für den gegebenen Jahreswärmebedarf.

    ``limits``: Heizgrenze je Knoten (°C), ``shifts``: Zeitversatz je Knoten (h); ohne beide
    folgen alle Knoten derselben Kurve. ``dhw_share``: Warmwasseranteil je Knoten (sonst DHW_SHARE).
    """
    e = np.asarray(heat_kwh_year, dtype=float)
    limits = np.full(len(e), HEAT_LIMIT_C) if limits is None else np.asarray(limits, dtype=float)
    share = np.full(len(e), DHW_SHARE) if dhw_share is None else np.asarray(dhw_share, dtype=float)
    t_eff = effective_temp(temp_c)
    degree = np.maximum(limits[None, :] - t_eff[:, None], 0)
    dsum = np.maximum(degree.sum(axis=0), 1e-9)
    dhw = np.tile(DHW_PROFILE, HOURS // 24) / (HOURS // 24)
    space = (1 - share) * degree / dsum * e                    # Raumwärme kWh je Stunde
    water = share * dhw[:, None] * e
    # Wärmepumpe ausgelegt auf den Bedarf am Bivalenzpunkt (Raumwärme + Warmwasserspitze)
    q_max = ((1 - share) * np.maximum(limits - BIVALENT_C, 0) / dsum + share * dhw.max()) * e
    heat = space + water
    hp_share = np.divide(np.minimum(heat, q_max[None, :]), heat, out=np.ones_like(heat), where=heat > 0)
    el = hp_share * (space / cop(t_eff)[:, None] + water / cop(t_eff, COP_DHW)[:, None]) + (1 - hp_share) * heat
    if shifts is not None:
        rows = (np.arange(HOURS)[:, None] - np.asarray(shifts)[None, :]) % HOURS
        el = el[rows, np.arange(len(e))[None, :]]
    return el


def heat_pump_kw_cells(temp_c, heat_kwh_year, cell_of, limits=None, shifts=None, dhw_share=None):
    """Wie heat_pump_kw, aber jede Spalte von ``temp_c`` gilt für die Knoten mit ``cell_of`` == Spalte."""
    heat_kwh_year = np.asarray(heat_kwh_year, dtype=float)
    out = np.zeros((HOURS, len(heat_kwh_year)), dtype=np.float32)
    for c in np.unique(cell_of[heat_kwh_year > 0]):
        idx = np.flatnonzero((cell_of == c) & (heat_kwh_year > 0))
        pick = lambda a: None if a is None else np.asarray(a)[idx]
        out[:, idx] = heat_pump_kw(temp_c[:, c], heat_kwh_year[idx], pick(limits), pick(shifts), pick(dhw_share))
    return out


def spread(n, seed=SEED):
    """Heizgrenze und Zeitversatz je Knoten (eigener Zufallsstrom, E-Autos bleiben unverändert)."""
    rng = np.random.default_rng(seed + 11)
    return rng.uniform(*HEAT_LIMIT_SPREAD, n), rng.integers(-SHIFT_H, SHIFT_H + 1, n)


def ev_kw(cars, temp_c, rng, first_weekday=6):
    """Ladeleistung (kW) je Stunde und Knoten; ``cars`` = Anzahl E-Autos je Knoten.

    ``first_weekday``: Wochentag des 1.1. (Mo = 0), Standard 2023 (Sonntag).
    """
    cars = np.asarray(cars, dtype=int)
    out = np.zeros((HOURS, len(cars)))
    days = HOURS // 24
    t_day = temp_c[:days * 24].reshape(days, 24).mean(axis=1)
    kwh_day = KM_PER_YEAR / 365 * KWH_PER_KM * (1 + COLD_PER_K * np.maximum(15 - t_day, 0))
    weekend = (np.arange(days) + first_weekday) % 7 >= 5
    for node in np.flatnonzero(cars):
        for _ in range(cars[node]):
            power = EV_KW_FAST if rng.random() < EV_FAST_SHARE else EV_KW_SLOW
            need = rng.uniform(0, EV_CHARGE_KWH)  # Startzustand streuen
            for d in range(days):
                need += kwh_day[d] * rng.uniform(0.5, 1.5)
                if need < EV_CHARGE_KWH:
                    continue
                mu, sd = ARRIVAL_WEEKEND if weekend[d] else ARRIVAL_WEEKDAY
                h = d * 24 + int(np.clip(rng.normal(mu, sd), 12, 23))
                grid = need / EV_ETA
                while grid > 1e-9 and h < HOURS:
                    step = min(power, grid)
                    out[h, node] += step
                    grid -= step
                    h += 1
                need = 0.0
    return out


def assign(nodes, scenario, rng):
    """Jahreswärme (kWh_th) und Anzahl E-Autos je Knoten; Knoten ohne Haushalt bekommen nichts.

    Knoten mit ``n['fw']`` (Fernwärme) bekommen keine Wärmepumpe; damit der Szenarioanteil über
    alle Wohngebäude gleich bleibt, steigt die Wahrscheinlichkeit bei den übrigen.
    """
    heat = np.zeros(len(nodes))
    cars = np.zeros(len(nodes), dtype=int)
    homes = [n for n in nodes if n['hh'] > 0]
    fw_frac = sum(bool(n.get('fw')) for n in homes) / max(len(homes), 1)
    p_wp = min(1.0, scenario['wp_share'] / max(1 - fw_frac, 1e-9))
    for i, n in enumerate(nodes):
        hh = n['hh']
        if hh <= 0:
            continue
        if rng.random() < p_wp and not n.get('fw'):
            heat[i] = HEAT_KWH_EFH if hh == 1 else HEAT_KWH_MFH_HH * hh
        cars[i] = rng.binomial(hh, scenario['ev_share'])
    return heat, cars


def extra_load(nodes, temp_c, scenario='2030', seed=SEED, cell_of=None, first_weekday=6, diversity=True,
               heat_kwh=None, dhw_share=None):
    """Zusatzlast (Wärmepumpe, E-Auto) in kW, je (8 760, Knoten) als float32.

    ``temp_c`` eindimensional (eine Temperatur für alle) oder (8 760, Zellen) mit ``cell_of``.
    ``diversity``: Heizgrenze und Zeitversatz je Gebäude streuen. ``heat_kwh``: Jahreswärme je
    Knoten (z. B. aus Gebäudegeometrie) statt der Pauschalwerte; gilt nur für Knoten mit Wärmepumpe,
    NaN behält den Pauschalwert. ``dhw_share``: Warmwasseranteil je Knoten, NaN = DHW_SHARE.
    """
    rng = np.random.default_rng(seed)
    heat, cars = assign(nodes, SCENARIOS[scenario], rng)
    if heat_kwh is not None:
        given = np.asarray(heat_kwh, dtype=float)
        heat = np.where((heat > 0) & ~np.isnan(given), given, heat)
    if dhw_share is not None:
        dhw_share = np.where(np.isnan(dhw_share), DHW_SHARE, dhw_share)
    limits, shifts = spread(len(nodes), seed) if diversity else (None, None)
    if temp_c.ndim == 2:
        wp = heat_pump_kw_cells(temp_c, heat, np.asarray(cell_of), limits, shifts, dhw_share)
        temp_c = temp_c.mean(axis=1)  # E-Auto: Gebietsmittel genügt
    else:
        wp = heat_pump_kw_cells(temp_c[:, None], heat, np.zeros(len(nodes), dtype=int), limits, shifts, dhw_share)
    ev = ev_kw(cars, temp_c, rng, first_weekday).astype(np.float32)
    return wp, ev
