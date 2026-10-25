// Regionen-Dashboard (Session 1f): echte gridsim-Läufe über alle 257 Stationen, Band wächst mit jedem Seed.
// Einbettung: mount(el, { apiBase: "/api/", stations, onSelectStation }) – siehe app.js der Seite.
import { createApi } from "./api.js";
import { BOTTLENECK, bandOf, bottleneckClass, bottleneckValues, fmt, lineStations, stationValues } from "./band.js";
import { el, renderCompare, renderDay, renderStrip, renderTiles } from "./charts.js";
import { createStationMap } from "./map.js";

const LABELS = {
  charging: { uncontrolled: "Uncontrolled charging", winap: "Winter low-price window 23:00 (WiNAP)", t3d: "Dynamic grid tariff per segment (T3d)",
    controlled: "Smart charging (DSO limit)", v2g: "Smart charging + V2G" },
  storage: { base: "Self-consumption", forecast: "Grid-serving (forecast)", room: "Grid-serving (night discharge)" },
  scenario: { heute: "Today", 2030: "2030", "2040m": "2040 moderate (35 % heat pumps)", 2040: "2040 stress case (70 % heat pumps)" },
  weather_year: { 2023: "2023 (mild)", 2017: "2017", 2012: "2012 (cold spell)" },
  pv_factor: { 1: "PV as today", 1.5: "PV × 1.5", 2: "PV × 2" },
  limits: { trafo: "Transformer only", "trafo+leitung": "Transformer + line limits" },
  netzspeicher: { false: "Off", true: "On" },
};
const FIELD_LABELS = { charging: "Charging control", storage: "Home batteries", scenario: "Scenario", weather_year: "Weather year", pv_factor: "PV build-out",
  limits: "Control limits", netzspeicher: "Grid storage at line bottlenecks" };
const DEFAULTS = { charging: "uncontrolled", storage: "base", scenario: "2030", weather_year: 2012, pv_factor: 1, limits: "trafo", netzspeicher: false };
const NUMERIC = ["weather_year", "pv_factor"];
const COMPARE = { charging: "Charging control", scenario: "Scenario", weather_year: "Weather year", limits: "Control limits" };
const COMPARE_KPI = { stations_load_congestion: ["Overloaded transformers", 0], e_net_mwh: ["Energy above limit (MWh)", 1],
  stations_line_load_congestion: ["Overloaded lines (stations)", 0] };

export function mount(root, { apiBase = "/api/", stations, onSelectStation = () => {} } = {}) {
  const api = createApi(apiBase);
  const state = { ...DEFAULTS, seeds: [], nSeeds: 20, runId: null, ids: [], stop: null, selected: null, options: null };
  const select = (name, values) => el("label", { class: "gs-field" }, el("span", { text: FIELD_LABELS[name] }),
    el("select", { name, onchange: e => { state[name] = NUMERIC.includes(name) ? +e.target.value : name === "netzspeicher" ? e.target.value === "true" : e.target.value; } },
      ...values.map(v => el("option", { value: v, text: LABELS[name][v] ?? v, selected: String(v) === String(state[name]) || undefined }))));
  const status = el("p", { class: "gs-status", role: "status", "aria-live": "polite" });
  const tiles = el("div", { class: "gs-tiles" });
  const strip = el("div", { class: "gs-chart" });
  const mapBox = el("div", { class: "gs-map" });
  const legend = el("div", { class: "gs-legend gs-map-legend" });
  const linesHint = el("span", { class: "gs-hint", role: "status" });
  const linesToggle = el("input", { type: "checkbox", onchange: e => toggleLines(e.target.checked) });
  const mapTools = el("div", { class: "gs-map-tools" },
    el("label", { class: "gs-check" }, linesToggle, el("span", { text: "Show LV lines (solid = cable, dashed = overhead; thick orange = stations where a line limits first)" })),
    linesHint, legend);
  const day = el("div", { class: "gs-chart gs-day-box" }, el("p", { class: "gs-hint", text: "Click a station on the map to see its worst day in 15-minute steps." }));
  const compareBox = el("div", { class: "gs-chart" });
  const costBox = el("div", { class: "gs-costs" });
  const runBtn = el("button", { type: "button", class: "gs-run", text: "Run simulation", onclick: () => run() });
  const controls = el("div", { class: "gs-controls" });
  const compareDim = el("select", { "aria-label": "Compare dimension" }, ...Object.entries(COMPARE).map(([k, v]) => el("option", { value: k, text: v })));
  const compareKpi = el("select", { "aria-label": "Compare value" }, ...Object.entries(COMPARE_KPI).map(([k, v]) => el("option", { value: k, text: v[0] })));
  const compareBtn = el("button", { type: "button", text: "Compare", onclick: () => compare() });

  root.classList.add("gs-root");
  root.replaceChildren(
    el("h3", { text: "Regional simulation: all 257 transformers in the Steyr area" }),
    el("p", { class: "gs-hint", text: "Each run simulates a full year hour by hour with 20 random seeds (where heat pumps and EVs are, when cars arrive). The band shows how much the result depends on chance." }),
    controls, status, tiles, strip,
    el("div", { class: "gs-split" }, el("div", { class: "gs-map-wrap" }, mapBox, mapTools), day),
    el("h4", { text: "Compare" }), el("div", { class: "gs-controls" }, compareDim, compareKpi, compareBtn), compareBox,
    el("h4", { text: "Storage vs. grid reinforcement" }), costBox,
    el("p", { class: "gs-foot", text: "All values are model values from the Steyr simulation, not measurements. Assumptions: heat demand from DORIS LoD1/TABULA, heat-pump efficiency per when2heat, EV 12 000 km/a, transformer sizing 2–3 kVA per home. Line results (when enabled) come from a synthetic low-voltage grid generated from roads and buildings, thermal limits only, not measured." }));

  const map = createStationMap(mapBox, stations || { features: [] }, id => showDay(id, true));

  function params() {
    const { weather_year, scenario, pv_factor, charging, storage, limits, netzspeicher, nSeeds } = state;
    return { weather_year, scenario, pv_factor, charging, storage, limits, netzspeicher, n_seeds: nSeeds };
  }

  function redraw() {
    renderTiles(tiles, state.seeds, state.nSeeds);
    renderStrip(strip, state.seeds, "stations_load_congestion", "Overloaded transformers per seed", 0);
    // Läufe mit Stationsnetzen: Farbe = erster Engpass (Median-Klasse über die bisherigen Seeds), sonst Überlaststunden
    const bn = bottleneckValues(state.seeds, state.ids);
    if (bn) map.update(bn, bottleneckClass); else map.update(stationValues(state.seeds, state.ids, "station_congestion_h"));
    map.highlightLines(bn ? lineStations(bn, state.ids) : []);
    renderLegend(!!bn);
  }

  // Farbe nie allein: Legende mit Text (Spec: auch ohne Farbunterscheidung lesbar)
  function renderLegend(bottleneck) {
    legend.replaceChildren(...(bottleneck ? [
      el("span", { text: "Station colour = first bottleneck (most frequent over seeds):" }),
      ...Object.values(BOTTLENECK).map(b => {
        const key = el("span", { class: "gs-key gs-key-swatch", text: b.label });
        key.style.setProperty("--sw", b.color);   // über CSSOM statt style-Attribut (CSP der Seite)
        return key;
      }),
    ] : []));
  }

  let linesLoaded = false;
  async function toggleLines(on) {
    map.showLines(on);
    if (!on || linesLoaded) { linesHint.textContent = ""; return; }
    linesHint.textContent = "Loading lines…";
    try {
      map.setLines(await api.lines(state.weather_year));
      linesLoaded = true;
      linesHint.textContent = "";
    } catch (e) {
      linesHint.textContent = e.status === 404 ? "No LV lines prepared on this server." : `Lines unavailable: ${e.message}`;
      linesToggle.checked = false;
      map.showLines(false);
    }
  }

  async function run() {
    state.stop?.();
    runBtn.disabled = true;
    state.seeds = [];
    redraw();
    status.textContent = "Starting…";
    try {
      state.ids = (await api.stations(state.weather_year)).map(s => s.id);
      const r = await api.startRun(params());
      state.runId = r.run_id;
      status.textContent = r.status === "queued" ? "Waiting for a free slot…" : r.status === "cached" ? "Replaying a finished run…" : "Running on the server…";
      const t0 = performance.now();
      state.stop = api.streamRun(r.run_id, s => {
        state.seeds.push(s);
        status.textContent = `${state.seeds.length} of ${state.nSeeds} seeds · ${fmt((performance.now() - t0) / 1000, 1)} s`;
        redraw();
      }, async done => {
        runBtn.disabled = false;
        status.textContent = done.status === "error" ? `Run failed: ${done.error}` : `${state.seeds.length} seeds in ${fmt((performance.now() - t0) / 1000, 1)} s`;
        if (state.selected) showDay(state.selected, false);
        updateCosts();
      });
    } catch (e) {
      runBtn.disabled = false;
      status.textContent = `Could not start: ${e.message}`;
    }
  }

  async function showDay(id, fromMap) {
    state.selected = id;
    map.select(id);
    if (fromMap) onSelectStation(id);
    day.replaceChildren(el("p", { class: "gs-hint", text: `Loading ${id}…` }));
    try {
      const { weather_year, scenario, pv_factor, charging, storage } = state;
      const c = await api.day(id, { weather_year, scenario, pv_factor, charging, storage, seed: 0 });
      const head = el("p", { class: "gs-hint", text: `${id} · worst day ${c.date} · peak ${fmt(Math.max(...c.trafo_kw))} kW at ${fmt(c.kva)} kVA · ${LABELS.charging[charging]} · seed 1` });
      const box = el("div");
      day.replaceChildren(head, box);
      renderDay(box, c);
    } catch (e) {
      day.replaceChildren(el("p", { class: "gs-hint", text: e.message.startsWith("no model data") ? `No model data for ${id}.` : `Could not load the day: ${e.message}` }));
    }
  }

  async function compare() {
    const dim = compareDim.value, kpi = compareKpi.value;
    const values = state.options?.[dim] ?? Object.keys(LABELS[dim]);
    const rows = values.map(v => ({ label: LABELS[dim][v] ?? String(v), value: v, band: null }));
    const draw = () => renderCompare(compareBox, rows, COMPARE_KPI[kpi][0], COMPARE_KPI[kpi][1]);
    compareBtn.disabled = true;
    for (const row of rows) {   // nacheinander, damit der Server nicht überläuft; Gecachtes kommt sofort
      row.pending = true; draw();
      const p = { ...params(), [dim]: row.value };
      try {
        const r = await api.startRun(p);
        const seeds = [];
        await new Promise(resolve => api.streamRun(r.run_id, s => {
          seeds.push(s);
          const b = bandOf(seeds, kpi);
          row.band = b.n ? b : null;   // z. B. Leitungskennzahl bei Lauf ohne Stationsnetze
          row.note = b.n ? undefined : "no line results";
          draw();
        }, resolve));
      } catch (e) { row.label += " (failed)"; }
      row.pending = false; draw();
    }
    compareBtn.disabled = false;
  }

  const costInputs = {};
  function costField(key, label, unit, placeholderNote) {
    const input = el("input", { type: "number", min: 0, step: "any", inputmode: "decimal", placeholder: placeholderNote ? "no source yet" : "", onchange: updateCosts });
    costInputs[key] = input;
    return el("label", { class: "gs-field" }, el("span", { text: `${label} (${unit})` }), input);
  }
  const costOut = el("div", { class: "gs-cost-out" });
  costBox.append(el("div", { class: "gs-controls" },
    costField("storage_eur_per_kwh", "Home battery", "€/kWh"),
    costField("trafo_step_eur", "Transformer one size up", "€ per step", true),
    costField("line_eur_per_m", "Cable reinforcement", "€/m", true)), costOut);

  async function updateCosts() {
    if (!state.runId || !state.seeds.length) { costOut.textContent = "Run a simulation first."; return; }
    const cost = {};
    for (const [k, input] of Object.entries(costInputs)) if (input.value !== "") cost[k] = +input.value;
    try {
      const c = await api.costs(state.runId, cost);
      costOut.replaceChildren(
        el("p", { text: `Home batteries: ${fmt(c.storage_eur / 1e6, 1)} M€ for the median battery need.` }),
        el("p", { text: c.trafo_eur === null ? "Transformers: enter a cost per size step (no sourced value yet)." : `Transformers: ${fmt(c.trafo_eur / 1e6, 1)} M€ (+1 size counts once, +2 or more counts twice).` }),
        el("p", { text: `Stations above 1000 kVA (new MV connection, not priced): ${fmt(c.trafo_over_1000)}.` }),
        el("p", { text: c.line_eur !== null ? `Cable reinforcement: ${fmt(c.line_eur / 1e6, 1)} M€ for the median length above rated current (synthetic LV grid, thermal only).`
          : state.seeds.some(s => typeof s.region.line_over_m === "number") ? "Cable reinforcement: enter a cost per metre (no sourced value yet)."
            : "Cable reinforcement: this run has no line results (no LV grid prepared on the server)." }),
        c.netzspeicher_eur !== null ? el("p", { text: `Grid storage at line bottlenecks: ${fmt(c.netzspeicher_eur / 1e6, 1)} M€ for the median installed capacity.` }) : null,
        c.placeholders.length ? el("p", { class: "gs-hint", text: `Placeholders without source: ${c.placeholders.join(", ")}` }) : null);
    } catch (e) { costOut.textContent = `Costs unavailable: ${e.message}`; }
  }

  api.options().then(o => {
    state.options = o;
    state.nSeeds = o.n_seeds;
    costInputs.storage_eur_per_kwh.value = o.cost_defaults.storage_eur_per_kwh;
    controls.replaceChildren(select("charging", o.charging), select("storage", o.storage), select("scenario", o.scenario),
      select("weather_year", o.weather_year), select("pv_factor", o.pv_factor),
      select("limits", o.limits ?? ["trafo", "trafo+leitung"]), select("netzspeicher", o.netzspeicher ?? [false, true]), runBtn);
    status.textContent = "Choose a setting and press Run.";
  }).catch(e => { status.textContent = `Simulation server not reachable (${e.message}).`; });
  costOut.textContent = "Run a simulation first.";
  redraw();

  return { showStation: id => showDay(id, false), destroy() { state.stop?.(); map.destroy(); root.replaceChildren(); root.classList.remove("gs-root"); } };
}
