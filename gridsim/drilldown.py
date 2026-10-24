"""Tageskurve einer Station in 15 Minuten: Haushalt, Wärmepumpe, E-Auto, PV, Speicher, V2G, Trafo.

Rechnet nur die Knoten der Station (gleiche Zufallsfolge wie run.flows), damit die Antwort unter 1 s bleibt.
Haushalt aus APCS viertelstündlich, PV linear aus Stundenmitteln interpoliert, Wärmepumpe, Speicher und
gesteuertes Laden stundenkonstant, ungesteuerte Ladeereignisse viertelstündlich neu gezeichnet.
"""
from dataclasses import replace
from datetime import date, timedelta

import numpy as np

from gridsim import control, legacy, profiles
from gridsim.run import seed_of

sim = legacy.load('steyr_sim_variant_a')
Q = 4  # Viertelstunden je Stunde


def _station_parts(p, params, s, i):
    seed = seed_of(i)
    rng = np.random.default_rng(seed)
    heat, cars = profiles.assign(p, params.scenario, rng)
    at_s = np.asarray(p.nodes_station) == s
    wp_st, wp_sto = profiles.heat_pump(p, np.where(at_s, heat, 0.0), seed)
    ev = profiles.ev_events(p, cars, rng)
    keep = ev.station == s
    ev = replace(ev, **{k: getattr(ev, k)[keep] for k in ('node', 'station', 'arrive_h', 'kwh_grid', 'kw', 'deadline_h')})
    ev = replace(ev, station=np.zeros(len(ev), dtype=np.int32))
    base_all = control.storage_flow(p, params.pv_factor, params.storage, wp_st, _storage_wp(p, heat, seed, at_s, wp_sto))
    kwp_st = np.asarray(p.nodes_kwp_bins, dtype=float)[at_s].sum(axis=0)
    pv = np.asarray(p.pv_bins, dtype=float) @ kwp_st * params.pv_factor
    household = np.asarray(p.h0, dtype=float) * sim.KWH_PER_HH * float(np.asarray(p.nodes_hh)[at_s].sum())
    wp = np.asarray(wp_st[:, s], dtype=float)
    base = np.asarray(base_all[:, s], dtype=float)
    storage_dis = (household + wp - pv) - base  # + = Speicher entlädt
    kva = p.kva[s:s + 1]
    if params.charging == 'winap':
        start = control.start_winap(ev, p.year)
    elif params.charging == 't3d':
        start = control.start_t3d_forecast(ev, base[:, None], kva, p.year)
    else:
        start = control.start_uncontrolled(ev)
    ev_h = control.render(ev, start, 1)
    v2g = np.zeros_like(ev_h)
    if params.charging in ('controlled', 'v2g'):
        ev_h, _ = control.controlled(base[:, None], ev_h, kva)
        if params.charging == 'v2g':
            v2g = control.v2g(np.maximum(base[:, None] + ev_h - kva[None, :], 0), np.array([cars[at_s].sum()]))
    flow = base + ev_h[:, 0] - v2g[:, 0]
    return {'ev': ev, 'start': start, 'ev_h': ev_h[:, 0], 'v2g': v2g[:, 0], 'pv': pv, 'household': household,
            'wp': wp, 'storage_dis': storage_dis, 'flow': flow, 'hh': float(np.asarray(p.nodes_hh)[at_s].sum())}


def _storage_wp(p, heat, seed, at_s, wp_sto):
    """Wärmepumpe der Speicherknoten: außerhalb der Station 0 (dort nicht berechnet)."""
    idx = np.flatnonzero(np.asarray(p.nodes_kwh) > 0)
    out = np.array(wp_sto, copy=True)
    out[:, ~at_s[idx]] = 0
    return out


def day_curve(p, params, station_id, seed_index=0, day=None):
    s = p.station_ids.index(station_id) if station_id in p.station_ids else None
    if s is None:
        raise KeyError(station_id)
    parts = _station_parts(p, params, s, seed_index)
    flow = parts['flow']
    if day is None:
        day = int(flow[:365 * 24].reshape(365, 24).max(axis=1).argmax())
    h = slice(day * 24, day * 24 + 24)
    hold = lambda a: np.repeat(a[h], Q)
    household = np.asarray(p.h0_q, dtype=float)[day * 96:(day + 1) * 96] * sim.KWH_PER_HH * parts['hh'] * Q
    hours = np.arange(len(parts['pv'])) + 0.5
    t = day * 24 + (np.arange(96) + 0.5) / Q
    pv = np.interp(t, hours, parts['pv'])
    if params.charging in ('controlled', 'v2g'):
        ev = hold(parts['ev_h'])
    else:
        ev = control.render(parts['ev'], parts['start'], 1, step_h=0.25)[day * 96:(day + 1) * 96, 0].astype(float)
    wp, storage, v2g = hold(parts['wp']), hold(parts['storage_dis']), hold(parts['v2g'])
    trafo = household + wp + ev - pv - storage - v2g
    r = lambda a: [round(float(x), 2) for x in a]
    return {'station': station_id, 'day': day, 'date': (date(p.year, 1, 1) + timedelta(days=day)).isoformat(),
            'kva': float(p.kva[s]), 'step_min': 15, 'household_kw': r(household), 'heat_pump_kw': r(wp), 'ev_kw': r(ev),
            'pv_kw': r(pv), 'storage_kw': r(storage), 'v2g_kw': r(v2g), 'trafo_kw': r(trafo),
            'params': {'weather_year': params.weather_year, 'scenario': params.scenario, 'pv_factor': params.pv_factor,
                       'charging': params.charging, 'storage': params.storage, 'seed': seed_of(seed_index)}}
