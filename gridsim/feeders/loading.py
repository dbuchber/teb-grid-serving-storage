"""Abschnittsfluss und Auslastung je Station (Spec 4.4, Entscheidung 8).

Abschnittsfluss = Summe der Knotenflüsse hinter dem Abschnitt (radial, ohne Verluste), Stunde für Stunde.
Die Haushaltslast bekommt je Abschnitt den Spitzenzuschlag f(n) = max(1, g(n)·P_HH / Spitze des H0-Profils je
Haushalt), n = Haushalte hinter dem Abschnitt (n = 0 → 1): Das H0-Profil ist für große Kollektive geglättet,
so verwenden Bemessung und Bewertung dieselbe Spitze. Der Trafo wird ohne Zuschlag bewertet (run.flows).
"""
import numpy as np

from gridsim.feeders.sizing import COS_LOAD, P_HH_KW, U_V, SizedGrid, g
from gridsim.feeders.topology import StationGrid

_K_KW_PER_A = np.sqrt(3.0) * U_V / 1000.0   # kW je A bei cos φ = 1


def surcharge_factor(n_hh, hh_peak_kw):
    """Spitzenzuschlag f(n) der Haushaltslast je Abschnitt; ``hh_peak_kw`` = max(h0)·KWH_PER_HH."""
    return np.maximum(1.0, g(n_hh) * P_HH_KW / float(hh_peak_kw))


def _columns(grid: StationGrid, block):
    """Spaltenreihenfolge des Blocks passend zu ``grid.node_index``."""
    nodes = np.asarray(block.nodes)
    if np.array_equal(nodes, grid.node_index):
        return None
    order = np.argsort(nodes)
    pos = order[np.searchsorted(nodes, grid.node_index, sorter=order)]
    if not np.array_equal(nodes[pos], grid.node_index):
        raise ValueError(f'Station {grid.station}: Knoten des Netzes fehlen im Knotenblock')
    return pos


def segment_flow(grid: StationGrid, sized: SizedGrid, block, surcharge=True) -> np.ndarray:
    """Abschnittsfluss (8760, m) in kW, + = Bezug: ``block.net() @ downstream.T`` plus (f(n) − 1)·Haushaltsanteil.

    ``surcharge=False`` lässt den Spitzenzuschlag weg (dann ist die Summe der Wurzelabschnitte = Stationsfluss).
    ``sized`` wird nicht gebraucht, steht aber für eine einheitliche Schnittstelle mit ``loading_pct`` da.
    """
    d = grid.downstream.astype(np.float32).tocsr()
    pos = _columns(grid, block)
    net = block.net()
    if pos is not None:
        net = net[:, pos]
    out = np.asarray((d @ net.T).T, dtype=np.float32)
    if surcharge:
        if block.hh is None or block.hh_peak_kw is None:
            raise ValueError('Knotenblock ohne hh/hh_peak_kw: Spitzenzuschlag nicht berechenbar')
        hh = np.asarray(block.hh, dtype=float) if pos is None else np.asarray(block.hh, dtype=float)[pos]
        extra = surcharge_factor(d @ hh, block.hh_peak_kw) - 1.0
        hit = np.flatnonzero(extra > 0)
        if len(hit):
            hh_kw = block.hh_kw if pos is None else block.hh_kw[:, pos]
            out[:, hit] += (np.asarray((d[hit] @ hh_kw.T).T) * extra[hit][None, :]).astype(np.float32)
    return out


def loading_pct(seg_flow, sized: SizedGrid) -> np.ndarray:
    """Auslastung (%) je Stunde und Abschnitt: Strom / ``i_max_a``; cos φ 0,97 bei Bezug, 1,0 bei Einspeisung.

    ``sized.i_max_a`` enthält die Parallelführung schon (nicht noch einmal mit ``parallel`` multiplizieren).
    """
    p = np.asarray(seg_flow, dtype=np.float32)
    cos = np.where(p > 0, np.float32(COS_LOAD), np.float32(1.0))
    i_a = np.abs(p) / (np.float32(_K_KW_PER_A) * cos)
    return (np.float32(100.0) * i_a / np.asarray(sized.i_max_a, dtype=np.float32)[None, :]).astype(np.float32)
