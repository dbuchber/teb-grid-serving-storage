// Folie „One week, hour by hour“: Karte der 257 Trafos, eingefärbt nach Auslastung, Woche abspielbar, zwei Varianten im Vergleich.
/* global maplibregl */
import { stations, week } from "./data.js?v=20261025a";
import { LOAD_STEPS, loadOf, stepOf, overloadedAt, everOverloaded, hourLabel, fileFor } from "./playback.js?v=20261025a";

const VENDOR = "vendor/maplibre-gl-4.7.1";
const BASEMAP = "https://mapsneu.wien.gv.at/basemap/bmapgrau/normal/google3857/{z}/{y}/{x}.png";
const HOURS_PER_S = 8;
const SPEEDS = [1, 2, 4];
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

const VARIANTS = {
  winter: [
    { v: "uncontrolled", label: "Cars charge on arrival",
      text: "Electric cars start charging as soon as they come home, on top of heat pumps and household use in the evening." },
    { v: "controlled", label: "Smart charging",
      text: "Smart charging: the grid operator slows wallboxes while the transformer is full; every car is still charged by 7 am. " +
            "Counted for all cars of a transformer together, so this is the best case." },
    { v: "v2g", label: "+ V2G",
      text: "Vehicle-to-grid (V2G): on top of smart charging, released cars give power back while heat pumps and households exceed the rating " +
            "(at most 11 kW and 15 kWh per car and evening, 70 % of evenings) and recharge at night. " +
            "Caution: counted for all cars of a transformer together, an upper bound. Our car-by-car model shows the catch: in a cold spell " +
            "there is little room to recharge, so cars leave with more energy missing. V2G is a reserve, not a cure." },
  ],
  summer: [
    { v: "base", label: "Batteries as today",
      text: "Home batteries store the first solar surplus of the morning and are often full before the midday peak." },
    { v: "room", label: "Grid-serving batteries",
      text: "Grid-serving: with the next day's weather forecast, batteries keep room and charge during the midday peak, and empty at night." },
  ],
};

const $ = id => document.getElementById(id);

export function playSlide() {
  const st = { season: "winter", variant: 0, year: "2012", scenario: "2040m", pv: "1.5", h: 0, playing: false, speed: 0 };
  let map = null, mapReady = null, geo = null, idx = null, weeks = [], raf = 0, last = 0, onEnd = null, loadSeq = 0;

  const variants = () => VARIANTS[st.season];
  const opts = v => ({ season: st.season, year: st.year, scenario: st.scenario, pv: st.pv, charging: v.v, storage: v.v });
  const shown = () => weeks[st.variant];

  // ---------- Karte ----------
  function initMap(features) {
    if (maplibregl.setWorkerUrl) maplibregl.setWorkerUrl(`${VENDOR}/maplibre-gl-csp-worker.js`);
    map = new maplibregl.Map({
      container: "play-map",
      style: { version: 8, sources: { basemap: { type: "raster", tiles: [BASEMAP], tileSize: 256, maxzoom: 19,
        attribution: "Basemap: basemap.at (CC BY 4.0)" } },
        layers: [{ id: "bg", type: "background", paint: { "background-color": "#111" } },
                 { id: "basemap", type: "raster", source: "basemap", paint: { "raster-saturation": -1 } }] },
      bounds: bbox(features), fitBoundsOptions: { padding: 40 }, attributionControl: { compact: true }, cooperativeGestures: true,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    theme(document.documentElement.dataset.theme);
    mapReady = new Promise(res => map.once("style.load", () => {
      map.addSource("st", { type: "geojson", data: geo });
      map.addLayer({ id: "st", type: "circle", source: "st", paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 10, ["case", [">", ["get", "load"], 100], 6, 4], 14, 12],
        "circle-color": ["step", ["get", "load"], ...LOAD_STEPS.flatMap((s, i) => (i === 0 ? [s.color] : [LOAD_STEPS[i - 1].max + 0.001, s.color]))],
        "circle-stroke-width": 1, "circle-stroke-color": "#0008",
      } });
      res();
    }));
  }
  function bbox(features) {
    const xs = features.map(f => f.geometry.coordinates[0]), ys = features.map(f => f.geometry.coordinates[1]);
    return [[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]];
  }
  function theme(t) {
    if (!map) return;
    const dark = t !== "light";
    const apply = () => {
      map.setPaintProperty("basemap", "raster-brightness-max", dark ? 0.32 : 1);
      map.setPaintProperty("basemap", "raster-brightness-min", dark ? 0.02 : 0.15);
      map.setPaintProperty("basemap", "raster-opacity", dark ? 0.9 : 0.75);
    };
    map.isStyleLoaded() ? apply() : map.once("style.load", apply);
  }

  // ---------- Daten ----------
  async function load() {
    const seq = ++loadSeq;
    const ws = await Promise.all(variants().map(v => week(fileFor(opts(v)))));
    if (seq !== loadSeq) return;
    weeks = ws;
    idx = new Map(ws[0].stations.map((id, i) => [id, i]));
    const d = new Date(`${ws[0].start}T00:00:00Z`);
    $("play-title").textContent = st.season === "winter"
      ? `Coldest week of ${st.year}: from ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]}`
      : `Sunniest week of ${st.year}: from ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]}`;
    drawSpark();
    frame();
  }

  // ---------- Darstellung ----------
  function frame() {
    const w = shown();
    if (!w) return;
    const h = st.h;
    $("play-clock").textContent = hourLabel(w.start, h);
    $("play-now").textContent = overloadedAt(w, h, st.season);
    $("play-ever").textContent = everOverloaded(w, h, st.season);
    $("play-pos").value = h;
    const c = $("play-spark").querySelector(".cursor");
    if (c) { c.setAttribute("x1", h * 320 / 167); c.setAttribute("x2", h * 320 / 167); }
    if (geo && map?.getSource("st")) {
      for (const f of geo.features) f.properties.load = loadOf(w.pct[idx.get(f.properties.id)][h], st.season);
      map.getSource("st").setData(geo);
    }
  }

  function drawSpark() {
    const svg = $("play-spark");
    const series = weeks.map(w => Array.from({ length: 168 }, (_, h) => overloadedAt(w, h, st.season)));
    const max = Math.max(10, ...series.flat());
    const line = s => s.map((v, h) => `${h ? "L" : "M"}${(h * 320 / 167).toFixed(1)} ${(86 - v / max * 80).toFixed(1)}`).join("");
    svg.innerHTML = `<line class="base" x1="0" x2="320" y1="86" y2="86"/>` +
      series.map((s, i) => `<path class="${"abc"[i]}" d="${line(s)}"/>`).join("") +
      `<line class="cursor" x1="0" x2="0" y1="0" y2="90"/>`;
    $("spark-legend").innerHTML = variants().map((v, i) => `<span class="sw ${"abc"[i]}"></span>${v.label}`).join(" ");
  }

  // ---------- Abspielen ----------
  function tick(t) {
    if (!st.playing) return;
    if (last) {
      const adv = (t - last) / 1000 * HOURS_PER_S * SPEEDS[st.speed];
      st.frac = (st.frac || 0) + adv;
      if (st.frac >= 1) {
        st.h = Math.min(167, st.h + Math.floor(st.frac));
        st.frac %= 1;
        frame();
      }
      if (st.h >= 167) { pause(); onEnd?.(); onEnd = null; return; }
    }
    last = t;
    raf = requestAnimationFrame(tick);
  }
  function play() {
    if (st.h >= 167) st.h = 0;
    st.playing = true; last = 0;
    $("play-btn").textContent = "❚❚"; $("play-btn").setAttribute("aria-label", "Pause");
    raf = requestAnimationFrame(tick);
  }
  function pause() {
    st.playing = false; cancelAnimationFrame(raf);
    $("play-btn").textContent = "▶"; $("play-btn").setAttribute("aria-label", "Play");
  }

  // ---------- Bedienelemente ----------
  function renderControls() {
    const seg = $("ctl-variant");
    seg.innerHTML = "";
    VARIANTS[st.season].forEach((v, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.role = "radio"; b.textContent = v.label;
      b.setAttribute("aria-checked", String(i === st.variant));
      b.addEventListener("click", () => { st.variant = i; renderControls(); frame(); });
      seg.append(b);
    });
    $("ctl-season").querySelectorAll("button").forEach(b => b.setAttribute("aria-checked", String(b.dataset.v === st.season)));
    $("ctl-scen-wrap").hidden = st.season !== "winter";
    $("ctl-pv-wrap").hidden = st.season !== "summer";
    $("play-explain").textContent = VARIANTS[st.season][st.variant].text;
  }
  function wire() {
    $("ctl-season").addEventListener("click", e => {
      const b = e.target.closest("button"); if (!b || b.dataset.v === st.season) return;
      st.season = b.dataset.v; st.variant = 0; st.h = 0; renderControls(); load();
    });
    $("ctl-year").addEventListener("change", e => { st.year = e.target.value; st.h = 0; load(); });
    $("ctl-scen").addEventListener("change", e => { st.scenario = e.target.value; load(); });
    $("ctl-pv").addEventListener("change", e => { st.pv = e.target.value; load(); });
    $("play-btn").addEventListener("click", () => (st.playing ? pause() : play()));
    $("play-pos").addEventListener("input", e => { st.h = Number(e.target.value); frame(); });
    $("play-speed").addEventListener("click", () => { st.speed = (st.speed + 1) % SPEEDS.length; $("play-speed").textContent = `${SPEEDS[st.speed]}×`; });
    $("play-legend").innerHTML = LOAD_STEPS.map(s => `<li><i style="background:${s.color}"></i>${s.label}</li>`).join("");
  }

  let init = null;
  function setup() {
    init ??= (async () => {
      wire(); renderControls();
      const s = await stations();
      geo = { type: "FeatureCollection", features: s.features.map(f => ({ type: "Feature", geometry: f.geometry, properties: { id: f.properties.id, load: 0 } })) };
      initMap(geo.features);
      await load();
      await mapReady;
      frame();
    })().catch(e => { console.error("playback:", e); $("play-explain").textContent = `Data could not be loaded: ${e.message}`; });
    return init;
  }

  return {
    async enter({ auto }) {
      await setup();
      map?.resize();
      if (auto || st.h === 0) {
        st.h = 0; frame();
        return new Promise(res => { onEnd = res; play(); });
      }
    },
    leave() { pause(); onEnd = null; },
    theme,
  };
}
