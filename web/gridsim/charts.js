// SVG-Diagramme des Dashboards (handgeschrieben, Farben über CSS-Klassen aus dashboard.css).
import { bandOf, fmt, linear, niceMax } from "./band.js";

const NS = "http://www.w3.org/2000/svg";

export function el(tag, attrs = {}, ...children) {
  const node = tag.startsWith("svg:") ? document.createElementNS(NS, tag.slice(4)) : document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined) node.append(c);
  return node;
}

const svg = (w, h, cls) => el("svg:svg", { viewBox: `0 0 ${w} ${h}`, class: cls, role: "img", preserveAspectRatio: "xMidYMid meet" });

export const TILES = [
  { key: "stations_load_congestion", label: "Transformers overloaded (demand)", unit: n => (n ? `of ${n}` : "stations"), digits: 0 },
  { key: "congestion_h_median", label: "Overload hours per year", unit: "median station", digits: 0 },
  { key: "e_net_mwh", label: "Energy above limit", unit: "MWh, sum of largest events", digits: 1 },
  { key: "storage_units", label: "Home batteries needed", unit: "10 kWh / 5 kW units", digits: 0 },
  { key: "trafo_plus1", label: "Transformer +1 size", unit: "stations", digits: 0 },
  { key: "trafo_plus2", label: "Transformer +2 sizes or more", unit: "stations", digits: 0 },
  { key: "trafo_over_1000", label: "Above 1000 kVA", unit: "needs new MV connection", digits: 0 },
  { key: "ev_unmet_mwh", label: "EV energy not charged by 7 am", unit: "MWh per year", digits: 1 },
  // Leitungskennzahlen: nur sichtbar, wenn der Lauf Stationsnetze hatte (sonst None → keine Werte)
  { key: "stations_line_load_congestion", label: "Lines overloaded (demand)", unit: "stations, synthetic LV grid", digits: 0, optional: true },
  { key: "stations_line_only", label: "Line limits before transformer", unit: "stations", digits: 0, optional: true },
  { key: "line_over_m", label: "Line length above rated current", unit: "m, thermal only", digits: 0, optional: true },
  { key: "netzspeicher_kwh", label: "Grid storage at line bottlenecks", unit: "kWh installed", digits: 0, optional: true },
];

// Stationszahl des Laufs (region.n_stations der Seeds), null vor dem ersten Seed
const stationCount = seeds => seeds.find(s => typeof s.region?.n_stations === "number")?.region.n_stations ?? null;
export const tileUnit = (t, seeds) => (typeof t.unit === "function" ? t.unit(stationCount(seeds)) : t.unit);
export const regionTitle = n => `Regional simulation: all ${n ? `${n} ` : ""}transformers in the Steyr area`;

// Kacheln, die zu den Seeds passen: optionale (Leitungs-)Kacheln nur, wenn mindestens ein Seed einen Wert liefert
export const visibleTiles = seeds => TILES.filter(t => !t.optional || seeds.some(s => typeof s.region[t.key] === "number"));

export function renderTiles(root, seeds, nTotal) {
  root.replaceChildren(...visibleTiles(seeds).map(t => {
    const b = bandOf(seeds, t.key);
    const range = b.n > 1 ? `${fmt(b.p10, t.digits)}–${fmt(b.p90, t.digits)}` : "";
    return el("div", { class: "gs-tile" },
      el("div", { class: "gs-tile-label", text: t.label }),
      el("div", { class: "gs-tile-value", text: b.n ? fmt(b.median, t.digits) : "–" }),
      el("div", { class: "gs-tile-unit", text: `${tileUnit(t, seeds)}${range ? ` · band ${range}` : ""}` }));
  }), el("div", { class: "gs-tile-foot", text: `Median and 10–90 % band over ${seeds.length} of ${nTotal} random seeds · model values` }));
}

// Streifen je Seed: jeder Punkt ist ein Zufallslauf, das Band wächst mit jedem fertigen Seed
export function renderStrip(root, seeds, key, label, digits = 1) {
  const W = 640, H = 70, pad = 24;
  const vals = seeds.map(s => s.region[key]);
  const max = niceMax(Math.max(1e-9, ...vals));
  const x = linear([0, max], [pad, W - pad]);
  const s = svg(W, H, "gs-strip");
  const b = bandOf(seeds, key);
  s.append(el("svg:line", { x1: pad, x2: W - pad, y1: 40, y2: 40, class: "gs-axis" }));
  if (b.n > 1) s.append(el("svg:rect", { x: x(b.p10), y: 28, width: Math.max(1, x(b.p90) - x(b.p10)), height: 24, class: "gs-band" }));
  vals.forEach((v, i) => s.append(el("svg:circle", { cx: x(v), cy: 40 + ((i % 5) - 2) * 3, r: 3, class: "gs-dot" })));
  if (b.n) s.append(el("svg:line", { x1: x(b.median), x2: x(b.median), y1: 22, y2: 58, class: "gs-median" }));
  [0, max / 2, max].forEach(t => s.append(el("svg:text", { x: x(t), y: 68, class: "gs-tick", "text-anchor": "middle", text: fmt(t, digits) })));
  s.append(el("svg:text", { x: pad, y: 14, class: "gs-label", text: `${label}: median ${fmt(b.median, digits)}${b.n > 1 ? `, band ${fmt(b.p10, digits)}–${fmt(b.p90, digits)}` : ""}` }));
  root.replaceChildren(s);
}

// Vergleich: je Wert der gewählten Dimension Median mit Band
export function renderCompare(root, rows, label, digits = 0) {
  const W = 640, rowH = 34, pad = 150, H = rows.length * rowH + 30;
  const max = niceMax(Math.max(1e-9, ...rows.flatMap(r => r.band ? [r.band.p90, r.band.median] : [0])));
  const x = linear([0, max], [pad, W - 20]);
  const s = svg(W, H, "gs-compare");
  rows.forEach((r, i) => {
    const y = 20 + i * rowH;
    s.append(el("svg:text", { x: pad - 8, y: y + 14, class: "gs-label", "text-anchor": "end", text: r.label }));
    if (!r.band) { s.append(el("svg:text", { x: pad, y: y + 14, class: "gs-tick", text: r.pending ? "running…" : r.note ?? "not run yet" })); return; }
    s.append(el("svg:rect", { x: pad, y: y + 4, width: Math.max(1, x(r.band.median) - pad), height: 14, class: "gs-bar" }));
    s.append(el("svg:line", { x1: x(r.band.p10), x2: x(r.band.p90), y1: y + 11, y2: y + 11, class: "gs-whisker" }));
    s.append(el("svg:text", { x: x(Math.max(r.band.p90, r.band.median)) + 6, y: y + 15, class: "gs-tick", text: `${fmt(r.band.median, digits)} (${r.band.n})` }));
  });
  s.append(el("svg:text", { x: pad, y: H - 4, class: "gs-tick", text: `${label} · median, whisker = 10–90 % band, (n seeds)` }));
  root.replaceChildren(s);
}

const LAYERS = [
  { key: "household_kw", label: "Households", cls: "gs-a-household" },
  { key: "heat_pump_kw", label: "Heat pumps", cls: "gs-a-heat" },
  { key: "ev_kw", label: "EV charging", cls: "gs-a-ev" },
];

// Tageskurve 15 min: gestapelte Lasten, PV/Speicher/V2G als Entlastung, Trafo-Fluss und Grenze
export function renderDay(root, c) {
  const W = 640, H = 260, L = 46, R = 12, T = 16, B = 34;
  const n = c.trafo_kw.length;
  const stack = c.trafo_kw.map((_, i) => LAYERS.reduce((a, l) => a + c[l.key][i], 0));
  const relief = c.trafo_kw.map((_, i) => c.pv_kw[i] + Math.max(c.storage_kw[i], 0) + c.v2g_kw[i]);
  const top = niceMax(Math.max(c.kva * 1.1, ...stack, ...c.trafo_kw));
  const maxRelief = Math.max(0, ...relief);
  const bottom = maxRelief > 0.05 * top ? -niceMax(maxRelief) : 0;  // kaum PV (Winter): keine negative Achse
  const x = linear([0, n - 1], [L, W - R]), y = linear([bottom, top], [H - B, T]);
  const s = svg(W, H, "gs-day");
  const area = (lo, hi, cls) => {
    const pts = hi.map((v, i) => `${x(i)},${y(v)}`).concat(lo.map((v, i) => `${x(i)},${y(v)}`).reverse());
    s.append(el("svg:polygon", { points: pts.join(" "), class: cls }));
  };
  let base = new Array(n).fill(0);
  for (const l of LAYERS) {
    const next = base.map((b, i) => b + c[l.key][i]);
    area(base, next, l.cls);
    base = next;
  }
  area(new Array(n).fill(0), relief.map(v => -v), "gs-a-pv");
  s.append(el("svg:polyline", { points: c.trafo_kw.map((v, i) => `${x(i)},${y(v)}`).join(" "), class: "gs-trafo" }));
  s.append(el("svg:line", { x1: L, x2: W - R, y1: y(c.kva), y2: y(c.kva), class: "gs-limit" }));
  s.append(el("svg:text", { x: W - R, y: y(c.kva) - 4, "text-anchor": "end", class: "gs-tick", text: `Transformer limit ${fmt(c.kva)} kVA` }));
  s.append(el("svg:line", { x1: L, x2: W - R, y1: y(0), y2: y(0), class: "gs-axis" }));
  [0, 6, 12, 18, 24].forEach(h => s.append(el("svg:text", { x: x(Math.min(h * 4, n - 1)), y: H - 18, "text-anchor": "middle", class: "gs-tick", text: `${h}:00` })));
  [...new Set([bottom, 0, top / 2, top])].forEach(v => s.append(el("svg:text", { x: L - 6, y: y(v) + 4, "text-anchor": "end", class: "gs-tick", text: fmt(v) })));
  s.append(el("svg:text", { x: 4, y: T - 4, class: "gs-tick", text: "kW" }));
  const legend = el("div", { class: "gs-legend" },
    ...LAYERS.map(l => el("span", { class: `gs-key ${l.cls}`, text: l.label })),
    el("span", { class: "gs-key gs-a-pv", text: "PV, battery, V2G (relief)" }),
    el("span", { class: "gs-key gs-k-trafo", text: "Transformer load" }));
  root.replaceChildren(s, legend);
}
