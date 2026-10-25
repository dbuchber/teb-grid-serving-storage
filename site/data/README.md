# Daten der TEB-Demo (Steyr)

Erzeugt mit `scripts/steyr_demo_export.py` aus den Läufen in
`hetzner-wikidata:/data/infra-kg-austria/work/steyr-pv-2026-10-24/`.
Stand 24.10.2026. Alles sind Modellwerte, keine Messungen. Koordinaten WGS84, Leistungen kW, Energien kWh.

| Datei | Inhalt |
|---|---|
| `stations.geojson` | 257 Ortsnetzstationen (Punkte), Eigenschaften siehe unten |
| `uw.geojson` | Umspannwerke mit freier Netzanschlusskapazität (ebUtilities, MW) |
| `building_station.json` | Zuordnung Knoten → Station, für PV-/Speicher-Layer mit derselben Segment-ID |
| `timeseries/index.json` | 5 Beispielstationen und ihre Dateien |
| `timeseries/<id>.json` | Trafo-Last am stärksten Sommertag (je Strategie) und Wintertag (WP und E-Auto getrennt) |
| `v2g.json` | V2G-Demo 2030/2040: Annahmen, Fälle, Abendzeitreihen |
| `v2g_cases.json` | 8 V2G-Fälle (2030/2040 × schwach/typisch × ungesteuert/gleichzeitig) mit 48-h-Stundenreihen |
| `mv_lines.geojson` | Synthetische Mittelspannungstrassen Umspannwerk → Station entlang der Straßen |
| `meta.json` | Achsen, Szenario-Anteile, Beispielstationen, Quellen für die Attribution |

## stations.geojson, `properties`

- `id`: OSM-ID (`node/…`, `way/…`) oder `demo:steyr:station-NNN`. Bei `synthetisch: true` ist die Station
  synthetisch platziert (k-Means), also gemockt, und muss so gekennzeichnet werden.
- `uw`, `netzart` (`stadt`/`land`), `klasse` (PV am Niederspannungsnetz), `kwp`, `haushalte`, `wohngebaeude`,
  `trafo_kva`, `abgaenge`, `abgang_max_m`, `speicher` (Anzahl Heimspeicher im Modell), `fernwaerme_haushalte`.
- `sommer.<strategie>` für `base`, `fixcap`, `forecast`, `room`:
  - `rueckspeisung_max_kw`, `bezug_max_kw`;
  - `spitze_vs_basis_pct` (Änderung der Rückspeisespitze);
  - `du_max_pct` (Spannungsanhebung, Lastfluss auf dem Straßennetz);
  - `kabel_max_pct`.
  - Wetter 2023, ohne Wärmepumpen und E-Autos.
- `engpass["<wetterjahr>|<szenario>|<pv_faktor>|<richtung>"]`. Ein Schlüssel fehlt, wenn die Station dort keinen Engpass hat.
  - Werte: `engpass_h`, `ereignisse`, `e_netto_kwh`, `p_max_kw`, `speicher_noetig`, `speicher_vorhanden`,
    `trafo_noetig_kva` und `trafo_stufen` (Normgrößen-Schritte; `null` = über 1 000 kVA).
  - Achsen laut `meta.json`: Wetterjahre 2012/2017/2023, Szenarien heute/2030/2040, PV-Faktor 1.0/1.5/2.0, Richtung `einspeisung`/`bezug`.

## building_station.json

`knoten` ist eine Liste von Zeilen nach `spalten`: `lon`, `lat`, `station`, `haushalte`, `kwp`, `speicher_kwh`, `fernwaerme` (0/1).

- Ein Knoten ist ein Wohngebäude (BEV-Adressregister, Eigenschaft 01/02) mit der PV, die innerhalb von 40 m dazu gehört.
- Ein Knoten ohne Haushalt ist eine eigenständige PV-Anlage (Stall, Halle).
- Zuordnung zur nächsten Station innerhalb von 600 m (EPSG:31287).
- Wer eigene Objekte zuordnen will: dieselbe Regel verwenden oder auf den nächsten Knoten mappen.

## lv_lines.geojson und lv_hausanschluesse.geojson (synthetische Niederspannungsnetze)

- Alle Leitungen sind **synthetisch**, aber **entlang der Straßen** (OpenStreetMap, ODbL) geführt. Einen echten Leitungsplan gibt es nicht.
- Aufbau des Netzes:
  - Von der Station läuft je Gebäude der kürzeste Weg im Straßennetz bis zum nächsten Straßenpunkt.
  - Die Vereinigung dieser Wege ist der Strang.
  - Jeder Ast ab der Station ist ein Abgang. Äste mit mehr als 27 Gebäuden werden an Abzweigen in weitere Abgänge geteilt (mehrere Kabel im selben Graben), höchstens 11 je Station.
  - Ergebnis: im Median 3 Abgänge je Station (P10–P90: 1–9).
- `lv_lines.geojson`: 18 115 Abschnitte, 4,9 MB, Koordinaten mit 5 Nachkommastellen, Geometrie auf 2 m vereinfacht.
  - Auf Sammlungsebene: `synthetisch: true`, `leitungstypen` und `trassen`.
  - Felder:
    - `station`
    - `abgang`: `A1`… Abgänge nach Größe; `D1`… Direktabgänge; `X` = Gebäude ohne Straße im Umkreis von 150 m, als Luftlinie.
    - `direkt`
    - `typ`: `kabel` = NAYY 4x150 (Stadt und Direktabgänge), `freileitung` = Al 95 Bündelleiter (Land).
    - `parallel`
    - `laenge_m`: echte Trassenlänge entlang der Straße.
    - `auslastung_max_pct`: höchste Auslastung im Lastfluss der 24 stärksten Rückspeisestunden. Grundlage: Basisfall, Wetter 2023, ohne Wärmepumpen und E-Autos.
- `lv_hausanschluesse.geojson`: 17 693 Hausanschlüsse (NAYY 4x50) vom Straßenpunkt zum Gebäude, 2,9 MB.
  - Felder: `station`, `abgang`.
  - Empfehlung: erst ab Zoom ≥ 16 einblenden.

## v2g_cases.json

- `faelle`: Liste mit 8 Einträgen. Die `id` setzt sich zusammen aus `<szenario>-<rolle>-<fall>`, zum Beispiel `2040-schwach-gleichzeitig`.
- Die beiden Stationen sind `schwach` = `way/235746848` und `typisch` = `node/12794591194`.
- Kennzahlen je Fall: `trafo_kva`, `e_autos`, `waermepumpen`, `spitze_kw`, `engpass_h_jahr`, `speicher_noetig`, `v2g_autos_noetig` und `gesteuert_ungeladen_kwh_jahr`.
- `zeit`: 48 Stundenstempel ab 00:00. Der Tag ist bei `gleichzeitig` der kälteste Tag (3.2.2012), sonst der Tag mit der höchsten Trafo-Spitze.
- `reihen` (je 48 Werte):
  - Last: `temperatur_c`, `haushalt_kw`, `waermepumpe_kw`;
  - E-Auto: `eauto_ungesteuert_kw`, `eauto_gesteuert_kw` (Ladeschluss 07:00), `v2g_kw` (Rückspeisung, positiv; begrenzt auf die Autos im Segment, die 70 % angesteckt);
  - Trafo: `trafo_ungesteuert_kw`, `trafo_gesteuert_kw`, `trafo_v2g_kw`. Liegt `trafo_v2g_kw` über `trafo_kva`, reichen die Autos nicht (2040 gleichzeitig).
- Annahmen in `annahmen` (V2G: 11 kW, 15 kWh nutzbar, Verfügbarkeit 0,7).

## mv_lines.geojson (synthetische Mittelspannung)

- Je Umspannwerk der kürzeste Weg im OSM-Straßennetz zu jeder seiner Stationen. Gemeinsame Abschnitte gibt es nur einmal, das Ergebnis ist also ein Baum je UW.
- Kein Lastfluss und keine Ringe, Kabelart offen. Es ist eine Darstellung, kein Leitungsplan.
- Felder:
  - `uw`
  - `trasse`: `strasse`, `stich` (Straßenpunkt → Station) oder `luftlinie`. Luftlinie heißt: Das Umspannwerk liegt außerhalb der Straßendaten (Bad Hall, Großraming, Haag Süd) oder die Station ist über 1 km von jeder erreichbaren Straße entfernt.
  - `stationen`: Zahl der Stationen hinter dem Abschnitt, als Maß für die Linienbreite.
  - `laenge_m`
  - `station`: nur bei `stich` und bei der Luftlinie zur Station.
- 716 Abschnitte, davon 4 Luftlinien. 395 km entlang der Straßen, 260 kB.

## Ergänzungen 24.10.2026 abends (Nachrechnung zum Gutachten)

Quelle: `hetzner-wikidata:/data/infra-kg-austria/work/steyr-gutachten-2026-10-25/`, Bericht
`docs/reports/2026-10-24-nachrechnung-gutachten.md`.

- `stations.geojson`, `engpass[...]`: neu `speicher_ohne_nachladen` (alte Zählung), `thermisch` (IEC 60076-7) und
  `heisspunkt_max_c`. `speicher_noetig` zählt jetzt eine Flotte mit Nachladen unter der Grenze.
  `sommer` enthält zusätzlich die Strategie `room_persist` (Persistenzprognose).
- `v2g_cases.json`: Simulation je Auto. Neue Felder `gesteuert_rest_h_jahr`, `gesteuert_rest_p_kw`, `v2g_rest_h_jahr`,
  `v2g_rest_p_kw`, `v2g_autos_max`, `v2g_kwh_jahr`, `v2g_ungeladen_kwh_jahr`, Reihe `eauto_v2g_laden_kw`;
  `v2g_autos_noetig` entfällt.
- `sensitivity.json`: Referenz 2040/2017, je Variante Kennzahlen und Abweichung, Seeds (P10/Median/P90).
- `cost_benefit.json`, `cost_benefit_nur_box.json`: günstigstes Mittel je Engpass-Station und Jahreskosten.
