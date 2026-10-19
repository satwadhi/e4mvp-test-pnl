import { formatOMR } from "@/lib/format";

export function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white/95 px-3 py-2 shadow-lg backdrop-blur" data-testid="chart-tooltip">
      <p className="mb-1 text-xs font-semibold text-slate-700">{label}</p>
      {payload.map((p) => (
        <div key={p.dataKey} className="flex items-center justify-between gap-4 text-xs">
          <span className="flex items-center gap-1.5 text-slate-500">
            <span className="h-2 w-2 rounded-full" style={{ background: p.color || p.payload?.fill }} />
            {p.name}
          </span>
          <span className="num font-medium text-slate-800">{formatOMR(p.value)}</span>
        </div>
      ))}
    </div>
  );
}
