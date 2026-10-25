// Karte: basemap.at grau, Umspannwerke, Ortsnetzstationen nach Engpass-Stunden, PV/Speicher je Gebäude.
/* global maplibregl */

const VENDOR = "vendor/maplibre-gl-4.7.1";
// Auch vom Regionen-Dashboard (js/gridsim/) genutzt
export const BASEMAP = "https://mapsneu.wien.gv.at/basemap/bmapgrau/normal/google3857/{z}/{y}/{x}.png";

// Engpass-Stunden je Jahr → Farbe (0 = kein Engpass)
export const ENGPASS_STEPS = [
  [0, "#9aa39a", "no bottleneck"], [1, "#e7c440", "1–9 h/yr"], [10, "#e08a3c", "10–99 h/yr"], [100, "#c8362b", "≥ 100 h/yr"],
];

export const REDUCE_MOTION = matchMedia("(prefers-reduced-motion: reduce)").matches;

export const PV_COLORS = { confirmed: "#1f5fae", only_boku: "#8fb6e8", new_since_2023: "#0f9d8a", synthetic: "#b3b1a8" };

export function createMap(container, data, onSelect) {
  if (maplibregl.setWorkerUrl) maplibregl.setWorkerUrl(`${VENDOR}/maplibre-gl-csp-worker.js`);
  else maplibregl.workerUrl = `${VENDOR}/maplibre-gl-csp-worker.js`;
  const map = new maplibregl.Map({
    container,
    style: {
      version: 8,
      sources: {
        basemap: { type: "raster", tiles: [BASEMAP], tileSize: 256, maxzoom: 19,
                   attribution: "Basemap: basemap.at (CC BY 4.0)" },
      },
      layers: [
        { id: "bg", type: "background", paint: { "background-color": "#e9e9e7" } },
        { id: "basemap", type: "raster", source: "basemap", paint: { "raster-saturation": -0.6, "raster-opacity": 0.85 } },
      ],
    },
    center: [14.42, 48.05], zoom: 11, maxZoom: 18, attributionControl: { compact: true },
    // Ein Finger scrollt die Seite, zwei Finger bzw. Strg/Cmd + Mausrad bewegen die Karte
    cooperativeGestures: true,
  });
  // ?debug: Karte für Tests in der Konsole erreichbar
  if (new URLSearchParams(location.search).has("debug")) window.demoMap = map;
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  map.on("error", e => console.error("Karte:", e.error?.message || e));

  // Ebenen nach dem Laden des Stils anlegen, nicht erst nach "load" (das wartet auf alle Kacheln)
  map.once("style.load", () => {
    map.addSource("mv", { type: "geojson", data: data.mvLines });
    // Mittelspannung entlang der Straßen (synthetisch); Breite nach Zahl der Stationen dahinter, Luftlinie gestrichelt
    const mvPaint = { "line-color": "#52514e", "line-opacity": 0.55,
      "line-width": ["interpolate", ["linear"], ["coalesce", ["get", "stationen"], 1], 1, 0.8, 40, 3] };
    map.addLayer({ id: "mv", type: "line", source: "mv", filter: ["!=", ["get", "trasse"], "luftlinie"], paint: mvPaint });
    map.addLayer({ id: "mv-air", type: "line", source: "mv", filter: ["==", ["get", "trasse"], "luftlinie"],
      paint: { ...mvPaint, "line-dasharray": [3, 3] } });
    addLv(data);
    map.addSource("pv", { type: "geojson", data: data.pv });
    map.addLayer({
      id: "pv", type: "circle", source: "pv", minzoom: 12.5,
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 12.5, 1.5, 16, 4],
        // Herkunft: BOKU 2021–23 (bestätigt / vom Modell 2025 nicht gefunden), Modell DOP 2025 neu, synthetischer Zubau
        "circle-color": ["match", ["get", "pv_evidence"],
          "synthetic", PV_COLORS.synthetic, "model_2025", PV_COLORS.new_since_2023,
          ["match", ["coalesce", ["get", "model_2025_status"], ""], "only_boku", PV_COLORS.only_boku, PV_COLORS.confirmed]],
        "circle-stroke-width": ["case", [">", ["get", "storage_kwh"], 0], 1.5, 0],
        "circle-stroke-color": "#0b0b0b",
      },
    });
    map.addSource("stations", { type: "geojson", data: data.stations, promoteId: "id" });
    map.addLayer({
      id: "stations", type: "circle", source: "stations",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["get", "trafo_kva"], 160, 4, 630, 7, 1000, 10],
        "circle-color": ["case", ["boolean", ["get", "synthetisch"], false], "#fcfcfb", colorExpr()],
        "circle-stroke-color": ["case", ["boolean", ["get", "synthetisch"], false], colorExpr(), "#0b0b0b"],
        "circle-stroke-width": ["case", ["boolean", ["feature-state", "selected"], false], 3,
                                ["boolean", ["get", "synthetisch"], false], 2, 0.8],
      },
    });
    map.addSource("uw", { type: "geojson", data: data.uw });
    map.addLayer({ id: "uw", type: "circle", source: "uw",
      paint: { "circle-radius": 7, "circle-color": "#0b0b0b", "circle-stroke-color": "#fcfcfb", "circle-stroke-width": 2 } });
    // Namen der Umspannwerke als Tooltip (eine Beschriftungsebene braeuchte Schrift-Glyphen von einem Server)

    map.on("click", "stations", e => onSelect(e.features[0].properties.id));
    for (const l of ["stations", "uw"]) {
      map.on("mouseenter", l, () => { map.getCanvas().style.cursor = "pointer"; });
      map.on("mouseleave", l, () => { map.getCanvas().style.cursor = ""; });
    }
    const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 8 });
    map.on("mousemove", "uw", e => {
      const p = e.features[0].properties;
      popup.setLngLat(e.lngLat).setText(`${p.name} · booked ${p.booked} / free ${p.available} MW (ebUtilities)`).addTo(map);
    });
    map.on("mouseleave", "uw", () => popup.remove());
    // Station: Kurzinfo beim Überfahren
    map.on("mousemove", "stations", e => {
      const p = e.features[0].properties;
      popup.setLngLat(e.lngLat).setText(`${p.id} · ${p.uw} · ${p.trafo_kva} kVA · ${p.eh ? `${p.eh} h/yr bottleneck` : "no bottleneck"} · click for the process`).addTo(map);
    });
    map.on("mouseleave", "stations", () => popup.remove());
    // PV-Punkt: Details beim Klick (Werte aus pv_storage.geojson, Speicher immer synthetisch)
    const PV_SOURCE = { boku: "BOKU 2021–23 aerial images", model_2025: "our model on 2025 aerial images", synthetic: "synthetic build-out" };
    const PV_STATUS = { confirmed: "confirmed by the 2025 model", new_since_2023: "new since 2023", only_boku: "not found by the 2025 model (usually missed)" };
    const pvPopup = new maplibregl.Popup({ offset: 6, maxWidth: "280px" });
    map.on("click", "pv", e => {
      const p = e.features[0].properties, el = document.createElement("div");
      const rows = [["PV", `${p.kwp} kWp${p.model_kwp ? ` (model: ${p.model_kwp} kWp)` : ""}`],
        ["Source", PV_SOURCE[p.pv_evidence] || p.pv_evidence], ["Status", PV_STATUS[p.model_2025_status] || "–"],
        ["Battery", p.storage_kwh > 0 ? `${p.storage_kwh} kWh / ${p.storage_kw} kW (synthetic)` : "none"],
        ["Station", p.segment_id || "–"]];
      el.className = "pv-popup";
      for (const [k, v] of rows) { const r = el.appendChild(document.createElement("div")); r.append(Object.assign(document.createElement("b"), { textContent: k + " " }), String(v)); }
      pvPopup.setLngLat(e.lngLat).setDOMContent(el).addTo(map);
    });
    map.on("mouseenter", "pv", () => { map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "pv", () => { map.getCanvas().style.cursor = ""; });
  });

  let linesOn = true;
  function addLv(lv) {
    const before = map.getLayer("pv") ? "pv" : undefined;
    if (lv.lvLines && !map.getSource("lv")) {
      map.addSource("lv", { type: "geojson", data: lv.lvLines });
      // Strichart kann in MapLibre 4.7 nicht vom Datenfeld abhängen: Kabel und Freileitung als zwei Ebenen
      const lvPaint = {
        "line-color": ["case", ["has", "auslastung_max_pct"],
          ["step", ["get", "auslastung_max_pct"], "#7a9a7a", 80, "#e08a3c", 100, "#c8362b"], "#6f7f8f"],
        "line-width": ["interpolate", ["linear"], ["zoom"], 14, 0.6, 17, 2],
      };
      map.addLayer({ id: "lv", type: "line", source: "lv", minzoom: 14,
        filter: ["!=", ["get", "typ"], "freileitung"], paint: lvPaint }, before);
      map.addLayer({ id: "lv-overhead", type: "line", source: "lv", minzoom: 14,
        filter: ["==", ["get", "typ"], "freileitung"], paint: { ...lvPaint, "line-dasharray": [2, 1.5] } }, before);
    }
    if (lv.lvHouse && !map.getSource("lv-house")) {
      map.addSource("lv-house", { type: "geojson", data: lv.lvHouse });
      map.addLayer({ id: "lv-house", type: "line", source: "lv-house", minzoom: 16,
        paint: { "line-color": "#8a8f96", "line-width": 0.7, "line-opacity": 0.8 } }, map.getLayer("lv") ? "lv" : before);
    }
    showLines(linesOn);
  }
  function showLines(on) {
    linesOn = on;
    for (const l of ["mv", "mv-air", "lv", "lv-overhead", "lv-house"]) if (map.getLayer(l)) map.setLayoutProperty(l, "visibility", on ? "visible" : "none");
  }

  let selected = null;
  return {
    map,
    // Engpass-Stunden der gewählten Kombination in die Eigenschaft `eh` schreiben und neu zeichnen
    setScenario(key) {
      for (const f of data.stations.features) f.properties.eh = f.properties.engpass[key]?.engpass_h ?? 0;
      const src = map.getSource("stations");
      if (src) src.setData(data.stations);
      else map.once("style.load", () => map.getSource("stations").setData(data.stations));
    },
    select(id, fly = true) {
      const apply = () => {
        if (selected) map.setFeatureState({ source: "stations", id: selected }, { selected: false });
        selected = id;
        map.setFeatureState({ source: "stations", id }, { selected: true });
        const f = data.byId.get(id);
        const view = { center: f?.geometry.coordinates, zoom: Math.max(map.getZoom(), 13.5) };
        if (f && fly) REDUCE_MOTION ? map.jumpTo(view) : map.easeTo(view);
      };
      map.getSource("stations") ? apply() : map.once("idle", apply);
    },
    showLines,
    // NS-Leitungen nachreichen; vor dem Laden des Stils warten
    addLv(lv) { map.getSource("mv") ? addLv(lv) : map.once("style.load", () => addLv(lv)); },
    showPv(on) {
      if (map.getLayer("pv")) map.setLayoutProperty("pv", "visibility", on ? "visible" : "none");
    },
  };
}

function colorExpr() {
  return ["step", ["coalesce", ["get", "eh"], 0],
    ENGPASS_STEPS[0][1], 1, ENGPASS_STEPS[1][1], 10, ENGPASS_STEPS[2][1], 100, ENGPASS_STEPS[3][1]];
}
