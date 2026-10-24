#!/usr/bin/env python3
"""V2G-Demo Steyr: Lastengpass am Winterabend auf einem schwachen und einem typischen Segment.

Fälle je Station (Wärmepumpen und E-Autos aus steyr_wp_ev.py, ohne Sperrzeiten):
  ungesteuert    Laden ab Ankunft wie in steyr_wp_ev.py
  gleichzeitig   wie ungesteuert, aber am Abend des kältesten Tags stecken alle E-Autos um
                 18 Uhr an und laden mit voller Wallbox-Leistung EV_CHARGE_KWH (Stresstest)

Lösungen je Fall, Grenze = 100 % Trafo-Bemessung:
  Heimspeicher       §7.2 wie steyr_storage_need.py
  gesteuertes Laden  Wallboxen werden gedrosselt, sobald der Trafo voll ist; die Energie wird
                     später nachgeladen. Was um 7 Uhr fehlt, bleibt ungeladen (Komfortverlust,
                     ausgewiesen); die Grenze wird nie überschritten
  V2G                angesteckte E-Autos speisen den Rest zurück (V2G_KW, V2G_KWH je Abend)

Vereinfachung: Heimspeicher arbeiten im Eigenverbrauch und entladen nicht ins E-Auto; die
Ladeleistung kommt auf Stationsebene dazu. Schwaches Segment = Station mit Netzart Land,
Trafo 160-250 kVA und höchster Winterauslastung, reale OSM-Station vor synthetischer;
typische Station = Stadt, Trafo 400 kVA, Auslastung nahe am Median. Alle Kennwerte sind Annahmen (Platzhalter), keine Messwerte.
"""
import argparse
import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np

import steyr_district_heating as dh
import steyr_heat_demand as hd
import steyr_sim_variant_a as sim
import steyr_storage_need as need
import steyr_wp_ev as wpev

V2G_KW = 11.0          # Annahme: bidirektionale Wallbox
V2G_KWH = 15.0         # Annahme: freigegebene Energie je Auto und Abend (SoC-Fenster)
V2G_AVAIL = 0.7        # Annahme: Anteil der Autos, die am Abend angesteckt und freigegeben sind
DEADLINE_H = 7         # gesteuertes Laden: Energie spätestens bis 7 Uhr nachgeladen
EVENING = (0, 48)      # Zeitreihe: Ereignistag 0 Uhr bis Folgetag 24 Uhr


def controlled(f0, ev, limit):
    """Ladeleistung je Stunde, gedrosselt auf den Platz unter ``limit``, Rest später nachgeholt.

    Gibt auch die je Frist (7 Uhr) ungeladene Energie zurück.
    """
    out, unmet, backlog = np.zeros_like(ev), [], 0.0
    for h in range(len(ev)):
        want = ev[h] + backlog
        serve = min(want, max(limit - f0[h], 0.0))
        out[h], backlog = serve, want - serve
        if h % 24 == DEADLINE_H:  # Frist: was fehlt, bleibt ungeladen
            unmet.append(backlog)
            backlog = 0.0
    return out, np.array(unmet)


def v2g_need(residual):
    """Autos für V2G nach Leistung und Energie (je Abend-Ereignis) für den Rest über der Grenze."""
    ev = need.events(residual)
    if not ev:
        return {'v2g_p_max_kw': 0.0, 'v2g_e_abend_kwh': 0.0, 'v2g_autos_leistung': 0, 'v2g_autos_energie': 0, 'v2g_autos': 0}
    p = max(x for _, x, _ in ev)
    e = max(x for x, _, _ in ev)
    n_p, n_e = math.ceil(p / (V2G_KW * V2G_AVAIL)), math.ceil(e / (V2G_KWH * V2G_AVAIL))
    return {'v2g_p_max_kw': round(p, 1), 'v2g_e_abend_kwh': round(e, 1), 'v2g_autos_leistung': n_p,
            'v2g_autos_energie': n_e, 'v2g_autos': max(n_p, n_e)}


def stress_ev(ev, cars, day):
    """Ladeprofil mit allen Autos ab 18 Uhr am Abend ``day``; dessen übliches Laden entfällt."""
    out = ev.copy()
    a, b = day * 24 + 12, day * 24 + 24 + DEADLINE_H
    out[a:b] = 0.0
    rng = np.random.default_rng(wpev.SEED + 7)
    for node in np.flatnonzero(cars):
        for _ in range(cars[node]):
            power = wpev.EV_KW_FAST if rng.random() < wpev.EV_FAST_SHARE else wpev.EV_KW_SLOW
            grid, h = wpev.EV_CHARGE_KWH / wpev.EV_ETA, day * 24 + 18
            while grid > 1e-9:
                out[h, node] += min(power, grid)
                grid -= power
                h += 1
    return out


def pick(meta, peak, kva):
    """Schwaches und typisches Segment aus den Stationsdaten der Variante A."""
    ratio = {s: peak[s] / kva[s] for s in peak}
    weak = [s for s in peak if meta.get(s, {}).get('netzart') == 'land' and 160 <= kva[s] <= 250]
    weak = max(weak, key=lambda s: (meta[s]['synthetic'] == '0', ratio[s], float(meta[s]['abgang_max_m'])))
    town = [s for s in peak if meta.get(s, {}).get('netzart') == 'stadt' and kva[s] == 400 and meta[s]['synthetic'] == '0'] or list(peak)
    med = float(np.median([ratio[s] for s in town]))
    typical = min(town, key=lambda s: abs(ratio[s] - med))
    return weak, typical


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--meta', type=Path, required=True, help='variante_a_stationen.csv (Netzart, Abgänge)')
    ap.add_argument('--scenario', default='2030', choices=sorted(wpev.SCENARIOS))
    ap.add_argument('--weather-year', type=int, default=2012)
    ap.add_argument('--large-share', type=float, default=0.2)
    ap.add_argument('--heat', choices=('pauschal', 'lod1'), default='lod1', help='Wärmebedarf je Gebäude')
    ap.add_argument('--district-heating', action='store_true', help='Fernwärme-Stadtteile ohne Wärmepumpe')
    ap.add_argument('--weak', help='Station (osm_id) statt automatischer Wahl')
    ap.add_argument('--typical', help='Station (osm_id) statt automatischer Wahl')
    args = ap.parse_args()
    sim.STORAGE_SHARE_LARGE = args.large_share
    args.output.mkdir(parents=True, exist_ok=True)
    year = args.weather_year

    stations, _, st_uw, nodes = sim.build_members(args.input)
    profiles = {b: sim.read_pvgis(args.input / f'pvgis_{b}_{year}.csv') for b in sim.PVGIS_BINS}
    h0 = sim.read_h0(args.input / 'apcs' / 'synthload2026.csv', year)
    temp, cell_of = need.read_inca(args.input, year, stations, nodes)
    if args.district_heating:
        dh.mark(nodes, dh.places(args.input / 'osm_places_steyr.json'))
    rng = np.random.default_rng(wpev.SEED)  # gleiche Zuteilung wie extra_load
    heat, cars = wpev.assign(nodes, wpev.SCENARIOS[args.scenario], rng)
    heat_kwh = dhw = None
    if args.heat == 'lod1':
        heat_kwh, dhw, _ = hd.node_heat(nodes, args.input / 'lod1_steyr.csv', hd.heating_degree_days(temp.mean(axis=1)), wpev.SEED)
        heat = np.where((heat > 0) & ~np.isnan(heat_kwh), heat_kwh, heat)
    wp_all, ev_all = wpev.extra_load(nodes, temp, args.scenario, cell_of=cell_of, first_weekday=date(year, 1, 1).weekday(),
                                     heat_kwh=heat_kwh, dhw_share=dhw)
    with open(args.meta, encoding='utf-8') as fh:
        meta = {r['station']: r for r in csv.DictReader(fh, delimiter=';') if r['strategie'] == 'base'}

    st_of = np.array([n['station'] for n in nodes])
    by_id, f0_of, ev_of, kva_of, wp_of = {}, {}, {}, {}, {}
    for si in sorted(set(st_of)):
        idx = np.flatnonzero(st_of == si)
        members = [nodes[i] for i in idx]
        sid = stations[si]['osm_id']
        kva_of[sid] = sim.trafo_kva(sum(m['hh'] > 0 for m in members), sum(m['hh'] for m in members), sum(m['kwp'] for m in members))
        by_id[sid] = (si, idx)
    peak = {}
    for sid, (si, idx) in by_id.items():
        pv = np.column_stack([sum(profiles[b] * k for b, k in nodes[i]['pv'].items()) if nodes[i]['pv'] else np.zeros(8760) for i in idx])
        load = np.column_stack([h0 * sim.KWH_PER_HH * nodes[i]['hh'] for i in idx]) + wp_all[:, idx]
        f0 = sim.simulate(pv, load, np.array([nodes[i]['kwh'] for i in idx]), 'base').sum(axis=1).astype(float)
        f0_of[sid], ev_of[sid] = f0, ev_all[:, idx].astype(float)
        wp_of[sid] = wp_all[:, idx].sum(axis=1).astype(float)
        peak[sid] = float((f0 + ev_of[sid].sum(axis=1)).max())
    weak, typical = args.weak or None, args.typical or None
    auto_weak, auto_typ = pick(meta, peak, kva_of)
    weak, typical = weak or auto_weak, typical or auto_typ

    t_day = temp.mean(axis=1)[:8760 // 24 * 24].reshape(-1, 24).mean(axis=1)
    cold_day = int(np.argmin(t_day))
    rows, series = [], {}
    for role, sid in (('schwach', weak), ('typisch', typical)):
        si, idx = by_id[sid]
        kva, f0 = kva_of[sid], f0_of[sid]
        n_cars = int(cars[idx].sum())
        for case in ('ungesteuert', 'gleichzeitig'):
            ev = ev_of[sid] if case == 'ungesteuert' else stress_ev(ev_of[sid], cars[idx], cold_day)
            e = ev.sum(axis=1)
            flow = f0 + e
            e_ctrl, unmet = controlled(f0, e, kva)
            flow_ctrl = f0 + e_ctrl
            res_unc, res_ctrl = np.maximum(flow - kva, 0), np.maximum(flow_ctrl - kva, 0)
            row72 = need.segment_row(flow, kva, np.array([nodes[i]['kwh'] for i in idx])) or {}
            if row72:
                row72['n_speicher'] = max(row72['n_speicher_energie'], row72['n_speicher_leistung'])
            v_unc, v_ctrl = v2g_need(res_unc), v2g_need(res_ctrl)
            rows.append({
                'rolle': role, 'station': sid, 'synthetic': stations[si].get('synthetic', 0), 'uw': st_uw[si],
                'netzart': meta.get(sid, {}).get('netzart'), 'abgang_max_m': meta.get(sid, {}).get('abgang_max_m'),
                'fall': case, 'szenario': args.scenario, 'wetterjahr': year, 'trafo_kva': kva,
                'haushalte': int(sum(nodes[i]['hh'] for i in idx)), 'waermepumpen': int((heat[idx] > 0).sum()), 'e_autos': n_cars,
                'spitze_kw': round(float(flow.max()), 1), 'auslastung_max': round(float(flow.max()) / kva, 2),
                'engpass_h_jahr': row72.get('engpass_h_jahr', 0), 'e_netto_kwh': row72.get('e_netto_kwh', 0),
                'p_max_kw': row72.get('p_max_kw', 0), 'e_inst_kwh': row72.get('e_inst_kwh', 0),
                'n_speicher_leistung': row72.get('n_speicher_leistung', 0), 'n_speicher_energie': row72.get('n_speicher_energie', 0),
                'n_speicher': row72.get('n_speicher', 0), 'netz_vollzyklen_jahr': row72.get('netz_vollzyklen_jahr', 0),
                'heimspeicher_vorhanden': int(sum(nodes[i]['kwh'] > 0 for i in idx)),
                'gesteuert_drossel_max_kw': round(float((e - e_ctrl).max()), 1),
                'gesteuert_wallboxen_pausiert': math.ceil(float((e - e_ctrl).max()) / wpev.EV_KW_FAST),
                'gesteuert_rest_h_jahr': int((res_ctrl > 0).sum()), 'gesteuert_rest_p_kw': round(float(res_ctrl.max()), 1),
                'gesteuert_ungeladen_kwh_jahr': round(float(unmet.sum()), 1), 'gesteuert_ungeladen_naechte': int((unmet > 0.1).sum()),
                'gesteuert_ungeladen_max_kwh': round(float(unmet.max()), 1),
                **{f'{k}_ungesteuert': v for k, v in v_unc.items()}, **{f'{k}_nach_steuerung': v for k, v in v_ctrl.items()},
            })
            # Zeitreihe: Abend mit der höchsten Spitze (gleichzeitig: Kältetag)
            day = cold_day if case == 'gleichzeitig' else int(np.argmax(flow[:-24].reshape(-1, 24).max(axis=1)))
            h = np.arange(day * 24 + EVENING[0], day * 24 + EVENING[1])
            # nur die Autos im Segment: reicht das nicht, bleibt am Trafo ein Rest über der Grenze
            v2g = np.minimum(res_unc[h], V2G_KW * V2G_AVAIL * min(v_unc['v2g_autos'], n_cars))
            series[(role, case)] = [{
                'rolle': role, 'station': sid, 'fall': case,
                'zeit': f'{(date(year, 1, 1) + timedelta(days=int(x) // 24)).isoformat()}T{int(x) % 24:02d}:00',
                'trafo_kva': kva, 'temperatur_c': round(float(temp[x, cell_of[idx[0]]]), 1),
                'haushalt_wp_kw': round(float(f0[x]), 1), 'waermepumpe_kw': round(float(wp_of[sid][x]), 1),
                'haushalt_netto_kw': round(float(f0[x] - wp_of[sid][x]), 1), 'eauto_ungesteuert_kw': round(float(e[x]), 1),
                'trafo_ungesteuert_kw': round(float(flow[x]), 1),
                'eauto_gesteuert_kw': round(float(e_ctrl[x]), 1), 'trafo_gesteuert_kw': round(float(flow_ctrl[x]), 1),
                'v2g_rueckspeisung_kw': round(float(v), 1), 'trafo_v2g_kw': round(float(flow[x] - v), 1),
            } for x, v in zip(h, v2g)]

    with open(args.output / 'v2g_segmente.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter=';')
        w.writeheader()
        w.writerows(rows)
    flat = [r for v in series.values() for r in v]
    with open(args.output / 'v2g_abend_zeitreihe.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(flat[0]), delimiter=';')
        w.writeheader()
        w.writerows(flat)
    summary = {'annahmen': {'v2g_kw': V2G_KW, 'v2g_kwh_je_abend': V2G_KWH, 'v2g_verfuegbar': V2G_AVAIL,
                            'frist_gesteuert_h': DEADLINE_H, 'szenario': args.scenario, 'wetterjahr': year,
                            'kaeltester_tag': (date(year, 1, 1) + timedelta(days=cold_day)).isoformat(),
                            'bivalenzpunkt_c': wpev.BIVALENT_C, 'waermebedarf': args.heat, 'fernwaerme': args.district_heating, 'heimspeicher': 'Eigenverbrauch, nicht ins E-Auto',
                            'temperatur': f'INCA 1 km je Station {year}'},
               'schwach': weak, 'typisch': typical, 'faelle': rows}
    (args.output / 'v2g_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    for r in rows:
        print(r['rolle'], r['fall'], r['station'], r['trafo_kva'], 'Spitze', r['spitze_kw'], 'Engpass-h', r['engpass_h_jahr'],
              'Speicher', r['n_speicher'], 'gesteuert Rest', r['gesteuert_rest_p_kw'], 'ungeladen', r['gesteuert_ungeladen_kwh_jahr'], 'V2G-Autos', r['v2g_autos_ungesteuert'],
              '/', r['v2g_autos_nach_steuerung'], 'von', r['e_autos'])


if __name__ == '__main__':
    main()
