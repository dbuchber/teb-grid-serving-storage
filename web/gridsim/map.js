// Kleine Stationskarte (MapLibre der Seite, Kacheln aus ../map.js); Farbe = Überlaststunden (Median der Seeds).
import { BASEMAP } from "../map.js";
import { colorClass } from "./band.js";

const COLORS = () => {
  const css = getComputedStyle(document.documentElement);
  const v = name => css.getPropertyValue(name).trim();
  return { ok: v("--ok"), warn: v("--warn"), bad: v("--warn"), "no-data": v("--muted") || "#898781", line: v("--line") };
};

export function createStationMap(container, stations, onClick) {
  const gl = globalThis.maplibregl;
  if (!gl) {
    container.textContent = "Map not available (MapLibre not loaded).";
    return { update() {}, select() {}, destroy() {} };
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
        "circle-color": ["match", ["get", "cls"], "ok", c.ok, "warn", c.warn, "bad", c.bad, c["no-data"]],
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
    if (pending) update(pending);
  });
  function update(values) {
    pending = values;
    if (ready) map.getSource("gs-stations").setData(data(id => colorClass(values, id)));
  }
  return {
    update,
    select(id) { if (ready) map.setFilter("gs-selected", ["==", ["get", "id"], id]); },
    destroy() { map.remove(); },
  };
}
