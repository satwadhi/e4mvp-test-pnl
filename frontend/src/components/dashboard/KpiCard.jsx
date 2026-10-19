import { Money } from "@/components/Money";
import { isNegative } from "@/lib/format";
import { cn } from "@/lib/utils";

export function KpiCard({ label, hint, value, signed, accent, loading, delay = 0, testId }) {
  const neg = signed && isNegative(value);
  const bar = signed ? (neg ? "bg-rose-500" : "bg-emerald-500") : accent;
  const id = testId || `kpi-${label.toLowerCase().replace(/[^a-z]+/g, "-")}`;
  return (
    <div
      className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-colors duration-200 hover:border-slate-300 fade-up"
      style={{ animationDelay: `${delay}ms` }}
      data-testid={id}
    >
      <span className={cn("absolute inset-x-0 top-0 h-1", bar)} />
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      {loading ? (
        <div className="mt-3 h-7 w-3/4 animate-pulse rounded bg-slate-100" />
      ) : (
        <Money value={value} signed={signed} className="mt-2 block text-xl font-bold tracking-tight text-slate-900 xl:text-[22px]" data-testid={`${id}-value`} />
      )}
      <p className="mt-2 text-xs text-slate-400">{hint}</p>
    </div>
  );
}
