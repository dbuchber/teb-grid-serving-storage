// Financial model: who pays to keep Steyr's 257 transformer stations within limits
// in winter (heat pumps + EVs), 2026 → 2040. Pure functions, no UI.

export type WeatherYear = "2023" | "2017" | "2012";

// ---------------------------------------------------------------------------
// Battery subsidy. "eag2026" = federal EAG investment grant as of October 2026; "tiered" = our proposal
// (subsidy rises with how much control the household allows). Sources: docs/research/08-foerderung-annahmen-2026-10.md

export type SubsidyScheme = "eag2026" | "tiered";

/** EAG investment grant 2026 for storage: fixed €/kWh, only with new or extended PV, capped kWh, EU bonus up to +30 %. */
export const EAG_2026 = { perKwh: 150, maxKwh: 50, euBonus: 0.3 };
/** Tiered proposal: share of the battery cost per tier 0–3; the box is fully paid from tier 1. */
export const TIER_SHARE = [0.4, 0.6, 0.8, 1.0];
export const TIER_LABEL = [
  "0 · no control interface",
  "1 · controllable when charging",
  "2 · controllable both ways",
  "3 · both ways + paid discharge",
];

export interface SubsidyInput {
  scheme: SubsidyScheme;
  tier: number; // 0..3, tiered scheme only
  newPv: boolean; // battery bought together with new or extended PV (EAG condition)
  madeInEurope: boolean; // EAG bonus
  batteryKwh: number;
  batteryCost: number; // € installed
  boxCost: number; // € control box incl. installation
}

export function batterySubsidy(s: SubsidyInput): { battery: number; box: number; total: number } {
  let battery = 0;
  let box = 0;
  if (s.scheme === "eag2026") {
    if (s.newPv) battery = Math.min(s.batteryKwh, EAG_2026.maxKwh) * EAG_2026.perKwh * (s.madeInEurope ? 1 + EAG_2026.euBonus : 1);
  } else {
    const tier = Math.max(0, Math.min(3, Math.round(s.tier)));
    battery = (TIER_SHARE[tier] ?? 0) * s.batteryCost;
    box = tier >= 1 ? s.boxCost : 0;
  }
  battery = Math.min(battery, s.batteryCost);
  return { battery, box, total: battery + box };
}

export interface Inputs {
  weatherYear: WeatherYear;
  stations: number; // transformer stations in study area
  householdsPerStation: number;
  // Peak gap anchors (avg kW above transformer rating per overloaded station)
  excessKw2030: number;
  excessKw2040: number;
  // Smart charging
  smartParticipation: number; // share of EVs controllable (0..1)
  smartKwPerEv: number; // firm kW shifted per participating EV at peak
  smartCostPerEv: number; // € control hardware / HEMS per EV (one-off)
  // V2G
  v2gShare: number; // share of EVs with bidirectional charger (0..1)
  v2gKw: number; // kW per car
  v2gAvailability: number; // plugged in at peak
  v2gPremium: number; // € extra for bidirectional charger
  // Home batteries
  batteryCostPerKwh2026: number; // € installed
  batteryCostDecline: number; // per year
  batteryKwh: number;
  batteryKw: number;
  batteryGridShare: number; // share of capacity reserved for the grid in winter (dashboard 0.326)
  peakHours: number; // duration of winter peak event (h)
  reliability: number; // confirmed delivery in test calls
  controlBoxCost: number; // € grid-serving control box per battery
  baseAdoption2040: number; // share of households with grid-serving battery without subsidy
  adoptionElasticity: number; // adoption multiplier per 100% of capex subsidised
  subsidyPerKwh: number; // € per kWh (EAG scheme; 2026: 150)
  subsidyScheme: SubsidyScheme;
  subsidyTier: number; // tiered scheme: grid-serving in winter needs tier 2 (both directions)
  dsoFeePerBattery: number; // € per year paid by DSO for availability
  // Grid reinforcement
  reinforceFixed: number; // € per station touched
  reinforcePerKw: number; // € per kW of added capacity
  // Finance
  wacc: number; // regulated DSO WACC
  assetLife: number; // years
  totalHouseholds: number; // tariff base
}

export const DEFAULTS: Inputs = {
  weatherYear: "2017",
  stations: 257,
  householdsPerStation: 150,
  excessKw2030: 60,
  excessKw2040: 210,
  smartParticipation: 0.6,
  smartKwPerEv: 2.5,
  smartCostPerEv: 250,
  v2gShare: 0.1,
  v2gKw: 11,
  v2gAvailability: 0.7,
  v2gPremium: 2500,
  batteryCostPerKwh2026: 650,
  batteryCostDecline: 0.05,
  batteryKwh: 10,
  batteryKw: 5,
  batteryGridShare: 0.326,
  peakHours: 4,
  reliability: 0.82,
  controlBoxCost: 600,
  baseAdoption2040: 0.08,
  adoptionElasticity: 1.5,
  subsidyPerKwh: EAG_2026.perKwh,
  subsidyScheme: "eag2026",
  subsidyTier: 2,
  dsoFeePerBattery: 50,
  reinforceFixed: 30000,
  reinforcePerKw: 350,
  wacc: 0.0488,
  assetLife: 40,
  totalHouseholds: 38550,
};

// From the dashboard: stations with winter overload today / 2030 / 2040 by weather year
export const OVERLOADED: Record<WeatherYear, [number, number, number]> = {
  "2023": [2, 39, 193],
  "2017": [4, 52, 200],
  "2012": [5, 90, 210],
};

export const EV_SHARE: [number, number, number] = [0.08, 0.25, 0.6];
export const HP_SHARE: [number, number, number] = [0.15, 0.35, 0.7];

export const YEARS = Array.from({ length: 15 }, (_, i) => 2026 + i);

/** Interpolate between anchors at 2026, 2030, 2040. */
export function interp(year: number, [a, b, c]: [number, number, number]): number {
  if (year <= 2026) return a;
  if (year <= 2030) return a + ((b - a) * (year - 2026)) / 4;
  if (year <= 2040) return b + ((c - b) * (year - 2030)) / 10;
  return c;
}

export function annuity(rate: number, years: number): number {
  return rate === 0 ? 1 / years : rate / (1 - Math.pow(1 + rate, -years));
}

/** Firm kW a single battery can be relied on for during a winter peak event. */
export function firmKwPerBattery(i: Inputs): number {
  const energyLimited = (i.batteryKwh * i.batteryGridShare) / Math.max(i.peakHours, 0.5);
  return Math.min(i.batteryKw * 0.85, energyLimited) * i.reliability;
}

export function batteryCapex(i: Inputs, year: number): number {
  const perKwh = i.batteryCostPerKwh2026 * Math.pow(1 - i.batteryCostDecline, year - 2026);
  return perKwh * i.batteryKwh;
}

/** Battery subsidy per household in a given year (box not included). EAG: assumes the battery comes with new PV. */
export function subsidyEach(i: Inputs, year: number): number {
  const capex = batteryCapex(i, year);
  if (i.subsidyScheme === "tiered") {
    return batterySubsidy({ scheme: "tiered", tier: i.subsidyTier, newPv: true, madeInEurope: false,
      batteryKwh: i.batteryKwh, batteryCost: capex, boxCost: 0 }).battery;
  }
  return Math.min(i.subsidyPerKwh * Math.min(i.batteryKwh, EAG_2026.maxKwh), capex);
}

/** Share of households adopting a grid-serving battery in a given year. */
export function adoptionShare(i: Inputs, year: number): number {
  const capex = batteryCapex(i, year);
  const subsidy = subsidyEach(i, year);
  const ramp = Math.min(1, Math.max(0, (year - 2025) / 15));
  return Math.min(0.6, i.baseAdoption2040 * ramp * (1 + i.adoptionElasticity * (subsidy / capex)));
}

export interface YearResult {
  year: number;
  overloaded: number;
  excessKw: number; // per overloaded station
  gapKw: number; // total
  smartKw: number;
  v2gKw: number;
  batteryKw: number;
  reinforceKw: number;
  batteries: number;
  evs: number;
  // cumulative investment (€) — stock needed by that year
  consumerCapex: number;
  subsidy: number;
  dsoCapex: number; // reinforcement + control boxes + smart control
  dsoAnnual: number; // annuity of DSO capex + availability fees
  baselineCapex: number; // reinforce everything
  baselineAnnual: number;
  tariffPerHh: number; // € per household per year
  baselineTariffPerHh: number;
}

export function runYear(i: Inputs, year: number): YearResult {
  const [t, a, b] = OVERLOADED[i.weatherYear];
  const overloaded = Math.round(interp(year, [t, a, b]));
  const excessKw = interp(year, [10, i.excessKw2030, i.excessKw2040]);
  const gapKw = overloaded * excessKw;

  const hh = overloaded * i.householdsPerStation;
  const evs = hh * interp(year, EV_SHARE);

  let remaining = gapKw;
  const smartKw = Math.min(remaining, evs * i.smartParticipation * i.smartKwPerEv);
  remaining -= smartKw;
  const v2gCars = evs * i.v2gShare;
  const v2gKw = Math.min(remaining, v2gCars * i.v2gKw * i.v2gAvailability * i.reliability);
  remaining -= v2gKw;

  const firm = firmKwPerBattery(i);
  const available = hh * adoptionShare(i, year);
  const batteriesNeeded = firm > 0 ? remaining / firm : 0;
  const batteries = Math.min(available, batteriesNeeded);
  const batteryKw = batteries * firm;
  remaining -= batteryKw;
  const reinforceKw = Math.max(0, remaining);

  const capex = batteryCapex(i, year);
  const perBattery = subsidyEach(i, year);
  // tiered proposal: the box is paid by the subsidy (from tier 1), otherwise by the grid operator
  const boxBySubsidy = i.subsidyScheme === "tiered" && i.subsidyTier >= 1;
  const smartEvs = smartKw > 0 ? Math.min(evs * i.smartParticipation, smartKw / i.smartKwPerEv) : 0;
  const usedV2g = v2gKw > 0 ? v2gKw / (i.v2gKw * i.v2gAvailability * i.reliability) : 0;

  const consumerCapex = batteries * (capex - perBattery) + usedV2g * i.v2gPremium;
  const subsidy = batteries * (perBattery + (boxBySubsidy ? i.controlBoxCost : 0));
  const stationsReinforced = excessKw > 0 ? Math.min(overloaded, Math.ceil(reinforceKw / excessKw - 1e-9)) : 0;
  const reinforceCost = stationsReinforced * i.reinforceFixed + reinforceKw * i.reinforcePerKw;
  const dsoCapex = reinforceCost + (boxBySubsidy ? 0 : batteries * i.controlBoxCost) + smartEvs * i.smartCostPerEv;
  const ann = annuity(i.wacc, i.assetLife);
  const dsoAnnual = dsoCapex * ann + batteries * i.dsoFeePerBattery;

  const baselineCapex = overloaded * i.reinforceFixed + gapKw * i.reinforcePerKw;
  const baselineAnnual = baselineCapex * ann;

  return {
    year, overloaded, excessKw, gapKw, smartKw, v2gKw, batteryKw, reinforceKw,
    batteries, evs, consumerCapex, subsidy, dsoCapex, dsoAnnual, baselineCapex, baselineAnnual,
    tariffPerHh: dsoAnnual / i.totalHouseholds,
    baselineTariffPerHh: baselineAnnual / i.totalHouseholds,
  };
}

export function runPath(i: Inputs): YearResult[] {
  return YEARS.map((y) => runYear(i, y));
}

/** Sweep subsidy levels for one year: what does each € of subsidy buy? */
export function subsidySweep(i: Inputs, year: number, steps = [0, 100, 150, 200, 300, 400, 500, 650]) {
  return steps.map((s) => {
    const r = runYear({ ...i, subsidyScheme: "eag2026", subsidyPerKwh: s }, year);
    const avoided = r.baselineCapex - r.dsoCapex;
    return {
      subsidyPerKwh: s,
      batteryKw: Math.round(r.batteryKw),
      subsidyM: r.subsidy / 1e6,
      avoidedM: avoided / 1e6,
      eurPerKw: r.batteryKw > 0 ? r.subsidy / r.batteryKw : 0,
    };
  });
}

// ---------------------------------------------------------------------------
// Flexibility event: net consumer price and the never-worse-off guarantee.
// Prices in ct/kWh (net of VAT unless stated), money results in €.

export interface FlexInputs {
  spotCharge: number; // ct/kWh spot when battery charges (winter night)
  spotPeak: number; // ct/kWh spot during evening peak
  supplierMargin: number; // ct/kWh
  gridFee: number; // ct/kWh grid usage + losses
  levies: number; // ct/kWh taxes and levies
  vat: number; // 0.2
  p2pPrice: number; // ct/kWh energy-community sharing price
  ecGridDiscount: number; // grid-fee reduction for local energy community (0.28 / 0.57)
  batteryKwh: number;
  gridShare: number;
  efficiency: number; // round-trip
  peakHours: number;
  reliability: number;
  batteryCostPerKwh: number; // € installed
  cycleLife: number;
  dsoFeeYear: number; // € per battery per year
  eventsPerYear: number;
  opportunityCost: number; // € per event lost elsewhere (e.g. better p2p sale)
}

export const FLEX_DEFAULTS: FlexInputs = {
  spotCharge: 8, spotPeak: 18, supplierMargin: 1.5, gridFee: 7, levies: 2.5, vat: 0.2,
  p2pPrice: 10, ecGridDiscount: 0.28, batteryKwh: 10, gridShare: 0.326, efficiency: 0.9,
  peakHours: 4, reliability: 0.82, batteryCostPerKwh: 650, cycleLife: 6000,
  dsoFeeYear: 50, eventsPerYear: 20, opportunityCost: 0,
};

/** Gross retail price (ct/kWh) a household pays on a dynamic tariff. */
export function retailPrice(f: FlexInputs, spot: number): number {
  return (spot + f.supplierMargin + f.gridFee + f.levies) * (1 + f.vat);
}

/** Gross price (ct/kWh) a buyer pays for energy shared inside a local energy community. */
export function p2pBuyerPrice(f: FlexInputs): number {
  return (f.p2pPrice + f.supplierMargin + f.gridFee * (1 - f.ecGridDiscount) + f.levies) * (1 + f.vat);
}

export interface FlexEvent {
  deliveredKwh: number;
  chargedKwh: number;
  firmKw: number;
  chargePrice: number;
  peakPrice: number;
  chargeCost: number;
  avoidedCost: number;
  arbitrage: number;
  degradation: number;
  fee: number;
  opportunity: number;
  net: number; // before guarantee
  topUp: number; // guarantee payment max(0, -net)
  final: number; // net + topUp, always >= 0
  breakEvenFee: number; // fee per event at which net = 0
  annual: number; // final * events
}

export function flexEvent(f: FlexInputs): FlexEvent {
  const deliveredKwh = f.batteryKwh * f.gridShare;
  const chargedKwh = deliveredKwh / f.efficiency;
  const firmKw = (deliveredKwh / Math.max(f.peakHours, 0.5)) * f.reliability;
  const chargePrice = retailPrice(f, f.spotCharge);
  const peakPrice = retailPrice(f, f.spotPeak);
  const chargeCost = (chargedKwh * chargePrice) / 100;
  const avoidedCost = (deliveredKwh * peakPrice) / 100;
  const arbitrage = avoidedCost - chargeCost;
  const degradation = chargedKwh * (f.batteryCostPerKwh / (f.cycleLife * f.efficiency));
  const fee = f.eventsPerYear > 0 ? f.dsoFeeYear / f.eventsPerYear : 0;
  const opportunity = f.opportunityCost;
  const net = fee + arbitrage - degradation - opportunity;
  const topUp = Math.max(0, -net);
  const final = net + topUp;
  return {
    deliveredKwh, chargedKwh, firmKw, chargePrice, peakPrice, chargeCost, avoidedCost, arbitrage,
    degradation, fee, opportunity, net, topUp, final,
    breakEvenFee: Math.max(0, degradation + opportunity - arbitrage),
    annual: final * f.eventsPerYear,
  };
}

/** Household result across a range of peak spot prices (charge price fixed). */
export function spreadSweep(f: FlexInputs, peaks = [0, 4, 8, 12, 16, 20, 25, 30, 40]) {
  return peaks.map((p) => {
    const e = flexEvent({ ...f, spotPeak: p });
    return { spotPeak: p, net: +e.net.toFixed(2), final: +e.final.toFixed(2), topUp: +e.topUp.toFixed(2) };
  });
}

// ---------------------------------------------------------------------------
// One household's battery: subsidy, own cost and how much the grid calls load the battery.

export interface HouseholdInputs extends Omit<SubsidyInput, "batteryKwh" | "batteryCost" | "boxCost"> {
  boxCost: number;
  years: number; // horizon for the share of cycle life used by grid calls
}

export const HOUSEHOLD_DEFAULTS: HouseholdInputs = {
  scheme: "eag2026", tier: 2, newPv: true, madeInEurope: false, boxCost: 600, years: 15,
};

export interface HouseholdBattery {
  batteryCost: number;
  boxCost: number;
  subsidy: { battery: number; box: number; total: number };
  ownCost: number;
  callsYear: number; // discharge calls the household takes part in
  extraCyclesYear: number; // full cycles per year caused by grid calls
  lifeShare: number; // share of cycle life used by grid calls over `years`
  wearYear: number; // € battery wear per year from grid calls
  gridIncomeYear: number; // € per year after the never-worse-off guarantee
}

export function householdBattery(f: FlexInputs, h: HouseholdInputs): HouseholdBattery {
  const batteryCost = f.batteryKwh * f.batteryCostPerKwh;
  const subsidy = batterySubsidy({ ...h, batteryKwh: f.batteryKwh, batteryCost, boxCost: h.boxCost });
  // tiered scheme: winter discharge calls only from tier 2 (controllable in both directions)
  const callsYear = h.scheme === "tiered" && h.tier < 2 ? 0 : f.eventsPerYear;
  const e = flexEvent(f);
  const extraCyclesYear = (callsYear * e.chargedKwh) / f.batteryKwh;
  return {
    batteryCost, boxCost: h.boxCost, subsidy,
    ownCost: batteryCost + h.boxCost - subsidy.total,
    callsYear, extraCyclesYear,
    lifeShare: (extraCyclesYear * h.years) / f.cycleLife,
    wearYear: callsYear * e.degradation,
    gridIncomeYear: callsYear * e.final,
  };
}
