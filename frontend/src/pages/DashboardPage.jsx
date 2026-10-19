import { useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { PageHeader, EmptyState } from "@/components/PageHeader";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { toast } from "sonner";

const CARDS = [
  { key: "net_revenue", label: "Total Revenue", hint: "Sales + other income − returns", accent: "bg-sky-500" },
  { key: "cogs", label: "Total COGS", hint: "Materials consumed + labour + machine", accent: "bg-rose-500" },
  { key: "opex", label: "Total Operating Expenses", hint: "Salaries, utilities, rent & more", accent: "bg-amber-500" },
  { key: "gross_profit", label: "Gross Profit", hint: "Net revenue − COGS", signed: true },
  { key: "net_profit", label: "Net Profit", hint: "After operating & other costs", signed: true },
];

export default function DashboardPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/dashboard").then((r) => setData(r.data)).catch((e) => toast.error(errorMessage(e)));
  }, []);

  return (
    <div data-testid="dashboard-page">
      <PageHeader eyebrow="Overview" title="Dashboard" description={data ? <span data-testid="dashboard-period-label">{data.period_label}</span> : "Loading…"} />
      {data && !data.has_data && <div className="mb-6"><EmptyState testId="dashboard-empty-state" /></div>}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 2xl:grid-cols-5">
        {CARDS.map(({ key, ...c }, i) => (
          <KpiCard key={key} {...c} value={data?.cards[key]} loading={!data} delay={i * 50} />
        ))}
      </div>
      <div className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm fade-up" data-testid="trend-chart-card">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-slate-900">12-month trend</h2>
            <p className="text-sm text-slate-500">Revenue, total cost and net profit by month (current month to date)</p>
          </div>
        </div>
        {data ? <TrendChart rows={data.trend} /> : <div className="h-[320px] animate-pulse rounded-md bg-slate-100" />}
      </div>
    </div>
  );
}
