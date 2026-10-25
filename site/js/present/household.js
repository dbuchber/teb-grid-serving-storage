// Ein Heimspeicher: Förderung, Eigenanteil und Belastung durch Netzabrufe.
// Übernommen aus apps/insight-harbor/src/lib/model.ts (teb-grid-serving-storage); bei Änderungen beide anpassen.

export const EAG_2026 = { perKwh: 150, maxKwh: 50, euBonus: 0.3 };
export const TIER_SHARE = [0.4, 0.6, 0.8, 1.0];

export const FLEX_DEFAULTS = {
  spotCharge: 8, spotPeak: 18, supplierMargin: 1.5, gridFee: 7, levies: 2.5, vat: 0.2,
  batteryKwh: 10, gridShare: 0.326, efficiency: 0.9, batteryCostPerKwh: 650, cycleLife: 6000,
  dsoFeeYear: 50, eventsPerYear: 20, opportunityCost: 0,
};

export const HOUSEHOLD_DEFAULTS = { scheme: "eag2026", tier: 2, newPv: true, madeInEurope: false, boxCost: 600, years: 15 };

// Bruttopreis ct/kWh bei dynamischem Tarif
const retail = (f, spot) => (spot + f.supplierMargin + f.gridFee + f.levies) * (1 + f.vat);

export function batterySubsidy({ scheme, tier, newPv, madeInEurope, batteryKwh, batteryCost, boxCost }) {
  if (scheme === "eag2026") {
    const battery = newPv ? Math.min(batteryKwh, EAG_2026.maxKwh) * EAG_2026.perKwh * (madeInEurope ? 1 + EAG_2026.euBonus : 1) : 0;
    return { battery: Math.min(battery, batteryCost), box: 0, total: Math.min(battery, batteryCost) };
  }
  const battery = Math.min((TIER_SHARE[tier] ?? 0) * batteryCost, batteryCost);
  const box = tier >= 1 ? boxCost : 0;
  return { battery, box, total: battery + box };
}

// Ein Abruf: Abendspitze aus dem Speicher statt aus dem Netz, nachts nachgeladen; Garantie: nie schlechter gestellt
export function flexEvent(f) {
  const deliveredKwh = f.batteryKwh * f.gridShare;
  const chargedKwh = deliveredKwh / f.efficiency;
  const arbitrage = (deliveredKwh * retail(f, f.spotPeak) - chargedKwh * retail(f, f.spotCharge)) / 100;
  const degradation = chargedKwh * (f.batteryCostPerKwh / (f.cycleLife * f.efficiency));
  const fee = f.eventsPerYear > 0 ? f.dsoFeeYear / f.eventsPerYear : 0;
  const net = fee + arbitrage - degradation - f.opportunityCost;
  return { deliveredKwh, chargedKwh, degradation, net, final: Math.max(net, 0) };
}

export function householdBattery(f, h) {
  const batteryCost = f.batteryKwh * f.batteryCostPerKwh;
  const subsidy = batterySubsidy({ ...h, batteryKwh: f.batteryKwh, batteryCost });
  // gestuftes Modell: Entladeabrufe im Winter erst ab Stufe 2 (in beide Richtungen steuerbar)
  const callsYear = h.scheme === "tiered" && h.tier < 2 ? 0 : f.eventsPerYear;
  const e = flexEvent(f);
  const extraCyclesYear = (callsYear * e.chargedKwh) / f.batteryKwh;
  return {
    batteryCost, boxCost: h.boxCost, subsidy, ownCost: batteryCost + h.boxCost - subsidy.total,
    callsYear, extraCyclesYear, lifeShare: (extraCyclesYear * h.years) / f.cycleLife,
    wearYear: callsYear * e.degradation, gridIncomeYear: callsYear * e.final,
  };
}
