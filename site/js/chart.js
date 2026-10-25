// Kleine SVG-Diagramme ohne Fremdbibliothek: Linien (Zeitreihen) und gruppierte Balken.
// Farben kommen aus den CSS-Variablen der Seite, damit Hell/Dunkel stimmt.

const NS = "http://www.w3.org/2000/svg";

function el(name, attrs = {}, parent) {
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (parent) parent.appendChild(e);
  return e;
}

const fmt = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

// Runde Achsenteilung (1, 2, 2,5, 5 × 10^k) für Minimum und Maximum, damit keine krummen Zahlen entstehen
function niceScale(min, max, n = 5) {
  if (max <= min) max = min + 1;
  const raw = (max - min) / n, p = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map(f => f * p).find(s => s >= raw);
  const lo = Math.floor(min / step) * step, hi = Math.ceil(max / step) * step;
  const ticks = [];
  for (let v = lo; v <= hi + step / 2; v += step) ticks.push(Math.round(v * 1e6) / 1e6);
  return { lo, hi, ticks };
}

// series: [{name, values: [number], color}], x: Beschriftungen (gleich lang wie values)
// opts: {height, width, unit, limit: {value, label}, xTicks}; series: {…, width, dash, opacity}
export function lineChart(container, x, series, opts = {}) {
  const W = opts.width || 720, H = opts.height || 260, m = { l: 52, r: 12, t: 28, b: 28 };
  container.replaceChildren();
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img" }, container);
  if (opts.title) el("title", {}, svg).textContent = opts.title;
  const all = series.flatMap(s => s.values).concat(opts.limit ? [opts.limit.value] : []);
  const { lo: ymin, hi: ymax, ticks } = niceScale(Math.min(0, ...all), Math.max(...all));
  const sx = i => m.l + (i / Math.max(x.length - 1, 1)) * (W - m.l - m.r);
  const sy = v => H - m.b - ((v - ymin) / (ymax - ymin)) * (H - m.t - m.b);
  const g = el("g", { class: "axis" }, svg);
  for (const v of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: sy(v), y2: sy(v), class: v === 0 ? "grid zero" : "grid" }, g);
    el("text", { x: m.l - 6, y: sy(v) + 4, "text-anchor": "end" }, g).textContent = fmt.format(v);
  }
  const step = opts.xTicks || Math.ceil(x.length / 8);
  x.forEach((lab, i) => {
    if (i % step === 0) el("text", { x: sx(i), y: H - 8, "text-anchor": "middle" }, g).textContent = lab;
  });
  if (opts.unit) el("text", { x: 4, y: 14, class: "unit" }, g).textContent = opts.unit;
  if (opts.limit) {
    const y = sy(opts.limit.value);
    el("line", { x1: m.l, x2: W - m.r, y1: y, y2: y, class: "limit" }, svg);
    el("text", { x: W - m.r, y: y - 5, "text-anchor": "end", class: "limit-label" }, svg).textContent = opts.limit.label;
  }
  for (const s of series) {
    const d = s.values.map((v, i) => `${i ? "L" : "M"}${sx(i).toFixed(1)},${sy(v).toFixed(1)}`).join("");
    el("path", { d, fill: "none", stroke: s.color, "stroke-width": s.width || 2, "stroke-dasharray": s.dash || "",
                 "stroke-opacity": s.opacity ?? 1, "stroke-linejoin": "round" }, svg);
  }
  legend(container, series);
}

// groups: [{label, values: [number]}], names: Name je Wert, colors: Farbe je Wert
export function barChart(container, groups, names, colors, opts = {}) {
  const W = opts.width || 720, H = opts.height || 240, m = { l: 52, r: 12, t: 12, b: 40 };
  container.replaceChildren();
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, class: "chart", role: "img" }, container);
  if (opts.title) el("title", {}, svg).textContent = opts.title;
  const vals = groups.flatMap(gr => gr.values);
  const { lo: ymin, hi: ymax, ticks } = niceScale(Math.min(0, ...vals), Math.max(...vals));
  const sy = v => H - m.b - ((v - ymin) / (ymax - ymin)) * (H - m.t - m.b);
  const gw = (W - m.l - m.r) / groups.length, bw = Math.min(28, (gw * 0.8) / names.length);
  const g = el("g", { class: "axis" }, svg);
  for (const v of ticks) {
    el("line", { x1: m.l, x2: W - m.r, y1: sy(v), y2: sy(v), class: "grid" }, g);
    el("text", { x: m.l - 6, y: sy(v) + 4, "text-anchor": "end" }, g).textContent = fmt.format(v) + (opts.suffix || "");
  }
  groups.forEach((gr, i) => {
    const x0 = m.l + i * gw + (gw - bw * names.length) / 2;
    gr.values.forEach((v, j) => {
      const y = Math.min(sy(v), sy(0)), h = Math.abs(sy(v) - sy(0));
      const r = el("rect", { x: x0 + j * bw, y, width: bw - 2, height: Math.max(h, 1), fill: colors[j], rx: 2 }, svg);
      el("title", {}, r).textContent = `${gr.label} · ${names[j]}: ${fmt.format(v)}${opts.suffix || ""}`;
    });
    el("text", { x: m.l + i * gw + gw / 2, y: H - 22, "text-anchor": "middle" }, g).textContent = gr.label;
  });
  legend(container, names.map((name, j) => ({ name, color: colors[j] })));
}

function legend(container, items) {
  const ul = document.createElement("ul");
  ul.className = "legend";
  for (const s of items) {
    const li = document.createElement("li");
    const sw = document.createElement("span");
    sw.className = "swatch";
    sw.style.background = s.color;
    if (s.dash) { sw.className += " dashed"; sw.style.borderTopColor = s.color; }
    li.append(sw, s.name);
    ul.appendChild(li);
  }
  container.appendChild(ul);
}
