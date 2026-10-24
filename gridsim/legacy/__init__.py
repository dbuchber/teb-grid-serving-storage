"""Eingefrorene Kopien der Steyr-Skripte von hetzner (Stand FROZEN_AT, Prüfsummen in SHA256SUMS).

Die Skripte laden sich gegenseitig über ihren Dateinamen (``import steyr_pv_per_station as base``);
``load`` legt dieses Verzeichnis dafür an den Anfang von ``sys.path``. Nur für die Vorbereitung und als
Referenz in Tests, nicht im Live-Pfad.
"""
import importlib
import sys
from pathlib import Path

FROZEN_AT = '2026-10-24'
DIR = Path(__file__).parent


def load(name):
    if str(DIR) not in sys.path:
        sys.path.insert(0, str(DIR))
    return importlib.import_module(name)
