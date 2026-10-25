"""Leitungstypen für synthetische NS-Netze: Grenzströme aus Weisenstein et al. 2022, Tab. 10 (Spec 4.3)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class LineType:
    name: str
    i_max_a: float     # thermischer Grenzstrom
    r_ohm_km: float
    x_ohm_km: float
    overhead: bool     # Freileitung (Al-Bündel) statt Kabel


# Reihenfolge = Auswahlreihenfolge (kleinster passender Typ zuerst)
TRUNK_CABLE = [
    # r/x: pandapower-Standardtyp 'NAYY 4x50 SE'
    LineType('NAYY 4x50', 144, 0.642, 0.083, False),
    # r/x: pandapower-Standardtyp 'NAYY 4x150 SE'
    LineType('NAYY 4x150', 275, 0.208, 0.080, False),
    # r/x: Herstellerdatenblatt NAYY 4x240 (r ~ 0,125 Ohm/km); x ~ 0,08 wie 4x150, Annahme
    LineType('NAYY 4x240', 313, 0.125, 0.080, False),
]
TRUNK_OVERHEAD = [
    # r: Literatur Al-Luftkabel 4x70 (~0,443 Ohm/km); x = 0,083 wie RURAL_LINE in gridsim/legacy (Annahme für 4x70)
    LineType('Al 4x70', 255, 0.443, 0.083, True),
    # r/x: wie RURAL_LINE in gridsim/legacy/steyr_sim_variant_a.py (Al 95 Bündel)
    LineType('Al 4x95', 320, 0.320, 0.083, True),
]
SERVICE = {
    # Hausanschluss Kabel: r Herstellerdatenblatt NAYY 4x35 (~0,868 Ohm/km); x = 0,083 Annahme
    False: LineType('NAYY 4x35', 123, 0.868, 0.083, False),
    # Hausanschluss Freileitung: r Literatur Al 4x25 (~1,20 Ohm/km); x = 0,083 Annahme
    True: LineType('Al 4x25', 135, 1.20, 0.083, True),
}
