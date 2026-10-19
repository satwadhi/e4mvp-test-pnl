import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartTooltip } from "@/components/ChartTooltip";
import { formatCompact } from "@/lib/format";

export function RevenueCostChart({ rows }) {
  const dots = rows.length <= 31;
  return (
    <div className="h-[440px]" data-testid="revenue-cost-chart">
      <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 800, height: 320 }}>
        <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#64748B" }} tickLine={false} axisLine={{ stroke: "#CBD5E1" }} minTickGap={16} />
          <YAxis tickFormatter={formatCompact} tick={{ fontSize: 11, fill: "#64748B" }} tickLine={false} axisLine={false} width={56} />
          <Tooltip content={<ChartTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line type="monotone" dataKey="net_revenue" name="Net revenue" stroke="#0284C7" strokeWidth={2} dot={dots && { r: 3 }} />
          <Line type="monotone" dataKey="total_cost" name="Total cost" stroke="#E11D48" strokeWidth={2} dot={dots && { r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
