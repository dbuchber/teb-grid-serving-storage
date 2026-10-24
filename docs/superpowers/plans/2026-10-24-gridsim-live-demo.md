# gridsim Live-Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simulationsbibliothek `gridsim` (Steyr, 257 Stationen) mit Monte-Carlo-Läufen, Rechen-API und einem Dashboard-Modul, das Session 02 in teb-hackathon.bbger.at einbettet.

**Architecture:** Einmalige Vorbereitung je Wetterjahr nutzt die eingefrorenen Skripte (`gridsim/legacy/`) und schreibt Knoten-, Stations- und Profilmatrizen als `.npy`. Jeder Lauf (ein Seed) rechnet daraus vektorisiert Wärmepumpe, E-Auto (als Ladeereignisse), Steuerlogik und Speicher und verdichtet auf Stationsebene; Seeds laufen parallel im Prozesspool. Eine FastAPI-App startet Läufe, streamt je fertigem Seed per SSE und liefert den Tages-Drilldown; das ES-Modul zeichnet Kacheln, Band, Vergleich, Karte (MapLibre der Seite) und Tageskurve als SVG.

**Tech Stack:** Python ≥ 3.12, NumPy, SciPy, Shapely, pyproj (nur Vorbereitung), FastAPI + Uvicorn, pytest, uv; Vanilla-JS-ES-Module, MapLibre 4.7.1 (von der Seite), `node --test`; Docker auf hetzner.

**Spec:** `docs/superpowers/specs/2026-10-24-gridsim-live-demo-design.md` (freigegeben 24.10.2026)

## Global Constraints

- Deadline So 25.10.2026, 11:30. Bei Zeitnot: Breite kürzen (zuerst Wetter 2012 + 2023, Szenarien 2030 + 2040, PV × 1), keine Funktion streichen; Live-Rechnen vor Kosteneditor.
- Rechnen (Vorbereitung, Läufe, Abnahme) auf `hetzner-wikidata`, nicht am Mac. Unit-Tests mit synthetischen Mini-Daten dürfen lokal laufen.
- Eingaben: `/data/infra-kg-austria/work/steyr-pv-2026-10-24/input/` (read-only); nie ins Repo oder Image kopieren.
- Bestehende `steyr_*.py` im Repo infra-kg-austria und auf hetzner nicht ändern.
- Git: Arbeitsbranch `feat/gridsim` in teb-grid-serving-storage (nicht auf `main`); nicht pushen ohne Auftrag des Owners. Commit-Zeilen enden mit `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Modellannahmen = Stand der eingefrorenen Skripte (Spec § 4); Referenzkonfiguration der Abnahme: `--heat lod1 --district-heating`, `large_share = 0,0`, Diversity an, INCA je Station.
- Szenarien: heute 0,15/0,08, 2030 0,35/0,25, 2040 0,70/0,60 (Anteil WP/E-Auto).
- Seeds: 20 je Einstellung; Seed i = 20261024 + 1000·i; Anzeige Median und 10–90-%-Band.
- Zielwerte: Jahreslauf alle Stationen, 1 Seed, 1 Steuerlogik ≤ 10 s; 20 Seeds ≤ 30 s bis zum vollen Band; Drilldown ≤ 1 s; RAM je Worker ≤ 2 GB.
- Ladesteuerung: `uncontrolled`, `winap`, `t3d`, `controlled`, `v2g`; Speicherstrategie: `base`, `forecast`, `room`. Gesteuertes Laden/V2G drosseln nur Wallboxen gegen 100 % Trafo-Bemessung; Wärmepumpen bleiben ungesteuert. Netzseitiges Laden der Heimspeicher im Rabattfenster: Anteil 0 (nicht Teil dieses Plans).
- WiNAP: 1.10.–31.3., Fenster 23–5 Uhr. T3d: Gruppen 22/0/2 Uhr, nur an Tagen mit Engpassprognose (perfekte Prognose), sonst WiNAP.
- V2G: 11 kW, 15 kWh je Abend, 70 % verfügbar; gesteuertes Laden Frist 7 Uhr.
- Kosten: Speicher 600 €/kWh, Verschleiß 5 ct/kWh (ems-konzept § 7.3); Trafo-Stufe und Leitung ohne Quelle → Platzhalter, sichtbar gekennzeichnet; Leitungsausbau nie live gerechnet.
- Web: Dateien unter `deploy/teb-hackathon/site/js/gridsim/` im Repo infra-kg-austria (Owner der Seite: Session 02; dort nur diese Dateien anlegen). CSP: `script-src 'self'`, `connect-src 'self' https://mapsneu.wien.gv.at`, `worker-src 'self'`; kein CDN, kein Inline-Skript, kein WebSocket. Farben nur über `--surface`, `--line`, `--ink2`, `--accent`, `--warn`, `--ok`. Oberfläche Englisch. Jeder Wert als „model value“ gekennzeichnet.
- Einbettung: `export function mount(el, { apiBase: "/api/", stations, onSelectStation })`; `stations` = FeatureCollection aus `site/data/stations.geojson`, IDs `way/…`, `node/…`, `demo:steyr:station-NNN`.
- API unter `teb-hackathon.bbger.at/api/` (same origin, Login oauth2-proxy, Realm `teb-hackathon`, Gruppe `teb-access`); Caddy/nginx-Eintrag macht Session 18.

## Review Focus

1. Zwei Personen starten gleichzeitig verschiedene Läufe (oder dieselbe Einstellung doppelt) → beide bekommen Ergebnisse, gleiche Einstellung rechnet nur einmal, höchstens 2 Läufe gleichzeitig, kein Überlauf auf hetzner. → Task 9
2. SSE-Verbindung bricht ab oder Seite wird neu geladen mitten im Lauf → Modul holt per `GET /api/runs/{id}` alle bisherigen Seeds und zeigt weiter. → Tasks 9, 11
3. Station in `stations.geojson` ohne Modellergebnis (oder umgekehrt) → grau „no model data“, kein Fehler; Drilldown-Anfrage dafür → 404 mit Text. → Tasks 7, 11
4. Station ohne Wärmepumpe/E-Auto oder ohne Engpass → Kennzahlen 0, Drilldown zeichnet, keine Division durch null. → Tasks 5, 7
5. Ungültige Parameter (Wetterjahr 2020, PV-Faktor 3, unbekannte Steuerlogik) → HTTP 400 mit Meldung, nie 500. → Task 9

---

## File Structure (Repo teb-grid-serving-storage, Branch `feat/gridsim`)

| Datei | Verantwortung |
|---|---|
| `pyproject.toml` | Paket `gridsim` + `api`, Abhängigkeiten, pytest-Konfiguration |
| `gridsim/legacy/` | eingefrorene Kopien der hetzner-Skripte + `SHA256SUMS` + Lader |
| `gridsim/prepare.py` | Vorbereitung je Wetterjahr → `.npy`/`.json` |
| `gridsim/data.py` | `Prepared` laden (memory-mapped) |
| `gridsim/profiles.py` | Zuteilung WP/E-Auto, Wärmepumpe, E-Auto-Ereignisse |
| `gridsim/control.py` | Ladesteuerung (Ereignisse → Stationslast), gesteuertes Laden, V2G |
| `gridsim/metrics.py` | § 7.2-Kennzahlen, Region, Kosten |
| `gridsim/run.py` | `RunParams`, ein Seed, viele Seeds, Cache, Manifest |
| `gridsim/drilldown.py` | Tageskurve 15 min je Station |
| `gridsim/cli.py` | `python -m gridsim prepare|batch|precompute|validate` |
| `api/app.py`, `api/jobs.py` | FastAPI, Auftragsverwaltung, SSE, Replay |
| `web/gridsim/*.js`, `web/gridsim/dashboard.css` | Dashboard-Modul (Quelle; Kopie in die Seite von 02) |
| `deploy/Dockerfile`, `deploy/compose.yaml` | Container |
| `docs/gridsim-abnahme.md` | Abgleich mit Session 18 |
| `tests/` | pytest; `web/gridsim/*.test.mjs` für `node --test` |

---

### Task 1: Gerüst und eingefrorene Skripte

**Files:**
- Create: `pyproject.toml`, `gridsim/__init__.py`, `gridsim/legacy/__init__.py`, `gridsim/legacy/SHA256SUMS`, `gridsim/legacy/steyr_*.py` (Kopien), `tests/test_legacy.py`
- Modify: `.gitignore` (+ `.superpowers/`, `data/`, `cache/`)

**Interfaces:**
- Produces: `gridsim.legacy.load(name: str) -> module` (fügt `gridsim/legacy` zu `sys.path` hinzu, weil die Skripte sich per `import steyr_pv_per_station as base` gegenseitig laden); Konstante `gridsim.legacy.FROZEN_AT = "2026-10-24"`.

- [ ] **Step 1: Branch anlegen und Skripte einfrieren**

```bash
cd /Users/dbuchber/Desktop/tmp.nosync/vscode/teb-grid-serving-storage
git switch -c feat/gridsim
mkdir -p gridsim/legacy
scp 'hetzner-wikidata:/data/infra-kg-austria/work/steyr-pv-2026-10-24/steyr_{sim_variant_a,storage_need,wp_ev,v2g_demo,heat_demand,district_heating,pv_per_station}.py' gridsim/legacy/
(cd gridsim/legacy && shasum -a 256 steyr_*.py > SHA256SUMS)
```

- [ ] **Step 2: Failing test** `tests/test_legacy.py`

```python
def test_checksums_match():   # jede Datei in SHA256SUMS hat genau diese Prüfsumme
def test_load_resolves_cross_imports():
    m = legacy.load("steyr_storage_need")
    assert hasattr(m, "segment_row") and m.sim.TRAFO_SIZES == (125, 160, 250, 400, 630, 800, 1000)
```

- [ ] **Step 3:** `pytest tests/test_legacy.py -v` → FAIL (Modul fehlt)
- [ ] **Step 4:** `pyproject.toml` (Abhängigkeiten numpy, scipy, shapely, pyproj, fastapi, uvicorn, sse-starlette nicht nötig – SSE über `StreamingResponse`; dev: pytest, httpx) und `gridsim/legacy/__init__.py` mit `load()` schreiben; `.gitignore` ergänzen.
- [ ] **Step 5:** `uv run pytest tests/test_legacy.py -v` → PASS
- [ ] **Step 6: Commit** `git add -A pyproject.toml gridsim tests .gitignore && git commit -m "chore(gridsim): Gerüst und eingefrorene Steyr-Skripte"`

---

### Task 2: Vorbereitung je Wetterjahr

**Files:**
- Create: `gridsim/prepare.py`, `gridsim/data.py`, `tests/test_data.py`, `tests/test_prepare_hetzner.py`

**Interfaces:**
- Consumes: `legacy.load(...)`: `sim.build_members(inp)` (nach `sim.STORAGE_SHARE_LARGE = 0.0`), `sim.read_pvgis`, `sim.PVGIS_BINS`, `sim.trafo_kva`, `sim.KWH_PER_HH`, `need.read_inca(inp, year, stations, nodes)`, `dh.mark(nodes, dh.places(inp/'osm_places_steyr.json'))`, `hd.node_heat(nodes, inp/'lod1_steyr.csv', hd.heating_degree_days(temp.mean(axis=1)), wpev.SEED)`.
- Produces: `prepare(input_dir: Path, year: int, out_dir: Path) -> Path` schreibt nach `out_dir/<year>/`:
  - `nodes_station.npy` int32 (N), `nodes_hh.npy` int16, `nodes_kwp_bins.npy` float32 (N×4, Reihenfolge `sim.PVGIS_BINS`), `nodes_kwh.npy` float32, `nodes_fw.npy` bool, `nodes_cell.npy` int16, `nodes_heat_kwh.npy` float32 (NaN = Pauschal), `nodes_dhw.npy` float32 (NaN = Default)
  - `pv_bins.npy` float32 (8760×4, kW/kWp), `h0.npy` float32 (8760, Anteil/h), `h0_q.npy` float32 (35040, Anteil/Viertelstunde, gleiche Wochentagsverschiebung), `temp_cells.npy` float32 (8760×C)
  - `stations.json`: Liste `{id: osm_id, idx, kva, lon, lat, uw, synthetic, n_hh, n_buildings, kwp}` (lon/lat aus Stations-Dict), `manifest.json` (Jahr, SHA256 jeder Eingabedatei, `legacy.FROZEN_AT`, Erstellzeit)
- Produces: `gridsim.data.Prepared` (frozen dataclass mit obigen Arrays als `np.load(..., mmap_mode="r")`, `stations: list[dict]`, `station_ids: list[str]`, `first_weekday: int`) und `load_prepared(root: Path, year: int) -> Prepared`.

- [ ] **Step 1: Failing test** `tests/test_data.py` mit einem synthetischen Mini-Verzeichnis (3 Stationen, 10 Knoten, von einem Fixture-Helfer `write_fake_prepared(tmp_path, year=2023)` erzeugt, der auch in späteren Tasks genutzt wird – Datei `tests/fakes.py`):

```python
def test_load_prepared_roundtrip(tmp_path):
    p = load_prepared(write_fake_prepared(tmp_path), 2023)
    assert p.pv_bins.shape == (8760, 4) and p.nodes_station.shape == (10,)
    assert p.station_ids == ["way/1", "node/2", "demo:steyr:station-003"]
    assert p.first_weekday == 6   # 1.1.2023 Sonntag
```

- [ ] **Step 2:** `uv run pytest tests/test_data.py -v` → FAIL
- [ ] **Step 3:** `gridsim/data.py` und `tests/fakes.py` implementieren; `gridsim/prepare.py` implementieren (H0 viertelstündlich: APCS-Typ-1-Werte normiert, um denselben Wochentags-Shift wie `sim.read_h0` × 4 gerollt).
- [ ] **Step 4:** `uv run pytest tests/test_data.py -v` → PASS
- [ ] **Step 5: Integrationstest auf hetzner** `tests/test_prepare_hetzner.py`, übersprungen ohne Umgebungsvariable `GRIDSIM_INPUT`:

```python
def test_prepare_real(tmp_path):
    p = load_prepared(prepare(Path(os.environ["GRIDSIM_INPUT"]), 2012, tmp_path), 2012)
    assert len(p.stations) == 257
    assert p.nodes_fw.sum() == 1043          # Fernwärme-MFH laut Session 18
    assert abs(p.pv_bins.sum(axis=0).mean() - 1000) < 300   # kWh/kWp plausibel
```

Run (hetzner, Repo per `rsync -a --exclude .git` nach `/data/infra-kg-austria/work/gridsim/`):
`cd /data/infra-kg-austria/work/gridsim && GRIDSIM_INPUT=/data/infra-kg-austria/work/steyr-pv-2026-10-24/input uv run pytest tests/test_prepare_hetzner.py -v` → PASS
- [ ] **Step 6:** Vorbereitung für 2012, 2017, 2023 nach `/data/infra-kg-austria/work/gridsim/prepared/` laufen lassen (`uv run python -m gridsim prepare` folgt in Task 6; bis dahin `python -c "from gridsim.prepare import prepare; ..."`).
- [ ] **Step 7: Commit** `feat(gridsim): Vorbereitung je Wetterjahr als Arrays`

---

### Task 3: Profile – Zuteilung, Wärmepumpe, E-Auto-Ereignisse

**Files:**
- Create: `gridsim/profiles.py`, `tests/test_profiles.py`

**Interfaces:**
- Consumes: `Prepared` (Task 2); Formeln aus `legacy.load("steyr_wp_ev")` (`heat_pump_kw_cells`, `spread`, Konstanten `HEAT_KWH_EFH`, `HEAT_KWH_MFH_HH`, `KM_PER_YEAR`, `KWH_PER_KM`, `COLD_PER_K`, `EV_ETA`, `EV_KW_FAST`, `EV_KW_SLOW`, `EV_FAST_SHARE`, `EV_CHARGE_KWH`, `ARRIVAL_WEEKDAY`, `ARRIVAL_WEEKEND`, `SCENARIOS`).
- Produces:
  - `assign(p: Prepared, scenario: str, rng) -> tuple[np.ndarray, np.ndarray]` (heat_kwh float (N), cars int (N)); gleiche Logik wie legacy `assign` inkl. Fernwärme-Hochskalierung, LoD1-Wärme ersetzt Pauschale wo nicht NaN; vektorisiert.
  - `heat_pump(p, heat_kwh, seed) -> tuple[np.ndarray, np.ndarray]`: (Stationssumme float32 8760×S, Matrix nur der Speicherknoten `nodes_kwh > 0` float32 8760×K); legacy `heat_pump_kw_cells` mit `spread(N, seed)` und `nodes_dhw`, zellenweise berechnet und sofort auf Stationen verdichtet, damit keine volle 8760×N-Matrix im Speicher liegt (RAM ≤ 2 GB je Worker).
  - `@dataclass EvEvents: node: int32[M], station: int32[M], arrive_h: int32[M] (absolute Stunde), kwh_grid: float32[M], kw: float32[M], deadline_h: int32[M] (nächster Tag 7 Uhr)`.
  - `ev_events(p, cars, rng) -> EvEvents`: vektorisiert über alle Autos, Schleife nur über die 365 Tage (Bedarf je Auto akkumulieren, laden ab `EV_CHARGE_KWH`, Ankunft `clip(normal(mu, sd), 12, 23)`, Leistung je Auto einmal ziehen, Tagesbedarf nach Gebietsmitteltemperatur `temp_cells.mean(axis=1)`).
  - `station_sum(values_by_node: np.ndarray, p) -> np.ndarray` (8760×S) über `nodes_station`.

- [ ] **Step 1: Failing tests** (mit `write_fake_prepared`):

```python
def test_assign_shares_and_fw():          # 2040: WP-Anteil der Wohnknoten ± 0,05 von 0,70; fw-Knoten nie WP
def test_ev_energy_conserved():           # Summe kwh_grid ≈ Summe Tagesbedarf/EV_ETA ab erster Ladung (rel 1e-3)
def test_ev_arrivals_evening():           # 90 % der Ankünfte werktags zwischen 15 und 21 Uhr
def test_ev_events_match_legacy_stats():  # 500 Autos, 2 Jahre Seeds: Jahresenergie je Auto und Stunde der Spitze wie legacy ev_kw (± 5 %, gleiche Stunde ± 1)
def test_ev_events_speed():               # 20 000 Autos < 2 s
def test_heat_pump_matches_legacy():      # Stationssumme == legacy heat_pump_kw_cells summiert (rtol 1e-4); Speicherknoten-Matrix == deren Spalten
def test_station_without_homes_has_zero_load():  # Review Focus 4
```

- [ ] **Step 2:** `uv run pytest tests/test_profiles.py -v` → FAIL
- [ ] **Step 3:** `gridsim/profiles.py` implementieren.
- [ ] **Step 4:** `uv run pytest tests/test_profiles.py -v` → PASS
- [ ] **Step 5: Commit** `feat(gridsim): vektorisierte Wärmepumpen- und E-Auto-Profile`

---

### Task 4: Ladesteuerung, gesteuertes Laden, V2G, Speicher

**Files:**
- Create: `gridsim/control.py`, `tests/test_control.py`

**Interfaces:**
- Consumes: `EvEvents`, `Prepared`; `legacy sim.simulate(pv_kw, load_kw, cap, strategy)` für Speicherknoten.
- Produces:
  - `render(ev: EvEvents, start_h: np.ndarray, n_stations: int, step_h: float = 1.0, hours: int = 8760) -> np.ndarray` float32 (hours/step × S): Ladeleistung ab `start_h` mit `kw`, bis `kwh_grid` erreicht (letzter Schritt anteilig); `step_h=0.25` für den Drilldown.
  - `start_uncontrolled(ev) -> arrive_h`
  - `start_winap(ev, first_weekday, year) -> np.ndarray`: Winterereignis (Tag in 1.10.–31.3.) startet um 23 Uhr desselben Tages, wenn `kwh_grid / kw <= 8` (bis 7 Uhr fertig), sonst bei Ankunft; Ankunft nach 23 Uhr bleibt.
  - `start_t3d(ev, signal: np.ndarray bool (S×365), group: np.ndarray int (S), year) -> np.ndarray`: an Signal-Tagen startet das Ereignis zur Gruppenzeit (0 → 22 Uhr, 1 → 0 Uhr, 2 → 2 Uhr), sonst wie WiNAP. `group = int(sha1(station_id)) % 3`.
  - `engpass_signal(flow_uncontrolled: (8760×S), kva: (S,)) -> bool (S×365)`: Tag d ist Signal, wenn der Fluss zwischen d 16 Uhr und d+1 8 Uhr über `kva` liegt.
  - `controlled(f0: (8760×S), ev: (8760×S), kva: (S,)) -> tuple[ev_ctrl (8760×S), unmet (S×365)]`: wie legacy `steyr_v2g_demo.controlled`, aber für alle Stationen gleichzeitig (Schleife über Stunden, Vektor über Stationen).
  - `v2g(residual: (8760×S), cars_per_station: (S,)) -> np.ndarray (8760×S)`: Rückspeisung = min(Rest, 11 kW·0,7·Autos), Energie je Abend (12–12 Uhr) ≤ 15 kWh·0,7·Autos.
  - `storage_flow(p: Prepared, pv_scale: float, strategy: str, wp_storage_nodes: np.ndarray) -> np.ndarray` (8760×S): Netto-Stationsfluss aus PV, H0 und Wärmepumpe, ohne E-Auto. Nur Knoten mit `nodes_kwh > 0` laufen per `sim.simulate` (Last = H0 + WP dieser Knoten, `wp_storage_nodes` = 8760 × Anzahl Speicherknoten); alle übrigen Knoten als Bilanz PV − H0 − WP direkt auf Stationsebene. Speicher entladen nicht ins E-Auto (wie `steyr_v2g_demo`); in der Abnahme (Task 8) als möglicher Grund für Abweichungen zu `steyr_storage_need` nennen, das E-Autos in die Speicherlast nimmt.

- [ ] **Step 1: Failing tests:**

```python
def test_render_energy_and_power():       # Summe = kwh_grid, max ≤ kw, step 0,25 gleiche Energie
def test_winap_starts_at_23_in_winter():  # Januar-Ereignis mit 10 kWh/11 kW startet 23 Uhr; Juli-Ereignis bleibt
def test_winap_creates_synchronous_peak():  # 200 Autos: Spitze WiNAP > Spitze ungesteuert
def test_t3d_staggers_by_group():         # 3 Stationen in 3 Gruppen: Starts 22/0/2 Uhr an Signal-Tagen
def test_t3d_peak_below_winap():          # gleiche Ereignisse: Summen-Spitze T3d < WiNAP
def test_controlled_never_exceeds_kva():  # max(f0 + ev_ctrl) ≤ kva + 1e-6, wenn f0 ≤ kva
def test_controlled_matches_legacy_single_station():  # == legacy controlled für 1 Station
def test_v2g_caps():                      # Rückspeisung ≤ Rest, ≤ 7,7 kW·Autos, Abendenergie ≤ 10,5 kWh·Autos
def test_storage_flow_matches_legacy_base():  # Fake-Daten: == Summe legacy simulate je Station (rtol 1e-5)
```

- [ ] **Step 2:** `uv run pytest tests/test_control.py -v` → FAIL
- [ ] **Step 3:** `gridsim/control.py` implementieren.
- [ ] **Step 4:** `uv run pytest tests/test_control.py -v` → PASS
- [ ] **Step 5: Commit** `feat(gridsim): Ladesteuerung WiNAP/T3d, gesteuertes Laden, V2G, Speicher`

---

### Task 5: Kennzahlen und Kosten

**Files:**
- Create: `gridsim/metrics.py`, `tests/test_metrics.py`

**Interfaces:**
- Consumes: legacy `need.events`, `need.segment_row` (als Referenz im Test).
- Produces:
  - `station_rows(flow: (8760×S), kva: (S,), cap_kwh: (S,), direction: str) -> list[dict | None]` – gleiche Felder wie legacy `segment_row` plus `n_speicher`.
  - `region_kpis(rows_load, rows_feed, unmet: (S×365) | None, n_stations: int) -> dict` mit Schlüsseln `stations_load_congestion`, `stations_feed_congestion`, `congestion_h_median`, `e_net_mwh`, `storage_units`, `trafo_plus1`, `trafo_plus2`, `trafo_over_1000`, `ev_unmet_mwh`.
  - `COST_DEFAULTS = {"storage_eur_per_kwh": 600, "wear_eur_per_kwh": 0.05, "trafo_step_eur": None, "line_eur_per_m": None}` (None = Platzhalter ohne Quelle).
  - `costs(kpis: dict, params: dict) -> dict` mit `storage_eur`, `trafo_eur` (None, wenn Platzhalter), `placeholders: list[str]`.

- [ ] **Step 1: Failing tests:**

```python
def test_station_rows_equal_legacy():     # Zufallsfluss, 5 Stationen: Felder identisch zu legacy segment_row
def test_no_congestion_gives_none_and_zero_kpis():  # Review Focus 4: Fluss < kva überall → rows None, KPIs 0, kein Fehler
def test_costs_mark_placeholders():       # trafo_step_eur None → trafo_eur None und "trafo_step_eur" in placeholders
```

- [ ] **Step 2:** `uv run pytest tests/test_metrics.py -v` → FAIL
- [ ] **Step 3:** implementieren (Logik von `events`/`segment_row` übernehmen, nicht importieren).
- [ ] **Step 4:** `uv run pytest tests/test_metrics.py -v` → PASS
- [ ] **Step 5: Commit** `feat(gridsim): Kennzahlen je Station und Region, Kosten`

---

### Task 6: Läufe, Seeds, Cache, CLI

**Files:**
- Create: `gridsim/run.py`, `gridsim/cli.py`, `gridsim/__main__.py`, `tests/test_run.py`

**Interfaces:**
- Consumes: Tasks 2–5.
- Produces:
  - `@dataclass(frozen=True) RunParams: weather_year: int (2012|2017|2023), scenario: str (heute|2030|2040), pv_factor: float (1.0|1.5|2.0), charging: str, storage: str, n_seeds: int = 20`; `RunParams.validate() -> None` (ValueError mit Text bei unbekanntem Wert); `RunParams.key() -> str` (sha1 der sortierten JSON-Felder, 12 Zeichen).
  - `seed_of(i: int) -> int` = 20261024 + 1000·i.
  - `@dataclass SeedResult: index: int, seed: int, region: dict, station_load_kw_max: list[float] (S), station_congestion_h: list[int] (S), worst_day: list[int] (S), runtime_s: float`.
  - `run_seed(p: Prepared, params: RunParams, i: int) -> SeedResult`: Ablauf: `assign` → `heat_pump` → `ev_events` → `storage_flow` → Startzeiten je `charging` (bei `t3d` vorher `engpass_signal` aus dem ungesteuerten Fluss) → `render` → bei `controlled`/`v2g` `controlled` (+ `v2g`) → `station_rows` (Bezug und Einspeisung) → `region_kpis`.
  - `run_many(root: Path, params, workers: int = 20) -> Iterator[SeedResult]`: `ProcessPoolExecutor`, Worker laden `Prepared` einmal im Initializer, liefert in Fertigstellungsreihenfolge.
  - Cache: `cache_dir/<key>/seed_<i>.json` + `manifest.json` (Parameter, Code-Version `git rev-parse --short HEAD` oder „unknown“, `legacy` SHA256SUMS-Hash, Manifest-Hash der Vorbereitung, Seeds, Laufzeit). `cached_seeds(cache_dir, params) -> list[SeedResult]`.
  - CLI: `python -m gridsim prepare --input IN --years 2012 2017 2023 --out PREP`; `batch --prepared PREP --cache CACHE --years … --scenarios … --charging … --storage base --pv 1.0` (schreibt je Einstellung `region.csv` mit Median/P10/P90); `precompute` = `batch` für das Pitch-Minimum (Wetter 2012, 2023 × Szenario 2030, 2040 × alle 5 Ladesteuerungen × `base` × PV 1,0); `validate` (Task 8).

- [ ] **Step 1: Failing tests:**

```python
def test_params_validate_rejects_unknown():   # Review Focus 5: weather_year 2020, pv 3.0, charging "foo" → ValueError mit Feldname
def test_key_stable_and_distinct():
def test_run_seed_fake_deterministic():       # gleiche Params + i → gleiche region; anderes i → andere
def test_run_many_yields_all_seeds(tmp_path): # n_seeds=3, workers=2 → Indizes {0,1,2}, Cache-Dateien vorhanden
```

- [ ] **Step 2:** `uv run pytest tests/test_run.py -v` → FAIL
- [ ] **Step 3:** implementieren.
- [ ] **Step 4:** `uv run pytest tests/test_run.py -v` → PASS
- [ ] **Step 5: Laufzeit auf hetzner** messen:
`cd /data/infra-kg-austria/work/gridsim && /usr/bin/time -v uv run python -m gridsim batch --prepared prepared --cache cache --years 2012 --scenarios 2040 --charging uncontrolled --storage base --pv 1.0`
Expected: je Seed ≤ 10 s, 20 Seeds ≤ 30 s gesamt, Maximum resident je Worker ≤ 2 GB (sonst Profil mit `python -m cProfile` und vor Task 7 beheben).
- [ ] **Step 6: Commit** `feat(gridsim): Läufe mit Seeds, Prozesspool, Cache und CLI`

---

### Task 7: Drilldown 15 min

**Files:**
- Create: `gridsim/drilldown.py`, `tests/test_drilldown.py`

**Interfaces:**
- Consumes: `run_seed`-Bausteine (gleiche Zwischenschritte für eine Station), `render(..., step_h=0.25)`.
- Produces: `day_curve(p: Prepared, params: RunParams, station_id: str, seed_index: int = 0, day: int | None = None) -> dict` mit `station`, `date` (ISO), `kva`, `step_min: 15` und Listen à 96 Werte `household_kw`, `heat_pump_kw`, `ev_kw`, `pv_kw`, `storage_kw`, `v2g_kw`, `trafo_kw`; `day=None` → schlimmster Tag (höchste Tagesspitze im Stundenlauf). PV linear aus Stundenwerten interpoliert, WP stundenkonstant, H0 aus `h0_q`. Unbekannte `station_id` → `KeyError`.

- [ ] **Step 1: Failing tests:**

```python
def test_day_curve_shape_and_balance():  # 96 Werte je Liste; trafo = household + heat_pump + ev − pv − storage − v2g (atol 1e-3)
def test_day_curve_energy_matches_hourly():  # Tagesenergie ≈ Summe der Stundenwerte desselben Tages (rel 2 %)
def test_unknown_station_raises():       # Review Focus 3
def test_station_without_ev_wp():        # Review Focus 4: ev/heat_pump 0, kein Fehler
```

- [ ] **Step 2:** `uv run pytest tests/test_drilldown.py -v` → FAIL
- [ ] **Step 3:** implementieren.
- [ ] **Step 4:** `uv run pytest tests/test_drilldown.py -v` → PASS; auf hetzner eine echte Station messen: ≤ 1 s.
- [ ] **Step 5: Commit** `feat(gridsim): Tageskurve je Station in 15 Minuten`

---

### Task 8: Abnahme gegen Session 18

**Files:**
- Create: `gridsim/validate.py`, `docs/gridsim-abnahme.md`, `tests/test_validate.py`

**Interfaces:**
- Produces: `REFERENCE` (Dict aus Spec § 9: `(year, scenario) -> (stations_load_congestion, e_net_mwh)`, Einspeisung PV × 1/1,5/2 → (1–3, 19, 31–34)); `compare(results: dict, reference=REFERENCE, tol=0.30) -> list[dict]` mit `ok`, `ratio`, `trend_ok` (Reihenfolge heute < 2030 < 2040 und 2023 < 2017 < 2012 wie Referenz).

- [ ] **Step 1: Failing test** `test_compare_flags_outside_tolerance()` (Wert 1,5 × Referenz → `ok False`), `test_trend_check()`.
- [ ] **Step 2:** FAIL → implementieren → PASS (`uv run pytest tests/test_validate.py -v`).
- [ ] **Step 3: Auf hetzner** `uv run python -m gridsim validate --prepared prepared --cache cache` für alle 9 Kombinationen (Ladesteuerung `uncontrolled`, Speicher `base`, PV 1,0; Einspeisung zusätzlich PV 1,5 und 2,0 mit Szenario `heute`). Ergebnis-Tabelle (Median + Band, Referenz, Verhältnis) nach `docs/gridsim-abnahme.md`; jede Abweichung > 30 % oder umgekehrte Tendenz mit Grund (z. B. vektorisiertes E-Auto-Modell, Seeds) erklären.
- [ ] **Step 4:** Owner kurz informieren, falls Abweichungen nicht erklärbar sind (Abnahme = „plausibel“, Spec § 9).
- [ ] **Step 5: Commit** `test(gridsim): Abnahme gegen die Tabellen von Session 18`

---

### Task 9: API mit Aufträgen, SSE und Replay

**Files:**
- Create: `api/__init__.py`, `api/jobs.py`, `api/app.py`, `tests/test_api.py`

**Interfaces:**
- Consumes: `RunParams`, `run_many`, `cached_seeds`, `day_curve`, `load_prepared`, `COST_DEFAULTS`, `costs`.
- Produces (Pfade relativ zu `/api/`; Konfiguration per Umgebung `GRIDSIM_PREPARED`, `GRIDSIM_CACHE`, `GRIDSIM_MAX_JOBS=2`, `GRIDSIM_WORKERS=20`, `GRIDSIM_REPLAY_DELAY_S=0.4`):
  - `GET health` → `{"ok": true}`
  - `GET options` → erlaubte Werte je Feld, `cost_defaults`, `placeholders`
  - `GET stations` → `[{id, kva, n_hh, uw, synthetic}]`
  - `POST runs` Body `RunParams`-Felder → 400 `{"error": "..."}` bei ungültig; sonst `{"run_id": key, "status": "running"|"cached"}`. Gleiche Einstellung läuft nur einmal; mehr als `GRIDSIM_MAX_JOBS` gleichzeitig → Warteschlange (`status: "queued"`).
  - `GET runs/{run_id}` → `{status, params, seeds: [SeedResult…], n_seeds}` (Polling und Wiederanlauf)
  - `GET runs/{run_id}/events` → `text/event-stream`, Ereignis `seed` je SeedResult (bereits fertige zuerst), dann `done`; bei vollständig gecachter Einstellung **Replay** mit `GRIDSIM_REPLAY_DELAY_S` zwischen den Seeds, damit das Band auch im Fallback sichtbar wächst.
  - `GET stations/{station_id}/day?weather_year=&scenario=&pv_factor=&charging=&storage=&seed=0` → `day_curve`; unbekannt → 404 `{"error": "no model data for station …"}`.
  - `POST costs` Body `{run_id, params}` → `costs(...)` mit Median-KPIs.
  - `station_id` in Pfaden URL-kodiert (`way%2F123`).

- [ ] **Step 1: Failing tests** (FastAPI `TestClient`, `run_many` durch Fake ersetzt, `write_fake_prepared`):

```python
def test_invalid_params_400():                # Review Focus 5
def test_same_params_run_once():              # Review Focus 1: zwei POST gleicher Params → ein Lauf (Fake zählt Aufrufe)
def test_max_jobs_queue():                    # Review Focus 1: 3 verschiedene POST bei MAX_JOBS=2 → einer "queued", am Ende alle fertig
def test_resume_after_disconnect():           # Review Focus 2: SSE nach 1 Seed schließen, GET runs/{id} liefert alle bisherigen Seeds
def test_sse_replay_cached():                 # gecachter Lauf: n Ereignisse "seed", dann "done"
def test_day_unknown_station_404():           # Review Focus 3
```

- [ ] **Step 2:** `uv run pytest tests/test_api.py -v` → FAIL
- [ ] **Step 3:** implementieren (Aufträge in einem Thread je Lauf, der `run_many` konsumiert; Zustand im Speicher + Cache auf Platte; SSE via `StreamingResponse`).
- [ ] **Step 4:** `uv run pytest tests/test_api.py -v` → PASS
- [ ] **Step 5: Commit** `feat(api): Läufe, SSE, Replay, Drilldown und Kosten`

---

### Task 10: Container und Vorberechnung auf hetzner

**Files:**
- Create: `deploy/Dockerfile`, `deploy/compose.yaml`, `deploy/README.md`

**Interfaces:**
- Produces: Image `gridsim-api`, Start `uvicorn api.app:app --host 0.0.0.0 --port 8000 --root-path /api`; Compose: Port `127.0.0.1:17061:8000` (mit Session 18 bestätigen), Volumes `/data/infra-kg-austria/work/gridsim/prepared:/prepared:ro`, `/data/infra-kg-austria/work/gridsim/cache:/cache`, Benutzer ohne Root, `read_only: true`, `tmpfs: /tmp`, `cpus: 20`, `mem_limit: 40g`, `network_mode: bridge` (Docker-Adresspools auf hetzner erschöpft).

- [ ] **Step 1:** Dockerfile (python:3.12-slim, `uv pip install --system .`, kein Kopieren von Eingabedaten) und Compose schreiben.
- [ ] **Step 2:** Auf hetzner bauen und starten: `docker compose -f deploy/compose.yaml up -d --build`; prüfen: `curl -s 127.0.0.1:17061/health` → `{"ok":true}`.
- [ ] **Step 3:** Vorberechnung (Fallback) im Container: `docker compose exec gridsim python -m gridsim precompute --prepared /prepared --cache /cache`; prüfen: 20 Einstellungen × 20 Seeds im Cache.
- [ ] **Step 4:** Session 18 per SendMessage: Image/Compose-Pfad, Port, Pfad `/api/` → Container, gleiche Login-Kette wie die Seite; Antwort abwarten, dann `curl -s https://teb-hackathon.bbger.at/api/health` mit Login-Cookie → ok.
- [ ] **Step 5: Commit** `chore(deploy): Container für die gridsim-API`

---

### Task 11: Dashboard-Modul

**Files:**
- Create: `web/gridsim/dashboard.js` (mount), `web/gridsim/api.js` (Fetch, SSE mit Polling-Rückfall), `web/gridsim/band.js` (reine Funktionen: Median/P10/P90 über Seeds, Skalen, SVG-Pfade), `web/gridsim/charts.js` (Kacheln, Band, Vergleich, Tageskurve als SVG), `web/gridsim/map.js` (kleine MapLibre-Karte: Inline-Stilobjekt mit Rasterquelle aus `import { BASEMAP } from "../map.js"`, tileSize 256, maxzoom 19, Attribution „Basemap: basemap.at (CC BY 4.0)“; kein `setWorkerUrl`, das macht die Seite), `web/gridsim/dashboard.css`, `web/gridsim/band.test.mjs`, `web/gridsim/api.test.mjs`
- Copy to: `/Users/dbuchber/Desktop/tmp.nosync/vscode/infra-kg-austria/deploy/teb-hackathon/site/js/gridsim/` (nur diese Dateien, ohne `*.test.mjs`)

**Interfaces:**
- Consumes: API aus Task 9; `window.maplibregl` (lädt die Seite); `stations` FeatureCollection (`properties.id` bzw. `feature.id` – beim Bauen in `site/data/stations.geojson` nachsehen).
- Produces: `export function mount(el, { apiBase = "/api/", stations, onSelectStation })` → `{ destroy() }`.
- Aufbau (Englisch): Einstellungen (Charging control, Storage strategy, Scenario, Weather year, PV factor, Run), Kacheln (Spec § 7), Band „Median and 10–90 % band over N seeds“, Vergleich (Dimension wählbar: charging / scenario / weather; startet fehlende Läufe nacheinander, nutzt Cache), Kosten „Storage vs. grid reinforcement“ (Trafo live, Leitungen „not in live model“, Platzhalter markiert, Werte änderbar → `POST costs`), Karte (Stationen nach Engpass-h eingefärbt, ohne Modellwert grau „no model data“), Drilldown-Tageskurve (gestapelte Komponenten + Grenze). Klick auf Station → Drilldown + `onSelectStation(id)`. Fußnote „All values are model values; assumptions: …“.
- CSS: nur Variablen der Seite; `dashboard.css` bindet `index.html` selbst ein (`<link rel="stylesheet" href="js/gridsim/dashboard.css">`); das Modul fügt keine Styles per JS ein; kein `innerHTML` mit Fremddaten.

- [ ] **Step 1: Failing tests** (`node --test web/gridsim/`):

```js
test("band median and p10/p90 over seeds", ...)       // [1..10] → median 5.5, p10 1.9, p90 9.1
test("band grows with each seed", ...)                 // 1 Seed → Band = Linie, 3 Seeds → Breite > 0
test("sse falls back to polling and dedups seeds", ...)  // Review Focus 2: Fake-EventSource bricht ab → Polling, kein Seed doppelt
test("missing station renders as no-data", ...)        // Review Focus 3: Farbe "no-data" für ID ohne Ergebnis
```

- [ ] **Step 2:** `node --test web/gridsim/` → FAIL
- [ ] **Step 3:** Module implementieren.
- [ ] **Step 4:** `node --test web/gridsim/` → PASS
- [ ] **Step 5: Im Browser prüfen** gegen die laufende API: Seite von 02 lokal mit Proxy `/api/` → hetzner (SSH-Tunnel `ssh -L 17061:127.0.0.1:17061 hetzner-wikidata`), Dateien nach `site/js/gridsim/` kopieren, `python3 -m http.server` im `site/`-Ordner hinter einem kleinen Proxy oder direkt auf der Live-Seite nach Deployment durch 02. Prüfen: Lauf startet, Band wächst sichtbar, Neuladen mitten im Lauf zeigt bisherige Seeds, Klick auf Station öffnet Tageskurve und markiert die Station auf der Karte von 02, hell/dunkel stimmt, Konsole ohne CSP-Fehler.
- [ ] **Step 6:** Session 02 per SendMessage: Dateien liegen unter `site/js/gridsim/`, bitte deployen.
- [ ] **Step 7: Commit** (Repo teb-grid-serving-storage) `feat(web): Regionen-Dashboard als ES-Modul`. Die Kopie im Repo infra-kg-austria committet Session 02 mit ihrer Seite.

---

### Task 12: Pitch-Probe und Doku

**Files:**
- Modify: `docs/ems-konzept.md` § 7.2 (Verweis auf gridsim und Abnahme), `docs/ems-konzept-kurzfassung.md` (neue Tabellen von Session 18), Online-Doc „EMS-Konzept Grid-Serving Storage“, `docs/arbeitsstand.md`

- [ ] **Step 1:** Komplette Pitch-Folge auf der Live-Seite am eigenen Laptop durchklicken (alle vier Minimum-Teile), Laufzeiten notieren; Fallback testen: Container neu starten, gecachte Einstellung → Replay wächst sichtbar.
- [ ] **Step 2:** Doku aktualisieren (Werte aus `docs/gridsim-abnahme.md`, Kurzfassung und Online-Doc synchron).
- [ ] **Step 3: Commit** `docs: gridsim-Ergebnisse und Pitch-Ablauf`
