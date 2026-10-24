// Zugriff auf die gridsim-API: Läufe starten, Seeds per SSE empfangen (Rückfall: Polling), Tageskurve, Kosten.

export function createApi(base = "/api/", { fetchFn = (...a) => fetch(...a), EventSourceCls = globalThis.EventSource, pollMs = 1000 } = {}) {
  const url = path => base.replace(/\/$/, "") + "/" + path.replace(/^\//, "");

  async function json(path, init) {
    const r = await fetchFn(url(path), { credentials: "same-origin", ...init });
    const body = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(body.error || `HTTP ${r.status}`);
    return body;
  }

  const post = (path, body) => json(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

  // ruft onSeed je neuem Seed genau einmal auf, dann onDone(status); bricht SSE ab, wird gepollt
  function streamRun(runId, onSeed, onDone) {
    const seen = new Set();
    let finished = false, es = null, timer = null;
    const deliver = s => { if (!seen.has(s.index)) { seen.add(s.index); onSeed(s); } };
    const finish = status => { if (finished) return; finished = true; es?.close(); clearTimeout(timer); onDone(status); };
    const poll = async () => {
      if (finished) return;
      try {
        const st = await json(`runs/${encodeURIComponent(runId)}`);
        st.seeds.forEach(deliver);
        if (["done", "cached", "error"].includes(st.status)) return finish(st);
      } catch (e) { /* kurz warten und erneut versuchen */ }
      timer = setTimeout(poll, pollMs);
    };
    if (EventSourceCls) {
      es = new EventSourceCls(url(`runs/${encodeURIComponent(runId)}/events`));
      es.addEventListener("seed", ev => deliver(JSON.parse(ev.data)));
      es.addEventListener("done", ev => finish(JSON.parse(ev.data)));
      es.onerror = () => { if (!finished) { es.close(); poll(); } };
    } else {
      poll();
    }
    return () => finish({ status: "cancelled" });
  }

  return {
    options: () => json("options"),
    stations: year => json(`stations?weather_year=${year}`),
    startRun: params => post("runs", params),
    status: id => json(`runs/${encodeURIComponent(id)}`),
    streamRun,
    day: (stationId, params) => json(`stations/${encodeURIComponent(stationId)}/day?` + new URLSearchParams(params)),
    costs: (runId, cost) => post("costs", { run_id: runId, cost }),
  };
}
