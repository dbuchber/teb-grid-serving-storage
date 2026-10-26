"""Kommandozeile: prepare, prepare-feeders, batch, precompute (Pitch-Minimum), validate, lines-report."""
import argparse
import csv
import itertools
import json
import time
from pathlib import Path

from gridsim import run as runmod

KPIS = ('stations_load_congestion', 'stations_feed_congestion', 'congestion_h_median', 'e_net_mwh', 'storage_units',
        'trafo_plus1', 'trafo_plus2', 'trafo_over_1000', 'ev_unmet_mwh')
PITCH_MINIMUM = {'years': (2012, 2023), 'scenarios': ('2030', '2040'), 'charging': runmod.CHARGING,
                 'storage': ('base',), 'pv': (1.0,)}


LINE_KPIS = ('stations_line_load_congestion', 'stations_line_feed_congestion', 'stations_line_only', 'line_over_m',
             'netzspeicher_n', 'netzspeicher_kwh', 'netzspeicher_kw', 'netzspeicher_vollzyklen')
NETZSPEICHER = {'off': False, 'on': True}
SAME_IN_LINE_MODE = ('uncontrolled', 'winap')   # Ladezeiten fest: trafo+leitung rechnet dasselbe wie trafo


def combos(years, scenarios, charging, storage, pv, limits=('trafo',), netzspeicher=(False,)):
    """Alle Einstellungen der Matrix; ``trafo+leitung`` entfällt für ungesteuert/WiNAP (identisch zu ``trafo``)."""
    for c in itertools.product(years, scenarios, charging, storage, pv, limits, netzspeicher):
        if c[5] == 'trafo+leitung' and c[2] in SAME_IN_LINE_MODE and 'trafo' in limits:
            continue
        yield c


def run_batch(prepared, cache, years, scenarios, charging, storage, pv, n_seeds=20, workers=4, limits=('trafo',),
              netzspeicher=(False,)):
    """Läuft die Matrix und schreibt je Einstellung ``region.csv``; Schlüssel (Jahr, Szenario, Laden, Speicher,
    PV, Grenzmodus, Netzspeicher). Leitungs- und Netzspeicherbänder nur, wenn der Lauf sie liefert (sonst None)."""
    out = {}
    for y, s, c, st, f, lim, ns in combos(years, scenarios, charging, storage, pv, limits, netzspeicher):
        params = runmod.RunParams(weather_year=y, scenario=s, pv_factor=f, charging=c, storage=st, n_seeds=n_seeds,
                                  limits=lim, netzspeicher=ns)
        t = time.perf_counter()
        results = list(runmod.run_many(prepared, params, workers=workers, cache_dir=cache))
        bands = {k: runmod.band(results, k) for k in KPIS}
        for k in LINE_KPIS:
            vals = [r.region.get(k) for r in results]
            bands[k] = None if any(v is None for v in vals) else runmod.band(results, k)
        d = Path(cache) / params.key()
        with open(d / 'region.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh, delimiter=';')
            w.writerow(['kpi', 'median', 'p10', 'p90', 'n'])
            for k, b in bands.items():
                if b is not None:
                    w.writerow([k, b['median'], b['p10'], b['p90'], b['n']])
        out[(y, s, c, st, f, lim, ns)] = bands
        line = bands['stations_line_load_congestion']
        print(json.dumps({'year': y, 'scenario': s, 'charging': c, 'storage': st, 'pv': f, 'limits': lim,
                          'netzspeicher': ns, 'key': params.key(),
                          'wall_s': round(time.perf_counter() - t, 1),
                          'seed_s_max': max(r.runtime_s for r in results),
                          'stations_load_congestion': bands['stations_load_congestion']['median'],
                          'stations_line_load_congestion': None if line is None else line['median'],
                          'e_net_mwh': bands['e_net_mwh']['median']}, ensure_ascii=False), flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog='gridsim')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare', help='Eingangsdaten je Wetterjahr nach --out/<jahr> verdichten')
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--years', type=int, nargs='+', default=list(runmod.WEATHER_YEARS))
    p.add_argument('--out', type=Path, required=True)
    f = sub.add_parser('prepare-feeders', help='synthetische NS-Stationsnetze je Station nach <prepared>/feeders/ '
                       '(nach jedem gridsim prepare neu ausführen)')
    f.add_argument('--input', type=Path, required=True)
    f.add_argument('--prepared', type=Path, required=True)
    f.add_argument('--extra-stations', action='store_true',
                   help='Zusatzstationen für zu lange Abgänge; schreibt eine neue Variante nach --out')
    f.add_argument('--out', type=Path, help='Ausgabeordner der Variante (nur mit --extra-stations, dort Pflicht)')
    helps = {'batch': 'Läufe für alle Kombinationen der Optionen in den Cache rechnen',
             'precompute': 'Mindestumfang für die Live-Demo in den Cache rechnen',
             'validate': 'Abnahme gegen die Referenzskripte (schreibt --report)'}
    for name in ('batch', 'precompute', 'validate'):
        b = sub.add_parser(name, help=helps[name])
        b.add_argument('--prepared', type=Path, required=True)
        b.add_argument('--cache', type=Path, required=True)
        b.add_argument('--seeds', type=int, default=20)
        b.add_argument('--workers', type=int, default=4)  # hetzner: Speicherbandbreite sättigt ab ca. 4 Prozessen
        if name == 'batch':
            b.add_argument('--years', type=int, nargs='+', default=[2023])
            b.add_argument('--scenarios', nargs='+', default=['2030'])
            b.add_argument('--charging', nargs='+', default=['uncontrolled'])
            b.add_argument('--storage', nargs='+', default=['base'])
            b.add_argument('--pv', type=float, nargs='+', default=[1.0])
            b.add_argument('--limits', nargs='+', default=['trafo'], choices=runmod.LIMITS,
                           help='Grenzen der Steuerung: trafo (Standard, nur Trafo-Grenze) oder '
                                'trafo+leitung (braucht <prepared>/feeders/, sonst Rückfall auf trafo)')
            b.add_argument('--netzspeicher', nargs='+', default=['off'], choices=list(NETZSPEICHER),
                           help='Netzspeicher an Leitungsengpässen: off (Standard) oder on (braucht feeders/)')
        if name == 'validate':
            b.add_argument('--report', type=Path, default=Path('docs/gridsim-abnahme.md'))
    lr = sub.add_parser('lines-report', help='Abnahmebericht NS-Leitungen aus prepared/feeders und dem Cache')
    lr.add_argument('--prepared', type=Path, required=True)
    lr.add_argument('--cache', type=Path, required=True)
    lr.add_argument('--report', type=Path, required=True, help='Markdown; Zahlen zusätzlich als .json daneben')
    args = ap.parse_args(argv)
    if args.cmd == 'prepare':
        from gridsim.prepare import prepare
        for y in args.years:
            prepare(args.input, y, args.out)
            print('prepared', y)
    elif args.cmd == 'prepare-feeders':
        from gridsim.feeders.prepare import prepare_feeders
        if args.out is not None and not args.extra_stations:
            ap.error('--out gilt nur mit --extra-stations (ohne schreibt prepare-feeders nach <prepared>/feeders/)')
        if args.extra_stations:
            if args.out is None:
                ap.error('--extra-stations braucht --out')
            from gridsim.feeders.extra_stations import prepare_extra_stations
            out = prepare_extra_stations(args.input, args.prepared, args.out)
        else:
            out = prepare_feeders(args.input, args.prepared)
        report = json.loads((out / 'report.json').read_text())
        print(json.dumps({k: report[k] for k in ('marked', 'extra_stations') if k in report}, ensure_ascii=False))
        print('prepared feeders', out)
    elif args.cmd == 'batch':
        run_batch(args.prepared, args.cache, args.years, args.scenarios, args.charging, args.storage, args.pv,
                  args.seeds, args.workers, args.limits, [NETZSPEICHER[x] for x in args.netzspeicher])
    elif args.cmd == 'precompute':
        m = PITCH_MINIMUM
        run_batch(args.prepared, args.cache, m['years'], m['scenarios'], m['charging'], m['storage'], m['pv'],
                  args.seeds, args.workers)
    elif args.cmd == 'lines-report':
        from gridsim.feeders.report import lines_report
        data = lines_report(args.prepared, args.cache, args.report)
        acc = data['acceptance']
        print(json.dumps(None if acc is None else {k: acc[k] for k in ('passed', 'missing_years')}
                         | {'over_100': acc['combined']['over_100'], 'over_120': acc['combined']['over_120']}))
        print('report', args.report)
    elif args.cmd == 'validate':
        from gridsim.validate import run_validation
        run_validation(args.prepared, args.cache, args.report, args.seeds, args.workers)
