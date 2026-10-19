import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartTooltip } from "@/components/ChartTooltip";
import { formatCompact } from "@/lib/format";

const GROUP_COLORS = { cogs: "#E11D48", opex: "#D97706", other: "#7C3AED" };
const LEGEND = [["cogs", "COGS"], ["opex", "Operating expenses"], ["other", "Other"]];

export function ExpenseBreakdownChart({ items }) {
  return (
    <div data-testid="expense-breakdown-chart">
      <div className="mb-2 flex gap-4 text-xs text-slate-500">
        {LEGEND.map(([k, l]) => (
          <span key={k} className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm" style={{ background: GROUP_COLORS[k] }} />{l}</span>
        ))}
      </div>
      <div className="h-[420px]">
        <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 800, height: 320 }}>
          <BarChart data={items} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
            <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" horizontal={false} />
            <XAxis type="number" tickFormatter={formatCompact} tick={{ fontSize: 11, fill: "#64748B" }} tickLine={false} axisLine={false} />
            <YAxis type="category" dataKey="label" width={170} tick={{ fontSize: 11, fill: "#475569" }} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "#F1F5F9" }} />
            <Bar dataKey="amount" name="Amount" radius={[0, 4, 4, 0]} barSize={16}>
              {items.map((it) => <Cell key={it.slug} fill={GROUP_COLORS[it.group]} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
