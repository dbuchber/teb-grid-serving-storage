import { test } from "node:test";
import assert from "node:assert/strict";
import { visibleTiles } from "./charts.js";

test("line tiles only appear for runs with line results", () => {
  const keys = seeds => visibleTiles(seeds).map(t => t.key);
  assert.ok(!keys([{ region: { stations_line_load_congestion: null } }]).includes("stations_line_load_congestion"));
  assert.ok(!keys([]).includes("line_over_m"));
  assert.ok(keys([{ region: { stations_line_load_congestion: 3, line_over_m: 120 } }]).includes("line_over_m"));
  assert.ok(keys([]).includes("stations_load_congestion"));   // Trafo-Kacheln bleiben immer
});
