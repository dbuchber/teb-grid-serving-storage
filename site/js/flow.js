// IES-Ablauf an einer Ortsnetzstation: Engpass → signierter Abruf → Reaktion → Smart-Meter-Verifikation
// → Zuverlässigkeit aktualisiert. Gerätedaten und Reaktion sind gemockt (devices.json, evidence=synthetic);
// Engpass und Leistung stammen aus der Simulation (stations.geojson).

const fmt = (v, d = 0) => new Intl.NumberFormat("en-GB", { maximumFractionDigits: d }).format(v);

// kleiner deterministischer Zufall, damit der Ablauf bei jedem Klick gleich aussieht
function rng(seed) {
  let s = 0;
  for (const c of seed) s = (s * 31 + c.charCodeAt(0)) >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 2 ** 32);
}

const STEPS = [
  ["1", "Bottleneck detected"], ["2", "Signed call"], ["3", "Batteries respond"],
  ["4", "Smart meter verifies"], ["5", "Reliability updated"],
]

export function runFlow(root, station, entry, devices, scenario) {
  const p = station.properties;
  const einsp = scenario.richtung === "einspeisung";
  root.replaceChildren();
  const nav = document.createElement("ol");
  nav.className = "steps";
  const body = document.createElement("div");
  body.className = "step-body";
  root.append(nav, body);

  const need = entry ? entry.p_max_kw : 0;
  // Auswahl: zuverlässige, gesunde Speicher zuerst, bis die erwartete Leistung den Bedarf deckt
  const ranked = [...devices].sort((a, b) => b.reliability_est * b.soh - a.reliability_est * a.soh);
  const chosen = [];
  let expected = 0;
  for (const d of ranked) {
    if (need && expected >= need) break;
    chosen.push(d);
    expected += d.power_kw * d.reliability_est;
  }
  const r = rng(p.id + scenario.key);
  const results = chosen.map(d => {
    const ok = r() < d.reliability_est;
    const delivered = ok ? d.power_kw * (0.85 + 0.15 * r()) : d.power_kw * 0.3 * r();
    const response = Math.round(d.response_s_median * (0.6 + 0.8 * r()));
    const verified = ok && r() > 0.03;
    const observed = verified ? delivered / d.power_kw : 0;
    return { d, delivered, response, verified, observed, newRel: 0.8 * d.reliability_est + 0.2 * observed };
  });
  const deliveredSum = results.reduce((s, x) => s + (x.verified ? x.delivered : 0), 0);

  const views = [
    () => `
      <p><b>${p.id}</b> · ${p.uw} · ${p.netzart === "stadt" ? "urban" : "rural"} · transformer ${fmt(p.trafo_kva)} kVA · ${fmt(p.haushalte)} households · ${fmt(p.kwp)} kWp PV
         ${p.synthetisch ? '<span class="tag mock">station placed synthetically</span>' : ""}</p>
      ${entry ? `
      <p>In the scenario <b>${scenario.label}</b> the transformer is above its rating for <b>${fmt(entry.engpass_h)} hours a year</b>
         (${einsp ? "feed-in" : "demand"}), in ${fmt(entry.ereignisse)} events. ${einsp ? "Largest surplus" : "Largest overload"}:
         <b>${fmt(entry.p_max_kw)} kW</b>, ${fmt(entry.e_netto_kwh)} kWh in the strongest event.</p>
      <p class="note">Without flexibility this would need ${entry.trafo_stufen == null ? "a transformer above 1,000 kVA" :
         `a transformer ${entry.trafo_stufen} standard size(s) larger (${fmt(entry.trafo_noetig_kva)} kVA)`}.</p>` :
      `<p class="good">In this scenario the station has no bottleneck. Pick a red or orange station
         or another scenario.</p>`}`,
    () => `
      <p>The grid operator sends a <b>signed command to the segment</b> (OpenADR event or LoRaWAN multicast).
         Each box checks signature, expiry and limits locally before it controls the battery.</p>
      <pre class="code">${escape(JSON.stringify({
        segment: p.id,
        event: einsp ? "charge_setpoint" : "discharge_setpoint",
        setpoint_kw_per_device: einsp ? "charge up to rated power" : "discharge up to rated power",
        target_total_kw: Math.round(need),
        start: "2026-06-13T11:00:00+02:00", max_duration_min: 120,
        valid_until: "2026-06-13T11:05:00+02:00",
        limits: { min_soc_pct: 20, ramp_kw_per_s: 0.5, random_delay_s: [0, 30] },
        signature: "ECDSA-P256 · DSO key · demo",
      }, null, 2))}</pre>
      <p>Selected: <b>${chosen.length} of ${devices.length} batteries</b> in the segment, ranked by reliability × state of health
         (SoH). Expected power ${fmt(expected)} kW for ${fmt(need)} kW needed.</p>
      ${devices.length ? "" : '<p class="bad">No battery with a box is registered in this segment.</p>'}`,
    () => `
      <p>The batteries respond with different speed and reliability. Median response time:
         <b>${fmt(median(results.map(x => x.response)))} s</b> (target per TOR: setpoint within 60 s).</p>
      ${deviceTable(results.slice(0, 12), ["Device", "Class", "kW", "kWh", "delivered kW", "response s"],
        x => [x.d.device_id, x.d.vendor_class, fmt(x.d.power_kw, 1), fmt(x.d.capacity_kwh, 1), fmt(x.delivered, 1), x.response])}
      ${results.length > 12 ? `<p class="note">… and ${results.length - 12} more.</p>` : ""}`,
    () => {
      const ver = results.filter(x => x.verified).length;
      return `
      <p>The smart meter at the grid connection point measures independently what really happened.
         <b>${ver} of ${results.length}</b> responses are confirmed, together <b>${fmt(deliveredSum)} kW</b>
         (${need ? fmt(100 * deliveredSum / need) : "–"} % of the need).</p>
      ${need && deliveredSum < need ? `
      <p class="bad">${fmt(need - deliveredSum)} kW are missing. The home batteries in this segment are not enough.</p>
      <p>Further levers from the same profile: more batteries with a box (subsidy), commercial batteries, peak capping
         of large PV systems via the mandatory interface (§ 76 ElWG) or a larger transformer.</p>` : need ? `
      <p class="good">The bottleneck is covered without replacing the transformer.</p>` : ""}
      <p class="note">Live plausibility check via the customer interface (1–5 s); binding are the 15-minute values
         in the grid operator's backend on the next day. Deviations feed into reliability.</p>
      ${deviceTable(results.filter(x => !x.verified).slice(0, 8), ["not confirmed", "Class", "requested kW", "measured kW"],
        x => [x.d.device_id, x.d.vendor_class, fmt(x.d.power_kw, 1), fmt(x.verified ? x.delivered : 0, 1)])}`;
    },
    () => {
      const byClass = {};
      for (const x of results) {
        const c = (byClass[x.d.vendor_class] ||= { n: 0, before: 0, after: 0 });
        c.n++; c.before += x.d.reliability_est; c.after += x.newRel;
      }
      return `
      <p>Every response updates the <b>reliability per device and vendor class</b> (moving average,
         weight 0.2). The next call selects accordingly, and the grid operator knows how much power
         it can rely on in the segment.</p>
      ${deviceTable(Object.entries(byClass).sort(), ["Class", "Devices", "before", "after"],
        ([k, c]) => [k, c.n, fmt(100 * c.before / c.n) + " %", fmt(100 * c.after / c.n) + " %"])}
      <p class="note">Vendor classes anonymised (A–E). Device data and responses are mocked.</p>`;
    },
  ];


  STEPS.forEach(([n, label], i) => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.type = "button";
    b.innerHTML = `<span>${n}</span>${label}`;
    b.addEventListener("click", () => show(i));
    li.appendChild(b);
    nav.appendChild(li);
  });
  const ctl = document.createElement("div");
  ctl.className = "step-ctl";
  const next = document.createElement("button");
  next.type = "button";
  next.className = "primary";
  ctl.appendChild(next);
  root.appendChild(ctl);
  let cur = 0;
  next.addEventListener("click", () => show(Math.min(cur + 1, STEPS.length - 1)));
  function show(i) {
    cur = i;
    [...nav.children].forEach((li, j) => li.classList.toggle("active", j === i));
    [...nav.children].forEach((li, j) => li.classList.toggle("done", j < i));
    body.innerHTML = views[i]();
    next.textContent = i < STEPS.length - 1 ? `Next: ${STEPS[i + 1][1]}` : "Process complete";
    next.disabled = i === STEPS.length - 1 || !entry;
  }
  show(0);
}

function deviceTable(rows, head, cells) {
  if (!rows.length) return "";
  return `<div class="tablewrap"><table><thead><tr>${head.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${
    rows.map(r => `<tr>${cells(r).map(c => `<td>${escape(String(c))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function median(a) {
  if (!a.length) return 0;
  const s = [...a].sort((x, y) => x - y);
  return s[Math.floor(s.length / 2)];
}

function escape(s) {
  return s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}
