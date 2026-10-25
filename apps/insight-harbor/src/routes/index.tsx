import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, ComposedChart, Legend, Line,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DEFAULTS, type Inputs, type WeatherYear, type SubsidyScheme, runPath, subsidySweep, firmKwPerBattery, batteryCapex,
  EAG_2026, TIER_LABEL, TIER_SHARE,
} from "@/lib/model";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Steyr Grid Flexibility: Cost Model 2030/2040" },
      { name: "description", content: "Who pays for winter grid peaks in Steyr? Subsidy, upfront investment and tariff burden of batteries, smart charging and V2G vs grid reinforcement." },
      { property: "og:title", content: "Steyr Grid Flexibility: Cost Model 2030/2040" },
      { property: "og:description", content: "Interactive financial model: subsidy, investment and tariff burden of grid flexibility vs reinforcement, 2026-2040." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Dashboard,
});

const eur = (v: number) =>
  Math.abs(v) >= 1e6 ? `€${(v / 1e6).toFixed(1)}m` : Math.abs(v) >= 1e3 ? `€${(v / 1e3).toFixed(0)}k` : `€${v.toFixed(0)}`;
const num = (v: number) => Math.round(v).toLocaleString("en-US");
const tip = { background: "var(--card)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--foreground)" };
const axis = { stroke: "var(--muted-foreground)", fontSize: 12 };

type Key = keyof Omit<Inputs, "weatherYear" | "subsidyScheme">;
interface Ctl { k: Key; label: string; min: number; max: number; step: number; fmt: (v: number) => string; src: string }

const GROUPS: { title: string; items: Ctl[] }[] = [
  { title: "Subsidy & adoption", items: [
    { k: "subsidyPerKwh", label: "Battery subsidy", min: 0, max: 650, step: 25, fmt: (v) => `€${v}/kWh`, src: "EAG investment grant 2026: €150/kWh, only with new or extended PV, max 50 kWh. Retrofits: no federal grant; Upper Austria ended its retrofit grant on 1 Jul 2026" },
    { k: "baseAdoption2040", label: "Grid-serving battery uptake 2040 (no subsidy)", min: 0, max: 0.3, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Assumption; DE: ~20% of new PV with storage → share opting into grid control" },
    { k: "adoptionElasticity", label: "Adoption response to subsidy", min: 0, max: 4, step: 0.1, fmt: (v) => `×${v.toFixed(1)}`, src: "Uptake multiplier per 100% capex covered" },
    { k: "dsoFeePerBattery", label: "DSO availability fee", min: 0, max: 200, step: 10, fmt: (v) => `€${v}/yr`, src: "Flex market benchmarks (GOPACS, Piclo): €20-100/kW/yr" },
  ]},
  { title: "Home batteries", items: [
    { k: "batteryCostPerKwh2026", label: "Installed cost 2026", min: 300, max: 1000, step: 25, fmt: (v) => `€${v}/kWh`, src: "EUPD/BNEF residential DACH 2025: €550-800/kWh" },
    { k: "batteryCostDecline", label: "Cost decline", min: 0, max: 0.1, step: 0.005, fmt: (v) => `${(v * 100).toFixed(1)}%/yr`, src: "NREL ATB 2024 mid: 4-6%/yr" },
    { k: "batteryGridShare", label: "Capacity usable for grid in winter", min: 0.1, max: 1, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Dashboard §7.2: 32.6%" },
    { k: "peakHours", label: "Winter peak duration", min: 1, max: 12, step: 0.5, fmt: (v) => `${v} h`, src: "Dashboard cold-day profiles: 3-6 h above rating" },
    { k: "reliability", label: "Confirmed delivery (test calls)", min: 0.5, max: 1, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Dashboard test calls, weighted avg ≈ 82%" },
  ]},
  { title: "EVs", items: [
    { k: "smartParticipation", label: "EVs under smart charging", min: 0, max: 1, step: 0.05, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "§14a EnWG (DE) style mandate → 60-90%" },
    { k: "smartKwPerEv", label: "Peak kW shifted per EV", min: 0.5, max: 7, step: 0.25, fmt: (v) => `${v} kW`, src: "11 kW wallbox × ~25% coincidence" },
    { k: "v2gShare", label: "EVs with V2G", min: 0, max: 0.5, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Assumption; few models V2G-ready today" },
    { k: "v2gPremium", label: "Bidirectional charger premium", min: 500, max: 6000, step: 250, fmt: (v) => eur(v), src: "DC V2G wallbox 2025: €4-7k vs €1k AC" },
  ]},
  { title: "Grid & finance", items: [
    { k: "excessKw2030", label: "Avg excess per overloaded station 2030", min: 5, max: 300, step: 5, fmt: (v) => `${v} kW`, src: "Dashboard cases: 14-419 kW" },
    { k: "excessKw2040", label: "Avg excess per overloaded station 2040", min: 20, max: 600, step: 10, fmt: (v) => `${v} kW`, src: "Dashboard cases: 198-233 kW" },
    { k: "reinforcePerKw", label: "Reinforcement cost", min: 100, max: 1000, step: 25, fmt: (v) => `€${v}/kW`, src: "Transformer 630 kVA + LV cable: €250-600/kW (dena, E-Control)" },
    { k: "reinforceFixed", label: "Fixed cost per station touched", min: 0, max: 100000, step: 5000, fmt: eur, src: "Civil works, permits: €20-50k" },
    { k: "wacc", label: "Regulated WACC", min: 0.02, max: 0.08, step: 0.0025, fmt: (v) => `${(v * 100).toFixed(2)}%`, src: "E-Control 5th reg. period: 4.88%" },
  ]},
];

function Dashboard() {
  const [inp, setInp] = useState<Inputs>(DEFAULTS);
  const [focus, setFocus] = useState<2030 | 2040>(2040);
  const path = useMemo(() => runPath(inp), [inp]);
  const sweep = useMemo(() => subsidySweep(inp, focus), [inp, focus]);
  const r = path.find((p) => p.year === focus)!;
  const firm = firmKwPerBattery(inp);
  const set = (k: Key, v: number) => setInp((s) => ({ ...s, [k]: v }));

  const mix = path.map((p) => ({
    year: p.year, "Smart charging": Math.round(p.smartKw), V2G: Math.round(p.v2gKw),
    "Home batteries": Math.round(p.batteryKw), Reinforcement: Math.round(p.reinforceKw),
  }));
  const money = path.map((p) => ({
    year: p.year, Consumers: p.consumerCapex / 1e6, Subsidy: p.subsidy / 1e6, DSO: p.dsoCapex / 1e6,
    "Reinforce-only": p.baselineCapex / 1e6,
  }));
  const tariff = path.map((p) => ({ year: p.year, "With flexibility": +p.tariffPerHh.toFixed(2), "Reinforce only": +p.baselineTariffPerHh.toFixed(2) }));
  const flexShare = r.gapKw > 0 ? (r.gapKw - r.reinforceKw) / r.gapKw : 0;
  const totalFlex = r.consumerCapex + r.subsidy + r.dsoCapex;

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-5 py-10">
        <header className="mb-8 border-b border-border pb-6">
          <p className="text-sm uppercase tracking-widest text-primary">Steyr · 257 transformer stations · winter demand</p>
          <h1 className="mt-2 text-3xl font-bold text-foreground md:text-4xl">Who pays to keep the grid within limits?</h1>
          <p className="mt-3 max-w-3xl text-muted-foreground">
            Financial layer on top of the hackathon simulation. Each overloaded station's winter peak is covered in order of cost:
            smart charging, V2G, grid-serving home batteries, then grid reinforcement for whatever is left. Move the sliders to test scenarios.
          </p>
          <Link to="/flex-event" className="mt-3 inline-block text-sm text-primary hover:underline">Open the flexibility event dashboard →</Link>
        </header>

        <div className="mb-6 flex flex-wrap items-center gap-4">
          <Tabs value={String(focus)} onValueChange={(v) => setFocus(Number(v) as 2030 | 2040)}>
            <TabsList><TabsTrigger value="2030">2030</TabsTrigger><TabsTrigger value="2040">2040</TabsTrigger></TabsList>
          </Tabs>
          <Tabs value={inp.weatherYear} onValueChange={(v) => setInp((s) => ({ ...s, weatherYear: v as WeatherYear }))}>
            <TabsList>
              <TabsTrigger value="2023">2023 mild</TabsTrigger>
              <TabsTrigger value="2017">2017</TabsTrigger>
              <TabsTrigger value="2012">2012 cold spell</TabsTrigger>
            </TabsList>
          </Tabs>
          <button onClick={() => setInp(DEFAULTS)} className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent">Reset inputs</button>
        </div>

        <section className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-4">
          <Kpi label={`Peak gap ${focus}`} value={`${(r.gapKw / 1000).toFixed(1)} MW`} sub={`${r.overloaded} stations × ${num(r.excessKw)} kW`} />
          <Kpi label="Covered by flexibility" value={`${(flexShare * 100).toFixed(0)}%`} sub={`${num(r.reinforceKw)} kW still needs reinforcement`} />
          <Kpi label="Upfront investment (flex path)" value={eur(totalFlex)} sub={`vs ${eur(r.baselineCapex)} reinforce-only`} />
          <Kpi label="Subsidy required" value={eur(r.subsidy)} sub={`${num(r.batteries)} batteries · ${r.batteryKw > 0 ? eur(r.subsidy / r.batteryKw) : "–"} per firm kW`} />
          <Kpi label="Consumers pay upfront" value={eur(r.consumerCapex)} sub="battery share after subsidy + V2G chargers" />
          <Kpi label="DSO investment" value={eur(r.dsoCapex)} sub="reinforcement + control boxes + smart-charging control" />
          <Kpi label="Grid tariff / household / yr" value={`€${r.tariffPerHh.toFixed(2)}`} sub={`vs €${r.baselineTariffPerHh.toFixed(2)} reinforce-only`} />
          <Kpi label="Firm kW per battery" value={`${firm.toFixed(2)} kW`} sub={`of ${inp.batteryKw} kW nominal · ${eur(batteryCapex(inp, focus))} each in ${focus}`} />
        </section>

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="space-y-6">
            <Card title="Path to 2040: how the winter peak gap is closed (kW)">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mix}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="year" {...axis} /><YAxis {...axis} />
                  <Tooltip contentStyle={tip} /><Legend />
                  <Area dataKey="Smart charging" stackId="1" fill="var(--chart-1)" stroke="var(--chart-1)" />
                  <Area dataKey="V2G" stackId="1" fill="var(--chart-5)" stroke="var(--chart-5)" />
                  <Area dataKey="Home batteries" stackId="1" fill="var(--chart-3)" stroke="var(--chart-3)" />
                  <Area dataKey="Reinforcement" stackId="1" fill="var(--chart-4)" stroke="var(--chart-4)" />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Upfront investment needed by year: who pays (€m, cumulative stock)">
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={money}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="year" {...axis} /><YAxis {...axis} />
                  <Tooltip contentStyle={tip} formatter={(v: number) => `€${v.toFixed(2)}m`} /><Legend />
                  <Bar dataKey="DSO" stackId="a" fill="var(--chart-2)" />
                  <Bar dataKey="Subsidy" stackId="a" fill="var(--chart-3)" />
                  <Bar dataKey="Consumers" stackId="a" fill="var(--chart-1)" />
                  <Line dataKey="Reinforce-only" stroke="var(--chart-4)" strokeWidth={2} dot={false} strokeDasharray="5 4" />
                </ComposedChart>
              </ResponsiveContainer>
            </Card>

            <Card title={`What does subsidy buy in ${focus}? Extra firm battery capacity per €/kWh (EAG-style grant)`}>
              <ResponsiveContainer width="100%" height={280}>
                <ComposedChart data={sweep}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="subsidyPerKwh" {...axis} tickFormatter={(v) => `€${v}`} />
                  <YAxis yAxisId="kw" {...axis} />
                  <YAxis yAxisId="m" orientation="right" {...axis} />
                  <Tooltip contentStyle={tip} labelFormatter={(v) => `Subsidy €${v}/kWh`} /><Legend />
                  <Bar yAxisId="kw" dataKey="batteryKw" name="Firm battery kW" fill="var(--chart-3)" />
                  <Line yAxisId="m" dataKey="subsidyM" name="Subsidy (€m)" stroke="var(--chart-2)" strokeWidth={2} />
                  <Line yAxisId="m" dataKey="avoidedM" name="Net DSO capex avoided (€m)" stroke="var(--chart-1)" strokeWidth={2} />
                </ComposedChart>
              </ResponsiveContainer>
              <table className="mt-4 w-full text-sm">
                <thead className="text-muted-foreground"><tr className="border-b border-border">
                  <th className="py-2 text-left font-medium">Subsidy</th><th className="text-right font-medium">Firm kW</th>
                  <th className="text-right font-medium">Subsidy total</th><th className="text-right font-medium">€ subsidy per kW</th>
                  <th className="text-right font-medium">DSO capex avoided</th></tr></thead>
                <tbody className="font-mono-num">
                  {sweep.map((s) => (
                    <tr key={s.subsidyPerKwh} className={`border-b border-border/50 ${s.subsidyPerKwh === inp.subsidyPerKwh ? "text-primary" : "text-foreground"}`}>
                      <td className="py-1.5">€{s.subsidyPerKwh}/kWh</td><td className="text-right">{num(s.batteryKw)}</td>
                      <td className="text-right">€{s.subsidyM.toFixed(2)}m</td><td className="text-right">{s.eurPerKw ? eur(s.eurPerKw) : "–"}</td>
                      <td className="text-right">€{s.avoidedM.toFixed(2)}m</td></tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-3 text-xs text-muted-foreground">
                Compare "€ subsidy per kW" with the reinforcement cost of €{inp.reinforcePerKw}/kW: subsidy only pays off for society when it is lower.
              </p>
            </Card>

            <Card title="Grid tariff burden per household (€/yr, annuitised DSO cost)">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={tariff}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="year" {...axis} /><YAxis {...axis} />
                  <Tooltip contentStyle={tip} /><Legend />
                  <Bar dataKey="Reinforce only" fill="var(--chart-4)" />
                  <Bar dataKey="With flexibility" fill="var(--chart-2)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Takeaways at current settings">
              <ul className="list-disc space-y-2 pl-5 text-sm text-foreground">
                <li>In {focus}, flexibility covers <b>{(flexShare * 100).toFixed(0)}%</b> of the {(r.gapKw / 1000).toFixed(1)} MW winter gap; smart charging alone delivers {num(r.smartKw)} kW at almost no cost.</li>
                <li>A home battery gives only <b>{firm.toFixed(2)} firm kW</b> in a {inp.peakHours} h cold peak, so each firm kW costs about {eur(batteryCapex(inp, focus) / Math.max(firm, 0.01))} of hardware, versus €{inp.reinforcePerKw}/kW for reinforcement.</li>
                <li>Upfront: {eur(totalFlex)} on the flexibility path (consumers {eur(r.consumerCapex)}, subsidy {eur(r.subsidy)}, DSO {eur(r.dsoCapex)}) vs {eur(r.baselineCapex)} if the DSO reinforced everything.</li>
                <li>On the tariff, all Steyr households pay €{r.tariffPerHh.toFixed(2)}/yr instead of €{r.baselineTariffPerHh.toFixed(2)}.</li>
              </ul>
            </Card>

            <Card title="Method and sources">
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>Overloaded stations per year and weather year come from the dashboard (today / 2030 / 2040), linearly interpolated. EV share 8 / 25 / 60% as in the dashboard. Each station is assumed to serve {inp.householdsPerStation} households ({num(inp.totalHouseholds)} total, tariff base).</p>
                <p>Firm battery kW = min(5 kW × 0.85, 10 kWh × grid share ÷ peak hours) × confirmed delivery, following §7.2. Battery uptake rises with the share of cost covered by subsidy, capped by households at overloaded stations.</p>
                <p>Investment shows the stock needed by each year (not yearly spend). DSO cost is annuitised over {inp.assetLife} years at the regulated WACC and spread over all households. Consumer savings from self-consumption are not included; batteries are often bought for that reason alone.</p>
                <p>Subsidy: “EAG 2026” is today's federal grant (€{EAG_2026.perKwh}/kWh with new PV; announced reform 2027 shifts funding to batteries and energy management, rules not yet published). “Tiered (proposal)” is our profile: {TIER_SHARE.map((t) => `${t * 100}%`).join(" / ")} of the battery cost for tiers 0–3, box paid from tier 1.</p>
                <p>Benchmarks: E-Control regulatory WACC, EAG investment grant 2026, EUPD/BNEF battery prices, NREL ATB cost declines, dena distribution grid study (reinforcement €/kW), §14a EnWG smart-charging rules. All values are editable and should be replaced with Netz OÖ / Stadtbetriebe Steyr figures.</p>
              </div>
            </Card>
          </div>

          <aside className="space-y-5 lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-y-auto lg:pr-1">
            <SubsidyPanel inp={inp} setInp={setInp} />
            {GROUPS.map((g) => (
              <div key={g.title} className="rounded-lg border border-border bg-card p-4">
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-primary">{g.title}</h3>
                <div className="space-y-4">
                  {g.items.map((c) => (
                    <div key={c.k}>
                      <div className="flex justify-between text-sm">
                        <span className="text-foreground">{c.label}</span>
                        <span className="font-mono-num text-primary">{c.fmt(inp[c.k])}</span>
                      </div>
                      <Slider className="mt-2" min={c.min} max={c.max} step={c.step} value={[inp[c.k]]} onValueChange={(vals) => set(c.k, vals[0] ?? 0)} />
                      <p className="mt-1 text-[11px] text-muted-foreground">{c.src}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </aside>
        </div>
      </div>
    </div>
  );
}

function Kpi({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="font-mono-num mt-1 text-2xl font-semibold text-foreground">{value}</p>
      <p className="mt-1 text-xs text-muted-foreground">{sub}</p>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-border bg-card p-5">
      <h2 className="mb-4 text-base font-semibold text-foreground">{title}</h2>
      {children}
    </section>
  );
}

function SubsidyPanel({ inp, setInp }: { inp: Inputs; setInp: React.Dispatch<React.SetStateAction<Inputs>> }) {
  const tiered = inp.subsidyScheme === "tiered";
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-primary">Subsidy scheme</h3>
      <Tabs value={inp.subsidyScheme} onValueChange={(v) => setInp((s) => ({ ...s, subsidyScheme: v as SubsidyScheme }))}>
        <TabsList className="w-full">
          <TabsTrigger value="eag2026" className="flex-1">EAG 2026 (today)</TabsTrigger>
          <TabsTrigger value="tiered" className="flex-1">Tiered (proposal)</TabsTrigger>
        </TabsList>
      </Tabs>
      {tiered ? (
        <div className="mt-3 space-y-1">
          {TIER_LABEL.map((label, t) => (
            <button key={t} onClick={() => setInp((s) => ({ ...s, subsidyTier: t }))}
              className={`flex w-full justify-between rounded-md border px-2 py-1 text-left text-xs ${inp.subsidyTier === t ? "border-primary text-foreground" : "border-border text-muted-foreground hover:bg-accent"}`}>
              <span>Tier {label}</span><span className="font-mono-num">{(TIER_SHARE[t] ?? 0) * 100}%</span>
            </button>
          ))}
          <p className="pt-1 text-[11px] text-muted-foreground">Grid-serving in winter needs tier 2 or higher. From tier 1 the subsidy also pays the box.</p>
        </div>
      ) : (
        <p className="mt-3 text-[11px] text-muted-foreground">Federal EAG grant: fixed €{EAG_2026.perKwh}/kWh, only with new or extended PV, no control obligation. Set the amount with the slider below.</p>
      )}
    </div>
  );
}
