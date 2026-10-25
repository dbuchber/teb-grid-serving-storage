// Folie „My battery“: Förderung, Eigenanteil und Belastung durch Netzabrufe für einen Heimspeicher.
import { FLEX_DEFAULTS, HOUSEHOLD_DEFAULTS, TIER_SHARE, flexEvent, householdBattery } from "./household.js?v=20261025a";

const TIERS = [
  ["Level 0", "no control"],
  ["Level 1", "grid operator may slow charging"],
  ["Level 2", "may also ask it to discharge"],
  ["Level 3", "level 2 plus paid discharge"],
];
const HINT = {
  eag2026: "Federal investment grant 2026 (Renewable Expansion Act, EAG): €150 per kWh, only together with new or extended solar, " +
           "up to 50 kWh. Adding a battery to an existing solar system gets nothing today; the Upper Austria grant ended on 1 July 2026.",
  tiered: "Our proposal: the more control the household allows, the larger the share of the battery price is paid, and the box is paid " +
          "from level 1. Discharge calls in winter need level 2.",
};

const $ = id => document.getElementById(id);
const eur = v => `€${Math.round(v).toLocaleString("en-GB")}`;

export function batterySlide() {
  const h = { ...HOUSEHOLD_DEFAULTS };
  let wired = false;

  function render() {
    const f = { ...FLEX_DEFAULTS, batteryKwh: Number($("bat-kwh").value), batteryCostPerKwh: Number($("bat-price").value),
                eventsPerYear: Number($("bat-calls").value) };
    h.newPv = $("bat-newpv").checked;
    h.madeInEurope = $("bat-eu").checked;
    const r = householdBattery(f, h), total = r.batteryCost + r.boxCost;
    $("o-kwh").textContent = `${f.batteryKwh} kWh`;
    $("o-price").textContent = `${eur(f.batteryCostPerKwh)}`;
    $("o-calls").textContent = String(f.eventsPerYear);
    $("bat-scheme").querySelectorAll("button").forEach(b => b.setAttribute("aria-checked", String(b.dataset.v === h.scheme)));
    $("bat-scheme-hint").textContent = HINT[h.scheme];
    $("bat-eag").hidden = h.scheme !== "eag2026";
    $("bat-tiered").hidden = h.scheme !== "tiered";
    $("bat-tier").querySelectorAll("button").forEach(b => b.setAttribute("aria-checked", String(Number(b.dataset.v) === h.tier)));
    $("bar-sub").style.flexBasis = `${(100 * r.subsidy.total / total).toFixed(1)}%`;
    $("bar-own").style.flexBasis = `${(100 * r.ownCost / total).toFixed(1)}%`;
    $("k-sub").textContent = eur(r.subsidy.total);
    $("k-own").textContent = eur(r.ownCost);
    $("k-total").textContent = eur(total);
    $("k-cycles").textContent = r.extraCyclesYear.toFixed(1);
    $("k-life").textContent = `${(100 * r.lifeShare).toFixed(1)} %`;
    $("k-income").textContent = eur(r.gridIncomeYear);
    $("life-fill").style.width = `${Math.min(100, 100 * r.lifeShare)}%`;
    const e = flexEvent(f);
    $("bat-note").textContent = r.callsYear === 0
      ? "At this level the grid operator may only slow charging, so there are no discharge calls and no extra wear."
      : `One call takes about ${e.deliveredKwh.toFixed(1)} kWh from the battery in the evening; it is recharged at night. ` +
        `A battery lasts about ${FLEX_DEFAULTS.cycleLife.toLocaleString("en-GB")} full cycles. Each call is paid so the household never ` +
        `loses money: the wear of about €${e.degradation.toFixed(2)} per call and the charging cost are covered. The box costs ${eur(h.boxCost)}.`;
  }

  function wire() {
    $("bat-tier").innerHTML = TIERS.map(([t, d], i) =>
      `<button type="button" role="radio" data-v="${i}"><b>${t} · ${Math.round(TIER_SHARE[i] * 100)} %</b>${d}</button>`).join("");
    $("bat-scheme").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { h.scheme = b.dataset.v; render(); } });
    $("bat-tier").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { h.tier = Number(b.dataset.v); render(); } });
    $("bat-form").addEventListener("input", render);
    $("bat-form").addEventListener("submit", e => e.preventDefault());
  }

  return { enter() { if (!wired) { wire(); wired = true; } render(); } };
}
