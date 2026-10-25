# Lückenanalyse für die Abgabe (25.10.2026, 11:30)

Stand: 25.10.2026, 09:35, Remote-Session auf hetzner. Grundlage: `docs/challenge/challenge-grid-serving-storage.txt`,
`docs/challenge/submission-template.txt`, `docs/context/profil-v2.md`, `docs/context/site/index.html` und `details.html`
(lokale Kopie, die Live-Seite kann neuer sein), Repo-Stand `feat/gridsim` (HEAD `232691f`).
Textvorschläge für das Formular sind auf Englisch und können direkt kopiert werden.

## 0. Das Wichtigste in drei Zeilen

1. **Die Jury kommt heute an nichts heran.** Das Repo `github.com/dbuchber/teb-grid-serving-storage` liefert ohne Anmeldung HTTP 404 (privat), und die Demo `teb-hackathon.bbger.at` leitet auf einen OAuth-Login um (HTTP 302 nach `/oauth2/start`). Beides muss vor 11:30 gelöst sein, sonst zählen Code, Demo und Doku nicht.
2. **Die README ist leer** („Repo angelegt; Projektdesign in Arbeit“). Das Template verlangt: lokal starten, Architektur, was echt und was gemockt ist.
3. **Viel Arbeit ist nicht committet** (`apps/`, `docs/context/` mit Profil v2 und Webseite, `docs/arbeitsstand.md`, `docs/research/08`, Änderungen an `web/gridsim/dashboard.js` u. a.). Das Profil v2, das Hauptergebnis der Challenge, liegt nicht im Repo.

Inhaltlich ist die Challenge gut abgedeckt: Profil mit Akteuren, 10 Prozessen, Schnittstellen, Sicherheit und Pilotplan; Simulation mit Abnahme; Live-Demo mit Präsentation, Detailseite und Dashboard. Es fehlen vor allem Zugang, Doku und Formulartexte.

## 1. Prioritätenliste bis 11:30

Reihenfolge nach Wirkung je Minute. Alle Schritte brauchen die Freigabe des Owners (diese Session committet, pusht und deployt nicht).

| Prio | Was | Wer | Aufwand | bis |
|---|---|---|---|---|
| P0 | Zugang Jury zur Demo: entweder öffentlicher Pfad ohne Login (nur statische Präsentation `/` und `/details`, Dashboard optional) oder Jury-Zugangsdaten im Feld „Notes“; vorher entscheiden | Owner + Session 18 (Caddy/oauth2-proxy) | 15–30 min | 10:30 |
| P0 | Repo-Zugang: Repo öffentlich machen **oder** TEB-Orga und Jury als Collaborator einladen (Template: „Public, or shared with the TEB organisers and the jury“). Vorher prüfen, dass keine Geheimnisse im Verlauf stehen (`.env` ist ignoriert; `git log -p` kurz nach Tokens, Hostnamen, Mails durchsuchen) | Owner | 10–20 min | 10:30 |
| P0 | Offene Arbeit committen und pushen: Profil v2 nach `docs/profil-v2.md` (aus `docs/context/`), Präsentation/Detailseite oder Link darauf, `apps/insight-harbor`, `gridsim/playback.py` mit `tests/test_playback.py` (beide unversioniert, laufen aber in den Tests mit), Recherche 08/09, die beiden neuen Dokumente; Logdateien `.remote-control.log` und `.jury-session*.log` **nicht** committen | Owner | 15 min | 10:45 |
| P0 | Formular ausfüllen mit den Texten aus Abschnitt 2 (Team, Kontakt, Track aus eigener Kenntnis ergänzen) | Owner | 20 min | 11:15 |
| P1 | README neu schreiben (Vorschlag in Abschnitt 3, ca. 60 Zeilen) | diese oder andere Session, Owner gibt frei | 15 min | 10:45 |
| P1 | Klarstellen, wo der KI-Code liegt: Das PV-Erkennungsmodell (Orthofotos, Recall 55 %, Precision 69 %) liegt nicht in diesem Repo, sondern in infra-kg (Session infra-kg-austria-51). Entweder Code bzw. Notebook und Kennzahlen-Skript ins Repo (`ai/pv-detection/`) oder in README und Notes ehrlich sagen, dass es ein separates Repo ist und ob es vor dem Hackathon existierte | Owner | 10 min (Text) / 30 min (Code) | 11:00 |
| P1 | Widerspruch Präsentation ↔ Profil v2 beheben: `index.html` sagt bei P5 „the box's signed measurement“; Profil v2 (Abschn. 6.6, 7) verifiziert über den Smart Meter, die Box liefert nur Eingaben. Ein Satz auf der Seite | Session Webseite | 5 min | 11:00 |
| P2 | Pitch-Deck-Link: die Präsentation unter `/` ist das Deck; im Feld „Pitch deck“ denselben Link angeben | Owner | 1 min | 11:15 |
| P2 | Ein Satz zu Großspeichern auf Seite und im Formular (siehe `docs/grossspeicher-integration.md`, Schritt C1) | Session Webseite | 15 min | 11:15 |
| P3 | Video-Fallback (≤ 5 min Bildschirmaufnahme der Demo) für den Fall, dass die Live-URL beim Juryzugriff ausfällt | Owner | 20 min | nur wenn Zeit bleibt |
| nach 11:30 | Großspeicher in gridsim, Profil v3, Lastprofile für Gewerbe | – | siehe Großspeicher-Dokument | Pitch/Nacharbeit |

Geprüft in dieser Session: `pytest` im Repo 78 bestanden, 1 übersprungen (25.10.2026, 09:33). Das ist der Beleg für „works“ in der README.

## 2. Feld für Feld: Status und Textvorschlag

Status: **fertig** = Inhalt da, nur übertragen; **Text fehlt** = Inhalt da, Formulartext fehlt; **Lücke** = Inhalt oder Zugang fehlt; **Owner** = nur der Owner kann es eintragen.

### 1. Project basics

| Feld | Status | Vorschlag |
|---|---|---|
| Project title | Text fehlt | **GridBox – Grid-Serving Storage** (Alternative ohne neuen Namen: „Grid-Serving Storage Steyr“, so heißt die Seite) |
| One-line pitch | Text fehlt | siehe unten |

> **One-line pitch:** An interoperability profile and a signed control box that let a grid operator briefly borrow home and business batteries to relieve overloaded transformers, tested on a year-long simulation of all 257 transformers around Steyr – and the household never loses money.

### 2. Team

| Feld | Status | Hinweis |
|---|---|---|
| Team name | Owner | nicht in den Unterlagen |
| Team members (Name – Organisation – GitHub – Rolle) | Owner | nicht in den Unterlagen; Primärkontakt zuerst |
| Primary contact email | Owner | Mail des Primärkontakts |

### 3. Challenge track

| Feld | Status | Vorschlag |
|---|---|---|
| Track | Owner (Auswahlfeld) | Critical Infrastructure & Energy Security – Challenge „Grid-Friendly / Grid-Serving Storage“ (Partner Smart Grids Austria) |
| Challenge prompt | fertig | Grid-Serving Storage: interoperability profile (IES method) for using customer storage against grid congestion |

### 4. What you built

**Problem you solved** – Status: Text fehlt (Inhalt in `index.html` Kap. 1–2).

> Distribution grids are running out of transformer capacity: in our year-long model of the Steyr region, 193 of 257 low-voltage transformers would be overloaded in a 2040 winter with heat pumps and electric cars, and rooftop PV already pushes some to their feed-in limit in summer. Thousands of home and business batteries sit in the same grid, but they only optimise self-consumption, the grid operator has no safe, standard way to use them, and the owner has no reason to let it. We focused on how a DSO can borrow those batteries for short, limited periods without harming the owner, the market or grid security.

**Solution overview** – Status: Text fehlt (Inhalt in Profil v2 und `index.html` Kap. 3–5).

> We designed a rough interoperability profile following the IES method: actors (DSO, household, supplier and balance responsible party, aggregator, TSO, smart-meter backend, trust anchor), ten use cases (P1 commissioning, P2 daily prices, P3 test calls, P4 congestion call, P5 verification and compensation, P6 fallback, P7 balance-group correction, P8 conflicts with third-party marketing, P9 segment assignment, P10 key revocation) and the interfaces between them. A certified box in the customer installation is the single entry point: the DSO sends one signed call per transformer segment via OpenADR (as required by the Austrian connection rules) or a LoRaWAN broadcast; the box checks signature, role, segment, sequence and hard limits, spreads the start and end over several minutes and drives the inverter locally via SunSpec, EEBUS or IEEE 2030.5. Verification uses smart-meter data and an open reference algorithm, and the household is compensated so it is never worse off; subsidies rise with the level of controllability. To size the problem we built a simulation of all 257 transformers in the Steyr region from open data (buildings, PV, real weather 2012/2017/2023, 20 random placements of heat pumps and cars), which compares battery strategies, smart charging, V2G and transformer upgrades. The live demo has a presentation, a detailed write-up, an interactive map and dashboard, and a cost calculator for the household.

**How AI is used** – Status: Text fehlt; **Lücke**: Code nicht in diesem Repo (siehe P1).

> AI is used to build the data, not to control the grid. We trained an image-recognition model on BOKU's PV outlines (aerial images 2021–23) and ran it on 2025 orthophotos to find solar systems built since then; it finds 55 % of real systems (recall) and 69 % of its finds are real (precision), and we checked it roof by roof against the BOKU map. Its output only feeds the simulation. All control decisions in the profile are deterministic and auditable on purpose: signed calls, fixed limits in the box, an open reference algorithm for compensation. Generative AI assistants (Claude) were used for research, coding and review; humans decided every design choice.

Hinweis: Den letzten Satz nur aufnehmen, wenn das Team das offenlegen will; die Jury schätzt Ehrlichkeit. Falls das PV-Modell vor dem 23.10. entstand, das hier sagen.

**Security and resilience** – Status: fertig (Inhalt in Profil v2 Abschn. 3, 5 und `index.html`), Text fehlt.

> Threat: an attacker, or a bug, that makes thousands of batteries switch at once and turns a grid-support tool into a grid-attack tool (forged or replayed commands, a stolen DSO key, fake prices from the home network, a radio or backend outage). Response: every role has its own key and certificate (ECDSA P-256, HSM at the DSO); the box accepts only signed calls for its own segment with a valid sequence number and expiry; hard limits in the firmware that no message can lift (at most 3 calls and 4 hours a day, ramp ≤ 10 %/min, random start and end spread over minutes, backup reserve never touched) cap what even a stolen key can do; keys are revoked over the radio with epoch counters; on loss of communication each box falls back to self-consumption with a staggered return. No manufacturer cloud is in the command path. A formal threat analysis (IEC 62443/NIS2) is still open and planned before the pilot.

**Data and environments** – Status: fertig, Text fehlt.

> Open data only: Austrian address and building register (BEV), OpenStreetMap substations and roads, BOKU PV map plus our own detection on 2025 orthophotos, PVGIS solar profiles, GeoSphere INCA temperatures for weather years 2012, 2017 and 2023, APCS standard load profiles, LoD1 building models for heat demand, published grid connection capacities. Synthetic: low-voltage cables, some transformer sites, which households get heat pumps, cars and batteries (20 random seeds). Mocked: test-call reliability per manufacturer and the battery devices. Steyr is only our test region; the method runs for any region with open data. We confirm that nothing was tested against live infrastructure, the venue network, real devices or other teams' systems.

**Tech stack** – Status: fertig, Text fehlt (nur, was im Repo liegt).

> Backend/simulation: Python 3.12+, NumPy, SciPy, Shapely, pyproj, FastAPI + Uvicorn (simulation API with job queue and cache), pytest; legacy grid models with pandapower. Frontend: static HTML/CSS and vanilla ES modules for the presentation, write-up and region dashboard (map, charts); household cost calculator in TypeScript, React, TanStack Start, Tailwind CSS, Recharts, Vitest (built with Lovable). AI: image-recognition model for PV detection on orthophotos (separate repo – link). Deployment: Docker Compose behind Caddy and oauth2-proxy on a Hetzner server. Standards referenced in the profile: OpenADR 3 / IEC 62746-10-1, LoRaWAN (TS004, TS005), SunSpec Modbus, EEBUS LPC/LPP, IEEE 2030.5, IEC 62559-2.

Prüfen: ob pandapower noch gebraucht wird (steht nicht in `pyproject.toml`, nur in `gridsim/legacy`); ggf. weglassen.

### 5. Links

| Feld | Status | Vorschlag / was fehlt |
|---|---|---|
| Code repository | **Lücke (P0)** | `https://github.com/dbuchber/teb-grid-serving-storage` – öffentlich machen oder Jury einladen; vorher committen und pushen |
| Demo link | **Lücke (P0)** | `https://teb-hackathon.bbger.at` – derzeit Login-Pflicht; öffentlich schalten oder Zugang in Notes |
| Documentation | **Lücke (P1)** | README neu (Abschnitt 3); dazu `https://teb-hackathon.bbger.at/details` und `docs/profil-v2.md` |
| Pitch deck | fertig, sobald Demo erreichbar | `https://teb-hackathon.bbger.at/` (die Präsentation ist das Deck) |
| Other links | Text fehlt | Interoperabilitätsprofil v2 (`docs/profil-v2.md`), Simulation-Abnahme (`docs/gridsim-abnahme.md`), Recherche (`docs/research/`), KI-Repo (falls freigegeben) |

### 6. Notes for the jury

Status: Text fehlt. Vorschlag (ehrlich, wie das Template es wünscht):

> All grid figures are model results from open data, not measurements; low-voltage cables, some transformer sites and the placement of heat pumps, cars and batteries are synthetic, and transformer ratings are estimated. The interoperability profile is a draft for discussion with a DSO, not a finished specification; values marked as proposals (limits, compensation rates, subsidy shares) are placeholders. The box, the radio channel and test-call reliability are mocked – there is no hardware. The PV detection model lives in a separate repository [link / or: is described but not included]. Business and commercial storage are covered by the same call and limits in the profile; a dedicated class for medium-voltage storage and its simulation are next steps. Steyr is only our test region. [If access needs login: Demo login: …]

### 7. Follow-up

Owner entscheidet; beeinflusst die Bewertung nicht.

## 3. README-Vorschlag (Gliederung, ca. 60 Zeilen)

1. Ein Absatz: was das Projekt ist (One-line pitch), Links zu Demo, Details, Profil.
2. **Ergebnis der Challenge:** Interoperabilitätsprofil v2 (`docs/profil-v2.md`) – Akteure, P1–P10, harte Grenzen, PKI, LoRaWAN, Verifikation, Pilotplan.
3. **Architektur** (5 Zeilen + kleine Liste): `gridsim/` Simulation (prepare → run → metrics), `api/` FastAPI mit Job-Queue und Cache, `web/gridsim/` Dashboard, `apps/insight-harbor/` Kostenrechner, `deploy/` Docker Compose.
4. **Lokal starten:** `uv sync --group dev`, `uv run pytest`; `uv run python -m gridsim prepare --input <input> --out prepared`; `uv run uvicorn api.app:app_from_env --factory`; Kostenrechner: `cd apps/insight-harbor && bun install && bun run dev`. Hinweis: Eingangsdaten (OSM, BEV, BOKU, PVGIS, INCA) sind nicht im Repo; Quellen und Lizenzen in `docs/`.
5. **Echt / synthetisch / gemockt:** Tabelle aus Abschnitt „Data and environments“.
6. **Status:** Tests (78 bestanden), Abnahme gegen Referenzrechnung (`docs/gridsim-abnahme.md`), bekannte Grenzen (keine Lastflussrechnung im Live-Modell, keine Gewerbelasten, Leitungsausbau nicht bepreist).
7. **Daten- und Hackathon-Erklärung:** nur offene/synthetische Daten, nichts gegen Live-Infrastruktur getestet; was vor dem Hackathon existierte (infra-kg als Werkzeug, siehe offene Frage in `docs/anforderungen.md`).

## 4. Abgleich mit der Challenge

| Forderung der Challenge | Abgedeckt durch | Status |
|---|---|---|
| IES-Methode, Prozesse | Profil v2 Abschn. 2 (IEC-62559-2-Stil), P1–P10 | erfüllt; Sequenzdiagramme offen (im Profil so vermerkt) |
| Schnittstellen | Profil v2 Abschn. 4 (Wechselrichter), 6 (LoRaWAN), OpenADR nach TOR | erfüllt |
| „Grob, konkret, wiederverwendbar, keine technischen Details“ | Profil + Grenzen; teils sehr detailliert (Byte-Layout, Time-on-Air) | erfüllt; im Pitch betonen, dass Details nur Machbarkeitsbelege sind |
| Speicher von Haushalt **bis Gewerbe** | ein Satz in `index.html`; keine eigene Klasse | **teilweise** – siehe `docs/grossspeicher-integration.md` |
| Betrieb bestimmt der Anlagenbetreiber, VNB nur in Ausnahmen, zeitlich begrenzt | Prioritätskette, harte Grenzen, Schadlosstellung | erfüllt |
| Viele Speicher in einem Segment | Segment-Broadcast, P9, Streuung von Start/Ende | erfüllt |
| Abregelung vermeiden | Simulation: Speicher vs. Trafoausbau vs. Abregelung | erfüllt (Modellwerte) |
| Mit anderen Expert:innen erarbeitet | Recherche 01–09, Gutachten | im Pitch erwähnen |

## Quellen

- Aufgabentext und Template: `docs/challenge/`.
- Profil v2: `docs/context/profil-v2.md`; Präsentation und Details: `docs/context/site/`.
- Zugangsprüfung 25.10.2026, 09:30: `curl https://teb-hackathon.bbger.at/` → 302 auf `/oauth2/start?rd=/`; `curl https://github.com/dbuchber/teb-grid-serving-storage` → 404 (ohne Anmeldung).
- Repo-Stand: `git status` (unversionierte Dateien), `pyproject.toml`, `deploy/Dockerfile`, `apps/insight-harbor/package.json`.
