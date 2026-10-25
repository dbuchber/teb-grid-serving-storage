"""Kennzahlen nach ems-konzept § 7.2 je Station und für die Region, Kosten Speicher gegen Netzausbau.

Logik wie ``steyr_storage_need.events`` / ``segment_row`` (eingefroren): Ereignis = zusammenhängende
Überlaststunden, bei weniger als MIN_PAUSE_H Stunden Pause zusammengefasst.

Leitungskennzahlen (Spec 4.4, nur thermisch): ``line_kpis`` je Station aus der Abschnittsauslastung,
``first_bottleneck`` für „Engpass zuerst“ je Richtung, ``line_region_kpis`` für die Region.
"""
import math

import numpy as np

TRAFO_SIZES = (125, 160, 250, 400, 630, 800, 1000)
FACTOR_INST = 0.6 * 0.85 * 0.8 * 0.8
KW_PER_UNIT, RELIABILITY, KWH_PER_UNIT = 5.0, 0.85, 10.0
MIN_PAUSE_H = 8
LINE_LIMIT_PCT = 100.0   # Planungsgrenze: 100 % Grenzstrom

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


def line_kpis(loading_pct, sized, grid):
    """Leitungskennzahlen einer Station aus der Abschnittsauslastung ``loading_pct`` (8760, m) in %.

    ``loading_pct`` ist vorzeichenbehaftet: + = Bezug (Abschnittsfluss zum Kunden), − = Einspeisung; Betrag wie
    ``feeders.loading.loading_pct``. Überlast = Betrag > 100 %. ``grid`` liefert Länge und Abgang je Abschnitt,
    ``sized``/``grid`` die markierten Abgänge (Entscheidung 7), ``grid.tail`` die Ausläufer.
    """
    pct = np.asarray(loading_pct, dtype=np.float32)
    n_feeder = len(grid.marked)
    over_load = pct > LINE_LIMIT_PCT
    over_feed = pct < -LINE_LIMIT_PCT
    length = np.asarray(grid.length_m, dtype=float)
    feeder = np.asarray(grid.feeder, dtype=np.int64)
    seg_load, seg_feed = over_load.any(axis=0), over_feed.any(axis=0)

    def feeder_hours(over):
        out = np.zeros(n_feeder, dtype=np.int64)
        for k in np.unique(feeder[over.any(axis=0)]):
            out[k] = int(over[:, feeder == k].any(axis=1).sum())
        return [int(x) for x in out]

    def max_abs(a):
        return float(a.max()) if a.size else 0.0

    tail = np.asarray(grid.tail, dtype=bool) if grid.tail is not None else np.zeros(n_feeder, bool)
    return {
        'max_pct': max_abs(np.abs(pct)),
        'max_pct_load': max_abs(np.maximum(pct, 0)),
        'max_pct_feed': max_abs(np.maximum(-pct, 0)),
        'load_h': int(over_load.any(axis=1).sum()),
        'feed_h': int(over_feed.any(axis=1).sum()),
        'feeder_load_h': feeder_hours(over_load),
        'feeder_feed_h': feeder_hours(over_feed),
        'over_m': float(length[seg_load | seg_feed].sum()),
        'over_m_load': float(length[seg_load].sum()),
        'over_m_feed': float(length[seg_feed].sum()),
        'marked_feeders': int((np.asarray(grid.marked, bool) | np.asarray(sized.marked, bool)).sum()),
        'tail_feeders': int(tail.sum()),
    }


def first_bottleneck(trafo_pct, line_pct):
    """„Engpass zuerst“ einer Richtung aus der höchsten Auslastung (%) von Trafo und Leitung (Entscheidung 9).

    ``'trafo' | 'leitung' | 'beide' | 'keiner'``; Überlast heißt > 100 %. None, wenn ``line_pct`` None ist
    (kein Netz für die Station).
    """
    if line_pct is None:
        return None
    t, l_ = trafo_pct > LINE_LIMIT_PCT, line_pct > LINE_LIMIT_PCT
    return 'beide' if t and l_ else 'trafo' if t else 'leitung' if l_ else 'keiner'


LINE_REGION_KEYS = ('stations_line_load_congestion', 'stations_line_feed_congestion', 'stations_line_only',
                    'line_over_m', 'line_over_m_load', 'line_over_m_feed', 'marked_feeders', 'tail_feeders')


def line_region_kpis(kpis, first_load, first_feed):
    """Regionskennzahlen der Leitungen aus ``line_kpis`` je Station (None = Station ohne Netz).

    ``stations_line_only``: Stationen, an denen in mindestens einer Richtung nur die Leitung überlastet ist
    („Leitung vor Trafo“). Ohne jedes Stationsnetz sind alle Werte None.
    """
    if all(k is None for k in kpis):
        return dict.fromkeys(LINE_REGION_KEYS)
    rows = [k for k in kpis if k is not None]
    return {
        'stations_line_load_congestion': sum(k['load_h'] > 0 for k in rows),
        'stations_line_feed_congestion': sum(k['feed_h'] > 0 for k in rows),
        'stations_line_only': sum('leitung' in (a, b) for a, b in zip(first_load, first_feed)),
        'line_over_m': round(sum(k['over_m'] for k in rows), 1),
        'line_over_m_load': round(sum(k['over_m_load'] for k in rows), 1),
        'line_over_m_feed': round(sum(k['over_m_feed'] for k in rows), 1),
        'marked_feeders': sum(k['marked_feeders'] for k in rows),
        'tail_feeders': sum(k['tail_feeders'] for k in rows),
    }


def costs(kpis, params):
    """Kosten aus Median-Kennzahlen; Platzhalter (None) werden nicht gerechnet, sondern gemeldet."""
    placeholders = [k for k, v in params.items() if v is None]
    storage = kpis['storage_units'] * KWH_PER_UNIT * params['storage_eur_per_kwh']
    trafo = None
    if params.get('trafo_step_eur') is not None:
        trafo = (kpis['trafo_plus1'] + 2 * kpis['trafo_plus2']) * params['trafo_step_eur']
    line = None
    if params.get('line_eur_per_m') is not None and kpis.get('line_over_m') is not None:
        line = kpis['line_over_m'] * params['line_eur_per_m']
    return {'storage_eur': storage, 'trafo_eur': trafo, 'line_eur': line,
            'trafo_over_1000': kpis['trafo_over_1000'], 'placeholders': placeholders,
            'note': 'Model values. Line reinforcement = length of LV segments above 100 % of rated current '
                    '(synthetic LV grid, thermal only) × cost per metre; None without a cost rate or without a grid. '
                    'trafo_plus2 counts as two steps; stations above 1000 kVA need a new MV connection (not priced).'}
