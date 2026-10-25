import { describe, it, expect } from "vitest";
import { DEFAULTS, runYear, firmKwPerBattery, interp, adoptionShare } from "@/lib/model";

describe("financial model", () => {
  it("uses dashboard overloaded-station counts for 2030 and 2040", () => {
    expect(runYear({ ...DEFAULTS, weatherYear: "2012" }, 2030).overloaded).toBe(90);
    expect(runYear({ ...DEFAULTS, weatherYear: "2017" }, 2040).overloaded).toBe(200);
  });

  it("levers plus reinforcement exactly cover the gap", () => {
    const r = runYear(DEFAULTS, 2040);
    expect(r.smartKw + r.v2gKw + r.batteryKw + r.reinforceKw).toBeCloseTo(r.gapKw, 6);
  });

  it("battery firm kW is energy-limited in a 4h winter peak", () => {
    // 10 kWh * 0.326 / 4h = 0.815 kW, * 0.82 reliability
    expect(firmKwPerBattery(DEFAULTS)).toBeCloseTo(0.6683, 3);
  });

  it("more subsidy raises adoption", () => {
    expect(adoptionShare({ ...DEFAULTS, subsidyPerKwh: 400 }, 2035)).toBeGreaterThan(
      adoptionShare({ ...DEFAULTS, subsidyPerKwh: 0 }, 2035),
    );
  });

  it("interpolates anchors", () => {
    expect(interp(2035, [0, 10, 20])).toBe(15);
  });
});
