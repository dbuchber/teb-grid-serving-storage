// Abspielwoche: Auslastung je Trafo (Prozent der Nennleistung) aus gridsim.playback, ohne DOM.

// Auslastung → Farbe und Beschriftung; obere Grenze inklusive
export const LOAD_STEPS = [
  { max: 80, color: "#7f8a86", label: "up to 80 %" },
  { max: 100, color: "#e7c440", label: "80–100 %" },
  { max: 130, color: "#e08a3c", label: "over 100 %: overloaded" },
  { max: Infinity, color: "#e5534b", label: "over 130 %" },
];

// Winter zählt Bezug, Sommer Rückspeisung (negativer Fluss) jeweils als positive Last
export const loadOf = (pct, season) => (season === "summer" ? -pct : pct);
export const stepOf = load => LOAD_STEPS.find(s => load <= s.max);

export function overloadedAt(week, h, season) {
  let n = 0;
  for (const s of week.pct) if (loadOf(s[h], season) > 100) n++;
  return n;
}

export function everOverloaded(week, h, season) {
  let n = 0;
  for (const s of week.pct) {
    for (let i = 0; i <= h; i++) if (loadOf(s[i], season) > 100) { n++; break; }
  }
  return n;
}

const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function hourLabel(start, h) {
  const d = new Date(`${start}T00:00:00Z`);
  d.setUTCHours(h);
  return `${DAYS[d.getUTCDay()]} ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]}, ${String(d.getUTCHours()).padStart(2, "0")}:00`;
}

export function fileFor(o) {
  return o.season === "winter"
    ? `winter_${o.year}_${o.scenario}_${o.charging}.json`
    : `summer_${o.year}_heute_${o.pv}_${o.storage}.json`;
}
