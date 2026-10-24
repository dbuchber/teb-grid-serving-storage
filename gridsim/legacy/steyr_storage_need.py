#!/usr/bin/env python3
"""Speicherbedarf je Netzsegment (Ortsnetzstation) im Raum Steyr nach ems-konzept.md §7.2.

Grundlage ist der Basisfall der Variante A (Speicher im Eigenverbrauch), stündlich, Wetterjahr
2023. Segmentgrenze = 100 % Trafo-Bemessung (kVA als kW, cos phi = 1); die Bemessung bleibt
beim Hochskalieren der PV unverändert. Mit ``--scenario`` kommen Wärmepumpen und E-Autos
(steyr_wp_ev.py) dazu; dann werden Einspeise- und Lastengpässe getrennt ausgewertet.
Mit ``--weather-year`` kommen PV (PVGIS) und Temperatur je Station (GeoSphere INCA, 1 km)
aus diesem Jahr (steyr_weather_fetch.py); ohne gilt PVGIS 2023 mit einem Temperaturpunkt.
Mit ``--heat lod1`` kommt der Wärmebedarf je Gebäude aus DORIS LoD1 und TABULA
(steyr_heat_demand.py), sonst gelten die Pauschalwerte; ``--no-diversity`` schaltet die Streuung
von Heizgrenze und Zeitversatz ab. ``--district-heating`` nimmt Mehrfamilienhäuser in den
belegten Fernwärme-Stadtteilen von der Wärmepumpe aus (steyr_district_heating.py).

Ereignis = zusammenhängende Stunden mit Überlast; Ereignisse mit weniger als MIN_PAUSE_H
Stunden Abstand gelten als eines (kein Nachladen bzw. Leeren dazwischen).
"""
import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path

import numpy as np

import steyr_district_heating as dh
import steyr_heat_demand as hd
import steyr_sim_variant_a as sim
import steyr_wp_ev as wpev

FACTOR_INST = 0.6 * 0.85 * 0.8 * 0.8   # Verfügbarkeit x Zuverlässigkeit x freigegeben x SoH (Platzhalter)
KW_PER_UNIT = 5.0
RELIABILITY = 0.85
KWH_PER_UNIT = 10.0                     # mittlere Nutzkapazität je Haushaltsspeicher (Annahme)
MIN_PAUSE_H = 8
PV_SCALES = (1.0, 1.5, 2.0)


def events(over):
    """Ereignisse als (Energie kWh, Spitze kW, Stunden), zusammengefasst bei kurzer Pause."""
    hours = np.flatnonzero(over > 0)
    if not len(hours):
        return []
    out, start, last = [], hours[0], hours[0]
    for h in hours[1:]:
        if h - last > MIN_PAUSE_H:
            out.append((start, last))
            start = h
        last = h
    out.append((start, last))
    return [(float(over[a:b + 1].sum()), float(over[a:b + 1].max()), int((over[a:b + 1] > 0).sum())) for a, b in out]


def trafo_steps(kva, peak):
    """Normgrößen-Schritte bis zur Deckung der Spitze ohne Speicher; None = über der größten Norm."""
    need = next((t for t in sim.TRAFO_SIZES if t >= peak), None)
    return None if need is None else sim.TRAFO_SIZES.index(need) - sim.TRAFO_SIZES.index(kva)


def segment_row(flow, kva, cap):
    """§7.2-Kennzahlen für eine Richtung (flow > 0 belastet den Trafo), None ohne Engpass."""
    ev = events(np.maximum(flow - kva, 0))
    if not ev:
        return None
    e_net = max(e for e, _, _ in ev)
    p_max = max(p for _, p, _ in ev)
    e_inst = e_net / FACTOR_INST
    return {'engpass_h_jahr': sum(h for _, _, h in ev), 'ereignisse': len(ev),
            'e_netto_kwh': round(e_net, 1), 'p_max_kw': round(p_max, 1), 'e_inst_kwh': round(e_inst, 1),
            'n_speicher_energie': math.ceil(e_inst / KWH_PER_UNIT),
            'n_speicher_leistung': math.ceil(p_max / (KW_PER_UNIT * RELIABILITY)),
            'speicher_im_modell': int((cap > 0).sum()),
            'netz_vollzyklen_jahr': round(sum(e for e, _, _ in ev) / e_inst, 1),
            'trafo_noetig_kva': next((t for t in sim.TRAFO_SIZES if t >= flow.max()), None),
            'trafo_stufen_hoeher': trafo_steps(kva, flow.max())}


def read_inca(inp, year, stations, nodes):
    """INCA-T2M (8 760, Zellen) und die Zelle je Knoten über die Station des Knotens."""
    with open(inp / 'inca' / 'stationen.csv', encoding='utf-8') as fh:
        cell_of_station = {r['station']: r['zelle'] for r in csv.DictReader(fh, delimiter=';')}
    with open(inp / 'inca' / f't2m_{year}.csv', encoding='utf-8') as fh:
        rows = list(csv.reader(fh, delimiter=';'))
    cols = rows[0][1:]
    temp = sim.drop_leap_day(np.array([[float(v) for v in r[1:]] for r in rows[1:]]))
    col = {c: i for i, c in enumerate(cols)}
    cell_of = np.array([col[cell_of_station[stations[n['station']]['osm_id']]] for n in nodes])
    return temp, cell_of


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--large-share', type=float, default=0.0)
    ap.add_argument('--scenario', choices=sorted(wpev.SCENARIOS), help='Wärmepumpen und E-Autos (Annahmen)')
    ap.add_argument('--weather-year', type=int, help='PVGIS und INCA dieses Jahres (steyr_weather_fetch.py)')
    ap.add_argument('--heat', choices=('pauschal', 'lod1'), default='pauschal', help='Wärmebedarf je Gebäude')
    ap.add_argument('--no-diversity', action='store_true', help='Heizgrenze und Zeitversatz nicht streuen')
    ap.add_argument('--district-heating', action='store_true', help='Fernwärme-Stadtteile ohne Wärmepumpe')
    args = ap.parse_args()
    sim.STORAGE_SHARE_LARGE = args.large_share
    args.output.mkdir(parents=True, exist_ok=True)

    stations, _, st_uw, nodes = sim.build_members(args.input)
    year = args.weather_year or 2023
    suffix = f'_{year}' if args.weather_year else ''
    profiles = {b: sim.read_pvgis(args.input / f'pvgis_{b}{suffix}.csv') for b in sim.PVGIS_BINS}
    h0 = sim.read_h0(args.input / 'apcs' / 'synthload2026.csv', year)
    pv_kw = np.column_stack([sum(profiles[b] * k for b, k in n['pv'].items()) if n['pv'] else np.zeros(8760)
                             for n in nodes])
    load_kw = np.column_stack([h0 * sim.KWH_PER_HH * n['hh'] for n in nodes]).astype(np.float32)
    fw_info = None
    if args.district_heating:
        n_fw = dh.mark(nodes, dh.places(args.input / 'osm_places_steyr.json'))
        fw_info = {'mfh_mit_fernwaerme': n_fw, 'haushalte_mit_fernwaerme': int(sum(n['hh'] for n in nodes if n.get('fw'))),
                   'stadtteile': list(dh.DISTRICTS), 'max_dist_m': dh.MAX_DIST_M}
    if args.scenario:
        if args.weather_year:
            temp, cell_of = read_inca(args.input, year, stations, nodes)
        else:
            temp, cell_of = wpev.read_t2m(args.input / 'pvgis_S35.csv'), None
        heat_kwh = dhw = None
        if args.heat == 'lod1':
            hdd = hd.heating_degree_days(temp.mean(axis=1) if temp.ndim == 2 else temp)
            heat_kwh, dhw, bgf = hd.node_heat(nodes, args.input / 'lod1_steyr.csv', hdd, wpev.SEED)
            heat_info = {'heizgradtage_20_12': round(hdd), 'knoten_mit_lod1': int((~np.isnan(bgf)).sum()),
                         'wohnknoten': int(sum(n['hh'] > 0 for n in nodes)),
                         'kwh_je_efh_median': round(float(np.nanmedian([h for h, n in zip(heat_kwh, nodes) if n['hh'] == 1]))),
                         'kwh_je_mfh_wohnung_median': round(float(np.nanmedian(
                             [h / n['hh'] for h, n in zip(heat_kwh, nodes) if n['hh'] > 1])))}
        wp, ev_load = wpev.extra_load(nodes, temp, args.scenario, cell_of=cell_of,
                                      first_weekday=date(year, 1, 1).weekday(), diversity=not args.no_diversity,
                                      heat_kwh=heat_kwh, dhw_share=dhw)
        load_kw += wp + ev_load
        del wp, ev_load
    cap = np.array([n['kwh'] for n in nodes])
    st_of = np.array([n['station'] for n in nodes])

    rows = []
    for scale in PV_SCALES:
        net = sim.simulate(pv_kw * scale, load_kw, cap, 'base')
        for si in sorted(set(st_of)):
            idx = np.flatnonzero(st_of == si)
            members = [nodes[i] for i in idx]
            kwp = sum(m['kwp'] for m in members)
            kva = sim.trafo_kva(sum(m['hh'] > 0 for m in members), sum(m['hh'] for m in members), kwp)  # Bemessung aus dem Ist-Stand
            p_station = net[:, idx].sum(axis=1)
            for direction, flow in (('einspeisung', -p_station), ('bezug', p_station)):
                row = segment_row(flow, kva, cap[idx])
                if row:
                    rows.append({'szenario': args.scenario or 'ohne WP/EV', 'pv_faktor': scale, 'richtung': direction,
                                 'station': stations[si]['osm_id'], 'synthetic': stations[si].get('synthetic', 0),
                                 'uw': st_uw[si], 'kwp_ns': round(kwp * scale, 1), 'trafo_kva': kva, **row})
    for r in rows:
        r['n_speicher'] = max(r['n_speicher_energie'], r['n_speicher_leistung'])

    fields = list(rows[0]) if rows else []
    with open(args.output / 'speicherbedarf_segmente.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=';')
        w.writeheader()
        w.writerows(rows)

    summary = {'annahmen': {'grenze': '100 % Trafo-Bemessung, kVA = kW', 'aufloesung': '1 h', 'min_pause_h': MIN_PAUSE_H,
                            'faktor_inst': round(FACTOR_INST, 3), 'kw_je_speicher': KW_PER_UNIT, 'zuverlaessigkeit': RELIABILITY,
                            'kwh_je_speicher': KWH_PER_UNIT, 'trafo': 'max(3 kVA je Wohngebäude, 2 kVA je Haushalt, 0,7 x kWp Ist, 125) auf Normgröße',
                            'szenario': args.scenario or 'ohne WP/EV',
                            'wetterjahr': year, 'temperatur': f'INCA 1 km je Station {year}' if args.weather_year else 'PVGIS T2m 2023, ein Punkt',
                            'bivalenzpunkt_c': wpev.BIVALENT_C, 'waermebedarf': args.heat,
                            'streuung': not args.no_diversity, 'cop_raum': wpev.COP_SPACE, 'cop_warmwasser': wpev.COP_DHW},
               'stationen_gesamt': len(set(st_of))}
    if args.scenario and args.heat == 'lod1':
        summary['waermebedarf_lod1'] = heat_info
    if fw_info:
        summary['fernwaerme'] = fw_info
    for scale, direction in [(s_, d_) for s_ in PV_SCALES for d_ in ('einspeisung', 'bezug')]:
        sel = [r for r in rows if r['pv_faktor'] == scale and r['richtung'] == direction]
        summary[f'pv_x{scale}_{direction}'] = {
            'segmente_mit_engpass': len(sel),
            'engpass_h_median': float(np.median([r['engpass_h_jahr'] for r in sel])) if sel else 0,
            'e_netto_mwh_summe': round(sum(r['e_netto_kwh'] for r in sel) / 1000, 2),
            'e_inst_mwh_summe': round(sum(r['e_inst_kwh'] for r in sel) / 1000, 2),
            'p_max_mw_summe': round(sum(r['p_max_kw'] for r in sel) / 1000, 2),
            'n_speicher_summe': sum(r['n_speicher'] for r in sel),
            'n_speicher_im_modell_dort': sum(r['speicher_im_modell'] for r in sel),
            'vollzyklen_median': float(np.median([r['netz_vollzyklen_jahr'] for r in sel])) if sel else 0,
            'e_netto_kwh_median': float(np.median([r['e_netto_kwh'] for r in sel])) if sel else 0,
            'e_inst_kwh_median': float(np.median([r['e_inst_kwh'] for r in sel])) if sel else 0,
            'n_speicher_median': float(np.median([r['n_speicher'] for r in sel])) if sel else 0,
            'vollzyklen_p10_p90': [float(np.percentile([r['netz_vollzyklen_jahr'] for r in sel], q)) for q in (10, 90)] if sel else [],
            'trafo_1_stufe_hoeher': sum(r['trafo_stufen_hoeher'] == 1 for r in sel),
            'trafo_2plus_stufen_hoeher': sum((r['trafo_stufen_hoeher'] or 0) >= 2 for r in sel),
            'trafo_ueber_1000kva': sum(r['trafo_stufen_hoeher'] is None for r in sel),
            'leistung_bindet_anteil': round(sum(r['n_speicher_leistung'] > r['n_speicher_energie'] for r in sel) / len(sel), 2) if sel else 0,
        }
    (args.output / 'speicherbedarf_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps({k: v.get('segmente_mit_engpass') for k, v in summary.items() if k.startswith('pv_')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
