import { test } from "node:test";
import assert from "node:assert/strict";
import { regionTitle, tileUnit, TILES, visibleTiles } from "./charts.js";

test("line tiles only appear for runs with line results", () => {
  const keys = seeds => visibleTiles(seeds).map(t => t.key);
  assert.ok(!keys([{ region: { stations_line_load_congestion: null } }]).includes("stations_line_load_congestion"));
  assert.ok(!keys([]).includes("line_over_m"));
  assert.ok(keys([{ region: { stations_line_load_congestion: 3, line_over_m: 120 } }]).includes("line_over_m"));
  assert.ok(keys([]).includes("stations_load_congestion"));   // Trafo-Kacheln bleiben immer
});

test("station count in tile unit and title comes from the run, not a fixed 257", () => {
  const tile = TILES.find(t => t.key === "stations_load_congestion");
  assert.equal(tileUnit(tile, [{ region: { n_stations: 465 } }]), "of 465");
  assert.equal(tileUnit(tile, []), "stations");
  assert.equal(tileUnit(TILES.find(t => t.key === "e_net_mwh"), []), "MWh, sum of largest events");
  assert.equal(regionTitle(465), "Regional simulation: all 465 transformers in the Steyr area");
  assert.equal(regionTitle(null), "Regional simulation: all transformers in the Steyr area");
});
