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

// Erster Engpass je Station (Lauf mit Stationsnetzen): Trafo, Leitung, beide oder keiner.
// Farben der Okabe-Ito-Palette (auch bei Farbsehschwäche unterscheidbar); die Legende nennt zusätzlich den Text.
export const BOTTLENECK = {
  "b-trafo": { color: "#0072B2", label: "Transformer first" },
  "b-leitung": { color: "#D55E00", label: "Line first" },
  "b-beide": { color: "#CC79A7", label: "Both at once" },
  "b-keiner": { color: "#009E73", label: "No bottleneck" },
};
const SEVERITY = ["keiner", "trafo", "leitung", "beide"];   // bei Gleichstand gewinnt die schwerere Klasse

// Häufigster ``station_first_load`` je Station über alle bisherigen Seeds; null, wenn kein Seed Leitungswerte hat
// (Lauf ohne Stationsnetze) – dann bleibt die Karte bei der Überlaststunden-Färbung.
export function bottleneckValues(seeds, ids) {
  const rows = seeds.map(s => s.extra?.station_first_load).filter(Array.isArray);
  if (!rows.length) return null;
  const out = new Map();
  ids.forEach((id, i) => {
    const count = {};
    for (const r of rows) if (SEVERITY.includes(r[i])) count[r[i]] = (count[r[i]] ?? 0) + 1;
    const best = Object.keys(count).sort((a, b) => count[b] - count[a] || SEVERITY.indexOf(b) - SEVERITY.indexOf(a))[0];
    if (best) out.set(id, best);
  });
  return out;
}

export function bottleneckClass(values, id) {
  const v = values?.get(id);
  return v ? `b-${v}` : "no-data";
}

// Stationsindizes (Reihenfolge der API = Stationsindex im Modell), an denen die Leitung (mit) zuerst begrenzt
// ``idxs``: Stationsindex je Eintrag von ``ids`` (``idx`` der API, passt zur Eigenschaft ``station`` der Leitungen)
export function lineStations(values, ids, idxs = ids.map((_, i) => i)) {
  return ids.flatMap((id, i) => ["leitung", "beide"].includes(values?.get(id)) ? [idxs[i]] : []);
}

// Die Tagesansicht (/api/stations/{id}/day) rechnet immer mit Trafo-Grenze und ohne Netzspeicher; Hinweis, wenn der
// Lauf (bzw. vor dem ersten Lauf die Auswahl) Leitungsgrenzen oder Netzspeicher nutzt, sonst leer
export const DAY_TRAFO_ONLY = "Day curve shows the transformer limit only, without grid storage.";
export function dayNotice(settings) {
  return settings && (settings.limits === "trafo+leitung" || settings.netzspeicher === true) ? DAY_TRAFO_ONLY : "";
}

// Hinweis, wenn ein Lauf die gewählten Grenzen nicht anwenden konnte (Server ohne Stationsnetze);
// leer, wenn alles galt oder ältere Seeds keine Angabe haben
export function effectiveNotice(seeds, requested) {
  const e = seeds.map(s => s.extra).find(x => x && "limits_effective" in x);
  if (!e) return "";
  const parts = [];
  if (requested.limits === "trafo+leitung" && e.limits_effective !== "trafo+leitung")
    parts.push("No line data on this server – computed with transformer limits only.");
  if (requested.netzspeicher && e.netzspeicher_effective === false)
    parts.push("Grid storage at line bottlenecks was not applied (needs line data).");
  return parts.join(" ");
}

// Zeilen der Kostenanzeige als reine Daten (keine null-Einträge, die ``replaceChildren`` als Text "null" ausgäbe);
// ``hasLineResults``: mindestens ein Seed hat Leitungskennzahlen
export function costItems(c, hasLineResults) {
  return [
    { text: `Home batteries: ${fmt(c.storage_eur / 1e6, 1)} M€ for the median battery need.` },
    { text: c.trafo_eur === null ? "Transformers: enter a cost per size step (no sourced value yet)."
      : `Transformers: ${fmt(c.trafo_eur / 1e6, 1)} M€ (+1 size counts once, +2 or more counts twice).` },
    { text: `Stations above 1000 kVA (new MV connection, not priced): ${fmt(c.trafo_over_1000)}.` },
    { text: c.line_eur !== null ? `Cable reinforcement: ${fmt(c.line_eur / 1e6, 1)} M€ for the median length above rated current (synthetic LV grid, thermal only).`
      : hasLineResults ? "Cable reinforcement: enter a cost per metre (no sourced value yet)."
        : "Cable reinforcement: this run has no line results (no LV grid prepared on the server)." },
    ...(c.netzspeicher_eur !== null ? [{ text: `Grid storage at line bottlenecks: ${fmt(c.netzspeicher_eur / 1e6, 1)} M€ for the median installed capacity.` }] : []),
    ...(c.placeholders.length ? [{ text: `Placeholders without source: ${c.placeholders.join(", ")}`, hint: true }] : []),
  ];
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
