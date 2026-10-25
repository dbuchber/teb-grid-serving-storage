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

class DeadES {
  constructor(url) { this.url = url; this.listeners = {}; setTimeout(() => this.onerror?.(new Event("error")), 0); }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  close() {}
}

test("unknown run (container restart) ends with error instead of polling forever", async () => {
  const fetchFn = async () => ({ ok: false, status: 404, json: async () => ({ error: "unknown run abc" }) });
  const api = createApi("/api/", { fetchFn, EventSourceCls: DeadES, pollMs: 1 });
  const done = await new Promise(resolve => api.streamRun("abc", () => {}, resolve));
  assert.equal(done.status, "error");
  assert.match(done.error, /unknown run/);
});

test("login redirect (HTML, not JSON) ends with error after retries", async () => {
  let calls = 0;
  const fetchFn = async () => { calls++; return { ok: true, status: 200, json: async () => { throw new SyntaxError("Unexpected token <"); } }; };
  const api = createApi("/api/", { fetchFn, EventSourceCls: DeadES, pollMs: 1, maxFailures: 3 });
  const done = await new Promise(resolve => api.streamRun("abc", () => {}, resolve));
  assert.equal(done.status, "error");
  assert.equal(calls, 3);
});

test("lines and startRun pass the new parameters through", async () => {
  const calls = [];
  const fetchFn = async (url, init) => { calls.push([url, init]); return { ok: true, json: async () => ({ ok: 1 }) }; };
  const api = createApi("/api/", { fetchFn, EventSourceCls: null });
  await api.lines(2012);
  assert.equal(calls[0][0], "/api/lines?weather_year=2012");
  await api.startRun({ limits: "trafo+leitung", netzspeicher: true });
  assert.deepEqual(JSON.parse(calls[1][1].body), { limits: "trafo+leitung", netzspeicher: true });
});
