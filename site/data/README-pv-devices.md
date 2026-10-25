# PV- und Speicher-Layer Steyr (TEB-Hackathon-Demo)

Erzeugt von `synth_pv_v2.py` und `site_data.py` (Seed 20261024), Stand 2026-10-24.

## pv_storage.geojson
Punkt je Gebäude mit PV (WGS84), 5321 Features.

| Feld | Bedeutung |
|---|---|
| id | Gebäude-/Anlagen-ID (`pv-bld-*` Dach, `pv-ground-*` BOKU ohne DKM-Gebäude) |
| gkz | Gemeindekennziffer (Statistik Austria) |
| class | klein / haus / gross / halle / freiflaeche / dach_ohne_dkm |
| kwp | Leistung in kWp |
| azimuth_deg, tilt_deg | Ausrichtung (0 = N, 180 = S) und Neigung |
| pv_evidence | `boku` = BOKU-PV-Polygone 2021–23 (echt), `model_2025` = vom nachtrainierten Modell auf DOP 2025 erkannt, ohne BOKU (Zubau oder Fehltreffer), `synthetic` = gemockter Zubau außerhalb des BOKU-Gebiets |
| model_2025_status | `confirmed` (BOKU und Modell), `new_since_2023` (nur Modell), `only_boku` (Modell findet nichts: abgebaut, verdeckt oder übersehen; Recall 55 %), leer außerhalb des BOKU-Gebiets |
| model_kwp | kWp aus der Modulfläche des Modells (5,5 m²/kWp; Modell unterschätzt Fläche ca. 15 %) |
| storage_kwh, storage_kw | Heimspeicher, **immer synthetisch** |
| storage_evidence | `synthetic` |
| segment_id | Ortsnetzstation (OSM-ID) aus building_station.json der Netzsimulation: nächster Knoten in EPSG:31287, über 600 m → null |
| device_id | Verweis auf devices.json |

## devices.json
1778 Speicher, **vollständig gemockt**: anonyme Herstellerklassen A–E (keine echten Marken),
angenommene Zuverlässigkeit je Klasse, je Gerät 6 Testabrufe (April–September 2026, je 15 min)
mit angefordert/geliefert, Reaktionszeit und Smart-Meter-Verifikation.

## Quellen und Lizenzen
- BOKU University, PV-Polygone aus Orthofoto-Segmentierung Österreich (Orthofotos 2021–2023), Zenodo doi:10.5281/zenodo.18152782, CC BY 4.0
- Modell: agademer/yolo-remote-sensing-photovoltaic (CC BY 4.0), nachtrainiert mit BOKU-Polygonen auf BEV DOP 2025 (CC BY 4.0); Validierung: Recall 55 %, Präzision 69 % gegenüber BOKU
- BEV, Digitale Katastralmappe (Gebäude), CC BY 4.0
- Statistik Austria, Gemeindegrenzen und Bevölkerung 1.1.2026, CC BY 4.0
- Zubau-Faktor 1,6 (Österreich ~6,2 GW Ende 2023 → ~9,9 GW Ende 2025) und alle Speicher-/Geräteangaben: Annahmen
