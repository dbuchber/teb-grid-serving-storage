"""Abspielwoche: Trafo-Auslastung aller Stationen Stunde für Stunde über 7 Tage, als JSON für die Präsentation.

Auslastung = Fluss / Nennleistung in Prozent, positiv = Bezug, negativ = Rückspeisung. Ein Seed, keine Bandbreite.
"""
import argparse
import itertools
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from gridsim.data import load_prepared
from gridsim.run import RunParams, flows, seed_of

HOURS = 168


def week_pct(flow, kva, start_day):
    """(S, 168) ganzzahlige Prozent der Nennleistung ab Tag start_day (0 = 1. Jänner)."""
    w = np.asarray(flow, dtype=float)[start_day * 24:start_day * 24 + HOURS]
    return np.rint(100 * w / np.asarray(kva, dtype=float)).astype(int).T


def busiest_week(flow, kva, first_weekday, direction='load'):
    """Erster Tag (Montag) der Woche mit den meisten Stationsstunden über der Nennleistung."""
    f = np.asarray(flow, dtype=float)
    f = f if direction == 'load' else -f
    over = (f > np.asarray(kva, dtype=float)).sum(axis=1)
    days = over[:over.shape[0] // 24 * 24].reshape(-1, 24).sum(axis=1)
    mondays = [d for d in range(len(days) - 6) if (first_weekday + d) % 7 == 0]
    return max(mondays, key=lambda d: (days[d:d + 7].sum(), -d))


def export_week(p, params, start_day, path, seed_index=0):
    pct = week_pct(flows(p, params, seed_index)['flow'], p.kva, start_day)
    d = {'start': (date(p.year, 1, 1) + timedelta(days=start_day)).isoformat(), 'hours': HOURS,
         'params': {k: getattr(params, k) for k in ('weather_year', 'scenario', 'pv_factor', 'charging', 'storage')},
         'seed_index': seed_index, 'seed': seed_of(seed_index), 'stations': p.station_ids,
         'kva': [float(k) for k in p.kva], 'pct': pct.tolist()}
    Path(path).write_text(json.dumps(d, separators=(',', ':')))
    return d


# Voreinstellungen der Präsentation: Winter (Bezug) und Sommer (Rückspeisung), je Woche mit den meisten Engpassstunden
WINTER = {'scenario': ('2040m', '2040'), 'charging': ('uncontrolled', 'controlled', 'v2g')}
SUMMER = {'scenario': ('heute',), 'pv_factor': (1.0, 1.5, 2.0), 'storage': ('base', 'room')}


def main(argv=None):
    ap = argparse.ArgumentParser(prog='gridsim.playback')
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--years', type=int, nargs='+', default=[2012, 2017, 2023])
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    index = []
    for y in args.years:
        p = load_prepared(args.prepared, y)
        # Woche je Jahr aus dem schwersten Fall wählen, damit die Varianten dieselben Stunden zeigen
        w_day = busiest_week(flows(p, RunParams(weather_year=y, scenario='2040'), 0)['flow'], p.kva, p.first_weekday)
        s_day = busiest_week(flows(p, RunParams(weather_year=y, scenario='heute', pv_factor=2.0), 0)['flow'],
                             p.kva, p.first_weekday, direction='feed')
        for season, grid, day in (('winter', WINTER, w_day), ('summer', SUMMER, s_day)):
            keys = list(grid)
            for values in itertools.product(*grid.values()):
                params = RunParams(weather_year=y, **dict(zip(keys, values)))
                name = '_'.join([season, str(y), *map(str, values)]) + '.json'
                d = export_week(p, params, day, args.out / name)
                index.append({'file': name, 'season': season, 'start': d['start'], **d['params']})
                print(name, flush=True)
    (args.out / 'index.json').write_text(json.dumps(index, indent=1))


if __name__ == '__main__':
    main()
