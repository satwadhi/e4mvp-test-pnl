import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ChartTooltip } from "@/components/ChartTooltip";
import { formatCompact } from "@/lib/format";

export function TrendChart({ rows }) {
  return (
    <div className="h-[320px]" data-testid="trend-chart">
      <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 800, height: 320 }}>
        <LineChart data={rows} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: "#64748B" }} tickLine={false} axisLine={{ stroke: "#CBD5E1" }} />
          <YAxis tickFormatter={formatCompact} tick={{ fontSize: 12, fill: "#64748B" }} tickLine={false} axisLine={false} width={56} />
          <Tooltip content={<ChartTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <ReferenceLine y={0} stroke="#94A3B8" />
          <Line type="monotone" dataKey="net_revenue" name="Revenue" stroke="#0284C7" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="total_cost" name="Total cost" stroke="#E11D48" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="net_profit" name="Net profit" stroke="#059669" strokeWidth={2.5} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
