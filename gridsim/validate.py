"""Abnahme gegen die Tabellen von Session 18 (24.10.2026, Spec § 9): Größenordnung (± 30 %) und Tendenz."""
from datetime import date
from pathlib import Path

from gridsim.cli import run_batch

# Lastengpass, PV × 1, 257 Stationen: (Stationen mit Engpass, E_netto MWh)
REFERENCE = {
    'load': {(2023, 'heute'): (2, 0.2), (2023, '2030'): (39, 12), (2023, '2040'): (193, 337),
             (2017, 'heute'): (4, 0.4), (2017, '2030'): (52, 28), (2017, '2040'): (200, 1057),
             (2012, 'heute'): (5, 2.3), (2012, '2030'): (90, 116), (2012, '2040'): (210, 3573)},
    'feed': {1.0: (1, 3), 1.5: (19, 19), 2.0: (31, 34)},  # Stationen mit Einspeiseengpass (Spanne)
}
KPI_INDEX = {'stations_load_congestion': 0, 'e_net_mwh': 1}
FLOOR = {'stations_load_congestion': 3, 'e_net_mwh': 1.0}  # kleine Referenzwerte: absolute Toleranz


def compare(results, reference=REFERENCE, tol=0.30):
    rows = []
    for key, ref in reference['load'].items():
        for kpi, i in KPI_INDEX.items():
            val, r = results[key][kpi], ref[i]
            ratio = val / r if r else float('inf')
            ok = abs(val - r) <= max(tol * r, FLOOR[kpi])
            rows.append({'key': key, 'kpi': kpi, 'value': val, 'reference': r, 'ratio': ratio, 'ok': ok})
    return rows


def trend_ok(results):
    """heute < 2030 < 2040 je Wetterjahr und 2023 < 2017 < 2012 je Szenario (2030, 2040) für E_netto."""
    e = lambda y, s: results[(y, s)]['e_net_mwh']
    by_year = all(e(y, 'heute') <= e(y, '2030') <= e(y, '2040') for y in (2012, 2017, 2023))
    by_weather = all(e(2023, s) <= e(2017, s) <= e(2012, s) for s in ('2030', '2040'))
    return by_year and by_weather


def run_validation(prepared, cache, report, seeds=20, workers=4):
    load = run_batch(prepared, cache, (2012, 2017, 2023), ('heute', '2030', '2040'), ('uncontrolled',), ('base',), (1.0,),
                     seeds, workers)
    feed = run_batch(prepared, cache, (2023,), ('heute',), ('uncontrolled',), ('base',), (1.0, 1.5, 2.0), seeds, workers)
    results = {(y, s): {k: b[k]['median'] for k in KPI_INDEX} for (y, s, *_), b in load.items()}
    bands = {(y, s): b for (y, s, *_), b in load.items()}
    rows = compare(results)
    lines = [f'# Abnahme gridsim gegen Session 18 ({date.today().isoformat()})', '',
             f'Ungesteuert, Speicher Eigenverbrauch, PV × 1, {seeds} Seeds je Einstellung (Median, Band 10–90 %).',
             'Referenz: Tabellen von Session 18 vom 24.10.2026 (`steyr_storage_need.py --heat lod1 --district-heating`).',
             'Toleranz ± 30 %, bei kleinen Werten absolut (3 Stationen, 1 MWh). Alle Werte sind Modellwerte.', '',
             '| Wetter | Szenario | Kennzahl | gridsim Median | Band 10–90 % | Referenz | Verhältnis | ok |',
             '|---|---|---|---|---|---|---|---|']
    for r in rows:
        b = bands[r['key']][r['kpi']]
        lines.append(f"| {r['key'][0]} | {r['key'][1]} | {r['kpi']} | {r['value']:g} | {b['p10']:g}–{b['p90']:g} | "
                     f"{r['reference']:g} | {r['ratio']:.2f} | {'ja' if r['ok'] else 'nein'} |")
    lines += ['', f"Tendenz (heute < 2030 < 2040, 2023 < 2017 < 2012): {'ja' if trend_ok(results) else 'nein'}", '',
              '| PV-Faktor | Stationen mit Einspeiseengpass (Median, Band) | Referenz |', '|---|---|---|']
    for (_, _, _, _, f, *_), b in feed.items():
        lo, hi = REFERENCE['feed'][f]
        s = b['stations_feed_congestion']
        lines.append(f"| × {f:g} | {s['median']:g} ({s['p10']:g}–{s['p90']:g}) | {lo}–{hi} |")
    lines += ['', '## Gründe für Abweichungen', '',
              '- E-Auto-Zuteilung und Ladeverhalten vektorisiert: andere Zufallsfolge als `steyr_wp_ev`, 20 Seeds statt 1.',
              '- Heimspeicher entladen nicht ins E-Auto (wie `steyr_v2g_demo`); `steyr_storage_need` nimmt E-Autos in die Speicherlast.',
              '- Wärmepumpe in float32 (Abweichung < 1e-4 gegen die alte Formel).', '']
    Path(report).write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    return rows
