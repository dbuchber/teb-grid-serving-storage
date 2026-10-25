# Grid-Serving Storage

TEB AI Hackathon: Critical Infrastructure & Energy Security, 23.–25.10.2026, weXelerate Wien. Challenge-Partner: Smart Grids Austria.

**Pitch:** Ein Interoperabilitätsprofil, mit dem ein Verteilnetzbetreiber Heimspeicher im Engpass signiert, begrenzt und überprüfbar abrufen kann, und eine Jahressimulation aller 257 Trafos in Steyr, die zeigt, wo das hilft und wo nicht.

## For the jury

- **What:** an interoperability profile (actors, processes P1–P10, interfaces, hard limits in a control box, PKI, LoRaWAN broadcast) plus `gridsim`, an hourly full-year simulation of all 257 transformers in Steyr / Steyr-Land for three real weather years.
- **Live demo:** https://teb-hackathon.bbger.at (login required): presentation at `/`, full write-up with all assumptions and sources at `/details`.
- **Key result:** home batteries are the wrong tool for winter peaks; they help for short summer peaks and as a bridge until a transformer is replaced. Controlled charging is the cheaper first step.
- **Profile:** [docs/context/profil-v2.md](docs/context/profil-v2.md). **Threat model:** [docs/bedrohungsmodell.md](docs/bedrohungsmodell.md).
- **Code:** `gridsim/` (simulation), `api/` (FastAPI), `web/gridsim/` (dashboard), `site/` (presentation), `apps/insight-harbor/` (battery calculator).
- **Tests:** `uv run pytest` → 78 passed, 1 skipped. Calculator: `bun run test` → 15 passed.
- **AI:** a PV detection model on 2025 aerial images (recall 55 %, precision 69 %); its result is shown on the map only, the simulation uses the BOKU PV data. No AI in the control path, by design.
- **Honesty:** simulation only, nothing was tested against live grids, devices or third-party systems. Real, synthetic and mocked data are marked (table below).
- **Built with AI coding assistants:** Claude Code for most code and texts; the calculator was generated with Lovable. The team reviewed the results.

## Aufbau des Repositorys

| Pfad | Inhalt |
|---|---|
| `gridsim/` | Simulation: Vorbereitung der Eingangsdaten (`prepare.py`), Lauf je Wetterjahr und Szenario (`run.py`, `control.py`, `profiles.py`), Kennzahlen (`metrics.py`), Tagesansicht (`drilldown.py`), Abspielwoche (`playback.py`), Abnahme gegen die Referenz (`validate.py`), CLI (`cli.py`). `legacy/` = eingefrorene Referenzskripte mit SHA256SUMS. |
| `api/` | FastAPI-Rechen-API für die Live-Demo (`app.py`: Stationen, Läufe mit Fortschritt per SSE, Tagesansicht, Kosten). |
| `web/gridsim/` | ES-Module des Dashboards (Karte, Bänder, Diagramme, API-Client), mit `node --test` getestet. |
| `site/` | Präsentation (`index.html`) und ausführliche Seite (`details.html`); Arbeitskopie unter `docs/context/site/`. |
| `apps/insight-harbor/` | Batterie- und Kostenrechner (React/TypeScript, mit Lovable erzeugt), Modell in `src/lib/model.ts`. |
| `docs/context/profil-v2.md` | Interoperabilitätsprofil v2 (Akteure, Prozesse, harte Grenzen, PKI, LoRaWAN-Rechnung, Pilotplan). |
| `docs/bedrohungsmodell.md` | Bedrohungsmodell auf einer Seite. |
| `docs/ems-konzept.md` | EMS-Konzept der Box (Kurzfassung: `docs/ems-konzept-kurzfassung.md`). |
| `docs/research/` | Recherche: Regulierung, Pilotprojekte, Protokolle, Security, Geräte, Förderung, Großspeicher. |
| `docs/gridsim-abnahme.md` | Abnahme von `gridsim` gegen die Referenzskripte. |
| `docs/challenge/` | Originaltext der Challenge und Abgabevorlage. |
| `deploy/` | Dockerfile, Compose und Betriebsnotizen für den Server. |
| `tests/` | pytest-Suite für `gridsim` und `api`. |

## Lokal starten

Voraussetzungen: Python ≥ 3.12 und [uv](https://docs.astral.sh/uv/); für den Rechner Node ≥ 20 bzw. Bun.

```sh
uv sync
uv run pytest                          # 78 passed, 1 skipped (Tests laufen mit Fakes, ohne Serverdaten)
node --test web/gridsim/*.test.mjs     # Dashboard-Module

cd apps/insight-harbor && bun install && bun run test   # Rechner: 15 Tests
bun run dev                                              # Rechner lokal
```

Simulation und API brauchen vorbereitete Eingangsdaten. **Diese stammen aus der Datenpipeline des Teams auf dem Server (`/data/infra-kg-austria/...`) und liegen nicht im Repository** (Größe, teils Lizenzen der Rohdaten). Mit Zugriff auf diese Daten:

```sh
uv run python -m gridsim prepare --input /data/infra-kg-austria/work/steyr-pv-2026-10-24/input --out prepared
uv run python -m gridsim batch --prepared prepared --cache cache --years 2023 --scenarios 2030
uv run python -m gridsim validate --prepared prepared --cache cache   # schreibt docs/gridsim-abnahme.md
GRIDSIM_PREPARED=prepared GRIDSIM_CACHE=cache uv run uvicorn api.app:app_from_env --factory --port 17061
```

Betrieb im Container: siehe [deploy/README.md](deploy/README.md).

## Architektur in Kürze

1. **Datenpipeline (außerhalb des Repos):** offene Daten (OSM, BEV, BOKU-PV, PVGIS, GeoSphere INCA, DORIS) → synthetische Niederspannungsnetze und Eingangsdateien je Trafo.
2. **`gridsim prepare`** verdichtet sie je Wetterjahr; **`gridsim/run.py`** rechnet 8 760 Stunden für alle 257 Trafos mit 20 Zufallsziehungen (Wärmepumpen, E-Autos), Lade- und Speichervarianten, Thermik nach IEC 60076-7; Ergebnisse werden mit Modellversion im Schlüssel gecacht.
3. **`api/`** startet Läufe, streamt Fortschritt und liefert Bänder (Median, P10–P90) und Tagesverläufe.
4. **`web/gridsim/` und `site/`** zeigen Karte, Bänder und die Prozesse P4/P5; die Seite liegt hinter oauth2-proxy.
5. **Rechner** (`apps/insight-harbor`) rechnet Förderung, Eigenkosten und Kostenvergleich Speicher gegen Trafotausch im Browser.

## Was ist echt, synthetisch, gemockt

Gleiche Einteilung wie in `details.html` (Schritte 1–8, Kapitel 7 „Quellen“) und Folie „Security, resilience and what is real“.

| Baustein | Status | Quelle bzw. Annahme |
|---|---|---|
| Trafostationen, Straßen (Schritt 1) | **echt** (offene Daten) | OpenStreetMap; Umspannwerke ebUtilities |
| Fehlende Trafostandorte (Schritt 1) | **synthetisch** | regelbasiert gesetzt, auf der Karte hohl |
| Gebäude und Adressen (Schritt 2) | **echt** | BEV-Adressregister, DORIS LoD1 |
| Niederspannungsnetz, Trafogrößen (Schritt 2) | **synthetisch** | entlang der Straßen, kalibriert an DG DemoNet und TU-Wien-Referenznetzen |
| PV-Anlagen 2021–23 (Schritt 3) | **echt** | BOKU, Zenodo (CC BY 4.0); Erzeugung je Stunde mit PVGIS 5.3 |
| PV-Zubau seit 2023 (Schritt 3) | **KI-Ergebnis, nur Karte** | eigenes Modell auf BEV-Orthofotos 2025; geht nicht in die Simulation ein |
| Künftiger PV-Ausbau ×1,5 / ×2 (Schritt 3) | **synthetisch** | Szenario |
| Heimspeicher (Schritt 4) | **synthetisch** | Regel: Hälfte der Haushalte mit PV, 20 % der Betriebe mit PV |
| Haushaltslast, Heizbedarf (Schritt 5) | **echt** (Profile) / **synthetisch** (Zuteilung) | APCS H0, TABULA, Statistik Austria, when2heat |
| Wer hat Wärmepumpe oder E-Auto (Schritt 5) | **synthetisch** | Zufall, 20 Ziehungen |
| Wetter 2012/2017/2023 (Schritt 6) | **echt** | GeoSphere Austria INCA, Station Wachtberg, PVGIS |
| Speichergeräte, Hersteller, Testabrufe, Zuverlässigkeit | **gemockt** | anonyme Herstellerklassen A–E, 6 Testabrufe je Gerät; veranschaulicht nur Prozess P3 |
| Box, PKI, LoRaWAN, OpenADR | **Konzept** | nicht implementiert, nicht gegen echte Geräte getestet |

Nichts wurde gegen Live-Netze, Geräte oder Drittsysteme getestet.

## KI im Projekt

**PV-Erkennung auf Orthofotos.** YOLO-Segmentierung (Ultralytics), Ausgangsmodell `agademer/yolo-remote-sensing-photovoltaic` (CC BY 4.0), nachtrainiert mit den BOKU-PV-Polygonen auf BEV-Orthofotos 2025 (DOP, CC BY 4.0) der Region Steyr. Validierung auf 310 Kacheln in getrennten ~1-km-Blöcken (nicht trainiert, aber zur Wahl der besten Trainingsrunde genutzt) gegen BOKU 2021–23: **Recall 55 %, Precision 69 %** (Ausgangsmodell 37 % / 58 %). Das Ergebnis wird **nur auf der Karte** gezeigt (Zubau seit 2023 oder Fehltreffer, nicht von Hand geprüft); die Simulation verwendet die BOKU-Anlagen.
Der Trainings- und Inferenzcode liegt in der Datenpipeline des Teams, nicht in diesem Repository: `/data/infra-kg-austria/pv-steyr/` (`make_dataset.py` Datensatz, `infer_tiles_gpu.py` Inferenz, `compare_model_boku.py` Vergleich mit BOKU, Gewichte `models/seg300.pt`, Datenbeschreibung `site-data/README.md`).

**Im Steuerungs- und Abrufpfad gibt es keine KI**, bewusst: Abrufe sind deterministisch, signiert und prüfbar, der VNB-Operator gibt frei.

**Werkzeuge beim Bauen:** Code, Recherche und Texte sind mit KI-Codingassistenten entstanden (Claude Code); der Rechner wurde mit Lovable erzeugt. Das Team hat die Ergebnisse geprüft und die Zahlen stichprobenartig nachgerechnet.

## Abgabe

Deadline Sonntag, 25.10.2026, 11:30. Struktur: [docs/challenge/submission-template.txt](docs/challenge/submission-template.txt). Anforderungen: [docs/anforderungen.md](docs/anforderungen.md).
