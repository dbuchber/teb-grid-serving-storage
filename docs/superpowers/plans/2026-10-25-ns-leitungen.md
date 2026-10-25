# NS-Leitungen in gridsim – Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** gridsim bewertet neben dem Trafo jeden NS-Leitungsabschnitt, steuert optional auch gegen Leitungsgrenzen und kann Netzspeicher am Leitungsengpass setzen.

**Architecture:** Ein neuer Vorbereitungsschritt baut je Station ein radiales NS-Netz (Gebietstyp, Straßenführung, Strangteilung, Querschnitt nach Planungsregel) und speichert je Station eine Matrix „Abschnitt × Knoten“. Im Lauf werden Knotenflüsse stationsweise rekonstruiert (nie alle 18 798 Knoten × 8 760 h gleichzeitig) und auf Abschnitte summiert. Neue Parameter `limits` und `netzspeicher` in `RunParams`; Default verhält sich wie heute.

**Tech Stack:** Python ≥ 3.12, NumPy, SciPy (sparse, cKDTree), pytest; Repo `teb-grid-serving-storage`, Branch von `origin/feat/gridsim`.

**Spec:** `docs/superpowers/specs/2026-10-25-ns-leitungen-design.md`. Recherche: `docs/research/2026-10-25-ns-leitungen-steyr.md`.

## Global Constraints

- `gridsim/legacy/` nicht ändern (SHA256SUMS).
- Default `RunParams(limits='trafo', netzspeicher=False)`: Trafo-Kennzahlen bitgleich zu `origin/feat/gridsim` bei gleichen Seeds und Eingaben.
- `MODEL_VERSION` auf `'2026-10-26.1'` erhöhen.
- Nur thermische Bewertung in Kennzahlen; Spannung nur als Hinweis in der Detailansicht mit Vermerk „synthetisches Netz, nicht belastbar“.
- Bisheriger Ordner `prepared/` bleibt unverändert; Zusatzstationen erzeugen einen neuen Ordner `prepared-ns/` (Task 5b, Spec Entscheidung 1 neu).
- Grenzströme (A): NAYY 4x50 144, 4x150 275, 4x240 313; Al 4x25 135, Al 4x70 255, Al 4x95 320 (Weisenstein et al. 2022, Tab. 10). Hausanschluss Kabel NAYY 4x35 123, Freileitung Al 4x25.
- Gleichzeitigkeit g(n) = 0,07 + 0,93·n^(−3/4); P_HH = 2,0 kW; cos φ 0,97 bei Bezug, 1,0 bei Einspeisung; U = 400 V.
- Gebietstypen: stadt (Median-Nachbarabstand < 30 m, Kabel 100 %, Strang ≤ 500 m), ort (30–80 m, 80 %, 700 m), streu (> 80 m, 50 %, 1 000 m); höchstens 30 Gebäude je Abgang; ab 30 kWp eigener Abgang.
- Planungsgrenzen: 100 % Grenzstrom, 5 % Spannungsfall (Bezug), 3 % Anhebung (Einspeisung).
- Auslegung „heute“ (wp_share/ev_share aus `profiles.SCENARIOS['heute']`), Erwartungswerte, kälteste Stunde Wetterjahr 2012; ein Netz für alle Jahre.
- Abnahme „heute“: Szenario heute, PV 1,0, Speicher base, ungesteuert, `limits='trafo'`, alle drei Wetterjahre, P90 über 20 Seeds der höchsten Abschnittsauslastung je Station: ≤ 5 von 257 Stationen > 100 %, keine > 120 %. Bei Verfehlen Regel ändern, nicht die Grenze.
- Markierte Abgänge > 10 % der Stationen: anhalten und Owner fragen (Spec Entscheidung 7).
- Rechnen auf hetzner (`/data/infra-kg-austria/work/gridsim/`), nicht am Mac; Unit-Tests dürfen lokal laufen.
- Texte auf Seiten erst nach Abnahme (Task 12).

## Review Focus

1. Station ohne Straße im Umkreis (RoadGraph liefert `None`): Netz entsteht trotzdem per Luftlinie, Abgänge werden gezählt – Test in Task 3.
2. Station nur mit PV-Hallen (alle `hh == 0`, z. B. fake Station 2): g(n) und Spitzenzuschlag bei n = 0 ohne Division durch null, Zuschlag = 1 – Test in Task 4 und Task 6.
3. Stunden, in denen schon der ungesteuerte Fluss über einer Grenze liegt: gesteuertes Laden liefert 0, nie negativ, Rest in `unmet` – Test in Task 8.
4. Knotenliste in `prepared/<jahr>` weicht zwischen Jahren oder von `build_members` ab: `prepare-feeders` bricht mit klarer Meldung ab – Test in Task 5.
5. Lauf ohne `feeders/`-Verzeichnis (alte Prepared-Ordner, Fakes, API-Demo): Lauf funktioniert wie bisher, Leitungskennzahlen sind `None` – Test in Task 7.

---

### Task 1: Arbeitsumgebung und Paketgerüst

**Files:**
- Create: `gridsim/feeders/__init__.py`, `docs/superpowers/specs/2026-10-25-ns-leitungen-design.md` (Kopie), `docs/superpowers/plans/2026-10-25-ns-leitungen.md` (Kopie)

- [x] **Step 1:** Worktree `~/Desktop/tmp.nosync/vscode/teb-gss-leitungen`, Branch `feat/ns-leitungen` von `origin/feat/gridsim` (vom Controller angelegt).
- [ ] **Step 2:** Spec, Recherche und Plan liegen bereits im Worktree (vom Controller committet); `gridsim/feeders/__init__.py` mit Docstring „Synthetische NS-Netze je Station und Leitungsbewertung (Spec 2026-10-25)“.
- [ ] **Step 3:** `uv sync && uv run pytest -q` → Expected: 78 passed, 1 skipped (Ausgangsstand).
- [ ] **Step 4:** Commit `docs: Spec und Plan NS-Leitungen`.

### Task 2: Gebietstyp und Leitungstypen

**Files:**
- Create: `gridsim/feeders/area.py`, `gridsim/feeders/types.py`
- Test: `tests/test_feeders_area.py`

**Interfaces:**
- Produces:
  - `AreaType(name: str, max_nn_m: float, cable_share: float, max_feeder_m: float)` (frozen dataclass); `AREAS: dict[str, AreaType]` mit `stadt`, `ort`, `streu` (Werte aus Global Constraints).
  - `classify(xy: np.ndarray (n,2) m, hh: np.ndarray (n,)) -> str`: Median über Wohngebäude des mittleren Abstands zu den 4 nächsten Wohngebäuden (cKDTree); < 5 Wohngebäude → `'streu'`.
  - `LineType(name, i_max_a, r_ohm_km, x_ohm_km, overhead: bool)`; `TRUNK_CABLE = [NAYY 4x50, 4x150, 4x240]`, `TRUNK_OVERHEAD = [Al 4x70, Al 4x95]`, `SERVICE = {False: NAYY 4x35, True: Al 4x25}`. R/X mit Quellenkommentar je Zeile (pandapower-Standardtypen bzw. Herstellerdatenblatt).

- [ ] **Step 1: Failing tests**
```python
def test_classify_grid_spacing():
    xy = np.array([[x, y] for x in range(0, 200, 20) for y in range(0, 200, 20)], float)
    assert classify(xy, np.ones(len(xy))) == 'stadt'          # 20 m Raster
    assert classify(xy * 3, np.ones(len(xy))) == 'ort'        # 60 m
    assert classify(xy * 6, np.ones(len(xy))) == 'streu'      # 120 m

def test_classify_ignores_halls_and_few_homes():
    xy = np.array([[0, 0], [10, 0], [20, 0], [5000, 0]], float)
    assert classify(xy, np.array([1, 1, 1, 0])) == 'streu'    # < 5 Wohngebäude

def test_line_types_pinned():
    assert [t.i_max_a for t in TRUNK_CABLE] == [144, 275, 313]
    assert [t.i_max_a for t in TRUNK_OVERHEAD] == [255, 320]
    assert SERVICE[False].i_max_a == 123 and SERVICE[True].i_max_a == 135
```
- [ ] **Step 2:** `uv run pytest tests/test_feeders_area.py -v` → FAIL (ImportError).
- [ ] **Step 3:** `area.py` und `types.py` implementieren.
- [ ] **Step 4:** Tests → PASS.
- [ ] **Step 5:** Commit `feat(feeders): Gebietstyp und Leitungstypen`.

### Task 3: Topologie je Station

**Files:**
- Create: `gridsim/feeders/roads.py` (Kopie von `infra-kg-austria/scripts/steyr_lv_roads.py`, Kopfkommentar mit Herkunft und SHA256 der Quelle), `gridsim/feeders/topology.py`
- Test: `tests/test_feeders_topology.py`, `tests/fakes.py` (Funktion `fake_roads(path)` ergänzen: kleines Overpass-JSON, Kreuz aus zwei Straßen)

**Interfaces:**
- Consumes: `AREAS`, `classify` (Task 2), `roads.RoadGraph`.
- Produces:
```python
@dataclass
class StationGrid:
    station: int                 # Index in prepared stations
    area: str
    node_index: np.ndarray       # (n,) globale Knotenindizes der Station
    parent: np.ndarray           # (m,) int32, Elternabschnitt, -1 = Sammelschiene
    length_m: np.ndarray         # (m,) float32
    feeder: np.ndarray           # (m,) int16, Abgangsnummer ab 0
    service: np.ndarray          # (m,) bool, Hausanschluss
    overhead: np.ndarray         # (m,) bool
    downstream: sparse.csr_matrix  # (m, n), 1 = Knoten liegt hinter dem Abschnitt
    marked: np.ndarray           # (n_feeder,) bool, „bräuchte eigene Station“
    geometry: list               # m Arrays (k,2), EPSG:31287
```
  `build_station_grid(station: int, st_xy, node_index, nodes_xy, nodes_hh, nodes_kwp, roads: RoadGraph | None) -> StationGrid`

Regeln (Spec 4.2): Weg entlang der Straße wie `build_net_roads`; ohne Straße an Station oder Gebäude Luftlinie × 1,2. Anlagen > 30 kWp eigener Abgang ab Sammelschiene. Abgänge an Abzweigen teilen, solange ein Abgang > 30 Gebäude hat oder seine Reichweite > `max_feeder_m`; geteilte Abgänge sind eigene Abschnitte ab Sammelschiene (gleicher Graben). Abgang, dessen Reichweite nach dem Teilen noch > `max_feeder_m`: `marked`. Freileitung: Abgänge nach Länge absteigend als `overhead` markieren, bis Anteil Freileitungslänge ≥ 1 − `cable_share`; Hausanschlüsse erben vom Abgang.

- [ ] **Step 1: Failing tests**
  - `test_downstream_root_rows_cover_all_nodes`: Summe der Zeilen aller Abschnitte mit `parent == -1` ergibt jeden Knoten genau einmal.
  - `test_feeder_split_limits_buildings`: 70 Wohngebäude an einer Straße (Typ ort) → jeder Abgang ≤ 30 Gebäude.
  - `test_long_feeder_marked`: ein Gebäude 1 500 m entlang der Straße bei Typ stadt → `marked.any()`.
  - `test_direct_feeder_for_large_pv`: Knoten mit 40 kWp hat eigenen Abgang mit `parent == -1`.
  - `test_overhead_share_streu`: Typ streu → Freileitungslänge / Trunklänge ≥ 0,5; Typ stadt → kein `overhead`.
  - `test_no_road_falls_back_to_air_line` (Review Focus 1): `roads=None` → Netz entsteht, jede Länge = 1,2 × Luftlinie.
- [ ] **Step 2:** Tests → FAIL.
- [ ] **Step 3:** `build_station_grid` implementieren; Straßenbaum über `RoadGraph.station_tree`/`contract` wie `build_net_roads`.
- [ ] **Step 4:** Tests → PASS.
- [ ] **Step 5:** Commit `feat(feeders): radiale NS-Topologie je Station`.

### Task 4: Bemessung nach Planungsregel

**Files:**
- Create: `gridsim/feeders/sizing.py`
- Test: `tests/test_feeders_sizing.py`

**Interfaces:**
- Consumes: `StationGrid`, `LineType`-Listen.
- Produces:
  - `g(n: np.ndarray) -> np.ndarray` (n = 0 → 0).
  - `p_ev(n_cars: np.ndarray) -> np.ndarray` = 0,53 + 10,47·n^(−1,264) kW je Auto (n = 0 → 0; ergibt 11 kW bei 1, 1,1 kW bei 10, ≈ 0,54 bei 224; Maier/Groiß 2026).
  - `design_flows(grid, hh, wp_kw_exp, cars_exp, kwp_peak_kw) -> tuple[np.ndarray, np.ndarray]`: je Abschnitt Auslegungsbezug (kW) = P_HH·g(n)·n + Σ wp_kw_exp + n_cars·p_ev(n_cars) über die nachgelagerten Knoten; Auslegungseinspeisung = Σ kwp_peak_kw.
  - `SizedGrid(types: list[str], parallel: np.ndarray, i_max_a: np.ndarray, r_ohm: np.ndarray, x_ohm: np.ndarray, du_load_pct: np.ndarray, du_feed_pct: np.ndarray, marked: np.ndarray)`; `size(grid, p_load, p_feed) -> SizedGrid`.

Verfahren: Hausanschlüsse fest (`SERVICE`). Trunk je Abschnitt kleinster Typ der Liste (Kabel oder Freileitung nach `overhead`), der den Auslegungsstrom trägt; dann je Abgang Spannungsfall vom Trafo bis zum entferntesten Knoten (Σ (R·P + X·Q)/U² auf dem Pfad) prüfen; > 5 % (Bezug) bzw. > 3 % (Einspeisung): den Abschnitt des Pfads mit dem größten Beitrag eine Stufe hochsetzen, wiederholen; über dem größten Typ `parallel = 2`; reicht auch das nicht, Abgang in `marked`.

- [ ] **Step 1: Failing tests**
```python
def test_g_values():
    assert g(np.array([1]))[0] == pytest.approx(1.0)
    assert g(np.array([0]))[0] == 0.0
    assert g(np.array([100]))[0] == pytest.approx(0.07 + 0.93 * 100 ** -0.75)

def test_p_ev_anchor_points():
    assert p_ev(np.array([1, 10]))[:].round(2).tolist() == [11.0, 1.1]
```
  - `test_size_picks_smallest_thermal`: ein Abschnitt 50 m, Typ stadt; 60 kW Bezug (≈ 89 A) → `'NAYY 4x50'`; 150 kW (≈ 223 A) → `'NAYY 4x150'`.
  - `test_size_voltage_drop_upgrades`: 600 m, 60 kW → Spannungsfall mit 4x50 > 5 % → stärkerer Typ, `du_load_pct ≤ 5`.
  - `test_size_marks_impossible`: 2 000 m, 200 kW → `marked`.
  - `test_halls_only_station` (Review Focus 2): alle `hh == 0` → kein Fehler, Auslegung nur aus Einspeisung.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(feeders): Querschnitt nach Grenzstrom und Spannungsfall`.

### Task 5: `prepare-feeders`

**Files:**
- Create: `gridsim/feeders/prepare.py`
- Modify: `gridsim/cli.py` (Unterbefehl `prepare-feeders --input --prepared`)
- Test: `tests/test_feeders_prepare.py`

**Interfaces:**
- Consumes: Tasks 2–4; `legacy.load('steyr_sim_variant_a').build_members(inp)` für Knoten- und Stationskoordinaten; `profiles.heat_pump_kw`, `wpev.spread`.
- Produces: `prepare_feeders(input_dir: Path, prepared_root: Path) -> Path` schreibt nach `prepared_root/feeders/`:
  - `<station_idx>.npz` (Felder von `StationGrid` und `SizedGrid`, `downstream` als CSR-Arrays),
  - `index.json` (je Station: area, n_feeders, marked, trunk_m, overhead_m),
  - `lines.geojson` (WGS84, Eigenschaften type, parallel, feeder, overhead, service),
  - `report.json` (Regionswerte für Task 11),
  - `manifest.json` (Eingabe-SHA256 wie `prepare.py`).
  - `load_feeders(prepared_root) -> dict[int, tuple[StationGrid, SizedGrid]] | None` (None ohne Verzeichnis).

Auslegungslast je Knoten: `wp_kw_exp` = p_wp × elektrische WP-Leistung in der Stunde mit der tiefsten Temperatur der Knotenzelle im Wetterjahr 2012 (`heat_pump_kw` mit Wärme wie `profiles.assign`, `limits` aus `wpev.spread(N, run.BASE_SEED)`, Versatz 0), p_wp wie in `profiles.assign` für `'heute'`; Fernwärmeknoten 0. `cars_exp` = ev_share(heute) × hh. `kwp_peak_kw` = kWp × max(`pv_bins`) von 2012.

- [ ] **Step 1: Failing tests** (mit `write_fake_prepared` für 2012 und 2023 und gepatchtem `build_members`, der die Fake-Knoten mit Koordinaten liefert):
  - `test_prepare_feeders_writes_all_stations`: `index.json` hat 3 Einträge, `load_feeders` liefert 3 Netze.
  - `test_prepare_feeders_rejects_node_mismatch` (Review Focus 4): `nodes_station` von 2023 geändert → `ValueError` mit „Knoten“ in der Meldung.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren (Stationen sequenziell oder Prozesspool, frei). **Step 4:** PASS.
- [ ] **Step 5:** Auf hetzner: `uv run python -m gridsim prepare-feeders --input /data/infra-kg-austria/work/steyr-pv-2026-10-24/input --prepared prepared` → 257 Dateien, `report.json`. Prüfen: Anteil Stationen mit markierten Abgängen; **> 10 % → anhalten, Owner fragen.**
- [ ] **Step 5a:** Einmalige Kalibrierung (Spec 4.1): Liegt der regionale Kabelanteil außerhalb 74–84 %, die Schwellen `max_nn_m` von stadt/ort in 5-m-Schritten verschieben, bis er im Band liegt; gewählte Werte mit Begründung in `area.py` und im Commit festhalten. Danach nicht mehr ändern.
- [ ] **Step 6:** Commit `feat(feeders): prepare-feeders mit Auslegung heute`.

### Task 5b: Zusatzstationen (Owner-Entscheidung 25.10.2026)

**Files:**
- Create: `gridsim/feeders/extra_stations.py`
- Modify: `gridsim/feeders/prepare.py` (Ausgabe in neuen Ordner), `gridsim/cli.py` (`prepare-feeders --extra-stations --out prepared-ns`)
- Test: `tests/test_feeders_extra.py`

**Interfaces:**
- Produces:
  - `plan_extra(st_xy, nodes_xy, nodes_hh, nodes_station, grids: dict) -> list[dict]`: je Station mit markiertem Abgang (Topologie oder Bemessung) neue Standorte: die Gebäude der markierten Abgänge per k-Means (k = kleinste Zahl, bei der kein Cluster mehr als 30 Gebäude hat und kein Gebäude weiter als `max_feeder_m`/1,2 Luftlinie vom Clusterzentrum liegt), Standort = Gebäude nächst dem Zentrum (auf einer Straße, wenn möglich). Jede neue Station: `{'id': 'demo:steyr:ns-NNN', 'x', 'y', 'lon', 'lat', 'synthetic': 1, 'parent': <alte Station-ID>}`.
  - Neuzuordnung: jedes Gebäude zur nächsten Station (alte + neue) entlang der Straße, Fallback Luftlinie ≤ 600 m wie bisher; Trafo je Station mit `sim.trafo_kva(n_buildings, n_hh, kwp)`.
  - `write_variant(prepared_root, out_root, stations, nodes_station)`: kopiert alle Arrays aller Wetterjahre, ersetzt `nodes_station.npy` und `stations.json` (gleiches Format, `uw` vom Elternknoten), Manifest mit Verweis auf die Ausgangsvariante.
  - Danach läuft `prepare_feeders` auf `out_root`.
- Abbruch: bleiben nach einem Durchgang > 10 % der Stationen markiert, einen zweiten Durchgang ausführen; danach berichten statt weiter zu iterieren.

- [ ] **Step 1: Failing tests** – `test_extra_station_splits_long_feeder` (Gebäude 1 500 m entfernt, Typ stadt → eine Zusatzstation, danach nicht mehr markiert); `test_variant_leaves_source_untouched` (Quellordner unverändert, SHA256 vor/nach); `test_new_station_ids_and_flags` (`synthetic == 1`, ID-Muster, `parent` gesetzt); `test_trafo_kva_rule` (kva = `sim.trafo_kva` der neuen Zuordnung).
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS, gesamte Suite grün.
- [ ] **Step 5:** Auf hetzner im Ordner `/data/infra-kg-austria/work/gridsim-leitungen`: `prepare-feeders --extra-stations --out prepared-ns`; `report.json` mit Stationszahl alt/neu, Anteil markierter Stationen, Abgänge je Station, Trasse je Station, Kabelanteil; nach `docs/feeders-report-ns-2026-10-26.json` kopieren.
- [ ] **Step 6:** Commit `feat(feeders): Zusatzstationen für zu lange Abgänge`.

Folgeaufgaben (6–11) rechnen auf `prepared-ns/`; der Abnahmebericht stellt Trafo-Kennzahlen `prepared/` gegen `prepared-ns/`.

### Task 6: Knotenflüsse je Station und Abschnittsauslastung

**Files:**
- Create: `gridsim/nodeflow.py`, `gridsim/feeders/loading.py`
- Modify: `gridsim/run.py` (`flows()` liefert zusätzlich `'storage_delta'` (8760, K) und `'storage_idx'`)
- Test: `tests/test_nodeflow.py`, `tests/test_feeders_loading.py`

**Interfaces:**
- Consumes: Ergebnis von `run.flows`, `StationGrid`, `SizedGrid`.
- Produces:
  - `NodeBlock(hh_kw, pv_kw, wp_kw, storage_kw, ev_kw, v2g_kw, nodes)` je (8760, n_s), float32; `.net()` = hh + wp − pv + storage + ev − v2g.
  - `station_block(p, params, f, s: int) -> NodeBlock`. WP je Knoten mit denselben `limits/shifts` wie `profiles.heat_pump` (gleicher Seed). E-Auto je Knoten: Ereignisse der Station mit lokalem Knotenindex rendern. Bei `controlled`/`v2g` im Modus `trafo`: Stationsentscheidung je Stunde anteilig auf die Knoten verteilen (Anteil am Bedarf inkl. Rückstau; V2G anteilig nach Autos).
  - `segment_flow(grid, sized, block) -> np.ndarray (8760, m)` = `block.net() @ downstream.T` + (f(n) − 1)·(`block.hh_kw @ downstream.T`), f(n) = max(1, g(n)·P_HH / (max(h0)·KWH_PER_HH)), n = Haushalte hinter dem Abschnitt, n = 0 → 1.
  - `loading_pct(seg_flow, sized) -> np.ndarray` mit cos φ 0,97 bei Bezug, 1,0 bei Einspeisung, Strom / (i_max × parallel).

- [ ] **Step 1: Failing tests**
  - `test_block_sums_to_station_flow` (für alle `CHARGING`-Werte, fake prepared): `block.net().sum(axis=1)` ≈ `f['flow'][:, s]` (atol 1e-3).
  - `test_root_segments_sum_without_surcharge`: ohne Zuschlag ist Summe der Wurzelabschnitte = Stationsfluss.
  - `test_surcharge_only_small_groups`: n = 1 → f > 1; n = 500 → f ≈ 1.
  - `test_loading_direction_pf`: +100 kW und −100 kW auf 4x150 → Auslastung Bezug = Einspeisung / 0,97.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS; `uv run pytest -q` gesamt grün.
- [ ] **Step 5:** Commit `feat(gridsim): Knotenflüsse je Station und Abschnittsauslastung`.

### Task 7: Lauf mit Leitungskennzahlen

**Files:**
- Modify: `gridsim/run.py` (`RunParams.limits: str = 'trafo'`, `RunParams.netzspeicher: bool = False`, `LIMITS = ('trafo', 'trafo+leitung')`, `MODEL_VERSION = '2026-10-26.1'`, `_init` lädt `load_feeders`, `run_seed` rechnet je Station), `gridsim/metrics.py`
- Test: `tests/test_run.py`, `tests/test_metrics.py`

**Interfaces:**
- Produces in `SeedResult.extra` (None-Werte ohne Feeders):
  - `station_line_max_pct: list[float]`, `station_line_load_h: list[int]`, `station_line_feed_h: list[int]`, `station_first_load: list[str]`, `station_first_feed: list[str]` mit Werten `'trafo' | 'leitung' | 'beide' | 'keiner'`.
  - Region (`region`-Dict, neue Schlüssel): `stations_line_load_congestion`, `stations_line_feed_congestion`, `stations_line_only`, `line_over_m` (Länge überlasteter Abschnitte), `marked_feeders`.
  - `metrics.line_kpis(loading_pct: np.ndarray, sized, grid) -> dict` je Station.
  - `metrics.costs`: `line_eur` = `line_over_m` × `line_eur_per_m` (Platzhalter `None` wie bisher gemeldet).

- [ ] **Step 1: Failing tests**
  - `test_default_params_trafo_kpis_unchanged`: `run_seed` mit Default-Params auf fake prepared liefert dieselben `region`-Trafo-Werte wie eine eingefrorene Referenz (vor der Änderung mit `origin/feat/gridsim` erzeugt und als JSON in `tests/data/` abgelegt).
  - `test_runs_without_feeders` (Review Focus 5): ohne `feeders/` sind alle Leitungswerte `None`, Lauf erfolgreich.
  - `test_first_classification`: Station mit Trafo 140 % und Leitung 90 % → `'trafo'`; beide > 100 % → `'beide'`.
  - `test_params_validate_limits`: `limits='x'` → `ValueError`.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(gridsim): Leitungskennzahlen im Lauf`.

### Task 8: Steuerung mit Leitungsgrenzen

**Files:**
- Create: `gridsim/control_lines.py`
- Modify: `gridsim/run.py` (Verzweigung bei `limits == 'trafo+leitung'`)
- Test: `tests/test_control_lines.py`

**Interfaces:**
- Produces:
  - `room(seg_flow0, sized, kva, station_flow0) -> (seg_room (8760, m), trafo_room (8760,))` in kW (≥ 0).
  - `controlled_lines(block0: NodeBlock, ev_want: np.ndarray (8760, n), grid, sized, kva) -> tuple[np.ndarray (8760, n), np.ndarray (n, 365)]`: Laden je Knoten und ungeladene Energie je Knoten und Tag (Frist 7 Uhr wie `control.controlled`).
  - `v2g_lines(block, cars_node, grid, sized, kva) -> tuple[out, recharge, unmet]` je Knoten.
  - `signal_lines(seg_flow, sized, station_flow, kva) -> np.ndarray (365,) bool`: T3d-Signal, wenn Trafo **oder** ein Abschnitt im Fenster über der Grenze (Fenster wie `control.SIGNAL_WINDOW`).

Verteilung je Stunde (Spec 4.5): Bedarf je Knoten; Abschnitte von den Blättern zur Wurzel: Faktor = min(1, Raum / Summe des bisher zugeteilten Bedarfs dahinter), auf die Knoten dahinter anwenden; zuletzt Trafo. V2G: Überlast je Abschnitt von den Blättern zur Wurzel mit Rückspeisung der Autos dahinter decken (Leistung `V2G_KW·V2G_AVAIL`, Energie `V2G_KWH·V2G_AVAIL` je Abend wie `control.v2g`), Nachladen bis 7 Uhr nur im Raum aller Abschnitte des Pfads.

- [ ] **Step 1: Failing tests**
  - `test_controlled_lines_respects_every_segment`: nach Steuerung kein Abschnitt und nicht der Trafo über der Grenze, wenn der ungesteuerte Fluss darunter lag.
  - `test_controlled_lines_never_negative` (Review Focus 3): Grundfluss schon über der Grenze → Laden 0, Bedarf in `unmet`.
  - `test_energy_conserved`: geladen + ungeladen = Bedarf je Knoten und Tag.
  - `test_trafo_only_equals_old_controlled`: Netz ohne enge Abschnitte (alle i_max sehr groß) → Stationssumme gleich `control.controlled`.
  - `test_v2g_lines_relieves_downstream_only`: Überlast auf Abgang A wird nur von Autos hinter A gedeckt.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(gridsim): gesteuertes Laden, V2G und T3d gegen Leitungsgrenzen`.

Hinweis zur Spec: Die Heimspeicher-Strategien (`base`, `forecast`, `room`) in gridsim reagieren heute nicht auf Abrufe; sie bleiben unverändert. Abrufe je Abgang setzt der Netzspeicher (Task 9) um. In den Abnahmebericht aufnehmen.

### Task 9: Netzspeicher am Leitungsengpass

**Files:**
- Create: `gridsim/netzspeicher.py`
- Modify: `gridsim/run.py` (bei `netzspeicher=True`: Bemessung aus Seed 0 derselben Params mit `netzspeicher=False`, im Cache unter `<key>/netzspeicher.json`), `gridsim/metrics.py`
- Test: `tests/test_netzspeicher.py`

**Interfaces:**
- Produces:
  - `place(grid, loading_pct) -> list[tuple[int, int]]`: (Abgang, lokaler Knoten) – je Abgang mit Überlast der Knoten direkt hinter dem Abschnitt mit der höchsten Auslastung, höchstens einer je Abgang.
  - `size(seg_flow_at, limit_kw) -> tuple[float, float] | None`: (kWh, kW) über `metrics.segment_row` auf dem Abschnittsfluss in beiden Richtungen, Energie = max der beiden `e_inst_kwh`, Leistung = max `p_max_kw`.
  - `dispatch(seg_flow_at: np.ndarray (8760,), limit_kw, kwh, kw, eta=0.95) -> np.ndarray (8760,)` (+ = Laden): Tageweise mit perfekter Prognose; lädt die Einspeiseüberlast, entlädt die Bezugsüberlast, sonst Richtung 50 % Ladezustand, ohne den Abschnitt dabei über die Grenze zu bringen.
  - Region: `netzspeicher_n`, `netzspeicher_kwh`, `netzspeicher_vollzyklen`, `line_over_m_rest`; Kosten `netzspeicher_eur` = kWh × `storage_eur_per_kwh`.

- [ ] **Step 1: Failing tests**
  - `test_dispatch_soc_bounds`: Ladezustand bleibt in [0, kWh].
  - `test_dispatch_removes_overload_when_sized`: Abschnittsfluss mit Spitze über der Grenze, Speicher nach `size` → nach Einsatz keine Überlast.
  - `test_dispatch_energy_balance`: Σ Laden·η − Σ Entladen/η = Δ Ladezustand.
  - `test_place_one_per_feeder`.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(gridsim): Netzspeicher am Leitungsengpass`.

### Task 10: API und Dashboard

**Files:**
- Modify: `api/app.py` (`/stations` liefert `area`, `marked`; `/runs`-Body akzeptiert `limits`, `netzspeicher`), `web/gridsim/*.js` (Stationsfarbe nach `station_first_load`, Ebene `lines.geojson` nach Auslastung des gewählten Laufs, Schalter für `limits`/`netzspeicher`), `gridsim/drilldown.py` (Spannungshinweis mit Vermerk)
- Test: `tests/test_api.py`, `web/gridsim/*.test.mjs`

- [ ] **Step 1:** Failing tests: API lehnt `limits='x'` mit 400 ab; `/stations` enthält `area`; Dashboard-Modul färbt `'leitung'` anders als `'trafo'`.
- [ ] **Step 2:** FAIL. **Step 3:** implementieren. **Step 4:** `uv run pytest -q` und `node --test web/gridsim/*.test.mjs` grün.
- [ ] **Step 5:** Commit `feat(api, web): Leitungen in API und Dashboard`.

### Task 11: Abnahme auf hetzner

**Files:**
- Create: `gridsim/feeders/report.py`, `tools/pp_compare.py` (läuft im pandapower-Container `/data/infra-kg-austria/work/steyr-gutachten-2026-10-25/py.sh`, nicht Teil der Paketabhängigkeiten), `docs/gridsim-leitungen-abnahme.md`
- Modify: `gridsim/cli.py` (Unterbefehl `lines-report --prepared --cache --report`)

- [ ] **Step 1:** `batch` für die Abnahmeeinstellung (Global Constraints) über 2012/2017/2023, 20 Seeds.
- [ ] **Step 2:** `lines-report` schreibt: Plausibilität gegen Referenzwerte (NS-Länge je Station Ziel ≈ 2,7 km, Abgänge 3,4–3,8, Kabelanteil ≈ 79 %, Typverteilung), Anteil markierter Abgänge, Abnahmegrenze bestanden ja/nein mit Zahlen.
- [ ] **Step 3:** Grenze verfehlt → Bemessungsregel prüfen, Änderung begründen, zurück zu Task 4; die Grenze bleibt.
- [ ] **Step 4:** Vergleich 2030 und 2040 (2012, 2023): `limits` trafo / trafo+leitung × `netzspeicher` aus / an × `charging` uncontrolled / controlled / v2g; Tabelle „Trafo / Leitung / beide“ und Reihenfolge heute → 2030 → 2040.
- [ ] **Step 5:** Stichprobe drei Stationen je Gebietstyp (Abschnittstabelle, Kartenausschnitt) und `pp_compare.py` für dieselben Stationen in den 24 stärksten Stunden: Abweichung der Abschnittsauslastung berichten.
- [ ] **Step 6:** Commit `docs: Abnahme NS-Leitungen`.

### Task 12: Profil und Seiten (nach Freigabe der Zahlen durch den Owner)

**Files:**
- Modify: `docs/context/profil-v2.md` (P4/P9: Abruf je Abgang, Netzspeicher als VNB-Element), `site/details.html` und `site/index.html` (ein Satz und eine Zahl „Leitungen vor Trafo“ je Szenario, Kennzeichnung synthetisch; Annahmen und Quellen auf der Detailseite); Live-Kopie in `infra-kg-austria/deploy/teb-hackathon/site/` nach Abstimmung mit der Seiten-Session.

- [ ] **Step 1:** Zahlen aus `docs/gridsim-leitungen-abnahme.md` dem Owner vorlegen; erst nach OK weiter.
- [ ] **Step 2:** Texte ändern; Präsentation mit Playwright in 1280×720, 1440×900 und 1920×1080 auf Überlauf prüfen.
- [ ] **Step 3:** Commit; Deploy nur nach Owner-OK (Bind-Mount-Dateien in place überschreiben).
