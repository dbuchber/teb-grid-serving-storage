"""Abnahmebericht NS-Leitungen (Spec 6, Task 11): Plausibilität, Abnahmegrenze „heute“, Modusvergleich.

Liest nur, was schon gerechnet ist: ``prepared/feeders/report.json`` und ``index.json`` (Netzbau) und die Seeds im
Cache (``<cache>/<key>/seed_<i>.json``, nur mit dem aktuellen Stand der Stationsnetze, ``run.cached_seeds``).
Gerechnet wird hier nur die optionale Diagnose (``segment_table`` für einen Seed).

Abnahmegrenze (Entscheidung 6, Global Constraints): Szenario heute, PV 1,0, Speicher base, ungesteuert,
Grenzmodus trafo, ohne Netzspeicher, Wetterjahre 2012/2017/2023; je Station und Jahr das P90 über die Seeds der
höchsten Abschnittsauslastung (``station_line_max_pct``, beide Richtungen), dann das Maximum über die Jahre.
Bestanden, wenn höchstens 5 Stationen über 100 % und keine über 120 % liegen, gleich wie viele Stationen die
Variante hat (Controller, Fix-Runde 1: 5 von 465 bei ``prepared-ns``). Gilt nur mit allen drei Wetterjahren und
mindestens ``MIN_SEEDS`` (20) Seeds je Jahr (Fix-Runde 5).
"""
import json
import re
import warnings
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import numpy as np

from gridsim import run as runmod

ACCEPT_PARAMS = {'scenario': 'heute', 'pv_factor': 1.0, 'storage': 'base', 'charging': 'uncontrolled',
                 'limits': 'trafo', 'netzspeicher': False}
ACCEPT_YEARS = (2012, 2017, 2023)
LIMIT_PCT, HARD_PCT = 100.0, 120.0
MAX_OVER = 5
MIN_SEEDS = 20     # Seeds je Wetterjahr, damit der Befund als Abnahme gilt (Fix-Runde 5)
SEVERITY = ('keiner', 'trafo', 'leitung', 'beide')     # Gleichstand: schwerere Klasse (wie web/gridsim/band.js)
CHAIN = ('heute', '2030', '2040')
ORDER = ('heute', '2030', '2040m', '2040r', '2040')   # Sortierung im Modusvergleich


# --- Cache lesen ------------------------------------------------------------------------------------------------

def cached_settings(cache, prepared):
    """{RunParams ohne n_seeds-Unterschied: [SeedResult]} aller Einstellungen im Cache mit dem aktuellen Netzstand.

    ``RunParams.n_seeds`` ist die Zahl der gefundenen Seeds (laut Manifest, nur vollständige Seeds zählen).
    """
    fp = runmod.feeders_fingerprint(prepared)
    out = {}
    for m in sorted(Path(cache).glob('*/manifest.json')):
        try:
            d = json.loads(m.read_text())
            params = runmod.RunParams(**d['params'])
        except (ValueError, TypeError, KeyError):
            continue
        if d.get('model_version') != runmod.MODEL_VERSION or params.key() != m.parent.name:
            continue
        seeds = runmod.cached_seeds(cache, params, fp)
        if seeds:
            seeds = sorted(seeds, key=lambda r: r.index)
            out[_norm(params, len(seeds))] = seeds
    return out


def _norm(params, n):
    d = asdict(params)
    d['n_seeds'] = n
    return runmod.RunParams(**d)


def find(settings, **kw):
    """Seeds der einzigen Einstellung, deren Felder zu ``kw`` passen; None, wenn keine (ValueError bei mehreren)."""
    hits = [r for p, r in settings.items() if all(getattr(p, k) == v for k, v in kw.items())]
    if len(hits) > 1:
        raise ValueError(f'mehrdeutig: {kw}')
    return hits[0] if hits else None


# --- Abnahmegrenze ----------------------------------------------------------------------------------------------

def station_p90(results, key='station_line_max_pct'):
    """P90 über die Seeds je Station (NaN für Stationen ohne Netz)."""
    arr = np.array([[np.nan if v is None else v for v in r.extra[key]] for r in results], dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)   # Stationen ohne Netz: NaN
        return np.nanpercentile(arr, 90, axis=0)


def acceptance(by_year, n_stations=None):
    """Abnahmegrenze aus ``{jahr: [SeedResult]}`` der Abnahmeeinstellung (siehe Moduldoku)."""
    years = {}
    p90s = []
    for y in sorted(by_year):
        p90 = station_p90(by_year[y])
        p90s.append(p90)
        years[y] = _verdict(p90, len(by_year[y]))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        worst = np.nanmax(np.vstack(p90s), axis=0) if p90s else np.zeros(0)
    n = int(n_stations if n_stations is not None else len(worst))
    out = {'years': years, 'combined': _verdict(worst, min((len(r) for r in by_year.values()), default=0)),
           'n_stations': n, 'max_over': MAX_OVER,
           'missing_years': [y for y in ACCEPT_YEARS if y not in by_year],
           'short_seeds': [y for y in sorted(by_year) if len(by_year[y]) < MIN_SEEDS], 'worst_p90': worst}
    c = out['combined']
    out['passed'] = (not out['missing_years'] and not out['short_seeds'] and c['over_100'] <= MAX_OVER
                     and c['over_120'] == 0)
    return out


def _verdict(p90, n_seeds):
    v = p90[np.isfinite(p90)]
    order = np.argsort(-np.nan_to_num(p90, nan=-1))
    return {'n_seeds': int(n_seeds), 'over_100': int((v > LIMIT_PCT).sum()), 'over_120': int((v > HARD_PCT).sum()),
            'median': float(np.median(v)) if len(v) else None, 'max': float(v.max()) if len(v) else None,
            'stations_over_100': [int(s) for s in order if np.isfinite(p90[s]) and p90[s] > LIMIT_PCT]}


# --- Engpass zuerst ---------------------------------------------------------------------------------------------

def station_class(results, key='station_first_load'):
    """Häufigste Klasse je Station über die Seeds (Gleichstand: schwerere); None ohne Netz."""
    n = len(results[0].extra[key])
    out = []
    for s in range(n):
        c = Counter(r.extra[key][s] for r in results if r.extra[key][s] is not None)
        out.append(max(c, key=lambda k: (c[k], SEVERITY.index(k))) if c else None)
    return out


def combined_class(load, feed):
    """Klasse über beide Richtungen: schwerere der beiden Richtungen je Station."""
    return [None if a is None else max(a, b, key=SEVERITY.index) for a, b in zip(load, feed)]


def class_counts(classes):
    c = Counter(x for x in classes if x is not None)
    return {k: int(c.get(k, 0)) for k in SEVERITY}


def chain(classes_by_scenario, end='2040'):
    """Reihenfolge heute → 2030 → 2040: je Station das erste Szenario mit Engpass und dessen Klasse.

    ``classes_by_scenario`` = {szenario: Klassen je Station}; Ergebnis: Zähler über (Szenario, Klasse) und
    ``'nie'`` für Stationen ohne Engpass bis zum letzten Szenario. ``end``: letztes Glied (2040 oder 2040r).
    """
    scen = [s for s in (*CHAIN[:-1], end) if s in classes_by_scenario]
    n = len(classes_by_scenario[scen[0]]) if scen else 0
    out = Counter()
    for i in range(n):
        for s in scen:
            c = classes_by_scenario[s][i]
            if c is None:
                break
            if c != 'keiner':
                out[(s, c)] += 1
                break
        else:
            out['nie'] += 1
    return dict(out)


def median_kpi(results, key):
    vals = [r.region.get(key) for r in results]
    if not vals or any(v is None for v in vals):
        return None
    return float(np.median(vals))


COMPARE_KPIS = ('stations_load_congestion', 'stations_line_load_congestion', 'stations_line_feed_congestion',
                'stations_line_only', 'line_over_m', 'ev_unmet_mwh', 'netzspeicher_n', 'netzspeicher_kwh',
                'netzspeicher_vollzyklen')


def compare_row(params, results):
    """Eine Zeile des Modusvergleichs: Einstellung, Medianwerte, Klassen (Bezug) je Station gezählt."""
    load = station_class(results, 'station_first_load')
    return {'year': params.weather_year, 'scenario': params.scenario, 'charging': params.charging,
            'limits': params.limits, 'netzspeicher': params.netzspeicher, 'n_seeds': len(results),
            **{k: median_kpi(results, k) for k in COMPARE_KPIS},
            'classes_load': class_counts(load),
            'classes_any': class_counts(combined_class(load, station_class(results, 'station_first_feed')))}


# --- Plausibilität ----------------------------------------------------------------------------------------------

def plausibility(rep):
    """Netzbau gegen Referenzwerte (Spec 4.1/4.2, Rechercheplan); Zeilen (Kennzahl, Wert, Ziel, im Ziel?)."""
    cs, km, fs = rep['cable_share'], rep['trunk_km_per_station'], rep['feeders_per_station']
    lo, hi = cs['band']
    rows = [('Kabelanteil nach Trassenlänge (Abnahmegröße)', f"{100 * cs['by_route_length']:.1f} %",
             f"{100 * cs['target']:.0f} % (Band {100 * lo:.0f}–{100 * hi:.0f} %)", lo <= cs['by_route_length'] <= hi),
            ('Kabelanteil nach Kabellänge', f"{100 * cs['by_cable_length']:.1f} %", 'nur Information', None),
            ('NS-Trasse je Station', f"{km['route_length']:.2f} km", f"ca. {km['target']} km", None),
            ('NS-Kabellänge je Station (Systeme einzeln)', f"{km['cable_length']:.2f} km", f"ca. {km['target']} km",
             None),
            ('Abgänge je Station (Mittel / Median)', f"{fs['mean']:.2f} / {fs['median']:g}",
             f"{fs['target'][0]}–{fs['target'][1]}", fs['target'][0] <= fs['mean'] <= fs['target'][1])]
    pb = rep.get('per_building')
    if pb:
        rows += [('Wohngebäude je Station (Mittel)', f"{pb['buildings_per_station']['mean']:.1f}",
                  f"ca. {pb['target']['buildings_per_station']}", None),
                 ('Trasse je Wohngebäude', f"{pb['route_m_per_building']:.1f} m",
                  f"ca. {pb['target']['route_m_per_building']} m", None)]
    return [(name, _comma(val), _comma(target), ok) for name, val, target, ok in rows]


def _comma(text):
    """Dezimalpunkt zwischen Ziffern → Komma (deutsche Schreibweise im Bericht)."""
    return re.sub(r'(\d)\.(\d)', r'\1,\2', text)


def type_table(rep):
    """Typverteilung (km, Systeme einzeln) mit Anteil an Strang bzw. Hausanschluss."""
    kt = rep['km_per_type']
    trunk = sum(v for k, v in kt.items() if 'Hausanschluss' not in k)
    svc = sum(v for k, v in kt.items() if 'Hausanschluss' in k)
    return [(k, v, 100 * v / (svc if 'Hausanschluss' in k else trunk)) for k, v in kt.items()]


# --- Diagnose: Abschnittstabelle eines Seeds ---------------------------------------------------------------------

def segment_table(p, params, i, feeders, stations):
    """Abschnittstabelle je Station für Seed ``i``: Typ, Länge, Grenzstrom, höchste Auslastung (%), Überlaststunden.

    {station: [zeile, ...]} mit Zeilen nach höchster Auslastung absteigend; ``tail`` = Abschnitt eines Ausläufers.
    Eine Rechnung von ``run.flows`` je Aufruf.
    """
    from gridsim.feeders.loading import loading_pct, segment_flow
    from gridsim.nodeflow import station_block
    f = runmod.flows(p, params, i, feeders=feeders)
    out = {}
    for s in stations:
        grid, sized = feeders[s]
        seg = segment_flow(grid, sized, station_block(p, params, f, s))
        pct = loading_pct(seg, sized)
        tail = np.zeros(len(grid.marked), bool) if grid.tail is None else np.asarray(grid.tail, bool)
        marked = np.asarray(grid.marked, bool) | np.asarray(sized.marked, bool)
        rows = []
        for j in range(pct.shape[1]):
            k = int(grid.feeder[j])
            col = pct[:, j]
            h = int(np.argmax(col))
            rows.append({'segment': j, 'feeder': k, 'type': sized.types[j], 'parallel': int(sized.parallel[j]),
                         'length_m': round(float(grid.length_m[j]), 1), 'service': bool(grid.service[j]),
                         'overhead': bool(grid.overhead[j]), 'tail': bool(tail[k]), 'marked': bool(marked[k]),
                         'i_max_a': float(sized.i_max_a[j]), 'max_pct': round(float(col[h]), 1),
                         'direction': 'Bezug' if seg[h, j] > 0 else 'Einspeisung',
                         'hours_over': int((col > LIMIT_PCT).sum()), 'n_downstream': int(grid.downstream[j].nnz)})
        out[s] = sorted(rows, key=lambda r: -r['max_pct'])
    return out


# --- Bericht ----------------------------------------------------------------------------------------------------

def _fmt(v, nd=0):
    if v is None:
        return '–'
    return f'{v:.{nd}f}'.replace('.', ',') if nd else f'{v:.0f}'


def render(rep, index, acc, rows, chains):
    """Markdown-Abschnitte des Abnahmeberichts (deutsch)."""
    n = rep['n_stations']
    L = ['## Plausibilität des Netzbaus', '', '| Kennzahl | Wert | Ziel | im Ziel |', '|---|---|---|---|']
    for name, val, target, ok in plausibility(rep):
        L.append(f"| {name} | {val} | {target} | {'–' if ok is None else 'ja' if ok else 'nein'} |")
    L += ['', '| Typ | km | Anteil |', '|---|---|---|']
    for k, v, share in type_table(rep):
        L.append(f'| {k} | {_fmt(v, 1)} | {_fmt(share, 1)} % |')
    mk, tl = rep['marked'], rep['tails']
    L += ['', f"Markierte Abgänge: {mk['feeders_any']} Abgänge an {mk['stations_any']} von {n} Stationen "
              f"({_fmt(100 * mk['stations_any_share'], 1)} %, Grenze 10 %); davon zu lang {mk['feeders_long']}, "
              f"Strom zu hoch {mk['feeders_sizing']}. Ausläufer (nicht markiert): {tl['feeders']} Abgänge an "
              f"{tl['stations']} Stationen.", '']
    vo = rep.get('voltage_only')
    if vo:
        by = vo['stations_by_area']
        L += [f"Nur Spannung (zählt nicht zur 10-%-Grenze): {vo['feeders']} Abgänge an {vo['stations']} Stationen "
              f"({_fmt(100 * vo['stations_share'], 1)} %; " + ', '.join(f'{a} {by.get(a, 0)}' for a in ('stadt', 'ort', 'streu'))
              + "). Dort müsste ein realer Netzbetreiber wegen der Spannung handeln.", '']
    areas = Counter(v['area'] for v in index.values())
    L += ['Gebietstypen: ' + ', '.join(f'{a} {areas.get(a, 0)}' for a in ('stadt', 'ort', 'streu')), '']
    L += ['## Abnahmegrenze „heute“', '']
    if acc is None:
        L += ['Nicht gerechnet (Abnahmeeinstellung fehlt im Cache).', '']
    else:
        c = acc['combined']
        L += ['| Wetterjahr | Seeds | Stationen > 100 % | Stationen > 120 % | Median P90 | Max P90 |',
              '|---|---|---|---|---|---|']
        for y, v in acc['years'].items():
            L.append(f"| {y} | {v['n_seeds']} | {v['over_100']} | {v['over_120']} | {_fmt(v['median'], 1)} % | "
                     f"{_fmt(v['max'], 1)} % |")
        L.append(f"| alle (Maximum je Station) | {c['n_seeds']} | {c['over_100']} | {c['over_120']} | "
                 f"{_fmt(c['median'], 1)} % | {_fmt(c['max'], 1)} % |")
        L += ['', f"Regel: höchstens {acc['max_over']} von {acc['n_stations']} Stationen über 100 %, keine über "
                  f"120 %. Ergebnis: **{'bestanden' if acc['passed'] else 'nicht bestanden'}**"
                  f" ({c['over_100']} über 100 %, {c['over_120']} über 120 %)."]
        if acc['missing_years']:
            L.append(f"Fehlende Wetterjahre: {acc['missing_years']}.")
        if acc['short_seeds']:
            L.append(f"Weniger als {MIN_SEEDS} Seeds in den Wetterjahren {acc['short_seeds']}.")
        L.append('')
    if rows:
        L += ['## Vergleich der Modi', '',
              '| Wetter | Szenario | Laden | Grenzen | Netzspeicher | Seeds | Trafo-Engpass | Leitung Bezug | '
              'Leitung Einsp. | nur Leitung | Überlast km | ungeladen MWh | NS Anzahl | NS kWh | '
              'Bezug: Trafo / Leitung / beide / keiner |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for r in rows:
            cl = r['classes_load']
            km = None if r['line_over_m'] is None else r['line_over_m'] / 1000
            L.append(f"| {r['year']} | {r['scenario']} | {r['charging']} | {r['limits']} | "
                     f"{'an' if r['netzspeicher'] else 'aus'} | {r['n_seeds']} | {_fmt(r['stations_load_congestion'])} | "
                     f"{_fmt(r['stations_line_load_congestion'])} | {_fmt(r['stations_line_feed_congestion'])} | "
                     f"{_fmt(r['stations_line_only'])} | {_fmt(km, 1)} | {_fmt(r['ev_unmet_mwh'], 1)} | "
                     f"{_fmt(r['netzspeicher_n'])} | {_fmt(r['netzspeicher_kwh'])} | "
                     f"{cl['trafo']} / {cl['leitung']} / {cl['beide']} / {cl['keiner']} |")
        L.append('')
    if chains:
        L += ['## Reihenfolge heute → 2030 → 2040r bzw. 2040 (ungesteuert, Grenzmodus trafo)', '',
              '| Wetter (letztes Glied) | zuerst Trafo | zuerst Leitung | beide zugleich | nie | davon schon heute (T / L / b) |',
              '|---|---|---|---|---|---|']
        for y, ch in chains.items():
            def tot(cls):
                return sum(v for k, v in ch.items() if k != 'nie' and k[1] == cls)
            today = '/'.join(str(ch.get(('heute', c), 0)) for c in ('trafo', 'leitung', 'beide'))
            L.append(f"| {y} | {tot('trafo')} | {tot('leitung')} | {tot('beide')} | {ch.get('nie', 0)} | {today} |")
        L.append('')
    return '\n'.join(L)


def lines_report(prepared, cache, report):
    """Schreibt ``report`` (Markdown) und ``report`` mit Endung ``.json`` (alle Zahlen); gibt das JSON zurück."""
    root = Path(prepared)
    rep = json.loads((root / 'feeders' / 'report.json').read_text())
    index = json.loads((root / 'feeders' / 'index.json').read_text())
    settings = cached_settings(cache, root)
    by_year = {y: r for y in ACCEPT_YEARS
               if (r := find(settings, weather_year=y, **ACCEPT_PARAMS)) is not None}
    acc = acceptance(by_year, rep['n_stations']) if by_year else None
    keys = sorted(settings, key=lambda p: (p.weather_year, ORDER.index(p.scenario) if p.scenario in ORDER else 9,
                                           runmod.CHARGING.index(p.charging), p.limits, p.netzspeicher))
    rows = [compare_row(p, settings[p]) for p in keys if p.pv_factor == 1.0 and p.storage == 'base']
    chains = {}
    for end in ('2040r', '2040'):
        steps = (*CHAIN[:-1], end)
        for y in sorted({p.weather_year for p in settings}):
            cls = {}
            for s in steps:
                r = find(settings, weather_year=y, **{**ACCEPT_PARAMS, 'scenario': s})
                if r is not None:
                    cls[s] = combined_class(station_class(r, 'station_first_load'),
                                            station_class(r, 'station_first_feed'))
            if set(cls) == set(steps):
                chains[y if end == '2040' else f'{y} bis 2040r'] = chain(cls, end=end)
    md = render(rep, index, acc, rows, chains)
    Path(report).parent.mkdir(parents=True, exist_ok=True)
    Path(report).write_text(md + '\n', encoding='utf-8')
    data = {'plausibility': [list(r) for r in plausibility(rep)], 'types': type_table(rep),
            'marked': rep['marked'], 'voltage_only': rep.get('voltage_only'), 'tails': rep['tails'],
            'acceptance': None if acc is None else {**acc, 'worst_p90': [None if not np.isfinite(x) else round(float(x), 1)
                                                                          for x in acc['worst_p90']]},
            'compare': rows, 'chains': {y: {('nie' if k == 'nie' else f'{k[0]}:{k[1]}'): v for k, v in ch.items()}
                                        for y, ch in chains.items()}}
    Path(report).with_suffix('.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
    return data
