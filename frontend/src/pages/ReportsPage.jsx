import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader, EmptyState } from "@/components/PageHeader";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PnlTable } from "@/components/reports/PnlTable";
import { ExpenseBreakdownChart } from "@/components/reports/ExpenseBreakdownChart";
import { RevenueCostChart } from "@/components/reports/RevenueCostChart";
import { CostPerUnitTable } from "@/components/reports/CostPerUnitTable";
import { api, errorMessage } from "@/lib/api";
import { addMonths, endOfMonth, formatDate, formatQty, todayMuscat } from "@/lib/format";
import { cn } from "@/lib/utils";

const SUMMARY = [
  { key: "net_revenue", label: "Net Revenue", hint: "Sales + other income − returns", accent: "bg-sky-500" },
  { key: "gross_profit", label: "Gross Profit", hint: "Net revenue − COGS", signed: true },
  { key: "operating_profit", label: "Operating Profit", hint: "Gross profit − operating expenses", signed: true },
  { key: "net_profit", label: "Net Profit", hint: "Operating profit − other", signed: true },
];

function Card({ title, subtitle, children, testId }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm fade-up" data-testid={testId}>
      <h2 className="text-lg font-semibold tracking-tight text-slate-900">{title}</h2>
      {subtitle && <p className="mb-4 text-sm text-slate-500">{subtitle}</p>}
      {children}
    </section>
  );
}

export default function ReportsPage() {
  const today = todayMuscat();
  const [start, setStart] = useState(addMonths(today, -2));
  const [end, setEnd] = useState(endOfMonth(today));
  const [granularity, setGranularity] = useState("monthly");
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = useCallback(async (s, e, g) => {
    if (!s || !e) return setError("Start and end dates are required");
    if (s > e) return setError("Start date must be before end date");
    setError("");
    setLoading(true);
    try {
      const { data } = await api.get("/reports/pnl", { params: { start: s, end: e, granularity: g } });
      setReport(data);
    } catch (err) {
      toast.error(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { run(start, end, granularity); }, [granularity]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div data-testid="reports-page">
      <PageHeader eyebrow="Analysis" title="Reports" description={report ? `${formatDate(report.start)} – ${formatDate(report.end)} · ${report.granularity === "daily" ? "Daily" : "Monthly"} view` : "Choose a period"} />

      <div className="mb-8 flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm" data-testid="report-filters">
        <div className="space-y-1.5">
          <Label htmlFor="start">Start date</Label>
          <Input id="start" type="date" value={start} onChange={(e) => setStart(e.target.value)} className="h-10 w-44" data-testid="filter-start-date" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="end">End date</Label>
          <Input id="end" type="date" value={end} onChange={(e) => setEnd(e.target.value)} className="h-10 w-44" data-testid="filter-end-date" />
        </div>
        <div className="space-y-1.5">
          <Label>View</Label>
          <div className="flex h-10 rounded-md border border-slate-200 bg-slate-50 p-1" data-testid="report-granularity-toggle">
            {["daily", "monthly"].map((g) => (
              <button key={g} type="button" onClick={() => setGranularity(g)} data-testid={`report-toggle-${g}`}
                className={cn("rounded px-4 text-sm capitalize transition-colors", granularity === g ? "bg-white font-medium text-blue-800 shadow-sm" : "text-slate-500 hover:text-slate-800")}>
                {g}
              </button>
            ))}
          </div>
        </div>
        <Button onClick={() => run(start, end, granularity)} disabled={loading} className="h-10 bg-blue-700 hover:bg-blue-800" data-testid="report-apply-button">
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} Apply
        </Button>
        {error && <p className="w-full text-sm font-medium text-rose-600" data-testid="report-date-error">{error}</p>}
      </div>

      {report && (
        <div className={cn("space-y-8 transition-opacity", loading && "opacity-60")}>
          {!report.has_data && <EmptyState testId="report-empty-state" />}
          <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
            {SUMMARY.map(({ key, ...c }, i) => <KpiCard key={key} {...c} value={report.total[key]} delay={i * 50} testId={`report-kpi-${key}`} />)}
          </div>
          {report.warnings.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800" data-testid="report-warnings">
              <p className="flex items-center gap-2 font-medium"><AlertTriangle className="h-4 w-4" /> {report.warnings.length} consumption line(s) valued at OMR 0.000: no purchase cost found</p>
              <ul className="mt-1 list-disc pl-6 text-xs">
                {report.warnings.slice(0, 5).map((w) => <li key={w.id}>{formatDate(w.date)} · {w.material} · {formatQty(w.qty_used)}</li>)}
              </ul>
            </div>
          )}
          <Card title="P&L summary" subtitle="One row per period, with a total row" testId="pnl-summary-card">
            <PnlTable rows={report.rows} total={report.total} daily={report.granularity === "daily"} />
          </Card>
          <div className="grid gap-8 2xl:grid-cols-2">
            <Card title="Expense breakdown" subtitle="COGS, operating and other expenses by category" testId="expense-breakdown-card">
              <ExpenseBreakdownChart items={report.expense_breakdown} />
            </Card>
            <Card title="Revenue vs cost" subtitle="Net revenue against total cost over the range" testId="revenue-cost-card">
              <RevenueCostChart rows={report.rows} />
            </Card>
          </div>
          <Card title="Cost per unit produced" subtitle="Total production cost ÷ quantity, from finished goods in the range" testId="cost-per-unit-card">
            <CostPerUnitTable data={report.cost_per_unit} />
          </Card>
        </div>
      )}
    </div>
  );
}
