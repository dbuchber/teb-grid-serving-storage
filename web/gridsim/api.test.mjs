import { test } from "node:test";
import assert from "node:assert/strict";
import { createApi } from "./api.js";

class FakeES {
  constructor(url) { FakeES.last = this; this.url = url; this.listeners = {}; setTimeout(() => this.emitSeedThenFail(), 0); }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  emitSeedThenFail() {
    this.listeners.seed?.({ data: JSON.stringify({ index: 0, region: {} }) });
    this.onerror?.(new Event("error"));
  }
  close() { this.closed = true; }
}

test("sse falls back to polling and dedups seeds", async () => {
  const seeds = [0, 1, 2].map(i => ({ index: i, region: {} }));
  const fetchFn = async url => ({ ok: true, json: async () => ({ status: "done", seeds, n_seeds: 3 }) });
  const api = createApi("/api/", { fetchFn, EventSourceCls: FakeES, pollMs: 5 });
  const got = [];
  await new Promise(resolve => api.streamRun("abc", s => got.push(s.index), resolve));
  assert.deepEqual(got.sort(), [0, 1, 2]);
  assert.ok(FakeES.last.closed);
  assert.equal(FakeES.last.url, "/api/runs/abc/events");
});
