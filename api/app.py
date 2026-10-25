"""Rechen-API für das Regionen-Dashboard (Pfade unter /api/, same origin hinter dem Login der Seite).

Umgebung: GRIDSIM_PREPARED, GRIDSIM_CACHE, GRIDSIM_MAX_JOBS (2), GRIDSIM_WORKERS (4), GRIDSIM_REPLAY_DELAY_S (0.4).
"""
import json
import os
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

from api.jobs import JobManager
from gridsim import metrics
from gridsim import run as runmod
from gridsim.data import load_prepared
from gridsim.drilldown import day_curve


class RunBody(BaseModel):
    weather_year: int = 2023
    scenario: str = '2030'
    pv_factor: float = 1.0
    charging: str = 'uncontrolled'
    storage: str = 'base'
    n_seeds: int = 20
    limits: str = 'trafo'
    netzspeicher: bool = False


class CostBody(BaseModel):
    run_id: str
    cost: dict[str, float | None] = {}


def _error(status, msg):
    return JSONResponse({'error': msg}, status_code=status)


def create_app(prepared_root=None, cache_dir=None, runner=None, max_jobs=None, workers=None, replay_delay=None,
               keepalive_s=15.0):
    root = Path(prepared_root or os.environ.get('GRIDSIM_PREPARED', '/prepared'))
    cache = Path(cache_dir or os.environ.get('GRIDSIM_CACHE', '/cache'))
    cache.mkdir(parents=True, exist_ok=True)
    delay = float(os.environ.get('GRIDSIM_REPLAY_DELAY_S', 0.4) if replay_delay is None else replay_delay)
    jobs = JobManager(root, cache, runner or runmod.run_many,
                      max_jobs=int(max_jobs or os.environ.get('GRIDSIM_MAX_JOBS', 2)),
                      workers=int(workers or os.environ.get('GRIDSIM_WORKERS', 4)))
    prepared = {}

    def prep(year):
        if year not in prepared:
            prepared[year] = load_prepared(root, year)
        return prepared[year]

    def feeders_index():
        """``feeders/index.json`` (Stationsindex → Gebietstyp, Abgänge, Markierungen); None ohne Stationsnetze."""
        f = root / 'feeders' / 'index.json'
        return json.loads(f.read_text()) if f.exists() else None

    app = FastAPI(title='gridsim', docs_url=None, redoc_url=None, openapi_url=None)
    r = APIRouter(prefix='/api')

    @app.exception_handler(RequestValidationError)
    async def bad_request(_: Request, exc: RequestValidationError):
        fields = ', '.join(str(e['loc'][-1]) for e in exc.errors())
        return _error(400, f'invalid parameter: {fields}')

    def params_of(body):
        p = runmod.RunParams(**body.model_dump())
        p.validate()
        return p

    @r.get('/health')
    def health():
        return {'ok': True}

    @r.get('/options')
    def options():
        return {'weather_year': list(runmod.WEATHER_YEARS), 'scenario': list(runmod.SCENARIOS),
                'pv_factor': list(runmod.PV_FACTORS), 'charging': list(runmod.CHARGING), 'storage': list(runmod.STORAGE),
                'limits': list(runmod.LIMITS), 'netzspeicher': [False, True],
                'n_seeds': 20, 'cost_defaults': metrics.COST_DEFAULTS,
                'placeholders': [k for k, v in metrics.COST_DEFAULTS.items() if v is None]}

    @r.get('/stations')
    def stations(weather_year: int = 2023):
        if weather_year not in runmod.WEATHER_YEARS:
            return _error(400, f'weather_year must be one of {list(runmod.WEATHER_YEARS)}')
        index = feeders_index()   # Gebietstyp und Zahl markierter Abgänge je Station; None ohne Stationsnetze
        out = []
        for s in prep(weather_year).stations:
            f = None if index is None else index.get(str(s['idx']))
            out.append({**{k: s[k] for k in ('id', 'idx', 'kva', 'n_hh', 'uw', 'synthetic', 'lon', 'lat')},
                        'area': f and f['area'], 'marked': f and f['marked']})
        return out

    @r.get('/lines')
    def lines(weather_year: int = 2023):
        if weather_year not in runmod.WEATHER_YEARS:
            return _error(400, f'weather_year must be one of {list(runmod.WEATHER_YEARS)}')
        f = root / 'feeders' / 'lines.geojson'
        if not f.exists():
            return _error(404, 'no LV lines prepared')
        return FileResponse(f, media_type='application/geo+json')

    @r.post('/runs')
    def start(body: RunBody):
        try:
            params = params_of(body)
        except ValueError as exc:
            return _error(400, str(exc))
        job = jobs.submit(params)
        return {'run_id': params.key(), 'status': job.status}

    @r.get('/runs/{run_id}')
    def status(run_id: str):
        job = jobs.get(run_id)
        return job.snapshot() if job else _error(404, f'unknown run {run_id}')

    @r.get('/runs/{run_id}/events')
    def events(run_id: str):
        job = jobs.get(run_id)
        if not job:
            return _error(404, f'unknown run {run_id}')
        replay = job.finished  # fertig (Cache oder früher gerechnet): Band trotzdem sichtbar wachsen lassen

        def stream():
            # nie unter job.cond yielden: bricht der Client ab, bliebe der Lock gehalten und der Lauf hinge
            sent = 0
            while True:
                with job.cond:
                    if sent >= len(job.seeds) and not job.finished:
                        job.cond.wait(timeout=keepalive_s)
                    new, finished = job.seeds[sent:], job.finished
                if not new and not finished:
                    yield ': keepalive\n\n'
                    continue
                for s in new:
                    if replay:
                        time.sleep(delay)
                    yield f'event: seed\ndata: {json.dumps(s)}\n\n'
                sent += len(new)
                if finished and sent >= len(job.seeds):
                    yield f'event: done\ndata: {json.dumps({"status": job.status, "error": job.error})}\n\n'
                    return

        return StreamingResponse(stream(), media_type='text/event-stream',
                                 headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    @r.get('/stations/{station_id:path}/day')
    def day(station_id: str, weather_year: int = 2023, scenario: str = '2030', pv_factor: float = 1.0,
            charging: str = 'uncontrolled', storage: str = 'base', seed: int = 0, day: int | None = None):
        try:
            params = params_of(RunBody(weather_year=weather_year, scenario=scenario, pv_factor=pv_factor,
                                       charging=charging, storage=storage, n_seeds=max(seed + 1, 1)))
        except ValueError as exc:
            return _error(400, str(exc))
        if day is not None and not 0 <= day < 365:
            return _error(400, 'day must be 0..364')
        try:
            return day_curve(prep(weather_year), params, station_id, seed_index=seed, day=day)
        except KeyError:
            return _error(404, f'no model data for station {station_id}')

    @r.post('/costs')
    def costs(body: CostBody):
        job = jobs.get(body.run_id)
        if not job or not job.seeds:
            return _error(404, f'no results for run {body.run_id}')
        unknown = set(body.cost) - set(metrics.COST_DEFAULTS)
        if unknown:
            return _error(400, f'unknown cost parameter: {sorted(unknown)}')
        seeds = job.snapshot()['seeds']
        keys = ('storage_units', 'trafo_plus1', 'trafo_plus2', 'trafo_over_1000')
        kpis = {k: float(np.median([s['region'][k] for s in seeds])) for k in keys}
        for k in ('line_over_m', 'netzspeicher_kwh'):   # None ohne Stationsnetze (bzw. ohne Netzspeicher)
            vals = [s['region'].get(k) for s in seeds]
            kpis[k] = None if any(v is None for v in vals) else float(np.median(vals))
        return metrics.costs(kpis, {**metrics.COST_DEFAULTS, **body.cost})

    app.include_router(r)
    return app


def app_from_env():
    return create_app()
