import { test } from "node:test";
import assert from "node:assert/strict";
import { quantile, bandOf, stationValues, colorClass } from "./band.js";

const seed = (i, v) => ({ index: i, region: { e_net_mwh: v }, station_congestion_h: [v, 0], station_load_kw_max: [1, 2] });

test("band median and p10/p90 over seeds", () => {
  const vals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  assert.equal(quantile(vals, 0.5), 5.5);
  assert.ok(Math.abs(quantile(vals, 0.1) - 1.9) < 1e-9);
  assert.ok(Math.abs(quantile(vals, 0.9) - 9.1) < 1e-9);
  const b = bandOf(vals.map((v, i) => seed(i, v)), "e_net_mwh");
  assert.deepEqual([b.median, b.n], [5.5, 10]);
});

test("band grows with each seed", () => {
  const one = bandOf([seed(0, 4)], "e_net_mwh");
  assert.equal(one.p90 - one.p10, 0);
  const three = bandOf([seed(0, 4), seed(1, 8), seed(2, 6)], "e_net_mwh");
  assert.ok(three.p90 - three.p10 > 0);
});

test("missing station renders as no-data", () => {
  const vals = stationValues([seed(0, 5), seed(1, 7)], ["way/1", "node/2"], "station_congestion_h");
  assert.equal(vals.get("way/1"), 6);
  assert.equal(colorClass(vals, "way/1"), "warn");
  assert.equal(colorClass(vals, "node/2"), "ok");
  assert.equal(colorClass(vals, "demo:steyr:station-999"), "no-data");
});

import { bottleneckValues, bottleneckClass, BOTTLENECK, lineStations } from "./band.js";

const lseed = (i, first) => ({ index: i, region: {}, extra: { station_first_load: first } });

test("bottleneck class: most frequent first bottleneck over seeds, leitung differs from trafo", () => {
  const seeds = [lseed(0, ["trafo", "leitung", "keiner"]), lseed(1, ["trafo", "leitung", "beide"]), lseed(2, ["leitung", "leitung", "beide"])];
  const vals = bottleneckValues(seeds, ["a", "b", "c"]);
  assert.equal(bottleneckClass(vals, "a"), "b-trafo");
  assert.equal(bottleneckClass(vals, "b"), "b-leitung");
  assert.equal(bottleneckClass(vals, "c"), "b-beide");
  assert.notEqual(BOTTLENECK["b-leitung"].color, BOTTLENECK["b-trafo"].color);
  assert.equal(new Set(Object.values(BOTTLENECK).map(x => x.color)).size, 4);   // vier verschiedene Farben
  assert.ok(Object.values(BOTTLENECK).every(x => x.label));                      // und Beschriftung für die Legende
});

test("bottleneck ties go to the more severe class", () => {
  const vals = bottleneckValues([lseed(0, ["trafo"]), lseed(1, ["leitung"])], ["a"]);
  assert.equal(bottleneckClass(vals, "a"), "b-leitung");
});

test("bottleneck values are null without line results (run without feeders)", () => {
  assert.equal(bottleneckValues([lseed(0, null)], ["a"]), null);
  assert.equal(bottleneckValues([{ index: 0, region: {} }], ["a"]), null);
  assert.equal(bottleneckValues([], ["a"]), null);
});

test("station without line grid (null entry) is no-data in bottleneck mode", () => {
  const vals = bottleneckValues([lseed(0, ["trafo", null])], ["a", "b"]);
  assert.equal(bottleneckClass(vals, "b"), "no-data");
});

test("lineStations lists station indices where a line is (also) the first bottleneck", () => {
  const vals = bottleneckValues([lseed(0, ["trafo", "leitung", "beide", "keiner"])], ["a", "b", "c", "d"]);
  assert.deepEqual(lineStations(vals, ["a", "b", "c", "d"]), [1, 2]);
});

import { costItems, effectiveNotice } from "./band.js";

const costs = over => ({ storage_eur: 6e6, trafo_eur: null, line_eur: null, netzspeicher_eur: null, trafo_over_1000: 0, placeholders: [], ...over });

test("costItems never yields null entries (no literal 'null' text in the panel)", () => {
  for (const c of [costs({}), costs({ placeholders: ["trafo_step_eur"] }), costs({ netzspeicher_eur: 1e6, line_eur: 2e6, trafo_eur: 3e6 })]) {
    const items = costItems(c, true);
    assert.ok(items.every(i => i && typeof i.text === "string" && i.text.length));
  }
});

test("costItems: grid storage line only when priced, placeholder hint only when present", () => {
  const texts = (c, has = true) => costItems(c, has).map(i => i.text);
  assert.ok(!texts(costs({})).some(t => t.startsWith("Grid storage")));
  assert.ok(texts(costs({ netzspeicher_eur: 2.5e6 })).some(t => t.startsWith("Grid storage") && t.includes("2.5 M€")));
  assert.ok(!texts(costs({})).some(t => t.startsWith("Placeholders")));
  assert.ok(texts(costs({ placeholders: ["a", "b"] })).some(t => t === "Placeholders without source: a, b"));
});

test("costItems: cable line distinguishes priced, no rate, no line results", () => {
  const cable = (c, has) => costItems(c, has).find(i => i.text.startsWith("Cable")).text;
  assert.match(cable(costs({ line_eur: 4e6 }), true), /4 M€/);
  assert.match(cable(costs({}), true), /enter a cost per metre/);
  assert.match(cable(costs({}), false), /no line results/);
});

test("effectiveNotice: empty when settings were honoured or no seed yet", () => {
  assert.equal(effectiveNotice([], { limits: "trafo+leitung", netzspeicher: true }), "");
  const ok = [{ extra: { limits_effective: "trafo+leitung", netzspeicher_effective: true } }];
  assert.equal(effectiveNotice(ok, { limits: "trafo+leitung", netzspeicher: true }), "");
  assert.equal(effectiveNotice([{ extra: { limits_effective: "trafo", netzspeicher_effective: false } }], { limits: "trafo", netzspeicher: false }), "");
  assert.equal(effectiveNotice([{ extra: {} }], { limits: "trafo+leitung", netzspeicher: false }), "");   // alter Cache ohne Angabe: nichts behaupten
});

test("effectiveNotice: tells when line limits or grid storage could not be applied", () => {
  const s = [{ extra: { limits_effective: "trafo", netzspeicher_effective: false } }];
  assert.match(effectiveNotice(s, { limits: "trafo+leitung", netzspeicher: false }), /No line data for this weather year .* transformer limits only/);
  assert.match(effectiveNotice(s, { limits: "trafo", netzspeicher: true }), /Grid storage .* not applied/);
  assert.match(effectiveNotice(s, { limits: "trafo+leitung", netzspeicher: true }), /transformer limits only.*Grid storage/s);
});
