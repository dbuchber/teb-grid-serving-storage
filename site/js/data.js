// Laden der vorab berechneten Dateien aus data/ und Zuordnung der Geräte zu Ortsnetzstationen.

async function json(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}

// NS-Leitungen (4,9 MB) und Hausanschlüsse (2,9 MB) erst nach dem ersten Bild nachladen; beide optional
export async function loadLv() {
  const [lvLines, lvHouse] = await Promise.all([
    json("data/lv_lines.geojson").catch(() => null), json("data/lv_hausanschluesse.geojson").catch(() => null)]);
  return { lvLines, lvHouse };
}

export async function loadAll() {
  const [stations, uw, meta, tsIndex, pv, devices, nodes] = await Promise.all([
    json("data/stations.geojson"), json("data/uw.geojson"), json("data/meta.json"),
    json("data/timeseries/index.json"), json("data/pv_storage.geojson"), json("data/devices.json"),
    json("data/building_station.json"),
  ]);
  // Stundenwerte der V2G-Fälle; fehlen sie, bleiben die PNG-Abbildungen stehen
  const v2gCases = await json("data/v2g_cases.json").catch(() => null);
  // MS-Trassen entlang der Straßen; fehlen sie, schematisch als Gerade UW -> Station
  const mvRoads = await json("data/mv_lines.geojson").catch(() => null);
  const timeseries = Object.fromEntries(await Promise.all(
    tsIndex.map(async t => [t.id, { ...(await json(`data/${t.datei}`)), rolle: t.rolle }])));
  assignSegments(pv, devices, nodes);
  const byId = new Map(stations.features.map(f => [f.properties.id, f]));
  const devicesBySegment = new Map();
  for (const d of devices.devices) {
    if (!d.segment_id) continue;
    if (!devicesBySegment.has(d.segment_id)) devicesBySegment.set(d.segment_id, []);
    devicesBySegment.get(d.segment_id).push(d);
  }
  return { stations, uw, meta, timeseries, pv, devices, byId, devicesBySegment, lvLines: null, lvHouse: null, v2gCases, mvLines: mvRoads || mvSchematic(stations, uw) };
}

// Rueckfall, solange pv_storage/devices noch keine segment_id tragen: dieselbe Regel wie die
// Simulation, angenaehert ueber den naechsten Knoten aus building_station.json (Raster ~550 m).
function assignSegments(pv, devices, nodes) {
  const cols = Object.fromEntries(nodes.spalten.map((c, i) => [c, i]));
  const CELL = 0.005, grid = new Map();
  const key = (lon, lat) => `${Math.floor(lon / CELL)},${Math.floor(lat / CELL)}`;
  for (const n of nodes.knoten) {
    const k = key(n[cols.lon], n[cols.lat]);
    if (!grid.has(k)) grid.set(k, []);
    grid.get(k).push(n);
  }
  const kx = 111.32 * Math.cos(48.05 * Math.PI / 180), ky = 111.32;  // km je Grad
  function nearest(lon, lat) {
    const cx = Math.floor(lon / CELL), cy = Math.floor(lat / CELL);
    let best = null, bd = 0.6;  // km
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
      for (const n of grid.get(`${cx + dx},${cy + dy}`) || []) {
        const d = Math.hypot((n[cols.lon] - lon) * kx, (n[cols.lat] - lat) * ky);
        if (d < bd) { bd = d; best = n; }
      }
    }
    return best ? best[cols.station] : null;
  }
  const segOfBuilding = new Map();
  for (const f of pv.features) {
    const p = f.properties;
    if (!p.segment_id) p.segment_id = nearest(...f.geometry.coordinates);
    segOfBuilding.set(p.id, p.segment_id);
  }
  for (const d of devices.devices) {
    if (!d.segment_id) d.segment_id = segOfBuilding.get(d.building_id) || null;
  }
}

export function engpassKey(s) {
  return `${s.wetterjahr}|${s.szenario}|${s.pv}|${s.richtung}`;
}

// Mittelspannung wird nicht simuliert: schematische Verbindung jeder Station zu ihrem Umspannwerk.
function mvSchematic(stations, uw) {
  const at = new Map(uw.features.map(f => [f.properties.name, f.geometry.coordinates]));
  return { type: "FeatureCollection", features: stations.features.filter(f => at.has(f.properties.uw)).map(f => ({
    type: "Feature", properties: { station: f.properties.id, uw: f.properties.uw },
    geometry: { type: "LineString", coordinates: [at.get(f.properties.uw), f.geometry.coordinates] },
  })) };
}
