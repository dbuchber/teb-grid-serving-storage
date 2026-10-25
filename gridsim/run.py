"""Ein Lauf = eine Einstellung (RunParams) über mehrere Seeds; Seeds parallel im Prozesspool, Ergebnisse im Cache."""
import hashlib
import json
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field, replace
from functools import lru_cache
from pathlib import Path

import numpy as np

from gridsim import control, control_lines, legacy, metrics, netzspeicher, profiles
from gridsim.data import load_prepared
from gridsim.feeders.loading import loading_pct, segment_flow
from gridsim.feeders.prepare import load_feeders
from gridsim.nodeflow import station_block

WEATHER_YEARS = (2012, 2017, 2023)
SCENARIOS = ('heute', '2030', '2040m', '2040')
PV_FACTORS = (1.0, 1.5, 2.0)
CHARGING = ('uncontrolled', 'winap', 't3d', 'controlled', 'v2g')
STORAGE = ('base', 'forecast', 'room')
LIMITS = ('trafo', 'trafo+leitung')
BASE_SEED = 20261024
# Bei jeder Änderung an Modell oder Kennzahlen erhöhen: Teil des Cache-Schlüssels, alte Ergebnisse gelten dann nicht mehr
MODEL_VERSION = '2026-10-26.3'  # .3: heute aus Ist-Abgleich, Mindestquerschnitt (Fix-Runde 2); .2: Fix-Runde 1
MAX_SEEDS = 50


@dataclass(frozen=True)
class RunParams:
    """Einstellung eines Laufs.

    ``limits``: Grenzmodus der Steuerung (Spec 4.5), ``'trafo'`` = bisheriges Verhalten (Trafo-Kennzahlen
    bitgleich), ``'trafo+leitung'`` = gesteuertes Laden, V2G und T3d auch gegen Abschnittsgrenzen
    (control_lines.py; ohne Stationsnetze wie ``'trafo'``, vermerkt in ``extra['limits_effective']``).
    ``netzspeicher``: Netzspeicher am Leitungsengpass (Spec 4.6, netzspeicher.py) an/aus; Ort und Größe aus dem
    Auslegungslauf (``netzspeicher_plan``), ohne Stationsnetze wie aus (vermerkt in
    ``extra['netzspeicher_effective']``).
    """
    weather_year: int = 2023
    scenario: str = '2030'
    pv_factor: float = 1.0
    charging: str = 'uncontrolled'
    storage: str = 'base'
    n_seeds: int = 20
    limits: str = 'trafo'
    netzspeicher: bool = False

    def validate(self):
        allowed = {'weather_year': WEATHER_YEARS, 'scenario': SCENARIOS, 'pv_factor': PV_FACTORS,
                   'charging': CHARGING, 'storage': STORAGE, 'limits': LIMITS}
        for name, values in allowed.items():
            if getattr(self, name) not in values:
                raise ValueError(f'{name} must be one of {list(values)}, got {getattr(self, name)!r}')
        if not isinstance(self.netzspeicher, bool):
            raise ValueError(f'netzspeicher must be true or false, got {self.netzspeicher!r}')
        if not (isinstance(self.n_seeds, int) and 1 <= self.n_seeds <= MAX_SEEDS):
            raise ValueError(f'n_seeds must be 1..{MAX_SEEDS}, got {self.n_seeds!r}')

    def key(self):
        d = asdict(self)
        d.pop('n_seeds')  # Seeds sind fest je Index; mehr Seeds ergänzen dieselbe Einstellung
        d['model_version'] = MODEL_VERSION
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
    feeders_fp: str = None   # Fingerabdruck der Stationsnetze (feeders_fingerprint), None = unbekannt


def seed_of(i):
    return BASE_SEED + 1000 * i


FIXED_START = ('uncontrolled', 'winap', 't3d')   # Ladezeiten stehen vor dem Netzspeicher fest


def flows(p, params, i, feeders=None, plan=None):
    """Zwischenschritte eines Seeds: Fluss ohne E-Auto, E-Auto-Last, Endfluss je Station, ungeladene Energie.

    ``storage_delta``/``storage_idx``: Wirkung der Heimspeicher je Speicherknoten, ``seed``: Seed des Laufs; beides
    für Knotenflüsse (nodeflow.py). ``feeders``: Stationsnetze für den Grenzmodus ``'trafo+leitung'``; dann stehen
    die Knotenentscheidungen von gesteuertem Laden/V2G in ``node_decisions``. ``limits_effective``: tatsächlich
    gerechneter Grenzmodus (``'trafo'``, wenn Netze fehlen).

    Netzspeicher (``params.netzspeicher``, ``plan`` aus ``netzspeicher_plan``, braucht ``feeders``): Reihenfolge
    Grundfluss (Haushalt, PV, Wärmepumpe, Heimspeicher) → Netzspeicher → E-Auto-Steuerung. Der Netzspeicher sieht
    dazu die E-Auto-Last, deren Startzeiten schon feststehen (ungesteuert, WiNAP, T3d; das T3d-Signal kommt daher
    ohne Netzspeicher zustande); gesteuertes Laden und V2G reagieren auf ihn. Seine Leistung steht in ``ns_kw``
    (8760, k) an den globalen Knoten ``ns_idx`` und ist in ``base`` und ``flow`` enthalten.
    """
    seed = seed_of(i)
    rng = np.random.default_rng(seed)
    heat, cars = profiles.assign(p, params.scenario, rng)
    wp_st, wp_sto = profiles.heat_pump(p, heat, seed)
    ev = profiles.ev_events(p, cars, rng)
    base, storage_delta, storage_idx = control.storage_flow(p, params.pv_factor, params.storage, wp_st, wp_sto,
                                                            return_delta=True)
    s = p.n_stations
    lines = params.limits == 'trafo+leitung' and feeders is not None
    part = {'heat': heat, 'seed': seed, 'cars': cars, 'storage_delta': storage_delta, 'storage_idx': storage_idx}
    if params.charging == 'winap':
        start = control.start_winap(ev, p.year)
    elif params.charging == 't3d' and lines:
        start = control_lines.start_t3d(p, params, part, ev, base, feeders)
    elif params.charging == 't3d':
        start = control.start_t3d_forecast(ev, base, p.kva, p.year)
    else:
        start = control.start_uncontrolled(ev)
    ev_load = control.render(ev, start, s)
    ns_on = bool(params.netzspeicher and feeders is not None)
    ns_kw, ns_idx = None, None
    if ns_on and plan:
        fixed = params.charging in FIXED_START
        ns_kw, ns_idx = netzspeicher.apply(p, params, part, plan, feeders, ev, start if fixed else None)
        base = np.asarray(base, dtype=float).copy()
        node_st = np.asarray(p.nodes_station)
        for c, g in enumerate(ns_idx):
            base[:, node_st[g]] += ns_kw[:, c]
        part['ns_kw'], part['ns_idx'] = ns_kw, ns_idx
    unmet, v2g, decisions = None, np.zeros_like(ev_load), None
    if params.charging in ('controlled', 'v2g') and lines:
        ev_load, v2g, unmet, decisions = control_lines.apply(p, params, part, ev, start, base, feeders)
    elif params.charging in ('controlled', 'v2g'):
        ev_load, unmet = control.controlled(base, ev_load, p.kva)
        if params.charging == 'v2g':
            cars_st = np.bincount(np.asarray(p.nodes_station), weights=cars, minlength=s)
            out, recharge, unmet_v2g = control.v2g_with_recharge(base, ev_load, p.kva, cars_st)
            v2g = out - recharge  # netto: Rückspeisung abends, Nachladen nachts
            unmet = unmet + unmet_v2g
    flow = np.asarray(base, dtype=float) + ev_load - v2g
    return {'heat': heat, 'cars': cars, 'wp_station': wp_st, 'ev': ev, 'start': start, 'base': base,
            'ev_load': ev_load, 'v2g': v2g, 'flow': flow, 'unmet': unmet,
            'storage_delta': storage_delta, 'storage_idx': storage_idx, 'seed': seed, 'node_decisions': decisions,
            'limits_effective': 'trafo+leitung' if lines else 'trafo',
            'ns_kw': ns_kw, 'ns_idx': ns_idx, 'netzspeicher_effective': ns_on}


NO_FEEDERS = 'none'


def feeders_fingerprint(root):
    """Fingerabdruck von ``root/feeders/``: sha256 über ``index.json``, ``manifest.json`` und alle Stationsdateien.

    ``'none'`` ohne Verzeichnis. Geht in jedes Seed-Ergebnis und ins Lauf-Manifest ein; Cache-Einträge mit anderem
    Fingerabdruck werden nicht wiederverwendet (neue Bemessungsregel oder neu angelegte Netze → neu rechnen).
    """
    d = None if root is None else Path(root) / 'feeders'
    if d is None or not (d / 'index.json').exists():
        return NO_FEEDERS
    h = hashlib.sha256()
    for f in [d / 'index.json', d / 'manifest.json', *sorted(d.glob('*.npz'))]:
        if f.exists():
            h.update(f.name.encode() + b'\0')
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


@lru_cache(maxsize=2)
def _feeders_at(root, fingerprint):
    return load_feeders(root)


def feeders_state(root):
    """(Fingerabdruck, Stationsnetze) zu ``root``; Netze je Prozess und Fingerabdruck einmal geladen, None ohne."""
    fp = feeders_fingerprint(root)
    return fp, (None if fp == NO_FEEDERS else _feeders_at(str(Path(root).resolve()), fp))


def line_kpis(p, params, f, feeders):
    """Leitungskennzahlen je Station (``metrics.line_kpis``, None für Stationen ohne Netz) aus dem Seed ``f``.

    Je Station werden die Knotenflüsse (nodeflow) und die Abschnittsauslastung einzeln gerechnet, nie alle
    Stationen gleichzeitig. Vorzeichen der Auslastung: + = Bezug, − = Einspeisung.
    """
    out = [None] * p.n_stations
    for s in range(p.n_stations):
        if s not in feeders:
            continue
        grid, sized = feeders[s]
        seg = segment_flow(grid, sized, station_block(p, params, f, s))
        pct = loading_pct(seg, sized)
        out[s] = metrics.line_kpis(np.where(seg < 0, -pct, pct), sized, grid)
    return out


LINE_EXTRA = ('station_line_max_pct', 'station_line_load_h', 'station_line_feed_h', 'station_first_load',
              'station_first_feed', 'station_line_over_m', 'station_feeder_load_h', 'station_feeder_feed_h',
              'station_marked_feeders')


def _line_results(p, f, kpis):
    """``extra`` je Station und Regionskennzahlen der Leitungen; ohne Netze alles None (Lauf wie bisher)."""
    if kpis is None:
        return dict.fromkeys(LINE_EXTRA), dict.fromkeys(metrics.LINE_REGION_KEYS)
    flow, kva = f['flow'], p.kva
    trafo_load = 100.0 * flow.max(axis=0) / kva
    trafo_feed = 100.0 * (-flow).max(axis=0) / kva

    def col(key, fn=lambda x: x):
        return [None if k is None else fn(k[key]) for k in kpis]

    first_load = [metrics.first_bottleneck(float(t), x) for t, x in zip(trafo_load, col('max_pct_load'))]
    first_feed = [metrics.first_bottleneck(float(t), x) for t, x in zip(trafo_feed, col('max_pct_feed'))]

    extra = {'station_line_max_pct': col('max_pct', lambda x: round(x, 1)),
             'station_line_load_h': col('load_h'), 'station_line_feed_h': col('feed_h'),
             'station_first_load': first_load, 'station_first_feed': first_feed,
             'station_line_over_m': col('over_m', lambda x: round(x, 1)),
             'station_feeder_load_h': col('feeder_load_h'), 'station_feeder_feed_h': col('feeder_feed_h'),
             'station_marked_feeders': col('marked_feeders')}
    return extra, metrics.line_region_kpis(kpis, first_load, first_feed)


def netzspeicher_plan(p, params, feeders):
    """Auslegungslauf der Netzspeicher: Seed 0 derselben Einstellung ohne Netzspeicher, je Station mit Netz Ort und
    Größe aus dessen Abschnittsflüssen (``netzspeicher.plan_station``); Liste nach Station sortiert."""
    p0 = replace(params, netzspeicher=False)
    f = flows(p, p0, 0, feeders=feeders)
    plan = []
    for s in sorted(feeders):
        grid, sized = feeders[s]
        plan += netzspeicher.plan_station(s, grid, sized, segment_flow(grid, sized, station_block(p, p0, f, s)))
    return plan


def _plan_path(cache_dir, params):
    return Path(cache_dir) / params.key() / 'netzspeicher.json'


def netzspeicher_plan_cached(cache_dir, params, feeders_fp, compute):
    """Plan aus ``<cache_dir>/<key>/netzspeicher.json``, wenn mit denselben Stationsnetzen (``feeders_fp``)
    bemessen; sonst ``compute()`` und speichern (atomar)."""
    path = _plan_path(cache_dir, params)
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if data.get('feeders_fp') == feeders_fp:
                return data['storages']
        except (ValueError, KeyError, AttributeError):   # abgebrochen geschrieben: neu bemessen
            pass
    plan = compute()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f'.{os.getpid()}.tmp')
    tmp.write_text(json.dumps({'feeders_fp': feeders_fp, 'model_version': MODEL_VERSION, 'storages': plan},
                              indent=1))
    os.replace(tmp, path)
    return plan


_FROM_ROOT = object()


def run_seed(p, params, i, feeders=_FROM_ROOT, feeders_fp=None, plan=None):
    """Ein Seed: Trafo-Kennzahlen wie bisher, dazu Leitungskennzahlen, wenn es Stationsnetze gibt.

    ``feeders``: Ergebnis von ``load_feeders`` (None = ohne Leitungen) mit ``feeders_fp`` als Fingerabdruck;
    ohne Angabe beides aus ``p.root/feeders/``. ``plan``: Netzspeicher aus ``netzspeicher_plan``; fehlt er bei
    ``params.netzspeicher``, wird er hier (im Speicher) bemessen.
    """
    t = time.perf_counter()
    if feeders is _FROM_ROOT:
        feeders_fp, feeders = feeders_state(p.root)
    elif feeders is None and feeders_fp is None:
        feeders_fp = NO_FEEDERS
    if params.netzspeicher and feeders is not None and plan is None:
        plan = netzspeicher_plan(p, params, feeders)
    f = flows(p, params, i, feeders=feeders, plan=plan)
    flow, kva = f['flow'], p.kva
    rows_load = metrics.station_rows(flow, kva, None)
    rows_feed = metrics.station_rows(-flow, kva, None)
    region = metrics.region_kpis(rows_load, rows_feed, f['unmet'], p.n_stations)
    extra, line_region = _line_results(p, f, None if feeders is None else line_kpis(p, params, f, feeders))
    region.update(line_region)
    region.update(_netzspeicher_region(f, plan, line_region))
    extra['limits_effective'] = f['limits_effective']
    extra['netzspeicher_effective'] = f['netzspeicher_effective']
    daily_max = flow[:flow.shape[0] // 24 * 24].reshape(-1, 24, flow.shape[1]).max(axis=1)
    return SeedResult(index=i, seed=seed_of(i), region=region,
                      station_load_kw_max=[round(float(x), 1) for x in flow.max(axis=0)],
                      station_congestion_h=[r['engpass_h_jahr'] if r else 0 for r in rows_load],
                      station_feed_h=[r['engpass_h_jahr'] if r else 0 for r in rows_feed],
                      worst_day=[int(x) for x in daily_max.argmax(axis=0)],
                      runtime_s=round(time.perf_counter() - t, 2), extra=extra, feeders_fp=feeders_fp)


def _netzspeicher_region(f, plan, line_region):
    """Regionskennzahlen der Netzspeicher; None, wenn ohne Netzspeicher gerechnet."""
    if not f['netzspeicher_effective']:
        return metrics.netzspeicher_region_kpis(None, 0.0, None)
    ns_kw = f['ns_kw']
    out_kwh = 0.0 if ns_kw is None else float(np.maximum(-np.asarray(ns_kw, float), 0.0).sum()) / netzspeicher.ETA
    return metrics.netzspeicher_region_kpis(plan or [], out_kwh, line_region.get('line_over_m'))


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


def cached_seeds(cache_dir, params, feeders_fp):
    """Gecachte Seeds der Einstellung, die mit den Stationsnetzen ``feeders_fp`` (``feeders_fingerprint``) gerechnet
    wurden; andere bleiben liegen und werden beim Neurechnen überschrieben."""
    out = []
    for i in range(params.n_seeds):
        path = _seed_path(cache_dir, params, i)
        if path.exists():
            try:
                r = SeedResult(**json.loads(path.read_text()))
            except (ValueError, TypeError):  # abgebrochen geschrieben: neu rechnen
                path.unlink(missing_ok=True)
                continue
            if r.feeders_fp == feeders_fp:
                out.append(r)
    return out


def _write_manifest(cache_dir, root, params, runtime, feeders_fp):
    d = Path(cache_dir) / params.key()
    prep = Path(root) / str(params.weather_year) / 'manifest.json'
    manifest = {'params': asdict(params), 'model_version': MODEL_VERSION, 'code_version': code_version(), 'legacy_frozen_at': legacy.FROZEN_AT,
                'legacy_sha256sums': hashlib.sha256((legacy.DIR / 'SHA256SUMS').read_bytes()).hexdigest(),
                'prepared_manifest_sha256': hashlib.sha256(prep.read_bytes()).hexdigest() if prep.exists() else None,
                'feeders_fingerprint': feeders_fp,
                'seeds': [seed_of(i) for i in range(params.n_seeds)], 'runtime_s': round(runtime, 1)}
    (d / 'manifest.json').write_text(json.dumps(manifest, indent=1))


_WORKER = {}


def _init(root, year):
    _WORKER['p'] = load_prepared(root, year)
    _WORKER['feeders_fp'], _WORKER['feeders'] = feeders_state(root)   # einmal je Prozess, nicht je Seed


def _work(params, i, plan=None):
    return run_seed(_WORKER['p'], params, i, feeders=_WORKER['feeders'], feeders_fp=_WORKER['feeders_fp'], plan=plan)


def run_many(root, params, workers=4, cache_dir=None):
    """Alle Seeds der Einstellung, in Fertigstellungsreihenfolge; Gecachtes (gleicher Netzstand) zuerst.

    Netzspeicher: Plan einmal im Hauptprozess (``netzspeicher_plan``, mit ``cache_dir`` über
    ``netzspeicher_plan_cached``) und an alle Seeds weitergegeben.
    """
    params.validate()
    t = time.perf_counter()
    fp = feeders_fingerprint(root)
    done = {r.index: r for r in cached_seeds(cache_dir, params, fp)} if cache_dir else {}
    yield from done.values()
    todo = [i for i in range(params.n_seeds) if i not in done]
    if todo:
        if cache_dir:
            (Path(cache_dir) / params.key()).mkdir(parents=True, exist_ok=True)
        plan = None
        if params.netzspeicher and fp != NO_FEEDERS:
            def compute():
                return netzspeicher_plan(load_prepared(root, params.weather_year), params, feeders_state(root)[1])
            plan = netzspeicher_plan_cached(cache_dir, params, fp, compute) if cache_dir else compute()
        with ProcessPoolExecutor(max_workers=max(1, min(workers, len(todo))), initializer=_init,
                                 initargs=(str(root), params.weather_year)) as pool:
            futures = [pool.submit(_work, params, i, plan) for i in todo]
            for fut in as_completed(futures):
                r = fut.result()
                if cache_dir:
                    path = _seed_path(cache_dir, params, r.index)
                    tmp = path.with_suffix(f'.{os.getpid()}.tmp')
                    tmp.write_text(json.dumps(asdict(r)))
                    os.replace(tmp, path)  # atomar: Leser sehen nie eine halbe Datei
                yield r
        if cache_dir:
            _write_manifest(cache_dir, root, params, time.perf_counter() - t, fp)


def band(results, key):
    vals = np.array([r.region[key] for r in results], dtype=float)
    return {'median': float(np.median(vals)), 'p10': float(np.percentile(vals, 10)),
            'p90': float(np.percentile(vals, 90)), 'n': len(vals)}
