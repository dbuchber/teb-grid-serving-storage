import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, ComposedChart, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import {
  FLEX_DEFAULTS, type FlexInputs, flexEvent, spreadSweep, p2pBuyerPrice,
  HOUSEHOLD_DEFAULTS, type HouseholdInputs, type SubsidyScheme, householdBattery, EAG_2026, TIER_LABEL, TIER_SHARE,
} from "@/lib/model";

export const Route = createFileRoute("/flex-event")({
  head: () => ({
    meta: [
      { title: "Flexibility Event: Net Consumer Price & Never-Worse-Off Check" },
      { name: "description", content: "Interactive model of a winter flexibility event in Steyr: spot prices, avoided costs, fees, battery wear and the never-worse-off guarantee." },
      { property: "og:title", content: "Flexibility Event: Net Consumer Price & Never-Worse-Off Check" },
      { property: "og:description", content: "Adjust spot prices, grid fees and DSO payments to see what one flexibility event earns a household." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: FlexEventPage,
});

const e2 = (v: number) => `${v < 0 ? "−" : ""}€${Math.abs(v).toFixed(2)}`;
const ct = (v: number) => `${v.toFixed(1)} ct`;
const tip = { background: "var(--card)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--foreground)" };
const axis = { stroke: "var(--muted-foreground)", fontSize: 12 };

type Key = keyof FlexInputs;
interface Ctl { k: Key; label: string; min: number; max: number; step: number; fmt: (v: number) => string; src: string }

const GROUPS: { title: string; items: Ctl[] }[] = [
  { title: "Wholesale & P2P prices", items: [
    { k: "spotCharge", label: "Spot price when charging (night)", min: -5, max: 30, step: 0.5, fmt: ct, src: "EPEX AT winter night ≈ 8 ct (unverified estimate)" },
    { k: "spotPeak", label: "Spot price at evening peak", min: 0, max: 50, step: 0.5, fmt: ct, src: "EPEX AT winter 17–21 h ≈ 15–20 ct (unverified estimate)" },
    { k: "p2pPrice", label: "Energy-community sharing price", min: 0, max: 25, step: 0.5, fmt: ct, src: "Typical AT energy communities 8–12 ct" },
    { k: "ecGridDiscount", label: "Energy-community grid-fee discount", min: 0, max: 0.6, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Local 28%, regional 57%" },
  ]},
  { title: "Fees & taxes", items: [
    { k: "supplierMargin", label: "Supplier margin (dynamic tariff)", min: 0, max: 5, step: 0.1, fmt: ct, src: "≈ 1.5 ct (estimate)" },
    { k: "gridFee", label: "Grid usage fee + losses", min: 0, max: 15, step: 0.1, fmt: ct, src: "Netz OÖ household ≈ 7 ct (estimate)" },
    { k: "levies", label: "Taxes & levies", min: 0, max: 6, step: 0.1, fmt: ct, src: "Electricity tax + renewables fee ≈ 2.5 ct (estimate)" },
    { k: "vat", label: "VAT", min: 0, max: 0.25, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Austria 20%" },
  ]},
  { title: "Battery", items: [
    { k: "batteryKwh", label: "Battery size", min: 3, max: 20, step: 0.5, fmt: (v) => `${v} kWh`, src: "Typical home battery 5–15 kWh" },
    { k: "gridShare", label: "Share kept for the grid", min: 0.1, max: 1, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Hackathon dashboard: 32.6%" },
    { k: "efficiency", label: "Round-trip efficiency", min: 0.7, max: 1, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Li-ion 88–94%" },
    { k: "peakHours", label: "Peak duration", min: 1, max: 8, step: 0.5, fmt: (v) => `${v} h`, src: "Dashboard cold-day profiles" },
    { k: "reliability", label: "Confirmed delivery", min: 0.5, max: 1, step: 0.01, fmt: (v) => `${(v * 100).toFixed(0)}%`, src: "Dashboard test calls ≈ 82%" },
    { k: "batteryCostPerKwh", label: "Installed cost", min: 300, max: 1000, step: 25, fmt: (v) => `€${v}/kWh`, src: "DACH 2025: €550–800/kWh" },
    { k: "cycleLife", label: "Cycle life", min: 2000, max: 10000, step: 250, fmt: (v) => `${v}`, src: "LFP warranties 6,000+" },
  ]},
  { title: "Grid company contract", items: [
    { k: "dsoFeeYear", label: "Availability payment", min: 0, max: 200, step: 5, fmt: (v) => `€${v}/yr`, src: "Assumption (flex markets €20–100/kW/yr)" },
    { k: "eventsPerYear", label: "Events per year", min: 1, max: 120, step: 1, fmt: (v) => `${v}`, src: "Assumption: ~20 cold-peak days" },
    { k: "opportunityCost", label: "Value lost elsewhere per event", min: 0, max: 3, step: 0.05, fmt: e2, src: "0 in winter: grid peak = own peak" },
  ]},
];

function FlexEventPage() {
  const [f, setF] = useState<FlexInputs>(FLEX_DEFAULTS);
  const [h, setH] = useState<HouseholdInputs>(HOUSEHOLD_DEFAULTS);
  const e = useMemo(() => flexEvent(f), [f]);
  const hb = useMemo(() => householdBattery(f, h), [f, h]);
  const sweep = useMemo(() => spreadSweep(f), [f]);
  const set = (k: Key, v: number) => setF((s) => ({ ...s, [k]: v }));

  const waterfall = [
    { name: "Charge cost", v: -e.chargeCost },
    { name: "Avoided peak buy", v: e.avoidedCost },
    { name: "Battery wear", v: -e.degradation },
    { name: "Lost elsewhere", v: -e.opportunity },
    { name: "Grid payment", v: e.fee },
    { name: "Guarantee top-up", v: e.topUp },
    { name: "Final result", v: e.final, total: true },
  ];
  const priceStack = [
    { name: "Night (charge)", Spot: f.spotCharge, Margin: f.supplierMargin, "Grid fee": f.gridFee, Levies: f.levies, VAT: e.chargePrice - (f.spotCharge + f.supplierMargin + f.gridFee + f.levies) },
    { name: "Evening peak", Spot: f.spotPeak, Margin: f.supplierMargin, "Grid fee": f.gridFee, Levies: f.levies, VAT: e.peakPrice - (f.spotPeak + f.supplierMargin + f.gridFee + f.levies) },
    { name: "Energy community", Spot: f.p2pPrice, Margin: f.supplierMargin, "Grid fee": f.gridFee * (1 - f.ecGridDiscount), Levies: f.levies, VAT: p2pBuyerPrice(f) - (f.p2pPrice + f.supplierMargin + f.gridFee * (1 - f.ecGridDiscount) + f.levies) },
  ];
  const safe = e.net >= 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-5 py-10">
        <header className="mb-8 border-b border-border pb-6">
          <Link to="/" className="text-sm text-primary hover:underline">← Cost model 2030/2040</Link>
          <p className="mt-4 text-sm uppercase tracking-widest text-primary">One winter evening · one household battery</p>
          <h1 className="mt-2 text-3xl font-bold text-foreground md:text-4xl">Flexibility event: is the household ever worse off?</h1>
          <p className="mt-3 max-w-3xl text-muted-foreground">
            The battery charges at night, then covers the home's own demand during the 17–21 h transformer peak. Move the sliders to change
            prices, fees and the contract. Price defaults are rounded 2025 estimates, not verified live data.
          </p>
        </header>

        <div className="mb-6 flex gap-3">
          <button onClick={() => setF(FLEX_DEFAULTS)} className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent">Reset inputs</button>
          <button onClick={() => setF((s) => ({ ...s, spotCharge: 15, spotPeak: 15 }))} className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent">Worst case: flat prices</button>
          <button onClick={() => setF((s) => ({ ...s, dsoFeeYear: 0 }))} className="rounded-md border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent">No grid payment</button>
        </div>

        <section className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-4">
          <Kpi label="Net price night" value={ct(e.chargePrice)} sub="per kWh incl. fees & VAT" />
          <Kpi label="Net price peak" value={ct(e.peakPrice)} sub={`energy community: ${ct(p2pBuyerPrice(f))}`} />
          <Kpi label="Energy per event" value={`${e.deliveredKwh.toFixed(2)} kWh`} sub={`${e.firmKw.toFixed(2)} kW firm · ${e.chargedKwh.toFixed(2)} kWh charged`} />
          <Kpi label="Result before guarantee" value={e2(e.net)} sub={safe ? "household gains without top-up" : "top-up needed"} />
          <Kpi label="Guarantee top-up" value={e2(e.topUp)} sub="max(0, −result), paid by grid company" />
          <Kpi label="Final household result" value={e2(e.final)} sub="never below €0" />
          <Kpi label="Break-even payment" value={e2(e.breakEvenFee)} sub={`per event · now ${e2(e.fee)}`} />
          <Kpi label="Household gain per year" value={e2(e.annual)} sub={`${f.eventsPerYear} events`} />
        </section>

        <div className={`mb-8 rounded-lg border p-4 ${safe ? "border-primary bg-card" : "border-destructive bg-card"}`}>
          <p className="font-semibold text-foreground">{safe ? "Never worse off: holds without the guarantee" : "Never worse off: holds only because of the guarantee"}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Result = payment {e2(e.fee)} + price gain {e2(e.arbitrage)} − wear {e2(e.degradation)} − lost value {e2(e.opportunity)} = <b className="text-foreground">{e2(e.net)}</b>.
            {" "}Top-up = max(0, −result) = {e2(e.topUp)}, so the final result is {e2(e.final)} ≥ €0 for any inputs.
          </p>
        </div>

        <MyBattery f={f} h={h} setH={setH} hb={hb} />

        <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
          <div className="space-y-6">
            <Card title="Household cash flow for one event (€)">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={waterfall}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="name" {...axis} interval={0} fontSize={11} /><YAxis {...axis} />
                  <Tooltip contentStyle={tip} formatter={(v: number) => e2(v)} />
                  <ReferenceLine y={0} stroke="var(--muted-foreground)" />
                  <Bar dataKey="v" name="€">
                    {waterfall.map((w, i) => (
                      <Cell key={i} fill={w.total ? "var(--primary)" : w.v >= 0 ? "var(--chart-1)" : "var(--chart-4)"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="What a kWh costs: spot price plus fees (ct/kWh)">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={priceStack} layout="vertical">
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis type="number" {...axis} /><YAxis type="category" dataKey="name" width={120} {...axis} />
                  <Tooltip contentStyle={tip} formatter={(v: number) => ct(v)} /><Legend />
                  <Bar dataKey="Spot" stackId="a" fill="var(--chart-1)" />
                  <Bar dataKey="Margin" stackId="a" fill="var(--chart-2)" />
                  <Bar dataKey="Grid fee" stackId="a" fill="var(--chart-3)" />
                  <Bar dataKey="Levies" stackId="a" fill="var(--chart-4)" />
                  <Bar dataKey="VAT" stackId="a" fill="var(--chart-5)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card title="Proof check: household result across peak spot prices (€ per event)">
              <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={sweep}>
                  <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
                  <XAxis dataKey="spotPeak" {...axis} label={{ value: "peak spot price (ct/kWh)", position: "insideBottom", offset: -4, fill: "var(--muted-foreground)", fontSize: 12 }} />
                  <YAxis {...axis} />
                  <Tooltip contentStyle={tip} formatter={(v: number) => e2(v)} /><Legend verticalAlign="top" />
                  <ReferenceLine y={0} stroke="var(--destructive)" strokeDasharray="4 4" />
                  <Bar dataKey="topUp" name="Guarantee top-up" fill="var(--chart-4)" />
                  <Line dataKey="net" name="Before guarantee" stroke="var(--chart-1)" strokeWidth={2} />
                  <Line dataKey="final" name="After guarantee" stroke="var(--primary)" strokeWidth={2} strokeDasharray="5 3" />
                </ComposedChart>
              </ResponsiveContainer>
              <p className="mt-2 text-xs text-muted-foreground">The line after the guarantee never drops below the red zero line, whatever the price.</p>
            </Card>
          </div>

          <aside className="space-y-5">
            {GROUPS.map((g) => (
              <div key={g.title} className="rounded-lg border border-border bg-card p-4">
                <h3 className="mb-3 text-sm font-semibold text-foreground">{g.title}</h3>
                <div className="space-y-4">
                  {g.items.map((c) => (
                    <div key={c.k}>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{c.label}</span>
                        <span className="font-mono-num text-foreground">{c.fmt(f[c.k])}</span>
                      </div>
                      <Slider className="mt-2" min={c.min} max={c.max} step={c.step} value={[f[c.k]]} onValueChange={(vals) => set(c.k, vals[0] ?? 0)} />
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

const eur0 = (v: number) => `€${Math.round(v).toLocaleString("en-US")}`;

function MyBattery({ f, h, setH, hb }: {
  f: FlexInputs; h: HouseholdInputs; setH: React.Dispatch<React.SetStateAction<HouseholdInputs>>;
  hb: ReturnType<typeof householdBattery>;
}) {
  const tiered = h.scheme === "tiered";
  return (
    <section className="mb-8 rounded-lg border border-border bg-card p-5">
      <h2 className="text-base font-semibold text-foreground">My battery: subsidy, own cost and how hard the grid calls work it</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        A {f.batteryKwh} kWh battery at €{f.batteryCostPerKwh}/kWh plus the control box. Compare today's federal grant with our tiered proposal.
      </p>
      <div className="mt-4 grid gap-6 lg:grid-cols-[320px_1fr]">
        <div className="space-y-3">
          <Tabs value={h.scheme} onValueChange={(v) => setH((s) => ({ ...s, scheme: v as SubsidyScheme }))}>
            <TabsList className="w-full">
              <TabsTrigger value="eag2026" className="flex-1">EAG 2026 (today)</TabsTrigger>
              <TabsTrigger value="tiered" className="flex-1">Tiered (proposal)</TabsTrigger>
            </TabsList>
          </Tabs>
          {tiered ? (
            <div className="space-y-1">
              {TIER_LABEL.map((label, t) => (
                <button key={t} onClick={() => setH((s) => ({ ...s, tier: t }))}
                  className={`flex w-full justify-between rounded-md border px-2 py-1 text-left text-xs ${h.tier === t ? "border-primary text-foreground" : "border-border text-muted-foreground hover:bg-accent"}`}>
                  <span>Tier {label}</span><span className="font-mono-num">{(TIER_SHARE[t] ?? 0) * 100}%</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-2 text-sm">
              <label className="flex items-center justify-between gap-3 text-muted-foreground">
                Bought with new or extended PV <Switch checked={h.newPv} onCheckedChange={(v) => setH((s) => ({ ...s, newPv: v }))} />
              </label>
              <label className="flex items-center justify-between gap-3 text-muted-foreground">
                “Made in Europe” bonus (up to +30 %) <Switch checked={h.madeInEurope} onCheckedChange={(v) => setH((s) => ({ ...s, madeInEurope: v }))} />
              </label>
            </div>
          )}
          <p className="text-[11px] text-muted-foreground">
            {tiered
              ? "Our proposal: subsidy rises with how much control the household allows; the box is paid from tier 1. Winter discharge calls need tier 2."
              : `EAG investment grant 2026: €${EAG_2026.perKwh}/kWh, max ${EAG_2026.maxKwh} kWh, only with new or extended PV. A retrofit to existing PV gets no grant today; Upper Austria ended its retrofit grant on 1 Jul 2026. Reform announced for 2027.`}
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <Kpi label="Battery + box" value={eur0(hb.batteryCost + hb.boxCost)} sub={`battery ${eur0(hb.batteryCost)} · box ${eur0(hb.boxCost)}`} />
          <Kpi label="Subsidy" value={eur0(hb.subsidy.total)} sub={`battery ${eur0(hb.subsidy.battery)} · box ${eur0(hb.subsidy.box)}`} />
          <Kpi label="Own cost" value={eur0(hb.ownCost)} sub="after subsidy" />
          <Kpi label="Grid income per year" value={e2(hb.gridIncomeYear)} sub={`${hb.callsYear} calls · never below €0`} />
          <Kpi label="Extra cycles per year" value={hb.extraCyclesYear.toFixed(1)} sub="full cycles caused by grid calls" />
          <Kpi label={`Cycle life used in ${h.years} years`} value={`${(hb.lifeShare * 100).toFixed(1)} %`} sub={`of ${f.cycleLife.toLocaleString("en-US")} cycles`} />
          <Kpi label="Wear per year" value={e2(hb.wearYear)} sub="covered by the grid payment" />
          <Kpi label="Calls per year" value={String(hb.callsYear)} sub={hb.callsYear ? "set in the contract below" : "no discharge calls at this tier"} />
        </div>
      </div>
    </section>
  );
}
