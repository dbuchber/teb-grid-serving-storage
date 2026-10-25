// Reine Rechenfunktionen für das Dashboard: Quantile über Seeds, Werte je Station, Farbklassen, Skalen.

export function quantile(values, q) {
  // lineare Interpolation wie numpy.percentile (Standard)
  const v = [...values].sort((a, b) => a - b);
  if (!v.length) return NaN;
  const pos = (v.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return v[lo] + (v[hi] - v[lo]) * (pos - lo);
}

export function bandOf(seeds, key) {
  const vals = seeds.map(s => s.region[key]).filter(x => typeof x === "number");
  return { median: quantile(vals, 0.5), p10: quantile(vals, 0.1), p90: quantile(vals, 0.9), n: vals.length };
}

// Median je Station über alle Seeds; ``ids`` = Stationsreihenfolge der API
export function stationValues(seeds, ids, field) {
  const out = new Map();
  if (!seeds.length) return out;
  ids.forEach((id, i) => out.set(id, quantile(seeds.map(s => s[field][i]), 0.5)));
  return out;
}

export const CONGESTION_BAD_H = 100;

export function colorClass(values, id) {
  const v = values.get(id);
  if (v === undefined || Number.isNaN(v)) return "no-data";
  if (v <= 0) return "ok";
  return v < CONGESTION_BAD_H ? "warn" : "bad";
}

export function linear([d0, d1], [r0, r1]) {
  const span = d1 - d0 || 1;
  return x => r0 + (x - d0) / span * (r1 - r0);
}

export function niceMax(x) {
  if (!(x > 0)) return 1;
  const p = 10 ** Math.floor(Math.log10(x)), m = x / p;
  return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 5 ? 5 : 10) * p;
}

export function fmt(x, digits = 0) {
  if (x === null || x === undefined || Number.isNaN(x)) return "–";
  return x.toLocaleString("en-GB", { maximumFractionDigits: digits, minimumFractionDigits: 0 });
}
