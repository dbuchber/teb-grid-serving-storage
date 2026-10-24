"""Kennzahlen nach ems-konzept § 7.2 je Station und für die Region, Kosten Speicher gegen Netzausbau.

Logik wie ``steyr_storage_need.events`` / ``segment_row`` (eingefroren): Ereignis = zusammenhängende
Überlaststunden, bei weniger als MIN_PAUSE_H Stunden Pause zusammengefasst.
"""
import math

import numpy as np

TRAFO_SIZES = (125, 160, 250, 400, 630, 800, 1000)
FACTOR_INST = 0.6 * 0.85 * 0.8 * 0.8
KW_PER_UNIT, RELIABILITY, KWH_PER_UNIT = 5.0, 0.85, 10.0
MIN_PAUSE_H = 8

# Kosten (Annahmen): Speicher und Verschleiß aus ems-konzept § 7.3; Trafo-Stufe und Leitung ohne Quelle
COST_DEFAULTS = {'storage_eur_per_kwh': 600.0, 'wear_eur_per_kwh': 0.05, 'trafo_step_eur': None, 'line_eur_per_m': None}


def events(over):
    hours = np.flatnonzero(over > 0)
    if not len(hours):
        return []
    out, start, last = [], hours[0], hours[0]
    for h in hours[1:]:
        if h - last > MIN_PAUSE_H:
            out.append((start, last))
            start = h
        last = h
    out.append((start, last))
    return [(float(over[a:b + 1].sum()), float(over[a:b + 1].max()), int((over[a:b + 1] > 0).sum())) for a, b in out]


def trafo_steps(kva, peak):
    need = next((t for t in TRAFO_SIZES if t >= peak), None)
    return None if need is None else TRAFO_SIZES.index(need) - TRAFO_SIZES.index(kva)


def segment_row(flow, kva):
    ev = events(np.maximum(flow - kva, 0))
    if not ev:
        return None
    e_net = max(e for e, _, _ in ev)
    p_max = max(p for _, p, _ in ev)
    e_inst = e_net / FACTOR_INST
    row = {'engpass_h_jahr': sum(h for _, _, h in ev), 'ereignisse': len(ev),
           'e_netto_kwh': round(e_net, 1), 'p_max_kw': round(p_max, 1), 'e_inst_kwh': round(e_inst, 1),
           'n_speicher_energie': math.ceil(e_inst / KWH_PER_UNIT),
           'n_speicher_leistung': math.ceil(p_max / (KW_PER_UNIT * RELIABILITY)),
           'netz_vollzyklen_jahr': round(sum(e for e, _, _ in ev) / e_inst, 1),
           'trafo_noetig_kva': next((t for t in TRAFO_SIZES if t >= flow.max()), None),
           'trafo_stufen_hoeher': trafo_steps(kva, flow.max())}
    row['n_speicher'] = max(row['n_speicher_energie'], row['n_speicher_leistung'])
    return row


def station_rows(flow, kva, cap_kwh):
    """§ 7.2-Zeile je Station (``flow`` > 0 belastet den Trafo in der betrachteten Richtung), None ohne Engpass."""
    flow = np.asarray(flow, dtype=float)
    return [segment_row(flow[:, s], float(kva[s])) for s in range(flow.shape[1])]


def region_kpis(rows_load, rows_feed, unmet, n_stations):
    load = [r for r in rows_load if r]
    feed = [r for r in rows_feed if r]
    steps = [r['trafo_stufen_hoeher'] for r in load]
    return {
        'n_stations': n_stations,
        'stations_load_congestion': len(load),
        'stations_feed_congestion': len(feed),
        'congestion_h_median': float(np.median([r['engpass_h_jahr'] for r in load])) if load else 0,
        'e_net_mwh': round(sum(r['e_netto_kwh'] for r in load) / 1000, 3),
        'e_inst_mwh': round(sum(r['e_inst_kwh'] for r in load) / 1000, 3),
        'storage_units': sum(r['n_speicher'] for r in load),
        'feed_e_net_mwh': round(sum(r['e_netto_kwh'] for r in feed) / 1000, 3),
        'trafo_plus1': sum(s == 1 for s in steps),
        'trafo_plus2': sum((s or 0) >= 2 for s in steps),
        'trafo_over_1000': sum(s is None for s in steps),
        'ev_unmet_mwh': round(float(np.sum(unmet)) / 1000, 3) if unmet is not None else 0,
    }


def costs(kpis, params):
    """Kosten aus Median-Kennzahlen; Platzhalter (None) werden nicht gerechnet, sondern gemeldet."""
    placeholders = [k for k, v in params.items() if v is None]
    storage = kpis['storage_units'] * KWH_PER_UNIT * params['storage_eur_per_kwh']
    trafo = None
    if params.get('trafo_step_eur') is not None:
        trafo = (kpis['trafo_plus1'] + 2 * kpis['trafo_plus2']) * params['trafo_step_eur']
    return {'storage_eur': storage, 'trafo_eur': trafo, 'line_eur': None,
            'trafo_over_1000': kpis['trafo_over_1000'], 'placeholders': placeholders,
            'note': 'Model values. Line reinforcement is not in the live model (no load flow). '
                    'trafo_plus2 counts as two steps; stations above 1000 kVA need a new MV connection (not priced).'}
