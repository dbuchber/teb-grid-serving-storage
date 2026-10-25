import { describe, it, expect } from "vitest";
import {
  DEFAULTS, FLEX_DEFAULTS, HOUSEHOLD_DEFAULTS, batterySubsidy, householdBattery, runYear, subsidyEach,
} from "@/lib/model";

describe("battery subsidy", () => {
  it("EAG 2026: €150/kWh only with new or extended PV, at most 50 kWh", () => {
    const base = { scheme: "eag2026" as const, tier: 2, newPv: true, madeInEurope: false, batteryKwh: 10, batteryCost: 6500, boxCost: 300 };
    expect(batterySubsidy(base).battery).toBe(1500);
    expect(batterySubsidy({ ...base, newPv: false }).total).toBe(0);
    expect(batterySubsidy({ ...base, batteryKwh: 80, batteryCost: 40000 }).battery).toBe(7500);
    expect(batterySubsidy({ ...base, madeInEurope: true }).battery).toBeCloseTo(1950, 6);
    expect(batterySubsidy(base).box).toBe(0);
  });

  it("tiered proposal: 40/60/80/100 % of the battery, box paid from tier 1", () => {
    const base = { scheme: "tiered" as const, tier: 0, newPv: false, madeInEurope: false, batteryKwh: 10, batteryCost: 6500, boxCost: 300 };
    expect([0, 1, 2, 3].map((tier) => batterySubsidy({ ...base, tier }).battery)).toEqual([2600, 3900, 5200, 6500]);
    expect(batterySubsidy({ ...base, tier: 0 }).box).toBe(0);
    expect(batterySubsidy({ ...base, tier: 1 }).box).toBe(300);
  });

  it("region model: tiered scheme moves the box from the grid operator to the subsidy", () => {
    const eag = runYear({ ...DEFAULTS, subsidyScheme: "eag2026" }, 2040);
    const tiered = runYear({ ...DEFAULTS, subsidyScheme: "tiered", subsidyTier: 2 }, 2040);
    expect(subsidyEach({ ...DEFAULTS, subsidyScheme: "eag2026" }, 2026)).toBe(1500);
    expect(tiered.subsidy / tiered.batteries).toBeGreaterThan(eag.subsidy / eag.batteries);
    expect(tiered.dsoCapex).toBeLessThan(eag.dsoCapex + 1e-6);
  });
});

describe("household battery", () => {
  it("counts the extra cycles that grid calls put on the battery", () => {
    const h = householdBattery(FLEX_DEFAULTS, HOUSEHOLD_DEFAULTS);
    // 20 calls × 3.62 kWh charged / 10 kWh = 7.2 extra full cycles per year
    expect(h.extraCyclesYear).toBeCloseTo(7.24, 1);
    expect(h.lifeShare).toBeCloseTo((7.24 * 15) / 6000, 3);
    expect(h.ownCost).toBeCloseTo(h.batteryCost + h.boxCost - h.subsidy.total, 6);
  });

  it("no discharge calls below tier 2 in the tiered scheme", () => {
    const h = householdBattery(FLEX_DEFAULTS, { ...HOUSEHOLD_DEFAULTS, scheme: "tiered", tier: 1 });
    expect(h.callsYear).toBe(0);
    expect(h.gridIncomeYear).toBe(0);
  });
});
