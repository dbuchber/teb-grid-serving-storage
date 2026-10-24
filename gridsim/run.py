"""Ein Lauf = eine Einstellung (RunParams) über mehrere Seeds; Seeds parallel im Prozesspool, Ergebnisse im Cache."""
import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from gridsim import control, legacy, metrics, profiles
from gridsim.data import load_prepared

WEATHER_YEARS = (2012, 2017, 2023)
SCENARIOS = ('heute', '2030', '2040')
PV_FACTORS = (1.0, 1.5, 2.0)
CHARGING = ('uncontrolled', 'winap', 't3d', 'controlled', 'v2g')
STORAGE = ('base', 'forecast', 'room')
BASE_SEED = 20261024
MAX_SEEDS = 50


@dataclass(frozen=True)
class RunParams:
    weather_year: int = 2023
    scenario: str = '2030'
    pv_factor: float = 1.0
    charging: str = 'uncontrolled'
    storage: str = 'base'
    n_seeds: int = 20

    def validate(self):
        allowed = {'weather_year': WEATHER_YEARS, 'scenario': SCENARIOS, 'pv_factor': PV_FACTORS,
                   'charging': CHARGING, 'storage': STORAGE}
        for name, values in allowed.items():
            if getattr(self, name) not in values:
                raise ValueError(f'{name} must be one of {list(values)}, got {getattr(self, name)!r}')
        if not (isinstance(self.n_seeds, int) and 1 <= self.n_seeds <= MAX_SEEDS):
            raise ValueError(f'n_seeds must be 1..{MAX_SEEDS}, got {self.n_seeds!r}')

    def key(self):
        d = asdict(self)
        d.pop('n_seeds')  # Seeds sind fest je Index; mehr Seeds ergänzen dieselbe Einstellung
        return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:12]


@dataclass
class SeedResult:
    index: int
    seed: int
    region: dict
    station_load_kw_max: list
    station_congestion_h: list
    station_feed_h: list
    worst_day: list
    runtime_s: float = 0.0
    extra: dict = field(default_factory=dict)


def seed_of(i):
    return BASE_SEED + 1000 * i


def flows(p, params, i):
    """Zwischenschritte eines Seeds: Fluss ohne E-Auto, E-Auto-Last, Endfluss je Station, ungeladene Energie."""
    seed = seed_of(i)
    rng = np.random.default_rng(seed)
    heat, cars = profiles.assign(p, params.scenario, rng)
    wp_st, wp_sto = profiles.heat_pump(p, heat, seed)
    ev = profiles.ev_events(p, cars, rng)
    base = control.storage_flow(p, params.pv_factor, params.storage, wp_st, wp_sto)
    s = p.n_stations
    if params.charging == 'winap':
        start = control.start_winap(ev, p.year)
    elif params.charging == 't3d':
        start = control.start_t3d_forecast(ev, base, p.kva, p.year)
    else:
        start = control.start_uncontrolled(ev)
    ev_load = control.render(ev, start, s)
    unmet, v2g = None, np.zeros_like(ev_load)
    if params.charging in ('controlled', 'v2g'):
        ev_load, unmet = control.controlled(base, ev_load, p.kva)
        if params.charging == 'v2g':
            cars_st = np.bincount(np.asarray(p.nodes_station), weights=cars, minlength=s)
            v2g = control.v2g(np.maximum(base + ev_load - p.kva[None, :], 0), cars_st)
    flow = np.asarray(base, dtype=float) + ev_load - v2g
    return {'heat': heat, 'cars': cars, 'wp_station': wp_st, 'ev': ev, 'start': start, 'base': base,
            'ev_load': ev_load, 'v2g': v2g, 'flow': flow, 'unmet': unmet}


def run_seed(p, params, i):
    t = time.perf_counter()
    f = flows(p, params, i)
    flow, kva = f['flow'], p.kva
    rows_load = metrics.station_rows(flow, kva, None)
    rows_feed = metrics.station_rows(-flow, kva, None)
    region = metrics.region_kpis(rows_load, rows_feed, f['unmet'], p.n_stations)
    daily_max = flow[:flow.shape[0] // 24 * 24].reshape(-1, 24, flow.shape[1]).max(axis=1)
    return SeedResult(index=i, seed=seed_of(i), region=region,
                      station_load_kw_max=[round(float(x), 1) for x in flow.max(axis=0)],
                      station_congestion_h=[r['engpass_h_jahr'] if r else 0 for r in rows_load],
                      station_feed_h=[r['engpass_h_jahr'] if r else 0 for r in rows_feed],
                      worst_day=[int(x) for x in daily_max.argmax(axis=0)],
                      runtime_s=round(time.perf_counter() - t, 2))


def code_version():
    if os.environ.get('GRIDSIM_VERSION'):
        return os.environ['GRIDSIM_VERSION']
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=Path(__file__).parent, capture_output=True,
                              text=True, timeout=5).stdout.strip() or 'unknown'
    except (OSError, subprocess.SubprocessError):
        return 'unknown'


def _seed_path(cache_dir, params, i):
    return Path(cache_dir) / params.key() / f'seed_{i}.json'


def cached_seeds(cache_dir, params):
    out = []
    for i in range(params.n_seeds):
        path = _seed_path(cache_dir, params, i)
        if path.exists():
            out.append(SeedResult(**json.loads(path.read_text())))
    return out


def _write_manifest(cache_dir, root, params, runtime):
    d = Path(cache_dir) / params.key()
    prep = Path(root) / str(params.weather_year) / 'manifest.json'
    manifest = {'params': asdict(params), 'code_version': code_version(), 'legacy_frozen_at': legacy.FROZEN_AT,
                'legacy_sha256sums': hashlib.sha256((legacy.DIR / 'SHA256SUMS').read_bytes()).hexdigest(),
                'prepared_manifest_sha256': hashlib.sha256(prep.read_bytes()).hexdigest() if prep.exists() else None,
                'seeds': [seed_of(i) for i in range(params.n_seeds)], 'runtime_s': round(runtime, 1)}
    (d / 'manifest.json').write_text(json.dumps(manifest, indent=1))


_WORKER = {}


def _init(root, year):
    _WORKER['p'] = load_prepared(root, year)


def _work(params, i):
    return run_seed(_WORKER['p'], params, i)


def run_many(root, params, workers=4, cache_dir=None):
    """Alle Seeds der Einstellung, in Fertigstellungsreihenfolge; Gecachtes zuerst."""
    params.validate()
    t = time.perf_counter()
    done = {r.index: r for r in cached_seeds(cache_dir, params)} if cache_dir else {}
    yield from done.values()
    todo = [i for i in range(params.n_seeds) if i not in done]
    if todo:
        if cache_dir:
            (Path(cache_dir) / params.key()).mkdir(parents=True, exist_ok=True)
        with ProcessPoolExecutor(max_workers=max(1, min(workers, len(todo))), initializer=_init,
                                 initargs=(str(root), params.weather_year)) as pool:
            futures = [pool.submit(_work, params, i) for i in todo]
            for fut in as_completed(futures):
                r = fut.result()
                if cache_dir:
                    _seed_path(cache_dir, params, r.index).write_text(json.dumps(asdict(r)))
                yield r
        if cache_dir:
            _write_manifest(cache_dir, root, params, time.perf_counter() - t)


def band(results, key):
    vals = np.array([r.region[key] for r in results], dtype=float)
    return {'median': float(np.median(vals)), 'p10': float(np.percentile(vals, 10)),
            'p90': float(np.percentile(vals, 90)), 'n': len(vals)}
