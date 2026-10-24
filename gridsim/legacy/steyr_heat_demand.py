#!/usr/bin/env python3
"""Jahreswärmebedarf je Wohngebäude im Raum Steyr aus Gebäudegeometrie und Bauperiode.

BGF = Grundfläche x Geschosse aus DORIS LoD1 (Geschosse = Höhe / STOREY_M, abgerundet,
mindestens 1). Das Adressgebäude (BEV-Punkt) wird dem LoD1-Umriss zugeordnet, der es enthält,
sonst dem nächsten innerhalb MATCH_M. Bauperiode je Gebäude zufällig nach der Verteilung der
Gemeinde Steyr (GWZ 2021); ein Baujahr je Gebäude ist nicht offen verfügbar. Vor 1991
errichtete Gebäude gelten mit RENOVATED_SHARE als saniert.

Heizwärmebedarf (HWB, kWh/m² BGF, Referenzklima 3 400 Heizgradtage): unsaniert = Mitte der
TABULA-Bandbreite je Bauperiode, saniert = Mittel der TABULA-Standardsanierungen. Fläche je
Haushalt auf die Spannweite der Statistik-Austria-Erhebung begrenzt. Der berechnete Bedarf liegt
deutlich über dem gemessenen Verbrauch (Prebound-Effekt, Mischnutzung im LoD1-Umriss); daher
wird die Raumwärme je Gebäudeart auf den mittleren Heizverbrauch je Haushalt laut Mikrozensus
kalibriert (Endenergie x HEAT_EFFICIENCY = Nutzwärme). LoD1 und TABULA bestimmen also die
Unterschiede zwischen Gebäuden, Statistik Austria das Niveau. Danach Skalierung mit den
Heizgradtagen (20/12) des Wetterjahrs. Warmwasser 12,78 kWh/m² BGF (TABULA).
Belege: docs/research/2026-10-24-netzmodell-belege.md (W1-W10). Ohne LoD1-Treffer (z. B.
niederösterreichische Gemeinden) gilt der kalibrierte Mittelwert je Haushalt.
"""
import csv

import numpy as np
from shapely import STRtree, wkt
from shapely.geometry import Point

STOREY_M = 3.0             # Annahme: Geschosshöhe inkl. Decke; Dachraum nicht gezählt (abgerundet)
MATCH_M = 10.0             # Annahme: Adresspunkt höchstens so weit neben dem Umriss
REFERENCE_HDD = 3400.0     # TABULA-Referenzklima (Heizgradtage 20/12)
DHW_KWH_M2 = 12.78         # TABULA Scientific Report D6.9, S. 19
# Gemeinde Steyr, Gebäude nach Bauperiode, GWZ 2021 (Statistik Austria, Gemeindeblatt G0403, Tab. 4.5)
AGE_COUNTS = {'bis 1918': 1421, '1919-1944': 1268, '1945-1960': 1166, '1961-1970': 565, '1971-1980': 611,
              '1981-1990': 651, '1991-2000': 666, '2001-2010': 463, 'ab 2011': 344}
# HWB unsaniert = Mitte der TABULA-Bandbreite (Broschüre Tab. 2 EFH, Tab. 4 MFH); Bauperioden
# der Statistik auf TABULA-Klassen I-VII abgebildet (1961-1980 -> IV, 2001-2020 -> VII)
HWB_EFH = {'bis 1918': 240, '1919-1944': 285, '1945-1960': 270, '1961-1970': 212, '1971-1980': 212,
           '1981-1990': 145, '1991-2000': 105, '2001-2010': 55, 'ab 2011': 55}
HWB_MFH = {'bis 1918': 180, '1919-1944': 205, '1945-1960': 210, '1961-1970': 152, '1971-1980': 152,
           '1981-1990': 110, '1991-2000': 80, '2001-2010': 45, 'ab 2011': 45}
HWB_RENOVATED = {'EFH': 64.5, 'MFH': 51.0}   # Mittel der TABULA-Standardsanierungen I-VI
RENOVATED_SHARE = {'EFH': 0.59, 'MFH': 0.42}  # vor 1991, Hauptwohnsitz (OÖ Energieraumplanung nach IIBW/UBA 2020)
RENOVATION_BEFORE = ('bis 1918', '1919-1944', '1945-1960', '1961-1970', '1971-1980', '1981-1990')
# Statistik Austria, Energieverwendung privater Haushalte 2025-2026: Heizenergie je Haushalt im
# Mikrozensus = modelliert / (1 - Abweichung), S. 13 und 15; Wohnfläche max. je Haushalt, S. 9
HEAT_FINAL_KWH_HH = {'EFH': 15893.2 / (1 - 0.2827), 'MFH': 6465.4 / (1 - 0.2261)}
HEAT_EFFICIENCY = 0.85     # Annahme: Nutzwärme / Endenergie im Bestand
MAX_AREA_HH = {'EFH': 600.0, 'MFH': 250.0}
BGF_PER_NF = 1.25          # Annahme: Brutto-Grundfläche je m² Wohnfläche


def heating_degree_days(temp_c):
    """Heizgradtage 20/12 aus Stundenwerten (Tagesmittel unter 12 °C zählen mit 20 - Tagesmittel)."""
    days = np.asarray(temp_c)[:len(temp_c) // 24 * 24].reshape(-1, 24).mean(axis=1)
    return float(np.where(days < 12, 20 - days, 0).sum())


def read_lod1(path):
    with open(path, encoding='utf-8') as fh:
        rows = [r for r in csv.DictReader(fh, delimiter=';') if r['gebaeudeart'] != 'Nebengebaeude']
    polys = [wkt.loads(r['wkt_31287']) for r in rows]
    floors = np.array([max(1, int(float(r['rel_oh_m']) // STOREY_M)) for r in rows])
    area = np.array([float(r['grundflaeche_m2']) for r in rows])
    return polys, area * floors


def match(nodes, polys):
    """Index des LoD1-Umrisses je Knoten oder -1."""
    tree = STRtree(polys)
    pts = [Point(n['xy']) for n in nodes]
    inside = tree.query(pts, predicate='within')       # (2, Treffer): Punkt-Index, Umriss-Index
    out = np.full(len(nodes), -1)
    out[inside[0]] = inside[1]
    rest = np.flatnonzero(out < 0)
    if len(rest):
        near, dist = tree.query_nearest([pts[i] for i in rest], max_distance=MATCH_M, return_distance=True)
        out[rest[near[0]]] = near[1]
    return out


def node_heat(nodes, lod1_path, hdd, seed, calibrate=True):
    """Jahreswärme (kWh_th), Warmwasseranteil und BGF je Knoten; NaN = ohne LoD1-Treffer.

    ``calibrate``: Raumwärme je Gebäudeart auf den Mikrozensus-Mittelwert je Haushalt skalieren.
    """
    rng = np.random.default_rng(seed + 23)
    polys, bgf_poly = read_lod1(lod1_path)
    idx = match(nodes, polys)
    periods = list(AGE_COUNTS)
    p = np.array(list(AGE_COUNTS.values()), dtype=float)
    p /= p.sum()
    space = np.full(len(nodes), np.nan)
    water = np.full(len(nodes), np.nan)
    bgf_out = np.full(len(nodes), np.nan)
    kinds = np.array(['EFH' if n['hh'] == 1 else 'MFH' for n in nodes])
    homes = (idx >= 0) & np.array([n['hh'] > 0 for n in nodes])
    shared = np.bincount(idx[homes], minlength=len(polys))  # mehrere Wohnadressen in einem Umriss
    for i, n in enumerate(nodes):
        period = periods[rng.choice(len(periods), p=p)]
        renovated = rng.random()
        if n['hh'] <= 0 or idx[i] < 0:
            continue
        kind = kinds[i]
        bgf = min(bgf_poly[idx[i]] / shared[idx[i]], MAX_AREA_HH[kind] * BGF_PER_NF * n['hh'])
        hwb = (HWB_EFH if kind == 'EFH' else HWB_MFH)[period]
        if period in RENOVATION_BEFORE and renovated < RENOVATED_SHARE[kind]:
            hwb = HWB_RENOVATED[kind]
        space[i], water[i], bgf_out[i] = hwb * bgf, DHW_KWH_M2 * bgf, bgf
    if calibrate:
        hh = np.array([n['hh'] for n in nodes], dtype=float)
        for kind in ('EFH', 'MFH'):
            sel = (kinds == kind) & ~np.isnan(space)
            if sel.any():
                target = HEAT_FINAL_KWH_HH[kind] * HEAT_EFFICIENCY
                space[sel] *= target / float(np.mean(space[sel] / hh[sel]))
                # ohne LoD1-Treffer: Mittelwert je Haushalt statt der alten Pauschalwerte
                miss = (kinds == kind) & np.isnan(space) & (hh > 0)
                space[miss] = target * hh[miss]
                water[miss] = float(np.mean(water[sel] / hh[sel])) * hh[miss]
    space *= hdd / REFERENCE_HDD
    heat = space + water
    return heat, water / heat, bgf_out
