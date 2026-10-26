// Zugriff auf die gridsim-API: Läufe starten, Seeds per SSE empfangen (Rückfall: Polling), Tageskurve, Kosten.

export function createApi(base = "/api/", { fetchFn = (...a) => fetch(...a), EventSourceCls = globalThis.EventSource, pollMs = 1000, maxFailures = 10 } = {}) {
  const url = path => base.replace(/\/$/, "") + "/" + path.replace(/^\//, "");

  async function json(path, init) {
    const r = await fetchFn(url(path), { credentials: "same-origin", ...init });
    let body;
    try { body = await r.json(); } catch {
      // z. B. Login-Seite nach abgelaufener Sitzung: HTML statt JSON
      const err = new Error(r.ok ? "Unexpected response (session expired? reload the page)" : `HTTP ${r.status}`);
      err.status = r.status;
      throw err;
    }
    if (!r.ok) { const err = new Error(body.error || `HTTP ${r.status}`); err.status = r.status; throw err; }
    return body;
  }

  const post = (path, body) => json(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

  // ruft onSeed je neuem Seed genau einmal auf, dann onDone(status); bricht SSE ab, wird gepollt
  function streamRun(runId, onSeed, onDone) {
    const seen = new Set();
    let finished = false, es = null, timer = null, failures = 0;
    const deliver = s => { if (!seen.has(s.index)) { seen.add(s.index); onSeed(s); } };
    const finish = status => { if (finished) return; finished = true; es?.close(); clearTimeout(timer); onDone(status); };
    const poll = async () => {
      if (finished) return;
      try {
        const st = await json(`runs/${encodeURIComponent(runId)}`);
        st.seeds.forEach(deliver);
        if (["done", "cached", "error"].includes(st.status)) return finish(st);
      } catch (e) {
        // unbekannter Lauf (Server neu gestartet) oder dauerhafte Störung: aufgeben statt endlos pollen
        if (e.status === 404 || ++failures >= maxFailures) return finish({ status: "error", error: e.message });
      }
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
    lines: () => json("lines"),   // ein Netz für alle Wetterjahre
    startRun: params => post("runs", params),
    status: id => json(`runs/${encodeURIComponent(id)}`),
    streamRun,
    day: (stationId, params) => json(`stations/${encodeURIComponent(stationId)}/day?` + new URLSearchParams(params)),
    costs: (runId, cost) => post("costs", { run_id: runId, cost }),
  };
}
