import { describe, it, expect } from "vitest";
import { FLEX_DEFAULTS, flexEvent, retailPrice, spreadSweep } from "@/lib/model";

describe("flexibility event", () => {
  it("retail price = (spot + margin + grid fee + levies) × 1.2", () => {
    expect(retailPrice(FLEX_DEFAULTS, 8)).toBeCloseTo(22.8, 6);
    expect(retailPrice(FLEX_DEFAULTS, 18)).toBeCloseTo(34.8, 6);
  });

  it("default event nets the household about +€2.38", () => {
    expect(flexEvent(FLEX_DEFAULTS).net).toBeCloseTo(2.38, 1);
  });

  it("flat prices still positive with €2.50 fee (~+€1.96)", () => {
    expect(flexEvent({ ...FLEX_DEFAULTS, spotCharge: 15, spotPeak: 15 }).net).toBeCloseTo(1.96, 1);
  });

  it("never worse off: guarantee tops up any loss", () => {
    const e = flexEvent({ ...FLEX_DEFAULTS, dsoFeeYear: 0, spotPeak: 0, opportunityCost: 1 });
    expect(e.net).toBeLessThan(0);
    expect(e.final).toBe(0);
    for (const r of spreadSweep({ ...FLEX_DEFAULTS, dsoFeeYear: 0 })) expect(r.final).toBeGreaterThanOrEqual(0);
  });
});
