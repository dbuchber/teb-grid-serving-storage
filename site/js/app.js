// Interaktive Demo: Szenario wählen → Karte, Stationstabelle, IES-Ablauf und Diagramme folgen der Auswahl.
import { loadAll, loadLv, engpassKey } from "./data.js";
import { createMap, ENGPASS_STEPS, PV_COLORS, REDUCE_MOTION } from "./map.js";
import { runFlow } from "./flow.js";
import { lineChart, barChart } from "./chart.js";

const fmt = (v, d = 0) => v == null ? "–" : new Intl.NumberFormat("en-GB", { maximumFractionDigits: d }).format(v);
const $ = id => document.getElementById(id);
const COLORS = { base: "#898781", fixcap: "#b4540a", forecast: "#2a78d6", room: "#006300", room_persist: "#7a3fa8" };
const STRATEGIE = { base: "today (self-consumption)", fixcap: "fixed limit", forecast: "forecast", room: "forecast + empty at night",
  room_persist: "simple forecast + empty at night" };
const ROLLE = { schwach: "weak rural grid", typisch: "typical urban", pv_stark: "PV-heavy", gewerbe_pv: "commercial PV", stadt_gross: "large urban station" };

const state = { wetterjahr: 2023, szenario: "heute", pv: "1.5", richtung: "einspeisung", station: null, sort: ["eh", -1] };

async function main() {
  let data;
  try {
    data = await loadAll();
  } catch (e) {
    $("demo-status").textContent = `Data could not be loaded: ${e.message}`;
    return;
  }
  $("demo-status").remove();
  const mapApi = createMap($("map"), data, id => select(id));
  let dashboard = null;  // Regionen-Dashboard (js/gridsim/), falls vorhanden
  legend();
  // NS-Leitungen erst nach dem ersten Bild nachladen
  loadLv().then(lv => { Object.assign(data, lv); mapApi.addLv(lv); legend(); });
  const scrollTo = el => el.scrollIntoView({ behavior: REDUCE_MOTION ? "auto" : "smooth" });

  for (const [id, key] of [["sel-jahr", "wetterjahr"], ["sel-szenario", "szenario"], ["sel-pv", "pv"], ["sel-richtung", "richtung"]]) {
    $(id).value = String(state[key]);
    $(id).addEventListener("change", e => { state[key] = e.target.value; update(); });
  }
  $("chk-pv").addEventListener("change", e => mapApi.showPv(e.target.checked));
  $("chk-lines").addEventListener("change", e => mapApi.showLines(e.target.checked));
  $("only-engpass").addEventListener("change", renderTable);

  const sel = $("sel-ts");
  for (const [id, t] of Object.entries(data.timeseries)) sel.add(new Option(`${ROLLE[t.rolle] || t.rolle} (${id})`, id));
  sel.addEventListener("change", renderTimeseries);

  function current() {
    const s = { ...state };
    s.key = engpassKey(s);
    s.label = `${s.szenario === "heute" ? "today" : s.szenario}, weather ${s.wetterjahr}, PV ×${s.pv}, ${s.richtung === "einspeisung" ? "feed-in" : "demand"}`;
    return s;
  }

  function update() {
    const s = current();
    mapApi.setScenario(s.key);
    const hit = data.stations.features.filter(f => f.properties.engpass[s.key]);
    const need = hit.reduce((a, f) => a + f.properties.engpass[s.key].speicher_noetig, 0);
    const have = hit.reduce((a, f) => a + f.properties.engpass[s.key].speicher_vorhanden, 0);
    $("kpi-stationen").textContent = `${hit.length} / ${data.stations.features.length}`;
    $("kpi-speicher").textContent = `${fmt(need)}`;
    $("kpi-vorhanden").textContent = `${fmt(have)}`;
    $("kpi-label").textContent = s.label;
    verdict(hit, need, have, s);
    // Ohne Engpass an der gewählten Station gibt es keinen Ablauf: dann die am stärksten betroffene wählen
    const worst = hit.sort((a, b) => b.properties.engpass[s.key].engpass_h - a.properties.engpass[s.key].engpass_h)[0];
    if (worst && !data.byId.get(state.station)?.properties.engpass[s.key]) state.station = worst.properties.id;
    renderTable();
    renderScenarioChart();
    if (state.station) select(state.station, false);
  }

  // Kernaussage zur Kennzahlen-Box: reichen Heimspeicher für die Engpässe dieses Szenarios?
  const CHEAPER_UP_TO = 6;  // Speicher je Trafo, bis zu denen sie günstiger sind als ein größerer Trafo (Kosten-Nutzen, Kapitel 4)
  function verdict(hit, need, have, s) {
    const el = $("kpi-verdict");
    if (!hit.length) {
      el.className = "takeaway good";
      el.innerHTML = "No transformer is above its rating in this scenario: no battery calls needed.";
      return;
    }
    const hh = hit.reduce((a, f) => a + (f.properties.haushalte || 0), 0);
    const cheap = hit.filter(f => f.properties.engpass[s.key].speicher_noetig <= CHEAPER_UP_TO).length;
    const perHh = hh ? need / hh : Infinity;
    const cost = `<small>Batteries are the cheapest fix at ${fmt(cheap)} of ${fmt(hit.length)} transformers (up to ${CHEAPER_UP_TO} batteries needed);
      elsewhere a larger transformer${s.richtung === "einspeisung" ? " or some curtailment" : ""} is cheaper (chapter 4, costs).</small>`;
    if (need <= have) {
      el.className = "takeaway good";
      el.innerHTML = `Feasible with the home batteries already installed: ${fmt(need)} needed, ${fmt(have)} there.${cost}`;
    } else if (perHh <= 0.5) {
      el.className = "takeaway mid";
      el.innerHTML = `Feasible only if home storage keeps growing: ${fmt(need)} batteries would mean one for every ${fmt(1 / perHh, 1)} households
        in these grid areas (${fmt(have)} there today).${cost}`;
    } else {
      el.className = "takeaway bad";
      el.innerHTML = `Batteries alone cannot remove these bottlenecks: ${fmt(need)} batteries would be needed, ${fmt(perHh, 1)} per household
        in these grid areas. Reinforce the grid; batteries can only lower the peak.${cost}`;
    }
  }

  // Gelieferte Leistung je Abruf aus den (gemockten) Testabrufen
  function delivered() {
    let req = 0, del = 0, n = 0;
    for (const d of data.devices.devices) for (const t of d.test_calls) { req += t.requested_kw; del += Math.min(t.delivered_kw, t.requested_kw); n++; }
    if (!n) return;
    const share = del / req;
    $("kpi-geliefert").textContent = `${fmt(5 * share, 1)} kW`;
    $("kpi-geliefert-text").textContent = `a 5 kW battery delivers per call on average in the mocked test calls (${fmt(100 * share)} % of the request; ${fmt(n)} calls)`;
  }

  function select(id, fly = true) {
    state.station = id;
    mapApi.select(id, fly);
    dashboard?.showStation(id);
    renderStation();
    if (data.timeseries[id]) { sel.value = id; renderTimeseries(); }
  }

  function renderStation() {
    const s = current(), f = data.byId.get(state.station);
    if (!f) return;
    const devices = data.devicesBySegment.get(state.station) || [];
    runFlow($("flow"), f, f.properties.engpass[s.key], devices, s);
    $("flow-title").textContent = `IES process at station ${state.station}`;
  }

  function renderTable() {
    const s = current(), only = $("only-engpass").checked;
    const rows = data.stations.features.map(f => f.properties).filter(p => !only || p.engpass[s.key]);
    const [k, dir] = state.sort;
    const val = p => k === "eh" ? (p.engpass[s.key]?.engpass_h ?? 0) : k === "need" ? (p.engpass[s.key]?.speicher_noetig ?? 0) : p[k];
    rows.sort((a, b) => (val(a) > val(b) ? 1 : val(a) < val(b) ? -1 : 0) * dir);
    const cols = [["id", "Station"], ["uw", "Substation"], ["netzart", "Area"], ["kwp", "PV kWp"], ["trafo_kva", "Transformer kVA"],
                  ["speicher", "Batteries today"], ["eh", "Bottleneck h/yr"], ["need", "Batteries needed"]];
    $("station-table").innerHTML = `<thead><tr>${cols.map(([c, l]) =>
      `<th data-k="${c}" class="${c === "id" || c === "uw" || c === "netzart" ? "l" : ""} sortable"${k === c ? ` aria-sort="${dir > 0 ? "ascending" : "descending"}"` : ""}><button type="button" class="th-sort">${l}${k === c ? (dir > 0 ? " ▲" : " ▼") : ""}</button></th>`).join("")}</tr></thead>
      <tbody>${rows.slice(0, 300).map(p => {
        const e = p.engpass[s.key];
        return `<tr data-id="${p.id}" tabindex="0" class="${p.id === state.station ? "sel" : ""}">
          <td class="l">${p.id}${p.synthetisch ? ' <span class="tag mock">synthetic</span>' : ""}</td><td class="l">${p.uw}</td><td class="l">${p.netzart === "stadt" ? "urban" : "rural"}</td>
          <td>${fmt(p.kwp)}</td><td>${fmt(p.trafo_kva)}</td><td>${fmt(p.speicher)}</td>
          <td class="${e ? "bad" : ""}">${e ? fmt(e.engpass_h) : "–"}</td><td>${e ? fmt(e.speicher_noetig) : "–"}</td></tr>`;
      }).join("")}</tbody>`;
    $("table-count").textContent = `${rows.length} stations`;
    for (const th of $("station-table").querySelectorAll("th.sortable")) {
      th.querySelector("button").addEventListener("click", () => {
        const c = th.dataset.k;
        state.sort = [c, state.sort[0] === c ? -state.sort[1] : -1];
        renderTable();
      });
    }
    for (const tr of $("station-table").querySelectorAll("tbody tr")) {
      const go = () => { select(tr.dataset.id); scrollTo($("demo")); };
      tr.addEventListener("click", go);
      tr.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
    }
  }

  function renderTimeseries() {
    const t = data.timeseries[sel.value];
    if (!t) return;
    const hours = [...Array(24).keys()].map(h => `${h}`);
    // Wo Strategien gleich handeln, liegen die Linien übereinander: "today" breit und blass darunter, "fixed limit" gestrichelt
    const LOOK = { base: { width: 6, opacity: 0.35 }, fixcap: { dash: "6 4" }, forecast: { width: 2 }, room: { width: 2.5 }, room_persist: { dash: "2 3" } };
    lineChart($("chart-summer"), hours, Object.entries(t.sommer.strategien).map(([k, v]) =>
      ({ name: STRATEGIE[k] || k, values: v.map(x => -x), color: COLORS[k] || "#000", ...LOOK[k] })),
      { unit: "kW feed-in", limit: { value: t.trafo_kva, label: `transformer ${t.trafo_kva} kVA` }, xTicks: 3,
        title: `Summer day ${t.sommer.datum}` });
    $("cap-summer").textContent = `${t.id}, ${t.sommer.datum} (weather ${t.sommer.wetterjahr}), hour of day. Positive = feed-in to the grid. ` +
      `Grid-serving strategies charge the battery during the midday peak instead of in the morning; where lines coincide, the strategies behave the same.`;
    const w = t.winter;
    const rest = w.gesamt_ungesteuert.map((v, i) => v - w.davon_waermepumpe[i] - w.davon_eauto[i]);
    lineChart($("chart-winter"), hours, [
      { name: "total at the transformer (uncontrolled)", values: w.gesamt_ungesteuert, color: "#c8362b", width: 2.5 },
      { name: "heat pumps", values: w.davon_waermepumpe, color: "#2a78d6" },
      { name: "EVs", values: w.davon_eauto, color: "#b4540a" },
      { name: "households after PV and battery", values: rest, color: "#898781", dash: "6 4" },
    ], { unit: "kW demand", limit: { value: t.trafo_kva, label: `transformer ${t.trafo_kva} kVA` }, xTicks: 3, title: `Winter day ${w.datum}` });
    // Bildunterschrift aus den Daten: Anteil der Wärmepumpen in der Spitzenstunde
    const peak = w.gesamt_ungesteuert.indexOf(Math.max(...w.gesamt_ungesteuert));
    const share = w.davon_waermepumpe[peak] / w.gesamt_ungesteuert[peak];
    $("cap-winter").textContent = `${t.id}, coldest day ${w.datum}, scenario ${w.szenario}, hour of day. ` +
      `At the daily peak (${peak}:00, ${fmt(w.gesamt_ungesteuert[peak])} kW) heat pumps are ${fmt(100 * share)} % of the load. ` +
      (Math.min(...w.gesamt_ungesteuert) < 0 ? "Negative values: PV feeds in at midday even in winter. " : "") +
      (share > 0.5 ? "The heat-pump load lasts all day: a home battery cannot bridge that." : "");
  }

  function renderScenarioChart() {
    const count = (j, sz, pv, r) => data.stations.features.filter(f => f.properties.engpass[`${j}|${sz}|${pv}|${r}`]).length;
    const j = state.wetterjahr;
    barChart($("chart-scen-ein"), ["1.0", "1.5", "2.0"].map(pv => ({ label: `PV ×${pv}`,
      values: ["heute", "2030", "2040"].map(sz => count(j, sz, pv, "einspeisung")) })),
      ["today", "2030", "2040"], ["#8fb6e8", "#2a78d6", "#0b3d7a"], { title: "Feed-in bottlenecks", width: 480, height: 260 });
    barChart($("chart-scen-bez"), ["heute", "2030", "2040"].map(sz => ({ label: sz === "heute" ? "today" : sz,
      values: [2012, 2017, 2023].map(y => count(y, sz, "1.0", "bezug")) })),
      ["2012 (cold spell)", "2017", "2023 (mild)"], ["#c8362b", "#e08a3c", "#e7c440"], { title: "Demand bottlenecks", width: 480, height: 260 });
  }

  function renderReliability() {
    const classes = data.devices.vendor_classes;
    const acc = {};
    for (const d of data.devices.devices) {
      const c = (acc[d.vendor_class] ||= { n: 0, ratio: 0, calls: 0, ver: 0, resp: [] });
      c.n++;
      for (const t of d.test_calls) {
        c.calls++; c.ratio += Math.min(t.delivered_kw / t.requested_kw, 1); c.ver += t.meter_verified ? 1 : 0; c.resp.push(t.response_s);
      }
    }
    const keys = Object.keys(classes).sort();
    $("rel-count").textContent = fmt(data.devices.devices.length);
    barChart($("chart-rel"), keys.map(k => ({ label: `Class ${k}`, values: [
      100 * classes[k].reliability_assumed, 100 * acc[k].ratio / acc[k].calls, 100 * acc[k].ver / acc[k].calls] })),
      ["assumed", "delivered / requested", "confirmed by smart meter"], ["#c3c2b7", "#2a78d6", "#006300"],
      { suffix: " %", title: "Reliability per vendor class" });
    $("rel-table").innerHTML = `<thead><tr><th class="l">Class</th><th>Devices</th><th>Test calls</th><th>delivered</th><th>confirmed</th><th>Response median</th></tr></thead><tbody>${
      keys.map(k => { const c = acc[k], r = [...c.resp].sort((a, b) => a - b)[Math.floor(c.resp.length / 2)];
        return `<tr><td class="l">${k}</td><td>${fmt(c.n)}</td><td>${fmt(c.calls)}</td><td>${fmt(100 * c.ratio / c.calls)} %</td><td>${fmt(100 * c.ver / c.calls)} %</td><td>${fmt(r)} s</td></tr>`; }).join("")}</tbody>`;
  }

  function legend() {
    $("map-legend").innerHTML = ENGPASS_STEPS.map(([, c, l]) => `<li><span class="swatch" style="background:${c}"></span>${l}</li>`).join("") +
      '<li><span class="swatch hollow"></span>synthetic station</li><li><span class="swatch" style="background:#0b0b0b"></span>substation</li>' +
      `<li><span class="swatch dot" style="background:${PV_COLORS.confirmed}"></span>PV 2021–23 (BOKU), confirmed by our model on 2025 images</li>` +
      `<li><span class="swatch dot" style="background:${PV_COLORS.only_boku}"></span>PV 2021–23 (BOKU), not found by the model (usually missed, rarely removed)</li>` +
      `<li><span class="swatch dot" style="background:${PV_COLORS.new_since_2023}"></span>PV new since 2023 (model on 2025 images)</li>` +
      `<li><span class="swatch dot" style="background:${PV_COLORS.synthetic}"></span>PV added since 2023, synthetic (outside the BOKU area)</li>` +
      '<li><span class="swatch dot ring"></span>with battery</li>' +
      '<li><span class="swatch line" style="background:#52514e"></span>medium voltage along roads (synthetic; thicker = more stations; dashed = straight line)</li>' +
      (data.lvLines ? '<li><span class="swatch line"></span>low voltage along streets (synthetic, from zoom 14; colour = max. loading)</li>' : '') +
      (data.lvHouse ? '<li><span class="swatch line" style="background:#8a8f96"></span>house connections (from zoom 16)</li>' : '');
  }

  // V2G-Fälle als SVG, sobald v2g_cases.json da ist (sonst bleiben die PNGs)
  function renderV2G() {
    const cases = data.v2gCases?.faelle;
    if (!cases) { $("sel-v2g-fall").closest("label").hidden = true; return; }
    const fall = $("sel-v2g-fall").value;
    for (const fig of document.querySelectorAll("figure[data-szenario]")) {
      const c = cases.find(x => String(x.szenario) === fig.dataset.szenario && x.rolle === fig.dataset.rolle && x.fall === fall);
      if (!c) continue;
      const r = c.reihen, x = r.trafo_ungesteuert_kw.map((_, i) => `${i % 24}`);
      lineChart(fig.querySelector(".chartbox"), x, [
        { name: "EVs uncontrolled", values: r.trafo_ungesteuert_kw, color: "#c8362b", width: 2.5 },
        { name: "smart charging", values: r.trafo_gesteuert_kw, color: "#2a78d6" },
        { name: "smart charging + V2G", values: r.trafo_v2g_kw, color: "#006300" },
        { name: "of which heat pumps", values: r.waermepumpe_kw, color: "#898781", dash: "6 4" },
      ], { unit: "kW at the transformer", limit: { value: c.trafo_kva, label: `transformer ${c.trafo_kva} kVA` }, xTicks: 6,
           title: `${c.szenario}, ${ROLLE[c.rolle] || c.rolle}` });
      // Datenzeile je Fall, damit die Unterschrift auch beim Umschalten stimmt
      const peak = k => fmt(Math.max(...r[k]));
      let line = fig.querySelector(".v2g-data");
      if (!line) { line = document.createElement("span"); line.className = "v2g-data"; fig.querySelector("figcaption").append(" ", line); }
      const rest = c.v2g_rest_h_jahr == null ? `V2G cars needed ${fmt(c.v2g_autos_noetig)}` :
        c.v2g_rest_h_jahr ? `with V2G still ${fmt(c.v2g_rest_h_jahr)} h/yr above the rating (up to ${fmt(c.v2g_rest_p_kw)} kW)` :
          c.v2g_autos_max ? `V2G keeps the transformer within its rating all year (at most ${fmt(c.v2g_autos_max)} cars feeding back at once)` :
            "V2G is not needed: smart charging alone stays within the rating";
      line.textContent = `This case: peak ${peak("trafo_ungesteuert_kw")} kW uncontrolled, ${peak("trafo_gesteuert_kw")} kW with smart charging, ` +
        `${peak("trafo_v2g_kw")} kW with V2G; ${fmt(c.e_autos)} EVs, ${fmt(c.waermepumpen)} heat pumps; ${rest}.`;
    }
    $("v2g-note").textContent = "Hour of day over two days (coldest day of 2012 and the day after), simulated car by car. Smart charging shares " +
      "the free room under the rating among the plugged-in cars and catches up by 7 am. V2G additionally lets released cars feed back " +
      "(11 kW, at most 15 kWh per car and evening, 70 % of evenings released) only as much as can be recharged by 7 am; that recharging counts.";
  }
  $("sel-v2g-fall").addEventListener("change", renderV2G);

  delivered();
  update();
  renderTimeseries();
  renderReliability();
  renderV2G();

  // Regionen-Dashboard von Session 1f (js/gridsim/dashboard.js, API unter /api/): optional, fehlt es, bleibt der Anker leer
  import("./gridsim/dashboard.js?v=20261026a").then(mod => {
    const el = $("region-dashboard");
    el.hidden = false;
    dashboard = mod.mount(el, { apiBase: "/api/", stations: data.stations,
      onSelectStation: id => { if (data.byId.has(id)) { select(id); scrollTo($("map")); } } });
  }).catch(() => {});
}

// Navigation: aktiven Teil markieren, sobald seine Überschrift im oberen Drittel steht
function trackToc() {
  const links = new Map([...document.querySelectorAll("nav.toc a")].map(a => [a.getAttribute("href").slice(1), a]));
  // aktiv ist der letzte Teil, dessen Überschrift schon im oberen Drittel steht (auch nach Sprüngen)
  let pending = false;
  const update = () => {
    pending = false;
    let current = null;
    for (const id of links.keys()) {
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top <= innerHeight * 0.3) current = id;
    }
    links.forEach((a, id) => a.classList.toggle("active", id === current));
  };
  addEventListener("scroll", () => { if (!pending) { pending = true; requestAnimationFrame(update); } }, { passive: true });
  update();
}

trackToc();
main();
