// Kleine Stationskarte (MapLibre der Seite, Kacheln aus ../map.js); Farbe = Überlaststunden (Median der Seeds)
// oder, bei Läufen mit Stationsnetzen, erster Engpass (Trafo/Leitung/beide/keiner); optionale Leitungsebene.
import { BASEMAP } from "../map.js";
import { BOTTLENECK, colorClass } from "./band.js";

const COLORS = () => {
  const css = getComputedStyle(document.documentElement);
  const v = name => css.getPropertyValue(name).trim();
  return { ok: v("--ok"), warn: v("--warn"), bad: v("--warn"), "no-data": v("--muted") || "#898781", line: v("--line"), ink2: v("--ink2") };
};

export function createStationMap(container, stations, onClick) {
  const gl = globalThis.maplibregl;
  if (!gl) {
    container.textContent = "Map not available (MapLibre not loaded).";
    return { update() {}, select() {}, setLines() {}, showLines() {}, highlightLines() {}, destroy() {} };
  }
  const map = new gl.Map({
    container, attributionControl: { compact: true },
    style: {
      version: 8,
      sources: { basemap: { type: "raster", tiles: [BASEMAP], tileSize: 256, maxzoom: 19, attribution: "Basemap: basemap.at (CC BY 4.0)" } },
      layers: [{ id: "basemap", type: "raster", source: "basemap" }],
    },
    center: [14.42, 48.04], zoom: 10.3,
  });
  let pending = null, ready = false;
  let lineState = { geojson: null, visible: false, stations: [] };   // Zustand der Leitungsebene, bis die Karte geladen ist
  const data = cls => ({
    type: "FeatureCollection",
    features: stations.features.map(f => ({ ...f, properties: { id: f.properties.id, cls: cls(f.properties.id) } })),
  });
  map.on("load", () => {
    const c = COLORS();
    map.addSource("gs-stations", { type: "geojson", data: data(() => "no-data") });
    map.addLayer({
      id: "gs-stations", type: "circle", source: "gs-stations",
      paint: {
        "circle-radius": ["interpolate", ["linear"], ["zoom"], 9, 3, 13, 7],
        "circle-color": ["match", ["get", "cls"], "ok", c.ok, "warn", c.warn, "bad", c.bad,
          ...Object.entries(BOTTLENECK).flatMap(([k, v]) => [k, v.color]), c["no-data"]],
        "circle-opacity": ["match", ["get", "cls"], "bad", 1, "no-data", 0.5, 0.85],
        "circle-stroke-width": ["case", ["==", ["get", "cls"], "bad"], 2, 0.5],
        "circle-stroke-color": c.line,
      },
    });
    map.addLayer({ id: "gs-selected", type: "circle", source: "gs-stations", filter: ["==", ["get", "id"], ""],
      paint: { "circle-radius": 10, "circle-color": "rgba(0,0,0,0)", "circle-stroke-width": 2, "circle-stroke-color": COLORS().ok } });
    map.on("click", "gs-stations", e => onClick(e.features[0].properties.id));
    map.on("mouseenter", "gs-stations", () => { map.getCanvas().style.cursor = "pointer"; });
    map.on("mouseleave", "gs-stations", () => { map.getCanvas().style.cursor = ""; });
    ready = true;
    if (pending) update(...pending);
    applyLines();
  });
  // Leitungsebene: Kabel durchgezogen, Freileitung gestrichelt; Abschnitte von Stationen mit Leitung als erstem Engpass
  // dick und farbig (Stationsebene, nicht je Abschnitt: das Ergebnis liegt je Station vor)
  const LINE_LAYERS = ["gs-lines-cable", "gs-lines-overhead", "gs-lines-hot"];
  const zoomWidth = (lo, hi) => ["interpolate", ["linear"], ["zoom"], 10, lo, 15, hi];
  function applyLines() {
    if (!ready || !lineState.geojson) return;
    if (!map.getSource("gs-lines")) {
      const ink = COLORS().ink2 || "#555555";
      map.addSource("gs-lines", { type: "geojson", data: lineState.geojson });
      const add = (id, filter, paint) => map.addLayer({ id, type: "line", source: "gs-lines", filter, layout: { visibility: "none" }, paint }, "gs-stations");
      add("gs-lines-cable", ["!", ["get", "overhead"]], { "line-color": ink, "line-opacity": 0.8, "line-width": zoomWidth(0.5, 2) });
      add("gs-lines-overhead", ["==", ["get", "overhead"], true],
        { "line-color": ink, "line-opacity": 0.8, "line-width": zoomWidth(0.5, 2), "line-dasharray": [2, 2] });
      add("gs-lines-hot", ["in", ["get", "station"], ["literal", []]],
        { "line-color": BOTTLENECK["b-leitung"].color, "line-opacity": 0.95, "line-width": zoomWidth(1.5, 5) });
    }
    for (const id of LINE_LAYERS) map.setLayoutProperty(id, "visibility", lineState.visible ? "visible" : "none");
    map.setFilter("gs-lines-hot", ["in", ["get", "station"], ["literal", lineState.stations]]);
  }
  // ``cls(values, id)`` liefert die Farbklasse; Standard = Überlaststunden, ``bottleneckClass`` = erster Engpass
  function update(values, cls = colorClass) {
    pending = [values, cls];
    if (ready) map.getSource("gs-stations").setData(data(id => cls(values, id)));
  }
  return {
    update,
    setLines(geojson) { lineState.geojson = geojson; applyLines(); },
    showLines(visible) { lineState.visible = visible; applyLines(); },
    highlightLines(stations) { lineState.stations = stations; applyLines(); },
    select(id) { if (ready) map.setFilter("gs-selected", ["==", ["get", "id"], id]); },
    destroy() { map.remove(); },
  };
}
