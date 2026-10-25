"""Kommandozeile: prepare, prepare-feeders, batch, precompute (Pitch-Minimum), validate."""
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


def run_batch(prepared, cache, years, scenarios, charging, storage, pv, n_seeds=20, workers=4):
    out = {}
    for y, s, c, st, f in itertools.product(years, scenarios, charging, storage, pv):
        params = runmod.RunParams(weather_year=y, scenario=s, pv_factor=f, charging=c, storage=st, n_seeds=n_seeds)
        t = time.perf_counter()
        results = list(runmod.run_many(prepared, params, workers=workers, cache_dir=cache))
        bands = {k: runmod.band(results, k) for k in KPIS}
        d = Path(cache) / params.key()
        with open(d / 'region.csv', 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh, delimiter=';')
            w.writerow(['kpi', 'median', 'p10', 'p90', 'n'])
            for k, b in bands.items():
                w.writerow([k, b['median'], b['p10'], b['p90'], b['n']])
        out[(y, s, c, st, f)] = bands
        print(json.dumps({'year': y, 'scenario': s, 'charging': c, 'storage': st, 'pv': f, 'key': params.key(),
                          'wall_s': round(time.perf_counter() - t, 1),
                          'seed_s_max': max(r.runtime_s for r in results),
                          'stations_load_congestion': bands['stations_load_congestion']['median'],
                          'e_net_mwh': bands['e_net_mwh']['median']}, ensure_ascii=False), flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog='gridsim')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--years', type=int, nargs='+', default=list(runmod.WEATHER_YEARS))
    p.add_argument('--out', type=Path, required=True)
    f = sub.add_parser('prepare-feeders')
    f.add_argument('--input', type=Path, required=True)
    f.add_argument('--prepared', type=Path, required=True)
    f.add_argument('--extra-stations', action='store_true',
                   help='Zusatzstationen für zu lange Abgänge; schreibt eine neue Variante nach --out')
    f.add_argument('--out', type=Path, help='Ausgabeordner der Variante (nur mit --extra-stations)')
    for name in ('batch', 'precompute', 'validate'):
        b = sub.add_parser(name)
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
        if name == 'validate':
            b.add_argument('--report', type=Path, default=Path('docs/gridsim-abnahme.md'))
    args = ap.parse_args(argv)
    if args.cmd == 'prepare':
        from gridsim.prepare import prepare
        for y in args.years:
            prepare(args.input, y, args.out)
            print('prepared', y)
    elif args.cmd == 'prepare-feeders':
        from gridsim.feeders.prepare import prepare_feeders
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
                  args.seeds, args.workers)
    elif args.cmd == 'precompute':
        m = PITCH_MINIMUM
        run_batch(args.prepared, args.cache, m['years'], m['scenarios'], m['charging'], m['storage'], m['pv'],
                  args.seeds, args.workers)
    elif args.cmd == 'validate':
        from gridsim.validate import run_validation
        run_validation(args.prepared, args.cache, args.report, args.seeds, args.workers)
