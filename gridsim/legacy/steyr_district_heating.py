#!/usr/bin/env python3
"""Näherung der Fernwärmegebiete in Steyr für die Wärmepumpen-Zuteilung.

Eine Netzkarte ist nicht veröffentlicht. Belegt sind Wohnungen mit Fernwärme in Münichholz,
Ennsleite, Resthof und Tabor (Biomasseheizkraftwerk Steyr, Fernheizwerke Ennsleite/Resthof),
getragen vor allem von rund 4 000 GWG- und fast 3 000 WAG-Wohnungen; insgesamt versorgt die
Fernwärme Steyr rund 8 000 Wohneinheiten (Belege: docs/research/2026-10-24-netzmodell-belege.md,
F1-F6). Abgrenzung: Ein Mehrfamilienhaus gilt als fernwärmeversorgt, wenn sein nächster
OSM-Stadtteilpunkt (place=suburb/quarter/neighbourhood) einer dieser Stadtteile ist und höchstens
MAX_DIST_M entfernt liegt (Voronoi-Zuordnung). Einfamilienhäuser bleiben ohne Fernwärme.
"""
import json

import numpy as np
from scipy.spatial import cKDTree

import steyr_pv_per_station as base

DISTRICTS = ('Münichholz', 'Ennsleite', 'Resthof', 'Tabor')
MAX_DIST_M = 800.0         # Annahme: Ausdehnung eines Stadtteils um seinen OSM-Punkt


def places(path):
    """OSM-Stadtteilpunkte (Name, Lambert-Koordinaten) aus einer Overpass-Antwort."""
    out = []
    for e in json.loads(path.read_text(encoding='utf-8'))['elements']:
        c = e.get('center', e)
        if 'lat' in c and e.get('tags', {}).get('name'):
            out.append((e['tags']['name'], base.TO_LAMBERT.transform(c['lon'], c['lat'])))
    return out


def mark(nodes, place_list, districts=DISTRICTS, max_dist=MAX_DIST_M):
    """Setzt ``n['fw']`` für Mehrfamilienhäuser in den Fernwärme-Stadtteilen; gibt die Anzahl zurück."""
    names = [p[0] for p in place_list]
    d, i = cKDTree(np.array([p[1] for p in place_list])).query(np.array([n['xy'] for n in nodes]))
    count = 0
    for n, dist, k in zip(nodes, d, i):
        n['fw'] = bool(n['hh'] > 1 and names[k] in districts and dist <= max_dist)
        count += n['fw']
    return count
