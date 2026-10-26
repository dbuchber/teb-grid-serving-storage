# TEB AI Hackathon – submission form (filled in)

Stand 25.10.2026, 10:25. Felder in der Reihenfolge des Formulars, Texte zum Kopieren.
`[TODO …]` = nur das Team kann es eintragen.

## 1. Project basics

**Project title**
Grid-Serving Storage Steyr

**One-line pitch**
An interoperability profile that lets a grid operator briefly borrow home batteries with signed, limited and verifiable calls to relieve overloaded transformers, tested on a year-long simulation of all 257 transformers around Steyr, which also shows where batteries do not help.

## 2. Team

**Team name**
[TODO]

**Team members**
[TODO Name — organisation — @githubhandle — role] (primary contact first; GitHub: @dbuchber)

**Primary contact email**
[TODO]

## 3. Challenge track

**Track**
Grid-Serving Storage (challenge partner Smart Grids Austria)

**Challenge prompt**
Rough interoperability profile (IES method) for using customer storage against congestion in a grid segment

## 4. What you built

**Problem you solved**
Local distribution grids are running out of transformer capacity: in summer rooftop PV pushes transformers to their feed-in limit, and in winter heat pumps and electric cars push them above their rating (in our model of the Steyr region up to 193 of 257 transformers in a 2040 stress case). Thousands of home batteries already sit in the same grid, but they run only for self-consumption, are often full before the midday peak, and the grid operator has no safe, standard way to ask them for help. We focused on how a DSO can borrow those batteries for short, limited periods without the owner losing money and without creating a new risk for the grid.

**Solution overview**
We wrote a rough interoperability profile following the IES method: actors and what each may sign (grid operator, household and its box, supplier, feed-in buyer, price authority, trusted authority, subsidy body), processes P1–P10 (commissioning, daily signed prices, regular test calls, congestion call per transformer segment, verification and compensation, fallback, balance-group correction, conflicts with other flexibility markets, segment assignment, key revocation) and the interfaces between them. A certified box next to the meter is the single entry point: the DSO sends one signed call per segment; the box checks signature, role, expiry, sequence number and hard limits, spreads start and end over minutes and controls the inverter locally via an open standard (SunSpec, EEBUS or IEEE 2030.5). We describe two hardware variants for this trusted control function. Variant A is a separate, modular box on the DIN rail next to the meter: a core module with a security chip that alone may issue battery commands, four identical slots for LoRaWAN (default), LTE or Ethernet, a meter interface and a wired link to the inverter; every module runs signed firmware on an authenticated CAN FD bus, and anyone may build modules, but only a trusted authority may approve them. It retrofits existing batteries of any brand. Variant B puts the same certified core function (keys, signature checks, hard limits, fallback) directly into the battery inverter, so new installations need no extra device. Smart-meter data verify what happened and a repeatable comparison run ensures the household is never worse off. To find out where this actually helps, we built gridsim, an hourly full-year simulation of all 257 transformers in Steyr and Steyr-Land from open data, with three real weather years and 20 random placements of heat pumps and cars; it compares battery strategies, smart charging, V2G and transformer upgrades. Result: batteries help against short summer peaks and as a bridge until a transformer is replaced, not against multi-day winter bottlenecks; smart charging is the cheaper first step. The demo is an animated presentation, a full write-up with all assumptions and sources, an interactive map and dashboard, and a battery cost calculator.

**How AI is used**
We trained an image-recognition (segmentation) model on the BOKU PV outlines (aerial images 2021–23) and ran it on 2025 aerial images to find solar systems built since then: on 310 held-out validation tiles it finds 55 % of real systems (recall) with 69 % precision, up from 37 %/58 % before retraining. Its result is shown on the map and compared roof by roof with BOKU; the simulation itself uses the BOKU data, and the 796 extra roofs the model finds have not been checked by hand yet. There is deliberately no AI in the control path: calls, limits and compensation are deterministic, signed and auditable, and the grid operator decides every call. AI coding assistants (Claude Code; Lovable for the calculator) wrote most of the code and texts; the team reviewed the results.

**Security and resilience**
We designed against an attacker or a bug that makes thousands of batteries switch at once and turns a grid-support tool into a grid-attack tool: forged or replayed commands, a stolen DSO key, fake prices from the home network, radio or backend outages. Every role has its own certificate and may sign only its own documents; the box accepts only signed calls for its own segment with a valid expiry and sequence number, and rejects prices outside fixed bounds. Hard limits in the box that no signed message can change (at most 3 calls and 4 hours a day, random start delays, staggered return over about 15 minutes) cap what even a stolen key can do; keys can be revoked over the radio, and without valid prices or a sign of life the box falls back to plain self-consumption. Home Assistant has its own channel with no route to the core module, and no manufacturer cloud is in the command path. In the box (variant A) only the core module with its security chip can create battery commands; modules run signed firmware, authenticate on the internal bus as in cars, and unapproved modules are switched off. In the inverter (variant B) the same checks run in a certified, separated core. Threat model: docs/bedrohungsmodell.md; a formal IEC 62443 analysis is still open.

**Data and environments**
Open data only: Austrian address and building register (BEV), OpenStreetMap transformer stations and roads, BOKU PV map (Zenodo, CC BY 4.0) plus our own detection on 2025 aerial images, PVGIS solar profiles, GeoSphere temperatures for the weather years 2012, 2017 and 2023, Austrian standard load profiles, published substation connection capacities (ebUtilities). Synthetic: low-voltage cables (routed along streets), some transformer sites and ratings, which buildings get heat pumps, cars and batteries (20 random draws). Mocked: the box, battery devices and test-call reliability; there is no hardware. Steyr is only our test region. We confirm that nothing was tested against live infrastructure, real devices, the venue network or other teams' systems.

**Tech stack**
Simulation/backend: Python 3.12, NumPy, SciPy, Shapely, pyproj, FastAPI + Uvicorn, pytest (78 tests passing). Frontend: static HTML/CSS and vanilla JavaScript modules, MapLibre GL for the map. Battery calculator: TypeScript, React, TanStack Start, Tailwind CSS, Recharts, Vitest (generated with Lovable). AI: PV segmentation model (Ultralytics YOLO) on aerial images. Deployment: Docker Compose, nginx, Caddy, oauth2-proxy, Keycloak on a Hetzner server. Standards in the profile: OpenADR, LoRaWAN, SunSpec, EEBUS, IEEE 2030.5, IES / IEC 62559-2.

## 5. Links

**Code repository**
https://github.com/dbuchber/teb-grid-serving-storage

**Demo link**
https://teb-hackathon.bbger.at

**Documentation**
https://github.com/dbuchber/teb-grid-serving-storage#readme and https://teb-hackathon.bbger.at/details

**Pitch deck**
https://teb-hackathon.bbger.at (the presentation is the deck)

**Other links**
Interoperability profile v2: https://github.com/dbuchber/teb-grid-serving-storage/blob/main/docs/context/profil-v2.md
Threat model: https://github.com/dbuchber/teb-grid-serving-storage/blob/main/docs/bedrohungsmodell.md
Simulation validation: https://github.com/dbuchber/teb-grid-serving-storage/blob/main/docs/gridsim-abnahme.md
Hardware concept (modular box, German): https://github.com/dbuchber/teb-grid-serving-storage/blob/main/docs/hardware-konzept.md

## 6. Notes for the jury

[TODO Demo login: user … / password …] All grid figures are model results from open data, not measurements; low-voltage cables, some transformer sites and ratings and the placement of heat pumps, cars and batteries are synthetic, and the 2040 count is an upper bound (with transformers as large as the biggest in published field grids it is about 100). The profile is a draft for discussion with a DSO; limits, compensation rates and subsidy shares marked "proposal" are placeholders. The box, the radio channel and test-call reliability are mocked; there is no hardware yet. The hardware concept details variant A (modular box: modules, bus, MCU candidates, off-the-shelf prototype parts); variant B (integrated in the inverter) is described at concept level only. Business-scale storage is covered by the same call and limits but not yet simulated separately. The PV detection model and the open-data pipeline come from our existing infra-kg project (separate, private repository); the model was retrained and evaluated during the hackathon. Some documents in the repository are in German.

## 7. Follow-up

[TODO ankreuzen: TEB Klub / Kontakt durch Partner / Veröffentlichung]
