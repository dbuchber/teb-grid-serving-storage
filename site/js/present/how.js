// Folie „How the tool computes“: Szenen 2–4 aus echten Daten einer Beispielstation (Woche 2023, Stressfall, ungesteuert).
import { stations, week } from "./data.js?v=20261025a";

const NS = "http://www.w3.org/2000/svg";
const EXAMPLE_FILE = "winter_2023_2040_uncontrolled.json";

function el(name, attrs, parent) {
  const e = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  parent?.append(e);
  return e;
}

// Beispiel: deutlich, aber nicht extrem überlastet, mit einer sichtbaren Zahl Häuser
function pickExample(w, props) {
  const rows = w.stations.map((id, i) => ({ id, i, max: Math.max(...w.pct[i]), p: props.get(id) }))
    .filter(r => r.p && r.max > 115 && r.max < 170 && r.p.haushalte >= 30 && r.p.haushalte <= 90 && !r.p.synthetisch);
  rows.sort((a, b) => b.p.haushalte - a.p.haushalte);
  return rows[0];
}

function drawTrafo(ex, w) {
  const kva = w.kva[ex.i], peak = Math.round(ex.max * kva / 100);
  const g = document.getElementById("how-houses");
  const n = Math.min(ex.p.wohngebaeude || ex.p.haushalte, 72), cols = 9;
  for (let k = 0; k < n; k++) {
    const x = 40 + (k % cols) * 30, y = 40 + Math.floor(k / cols) * 24;
    el("line", { x1: x + 8, y1: y + 8, x2: 352, y2: 130, class: "wire" }, g);
    el("path", { d: `M${x} ${y + 8}l8-7 8 7v8h-16z`, class: "mini-house", style: `--d:${k}` }, g);
  }
  // Balken: 190 px = 1,15 × max(Spitze, Nennleistung)
  const top = 40, h = 190, scale = h / (1.15 * Math.max(peak, kva));
  const fill = document.querySelector("#how-trafo-svg .bar-fill");
  fill.style.setProperty("--h", (peak * scale / h).toFixed(3));
  const yr = top + h - kva * scale;
  const line = document.querySelector("#how-trafo-svg .rating");
  line.setAttribute("y1", yr); line.setAttribute("y2", yr);
  const rt = document.getElementById("how-rating");
  rt.setAttribute("y", yr + 5);
  rt.textContent = `rating ${kva} kVA`;
  document.getElementById("how-peak").textContent = `${peak} kW`;
  document.getElementById("how-trafo-note").textContent =
    `A real example: a transformer with ${ex.p.haushalte} households, peak hour of a winter week in 2040 (stress case).`;
}

function drawWeek(ex, w) {
  const g = document.getElementById("how-week");
  const s = w.pct[ex.i], W = 560, H = 200, x0 = 30, y0 = 20;
  const max = Math.max(...s, 110) * 1.05, min = Math.min(0, ...s);
  const X = h => x0 + h * W / 167, Y = v => y0 + H - (v - min) / (max - min) * H;
  // Stunden über der Nennleistung als Flächen
  let d = "";
  for (let h = 0; h < 168; h++) if (s[h] > 100) d += `M${X(h - .5)} ${Y(100)}V${Y(s[h])}H${X(h + .5)}V${Y(100)}z`;
  el("path", { d, class: "over-area" }, g);
  const path = el("path", { d: s.map((v, h) => `${h ? "L" : "M"}${X(h).toFixed(1)} ${Y(v).toFixed(1)}`).join(""), class: "week-line" }, g);
  path.style.setProperty("--len", Math.ceil(path.getTotalLength?.() || 3000));
  el("line", { x1: x0, x2: x0 + W, y1: Y(100), y2: Y(100), class: "rating" }, g);
  el("text", { x: x0 + W, y: Y(100) - 6, "text-anchor": "end", class: "axis" }, g).textContent = "rating";
  ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].forEach((day, k) =>
    (el("text", { x: X(k * 24 + 12), y: y0 + H + 18, "text-anchor": "middle", class: "axis" }, g).textContent = day));
  const hours = s.filter(v => v > 100).length;
  document.getElementById("how-week-note").textContent =
    `The same transformer for one week (${hours} of 168 hours above its rating), out of 8,760 hours a year. ` +
    "Real weather from three years: 2012 (cold spell), 2017 and 2023 (mild).";
}

// 20 Ziehungen: Anteil 70 % Wärmepumpe, 60 % E-Auto, je Ziehung neu verteilt (nur Illustration, deterministisch)
function drawDraws() {
  const box = document.getElementById("how-draws");
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let k = 0; k < 20; k++) {
    const d = document.createElement("div");
    d.className = "draw";
    d.style.setProperty("--d", k);
    for (let j = 0; j < 24; j++) {
      const i = document.createElement("i"), hp = rnd() < .7, ev = rnd() < .6;
      i.className = hp && ev ? "both" : hp ? "hp" : ev ? "ev" : "";
      d.append(i);
    }
    box.append(d);
  }
}

export function howSlide() {
  let ready = null;
  function init() {
    ready ??= Promise.all([week(EXAMPLE_FILE), stations()]).then(([w, st]) => {
      const props = new Map(st.features.map(f => [f.properties.id, f.properties]));
      const ex = pickExample(w, props);
      if (ex) { drawTrafo(ex, w); drawWeek(ex, w); }
      drawDraws();
    }).catch(e => console.error("how:", e));
    return ready;
  }
  return { enter: () => { init(); } };
}
