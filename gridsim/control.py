"""Ladesteuerung (Startzeiten der Ladeereignisse), gesteuertes Laden, V2G und Heimspeicher je Station.

Steuerlogiken (Spec § 4): ungesteuert; WiNAP = im Winter Start um 23 Uhr, wenn bis 7 Uhr fertig;
T3d = an Tagen mit Engpassprognose Start zur Gruppenzeit des Haushalts (22/0/2 Uhr), sonst WiNAP.
Gesteuertes Laden und V2G drosseln nur Wallboxen gegen 100 % Trafo-Bemessung.
"""
import hashlib
from datetime import date, timedelta

import numpy as np

from gridsim import legacy

sim = legacy.load('steyr_sim_variant_a')
HOURS = 8760
DAYS = HOURS // 24
WINTER_MONTHS = (10, 11, 12, 1, 2, 3)
WINAP_START_H = 23
GROUP_START_H = (22, 24, 26)  # 22 Uhr, 0 Uhr, 2 Uhr (Folgetag) ab Tagesbeginn
DEADLINE_H = 7
SIGNAL_WINDOW = (16, 32)     # Engpassprognose: Tag 16 Uhr bis Folgetag 8 Uhr
V2G_KW, V2G_KWH, V2G_AVAIL = 11.0, 15.0, 0.7
V2G_WINDOW_START_H = 12      # Energiegrenze je Abend: 12 Uhr bis Folgetag 12 Uhr


def render(ev, start_h, n_stations, step_h=1.0, hours=HOURS):
    """Ladeleistung (kW) je Zeitschritt und Station; jedes Ereignis lädt ab ``start_h`` mit ``kw``."""
    n_steps = int(round(hours / step_h))
    out = np.zeros((n_steps, n_stations), dtype=np.float32)
    if not len(ev):
        return out
    per_step = ev.kw.astype(float) * step_h
    steps = np.ceil(ev.kwh_grid / per_step - 1e-9).astype(int)
    last = ev.kwh_grid - (steps - 1) * per_step       # Energie im letzten Schritt
    t0 = np.round(np.asarray(start_h, dtype=float) / step_h).astype(int)
    for k in range(int(steps.max())):
        act = (steps > k) & (t0 + k < n_steps)
        energy = np.where(k == steps - 1, last, per_step)[act]
        np.add.at(out, (t0[act] + k, ev.station[act]), (energy / step_h).astype(np.float32))
    return out


def start_uncontrolled(ev):
    return ev.arrive_h.copy()


def _winter(day, year):
    first = date(year, 1, 1)
    months = np.array([(first + timedelta(days=int(d))).month for d in range(DAYS + 1)])
    return np.isin(months[np.minimum(day, DAYS)], WINTER_MONTHS)


def _latest_start(ev):
    """Spätester Start, damit bis zur Frist (Folgetag 7 Uhr) fertig geladen ist."""
    return ev.deadline_h - np.ceil(ev.kwh_grid / ev.kw - 1e-9).astype(int)


def start_winap(ev, year):
    day = ev.arrive_h // 24
    window = day * 24 + WINAP_START_H
    shift = _winter(day, year) & (ev.arrive_h < window) & (window <= _latest_start(ev))
    return np.where(shift, window, ev.arrive_h).astype(np.int32)


def node_group(nodes):
    """Gruppe 0/1/2 je Haushaltsknoten (fest, gleichmäßig verteilt)."""
    return (np.asarray(nodes, dtype=np.int64) * 2654435761 % 2**32) % 3


def start_t3d(ev, signal, year):
    """An Signal-Tagen startet jedes Auto zur Zeit seiner Haushaltsgruppe (22/0/2 Uhr), sonst wie WiNAP.

    Gestaffelt wird innerhalb des Segments: für den Trafo zählt die Gleichzeitigkeit an der Station.
    """
    base = start_winap(ev, year)
    day = ev.arrive_h // 24
    on = signal[ev.station, np.minimum(day, signal.shape[1] - 1)]
    target = day * 24 + np.asarray(GROUP_START_H)[node_group(ev.node)]
    target = np.maximum(np.minimum(target, _latest_start(ev)), ev.arrive_h)
    return np.where(on, target, base).astype(np.int32)


def start_t3d_forecast(ev, base, kva, year):
    """T3d mit Engpassprognose des VNB: Fluss am Vortag unter den geltenden Tarifen (WiNAP) prognostiziert."""
    forecast = np.asarray(base, dtype=float) + render(ev, start_winap(ev, year), len(kva))
    return start_t3d(ev, engpass_signal(forecast, kva), year)


def engpass_signal(flow, kva):
    """Tag d ist Signal, wenn der Fluss zwischen d 16 Uhr und d+1 8 Uhr über der Trafo-Bemessung liegt."""
    over = np.asarray(flow) > np.asarray(kva)[None, :]
    padded = np.vstack([over, np.zeros((SIGNAL_WINDOW[1], over.shape[1]), dtype=bool)])
    out = np.zeros((over.shape[1], DAYS), dtype=bool)
    for d in range(DAYS):
        out[:, d] = padded[d * 24 + SIGNAL_WINDOW[0]: d * 24 + SIGNAL_WINDOW[1]].any(axis=0)
    return out


def controlled(f0, ev, kva):
    """Wallboxen gedrosselt auf den Platz unter ``kva``; Rest später, bis 7 Uhr, danach ungeladen."""
    f0, ev = np.asarray(f0, dtype=float), np.asarray(ev, dtype=float)
    out = np.zeros_like(ev)
    unmet = np.zeros((ev.shape[1], DAYS + 1))
    backlog = np.zeros(ev.shape[1])
    room = np.maximum(np.asarray(kva)[None, :] - f0, 0.0)
    for h in range(ev.shape[0]):
        want = ev[h] + backlog
        serve = np.minimum(want, room[h])
        out[h], backlog = serve, want - serve
        if h % 24 == DEADLINE_H:
            unmet[:, h // 24] = backlog
            backlog = np.zeros(ev.shape[1])
    return out, unmet[:, :DAYS]


def v2g(residual, cars):
    """Rückspeisung angesteckter E-Autos gegen den Rest über der Grenze, Leistung und Abendenergie begrenzt."""
    residual = np.asarray(residual, dtype=float)
    cars = np.asarray(cars, dtype=float)
    p_cap = V2G_KW * V2G_AVAIL * cars
    e_cap = V2G_KWH * V2G_AVAIL * cars
    out = np.zeros_like(residual)
    left = e_cap.copy()
    for h in range(residual.shape[0]):
        if h % 24 == V2G_WINDOW_START_H:
            left = e_cap.copy()
        out[h] = np.minimum(np.minimum(residual[h], p_cap), left)
        left -= out[h]
    return out


def v2g_with_recharge(base, ev, kva, cars):
    """V2G-Rückspeisung gegen den Rest über der Grenze und Nachladen dieser Energie bis 7 Uhr unter der Grenze.

    Gibt (Rückspeisung, Nachladen, bis 7 Uhr nicht nachgeladene Energie je Station und Tag) zurück.
    """
    flow = np.asarray(base, dtype=float) + np.asarray(ev, dtype=float)
    kva = np.asarray(kva, dtype=float)
    out = v2g(np.maximum(flow - kva[None, :], 0), cars)
    p_cap = V2G_KW * V2G_AVAIL * np.asarray(cars, dtype=float)
    recharge = np.zeros_like(out)
    unmet = np.zeros((out.shape[1], DAYS + 1))
    backlog = np.zeros(out.shape[1])
    for h in range(out.shape[0]):
        room = np.maximum(kva - flow[h] + out[h], 0.0)
        recharge[h] = np.minimum(np.minimum(backlog, room), p_cap)
        backlog = backlog - recharge[h] + out[h]
        if h % 24 == DEADLINE_H:
            unmet[:, h // 24] = backlog
            backlog = np.zeros(out.shape[1])
    return out, recharge, unmet[:, :DAYS]


def storage_flow(p, pv_scale, strategy, wp_station, wp_storage_nodes):
    """Netto-Stationsfluss (kW, + = Bezug) aus PV, Haushalt und Wärmepumpe, ohne E-Auto.

    Nur Knoten mit Heimspeicher laufen durch ``sim.simulate``; alle anderen gehen als Bilanz ein.
    """
    kwp = np.asarray(p.nodes_kwp_bins, dtype=float)
    hh = np.asarray(p.nodes_hh, dtype=float)
    st = np.asarray(p.nodes_station)
    pv_bins = np.asarray(p.pv_bins, dtype=float) * pv_scale
    h0 = np.asarray(p.h0, dtype=float) * sim.KWH_PER_HH
    n_st = p.n_stations
    kwp_st = np.zeros((n_st, kwp.shape[1]))
    np.add.at(kwp_st, st, kwp)
    hh_st = np.bincount(st, weights=hh, minlength=n_st)
    flow = h0[:, None] * hh_st[None, :] - pv_bins @ kwp_st.T + np.asarray(wp_station, dtype=float)
    idx = np.flatnonzero(np.asarray(p.nodes_kwh) > 0)
    if len(idx):
        pv_k = pv_bins @ kwp[idx].T
        load_k = h0[:, None] * hh[idx][None, :] + np.asarray(wp_storage_nodes, dtype=float)
        net_k = sim.simulate(pv_k, load_k, np.asarray(p.nodes_kwh, dtype=float)[idx], strategy)
        delta = net_k - (load_k - pv_k)  # Wirkung des Speichers
        corr = np.zeros((HOURS, n_st))
        for j, n in enumerate(idx):
            corr[:, st[n]] += delta[:, j]
        flow += corr
    return flow.astype(np.float32)
