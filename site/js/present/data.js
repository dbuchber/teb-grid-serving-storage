// Gemeinsamer Abruf der Daten für die Präsentation, je Datei nur einmal.
const cache = new Map();

export function json(path) {
  if (!cache.has(path)) {
    cache.set(path, fetch(path).then(r => {
      if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
      return r.json();
    }).catch(e => { cache.delete(path); throw e; }));
  }
  return cache.get(path);
}

export const stations = () => json("data/stations.geojson");
export const week = file => json(`data/playback/${file}`);
