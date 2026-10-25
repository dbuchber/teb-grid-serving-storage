"""Knotenflüsse einer Station (Spec 4.4/4.5): Haushalt, PV, Wärmepumpe, Speicher, E-Auto, V2G je Knoten.

Rekonstruiert aus dem Ergebnis von ``run.flows`` die Flüsse der Knoten genau einer Station, sodass die Summe
über die Knoten den Stationsfluss ergibt. Es liegt nie die volle Knotenmatrix aller Stationen im Speicher,
sondern je Aufruf (8760, n_s) je Bestandteil.

- Wärmepumpe: ``profiles.heat_pump_kw`` mit denselben ``limits/shifts`` (``wpev.spread(N, seed)``) wie
  ``profiles.heat_pump``; die Formel rechnet spaltenweise, daher gleiche Werte je Knoten.
- Speicher: Wirkung je Speicherknoten aus ``f['storage_delta']``.
- E-Auto ungesteuert/WiNAP/T3d: Ereignisse der Station mit lokalem Knotenindex gerendert.
- Gesteuert/V2G (Grenzmodus ``trafo``): je Stunde bekommt jeder Knoten den Anteil served/want der Station an
  seinem Bedarf (eigene ungesteuerte Last + eigener Rückstau); der Rückstau je Knoten verfällt wie in
  ``control.controlled`` um 7 Uhr. V2G (netto) anteilig nach Autos je Knoten.
"""
from dataclasses import dataclass, replace

import numpy as np

from gridsim import control, legacy, profiles

sim = legacy.load('steyr_sim_variant_a')
HOURS = 8760
_EPS_KW = 1e-6   # Stunden ohne Rückstau, in denen die Station alles lädt, bleiben ungesteuert


@dataclass
class NodeBlock:
    """Knotenflüsse (kW) einer Station, je (8760, n_s) float32; Spalten in Reihenfolge ``nodes`` (global)."""
    hh_kw: np.ndarray
    pv_kw: np.ndarray
    wp_kw: np.ndarray
    storage_kw: np.ndarray   # Wirkung des Heimspeichers, + = Bezug (Laden), − = Entladen
    ev_kw: np.ndarray
    v2g_kw: np.ndarray       # netto: + = Rückspeisung, − = Nachladen
    nodes: np.ndarray        # (n_s,) globale Knotenindizes
    hh: np.ndarray = None    # (n_s,) Haushalte je Knoten (für den Spitzenzuschlag)
    hh_peak_kw: float = None  # Spitze des H0-Profils je Haushalt (max(h0)·KWH_PER_HH)

    def net(self):
        """Netto-Knotenfluss, + = Bezug: hh + wp − pv + storage + ev − v2g."""
        return self.hh_kw + self.wp_kw - self.pv_kw + self.storage_kw + self.ev_kw - self.v2g_kw


def _wp_nodes(p, heat, seed, nodes):
    heat = np.asarray(heat, dtype=float)
    limits, shifts = profiles.wpev.spread(len(heat), seed)
    dhw = np.asarray(p.nodes_dhw, dtype=float)[nodes]
    dhw = np.where(np.isnan(dhw), profiles.wpev.DHW_SHARE, dhw)
    cells = np.asarray(p.nodes_cell)[nodes]
    temp = np.asarray(p.temp_cells, dtype=float)
    h = heat[nodes]
    out = np.zeros((HOURS, len(nodes)), dtype=np.float32)
    for c in np.unique(cells[h > 0]):
        loc = np.flatnonzero((cells == c) & (h > 0))
        g = nodes[loc]
        out[:, loc] = profiles.heat_pump_kw(temp[:, c], heat[g], limits[g], shifts[g], dhw[loc])
    return out


def _ev_nodes(ev, start, s, nodes):
    keep = np.asarray(ev.station) == s
    fields = ('node', 'station', 'arrive_h', 'kwh_grid', 'kw', 'deadline_h')
    ev_s = replace(ev, **{k: getattr(ev, k)[keep] for k in fields})
    ev_s = replace(ev_s, station=np.searchsorted(nodes, ev_s.node).astype(np.int32))
    return control.render(ev_s, np.asarray(start)[keep], len(nodes))


def distribute_controlled(raw, served):
    """Gesteuerte Stationsladung ``served`` (8760,) anteilig auf die Knoten mit ungesteuerter Last ``raw``.

    Je Stunde: Bedarf je Knoten = eigene Last + eigener Rückstau, alle Knoten bekommen denselben Anteil
    served/Bedarf der Station; Rückstau verfällt um 7 Uhr wie in ``control.controlled``.
    """
    raw = np.asarray(raw, dtype=float)
    served = np.asarray(served, dtype=float)
    out = raw.copy()
    total = raw.sum(axis=1)
    backlog = np.zeros(raw.shape[1])
    carry = False
    for h in range(raw.shape[0]):
        if carry or served[h] < total[h] - _EPS_KW:
            want = raw[h] + backlog
            w = want.sum()
            r = min(served[h] / w, 1.0) if w > 0 else 0.0
            out[h] = want * r
            backlog = want - out[h]
            carry = bool(backlog.sum() > 0)
        if h % 24 == control.DEADLINE_H and carry:
            backlog[:] = 0.0
            carry = False
    return out.astype(np.float32)


def station_block(p, params, f, s: int) -> NodeBlock:
    """Knotenflüsse der Station ``s`` aus dem Ergebnis ``f`` von ``run.flows`` (siehe Moduldoku)."""
    st = np.asarray(p.nodes_station)
    nodes = np.flatnonzero(st == s)
    hh = np.asarray(p.nodes_hh, dtype=float)[nodes]
    h0 = np.asarray(p.h0, dtype=float) * sim.KWH_PER_HH
    hh_kw = (h0[:, None] * hh[None, :]).astype(np.float32)
    kwp = np.asarray(p.nodes_kwp_bins, dtype=float)[nodes]
    pv_kw = ((np.asarray(p.pv_bins, dtype=float) * params.pv_factor) @ kwp.T).astype(np.float32)
    wp_kw = _wp_nodes(p, f['heat'], f['seed'], nodes)

    storage_kw = np.zeros((HOURS, len(nodes)), dtype=np.float32)
    sidx = np.asarray(f['storage_idx'])
    sel = np.flatnonzero(st[sidx] == s) if len(sidx) else np.zeros(0, int)
    if len(sel):
        storage_kw[:, np.searchsorted(nodes, sidx[sel])] = f['storage_delta'][:, sel]

    ev_kw = _ev_nodes(f['ev'], f['start'], s, nodes)
    v2g_kw = np.zeros_like(ev_kw)
    if params.charging in ('controlled', 'v2g'):
        ev_kw = distribute_controlled(ev_kw, f['ev_load'][:, s])
        if params.charging == 'v2g':
            cars = np.asarray(f['cars'], dtype=float)[nodes]
            if cars.sum() > 0:
                v2g_kw = (np.asarray(f['v2g'][:, s], dtype=float)[:, None] * (cars / cars.sum())[None, :]
                          ).astype(np.float32)
    return NodeBlock(hh_kw=hh_kw, pv_kw=pv_kw, wp_kw=wp_kw, storage_kw=storage_kw, ev_kw=ev_kw, v2g_kw=v2g_kw,
                     nodes=nodes, hh=hh, hh_peak_kw=float(h0.max()))
