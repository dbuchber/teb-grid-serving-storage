"""Gebietstyp je Station aus dem Abstand der Wohngebäude zu ihren Nachbarn (Spec 4.1)."""
from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

K_NEIGHBOURS = 4
MIN_HOMES = 5


@dataclass(frozen=True)
class AreaType:
    name: str
    max_nn_m: float       # obere Grenze des Median-Nachbarabstands (exklusiv)
    cable_share: float    # Kabelanteil der NS-Leitungen, Rest Freileitung
    max_feeder_m: float   # Grenze längster Strang


# Schwellen kalibriert (Plan Task 5 Step 5a, einmalig, danach fest): Startwerte stadt 30 m / ort 80 m ergaben auf
# prepared-ns einen Kabelanteil nach Trassenlänge von 68,6 % (Ziel 79 %, Band 74–84 %, Netz OÖ 2025). stadt und
# ort gemeinsam in 5-m-Schritten verschoben: +5 m → 75,3 % (+10 m → 80,7 %, −5 m → 66,8 %). Gewählt ist die
# kleinste Verschiebung ins Band, +5 m (stadt 35 m, ort 85 m). Nicht weiter nachstellen.
# Die 75,3 % stammen aus dem Kalibrierlauf auf prepared-ns; der abgenommene Endstand prepared-ns-fix4 hat nach
# späteren Regeländerungen (Mindestquerschnitt, Zusatzstationen) 74,4 %, weiter im Band (docs/gridsim-leitungen-abnahme.md).
AREAS = {a.name: a for a in (
    AreaType('stadt', 35.0, 1.0, 500.0),
    AreaType('ort', 85.0, 0.8, 700.0),
    AreaType('streu', float('inf'), 0.5, 1000.0),
)}


def classify(xy, hh):
    """Gebietstyp einer Station: Median über Wohngebäude des mittleren Abstands zu den 4 nächsten Wohngebäuden.

    ``xy`` (n, 2) in Metern, ``hh`` (n,) Haushalte je Gebäude; Hallen (hh == 0) zählen nicht.
    Weniger als 5 Wohngebäude: 'streu'.
    """
    homes = np.asarray(xy, dtype=float)[np.asarray(hh) > 0]
    if len(homes) < MIN_HOMES:
        return 'streu'
    k = min(K_NEIGHBOURS, len(homes) - 1)
    dist, _ = cKDTree(homes).query(homes, k=k + 1)    # Spalte 0 ist das Gebäude selbst
    median = float(np.median(dist[:, 1:].mean(axis=1)))
    return next(a.name for a in AREAS.values() if median < a.max_nn_m)
