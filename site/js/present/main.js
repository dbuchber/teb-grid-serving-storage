// Präsentation: Folien, Teilschritte, Punkte-Navigation, Tastatur, Auto-play, Hell/Dunkel. Folien-Logik in eigenen Modulen.
import { howSlide } from "./how.js?v=20261025a";
import { playSlide } from "./playmap.js?v=20261025a";
import { batterySlide } from "./battery.js?v=20261025a";

const REDUCE = matchMedia("(prefers-reduced-motion: reduce)").matches;
const AUTO_MS = 6500;  // ohne data-dwell; sonst Sekunden je Teilschritt aus der Folie (Summe ca. 5 min)
const root = document.getElementById("presentation");
const slides = [...root.querySelectorAll(".slide")];
const dots = document.getElementById("dots");
const status = document.getElementById("sr-status");
const autoBtn = document.getElementById("autoplay");

// Folien mit eigener Logik; enter() darf ein Promise liefern, das endet, wenn Auto-play weiter darf
const hooks = new Map([
  [slides.findIndex(s => s.classList.contains("how")), howSlide()],
  [slides.findIndex(s => s.classList.contains("play")), playSlide()],
  [slides.findIndex(s => s.classList.contains("battery")), batterySlide()],
]);

let current = -1, sub = 0, auto = false, timer = null;
const stepsOf = i => Number(slides[i].dataset.steps || 1);
const dwellOf = i => (slides[i].dataset.dwell ? Number(slides[i].dataset.dwell) * 1000 : AUTO_MS);

// ---- Hell/Dunkel ----
const themeBtn = document.getElementById("theme");
function setTheme(t) {
  document.documentElement.dataset.theme = t;
  themeBtn.textContent = t === "dark" ? "Light mode" : "Dark mode";
  themeBtn.setAttribute("aria-pressed", String(t === "light"));
  try { localStorage.setItem("teb-present-theme", t); } catch { /* privater Modus */ }
  for (const h of hooks.values()) h.theme?.(t);
}
let saved = null;
try { saved = localStorage.getItem("teb-present-theme"); } catch { /* privater Modus */ }
setTheme(saved || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"));
themeBtn.addEventListener("click", () => setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark"));

// ---- Punkte ----
slides.forEach((s, i) => {
  const b = document.createElement("button");
  b.type = "button";
  b.setAttribute("aria-label", s.dataset.label);
  b.title = s.dataset.label;
  b.append(document.createElement("span"));
  b.addEventListener("click", () => go(i));
  dots.append(b);
});

function renderSub() {
  const s = slides[current];
  s.dataset.step = sub;
  s.querySelectorAll("[data-at]").forEach(el => {
    const at = Number(el.dataset.at);
    el.classList.toggle("current", at === sub);
    el.classList.toggle("before", at < sub);
    el.classList.toggle("shown", at <= sub);
  });
  // IES-Folie: beteiligte Akteure der aktuellen Phase hervorheben
  const acts = (s.querySelector("[data-acts].current")?.dataset.acts || "").split(" ");
  s.querySelectorAll(".actors li").forEach(li => li.classList.toggle("on", acts.includes(li.dataset.act)));
  const count = s.querySelector(".step-count");
  if (count) count.textContent = `${sub + 1} / ${stepsOf(current)}`;
  hooks.get(current)?.step?.(sub);
  // auf schmalen Bildschirmen den aktuellen Teilschritt sichtbar halten
  if (sub > 0) s.querySelector("[data-at].current")?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  (s.querySelector("h2.cap.current") || s.querySelector("h1, h2"))?.focus({ preventScroll: true });
}

function go(i, back = false) {
  i = Math.max(0, Math.min(slides.length - 1, i));
  if (i === current) return;
  if (current >= 0) {
    slides[current].classList.remove("active");
    slides[current].setAttribute("aria-hidden", "true");
    slides[current].inert = true;
    hooks.get(current)?.leave?.();
  }
  current = i;
  sub = back ? stepsOf(i) - 1 : 0;
  const s = slides[i];
  s.classList.add("active");
  s.removeAttribute("aria-hidden");
  s.inert = false;
  [...dots.children].forEach((d, k) => (k === i ? d.setAttribute("aria-current", "step") : d.removeAttribute("aria-current")));
  status.textContent = `Slide ${i + 1} of ${slides.length}: ${s.dataset.label}`;
  document.title = `${s.dataset.label} · Grid-Serving Storage Steyr`;
  history.replaceState(null, "", `#${i + 1}`);
  const entered = hooks.get(i)?.enter?.({ auto });
  renderSub();
  schedule(entered);
}

function next() {
  if (sub < stepsOf(current) - 1) { sub++; renderSub(); schedule(); }
  else if (current < slides.length - 1) go(current + 1);
  else setAuto(false);
}
function previous() {
  if (sub > 0) { sub--; renderSub(); schedule(); }
  else go(current - 1, true);
}

// ---- Auto-play ----
function schedule(entered) {
  clearTimeout(timer);
  if (!auto) return;
  if (current === slides.length - 1) { setAuto(false); return; }
  if (entered && typeof entered.then === "function") {
    const at = current;
    entered.then(() => { if (auto && current === at) timer = setTimeout(next, dwellOf(at)); });
  } else {
    timer = setTimeout(next, dwellOf(current));
  }
}
function setAuto(on) {
  auto = on;
  autoBtn.setAttribute("aria-checked", String(on));
  if (on && hooks.get(current)?.enter) {
    // laufende Folie mit eigener Logik neu anstoßen, z. B. Woche abspielen
    const entered = hooks.get(current).enter({ auto: true });
    schedule(entered);
  } else schedule();
}
autoBtn.addEventListener("click", e => { e.stopPropagation(); setAuto(!auto); });

// ---- Klick und Tastatur ----
root.addEventListener("click", e => {
  if (e.target.closest("a, button, input, select, label, .play-map, form")) {
    if (e.target.closest(".continue")) next();
    return;
  }
  if (slides[current].classList.contains("tap")) next();
});
window.addEventListener("keydown", e => {
  if (e.target.closest("input, select, textarea, [contenteditable]")) return;
  if (e.key === " " && e.target.closest("button")) return;
  if (["ArrowRight", "ArrowDown", " ", "PageDown"].includes(e.key)) { e.preventDefault(); setAuto(false); next(); }
  if (["ArrowLeft", "ArrowUp", "PageUp"].includes(e.key)) { e.preventDefault(); setAuto(false); previous(); }
  if (e.key === "Home") go(0);
  if (e.key === "End") go(slides.length - 1);
});

slides.forEach(s => { s.setAttribute("aria-hidden", "true"); s.inert = true; });
const start = Number(location.hash.slice(1)) - 1;
go(Number.isInteger(start) && start >= 0 ? start : 0);
if (REDUCE) document.documentElement.classList.add("reduce-motion");
