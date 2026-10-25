# Abgabeformular – Texte zum Kopieren (Stand 25.10.2026, 10:25)

Grundlage: `docs/abgabe-lueckenanalyse.md` (09:35), korrigiert auf den aktuellen Stand von Live-Seite, Profil v2 (Abschnitte 1a, 1b) und `docs/bedrohungsmodell.md`.
Felder mit **[Owner]** kann nur das Team ausfüllen.

## 1. Project basics

**Project title:** Grid-Serving Storage Steyr (oder: GridBox – Grid-Serving Storage)

**One-line pitch:**
An interoperability profile and a signed control box that let a grid operator briefly borrow home and business batteries to relieve overloaded transformers, tested on a year-long simulation of all 257 transformers in our test region Steyr – and the household never loses money.

## 2. Team **[Owner]**

Team name, members (Name – organisation – GitHub – role, primary contact first), primary contact email.

## 3. Challenge track

**Track:** Critical Infrastructure & Energy Security **[Owner: Auswahlfeld]**
**Challenge prompt:** Grid-Friendly / Grid-Serving Storage – interoperability profile (IES method) for using customer storage against grid congestion

## 4. What you built

**Problem you solved**

Distribution grids are running out of transformer capacity. In our year-long model of the Steyr region, up to 193 of 257 low-voltage transformers could be overloaded in a 2040 winter (stress case with 70 % heat pumps and small transformers; about 100 if the real transformers are as large as the biggest in published field grids), and with twice today's solar 32–34 hit their feed-in limit in summer. Thousands of batteries sit in the same grid, but they only optimise self-consumption, the grid operator has no safe, standard way to use them, and the owner has no reason to let it. We focused on how a DSO can borrow them for short, limited periods without harming the owner, the market or grid security – and on where this helps and where it does not.

**Solution overview**

We designed a rough interoperability profile following the IES method: actors (DSO, household, supplier and balance responsible party, aggregator, TSO, smart-meter backend, trust anchor, price authority), twelve processes (P1 commissioning, P2 daily prices, P3 test calls, P4 congestion call, P5 verification and compensation, P6 fallback, P7 balance-group correction, P8 conflicts with third-party marketing, P9 segment assignment, P10 key revocation, P11 day-ahead flexibility schedule and P12 flexible grid access for large storage), a table of every information exchange (sender, receiver, information object, standard) and a sequence for one call. A certified box in the customer installation is the single entry point: the DSO sends one signed call per transformer segment via OpenADR (required for solar systems by the Austrian connection rules; for batteries our proposal) or a LoRaWAN broadcast; the box checks signature, role, segment, sequence and fixed limits, spreads start and end over several minutes and drives the inverter locally via SunSpec, EEBUS or IEEE 2030.5. Business batteries use the same call; large storage on the medium-voltage grid gets it via telecontrol with acknowledgement and relieves the substation instead of the street transformer. Verification uses smart-meter data and an open reference calculation; the household is compensated so it is never worse off, and subsidies rise with the level of control. A simulation of all 257 transformers (every hour of three real weather years, 20 random placements of heat pumps and cars) shows the honest result: batteries help with short summer peaks and as a bridge until a transformer is replaced; in long winter cold spells they cannot recharge, and smart charging of cars is the stronger lever. The live demo has a presentation, a detailed write-up, an interactive map and dashboard, and a household cost calculator.

**How AI is used**

AI is used to build the data, not to control the grid. We retrained a YOLO segmentation model (base: agademer/yolo-remote-sensing-photovoltaic) on BOKU's PV outlines and ran it on 2025 aerial images to find solar systems built since 2023: it finds 55 % of real systems and 69 % of its finds are real (310 validation tiles; a lower bound, since the reference is from 2021–23). Its result is shown on the map only; the simulation uses the BOKU PV data. No AI decides in the call path: calls are deterministic, signed and checkable, and a grid operator releases them. AI coding assistants (Claude Code) were used for research, coding and review, and the calculator was generated with Lovable; the team made every design decision.

**Security and resilience**

The box verifies every command itself (signature, role, network-area binding, expiry, replay counter) and enforces hard firmware limits no message can lift: at most 3 calls and 4 h per day, 3 h per call, ramps of at most 10 %/min, randomised start and staggered return, backup reserve never touched; keys are revoked over the radio via epochs within hours, and radio jamming only triggers a safe fallback to self-consumption. We state the residual risk openly: a stolen grid-operator key could still drive all batteries of one segment against the bottleneck for up to 4 h per day, so we propose two-person release in the HSM, a local plausibility check of call direction against the box's own measurement, and anomaly detection via transformer and smart-meter data. This is a concept only: nothing is implemented or tested against live infrastructure, and a formal IEC 62443 / NIS2 analysis is still open (threat model: docs/bedrohungsmodell.md).

**Data and environments**

Open data only: Austrian address register (BEV), OpenStreetMap transformer sites and roads, BOKU PV map, BEV aerial images 2025, PVGIS solar profiles, GeoSphere INCA temperatures for the weather years 2012, 2017 and 2023, APCS standard load profiles, DORIS LoD1 buildings and TABULA for heat demand, published grid connection capacities. Synthetic: low-voltage cables, some transformer sites, transformer ratings, which households get heat pumps, cars and batteries (20 random seeds). Mocked: the box and radio channel (no hardware) and test-call reliability per manufacturer group. Steyr is only our test region. We confirm that nothing was tested against live infrastructure, the venue network, real devices or other teams' systems.

**Tech stack**

Simulation and API: Python 3.12+, NumPy, SciPy, Shapely, pyproj, FastAPI and Uvicorn (job queue, cache, server-sent events), pytest (78 tests). Frontend: static HTML/CSS and vanilla ES modules with MapLibre for presentation, write-up and region dashboard; household calculator in TypeScript, React, TanStack Start, Tailwind CSS, Recharts and Vitest (built with Lovable). AI: Ultralytics YOLO segmentation for PV detection (in the team's data pipeline, not in this repo). Deployment: Docker Compose behind Caddy and oauth2-proxy. Standards in the profile: OpenADR (IEC 62746-10-1), LoRaWAN (TS004, TS005), SunSpec Modbus, EEBUS LPC/LPP, IEEE 2030.5, IEC 60870-5-104, IEC 62559-2.

## 5. Links

| Feld | Eintrag |
|---|---|
| Code repository | https://github.com/dbuchber/teb-grid-serving-storage (öffentlich, Branch `main`) |
| Demo link | https://teb-hackathon.bbger.at (Präsentation), https://teb-hackathon.bbger.at/details (ausführlich) – **derzeit Login-Pflicht: öffentlich schalten oder Zugang in den Notes angeben [Owner]** |
| Documentation | https://github.com/dbuchber/teb-grid-serving-storage#readme |
| Pitch deck | https://teb-hackathon.bbger.at/ (die Präsentation ist das Deck) |
| Other links | Interoperability profile v2: …/blob/main/docs/context/profil-v2.md · Threat model: …/blob/main/docs/bedrohungsmodell.md · Business and large storage: …/blob/main/docs/grossspeicher-integration.md · Simulation validation: …/blob/main/docs/gridsim-abnahme.md |

## 6. Notes for the jury

All grid figures are model results from open data, not measurements; low-voltage cables, transformer ratings and the placement of heat pumps, cars and batteries are synthetic, and the 2040 numbers are a stress case and upper bound. The interoperability profile is a draft for discussion with a DSO, not a finished specification; values marked as proposals (limits, compensation, subsidy shares) are placeholders. The box, the radio channel and test-call reliability are mocked – there is no hardware. Business and large storage are in the profile (storage classes, P11, P12) but not yet in the simulation. The PV detection code lives in the team's data pipeline, not in this repository. Steyr is only our test region. [Demo login: … – falls nötig]

## 7. Follow-up **[Owner]**
