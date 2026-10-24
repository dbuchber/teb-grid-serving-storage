"""Vorbereitete Arrays eines Wetterjahres laden (memory-mapped, siehe prepare.py)."""
import json
from dataclasses import dataclass
from datetime import date
from functools import cached_property
from pathlib import Path

import numpy as np

ARRAYS = ('nodes_station', 'nodes_hh', 'nodes_kwp_bins', 'nodes_kwh', 'nodes_fw', 'nodes_cell', 'nodes_heat_kwh',
          'nodes_dhw', 'pv_bins', 'h0', 'h0_q', 'temp_cells')


@dataclass(frozen=True)
class Prepared:
    year: int
    root: Path
    nodes_station: np.ndarray   # (N,) Index in stations
    nodes_hh: np.ndarray        # (N,) Haushalte, 0 = Halle/Stall
    nodes_kwp_bins: np.ndarray  # (N, 4) kWp je Ausrichtung (PVGIS_BINS)
    nodes_kwh: np.ndarray       # (N,) Heimspeicher kWh, 0 = keiner
    nodes_fw: np.ndarray        # (N,) Fernwärme, keine Wärmepumpe
    nodes_cell: np.ndarray      # (N,) Spalte in temp_cells
    nodes_heat_kwh: np.ndarray  # (N,) Jahreswärme aus LoD1, NaN = Pauschalwert
    nodes_dhw: np.ndarray       # (N,) Warmwasseranteil, NaN = Default
    pv_bins: np.ndarray         # (8760, 4) kW je kWp
    h0: np.ndarray              # (8760,) Anteil am Jahresverbrauch je Stunde
    h0_q: np.ndarray            # (35040,) Anteil je Viertelstunde
    temp_cells: np.ndarray      # (8760, C) °C
    stations: list

    @property
    def station_ids(self):
        return [s['id'] for s in self.stations]

    @property
    def n_stations(self):
        return len(self.stations)

    @property
    def first_weekday(self):
        return date(self.year, 1, 1).weekday()

    @cached_property
    def kva(self):
        return np.array([s['kva'] for s in self.stations], dtype=float)


def load_prepared(root, year):
    d = Path(root) / str(year)
    arrays = {name: np.load(d / f'{name}.npy', mmap_mode='r') for name in ARRAYS}
    stations = json.loads((d / 'stations.json').read_text())
    return Prepared(year=year, root=Path(root), stations=stations, **arrays)
