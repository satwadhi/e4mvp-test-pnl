import { Money } from "@/components/Money";
import { formatQty } from "@/lib/format";

function Row({ label, data, testId, total }) {
  return (
    <tr className={total ? "border-t-2 border-slate-300 bg-slate-50 font-semibold" : "border-b border-slate-100"} data-testid={testId}>
      <td className="px-3 py-2 text-slate-700">{label}</td>
      <td className="num px-3 py-2 text-right text-slate-700">{formatQty(data.qty)}</td>
      <td className="px-3 py-2 text-right"><Money value={data.total_cost} /></td>
      <td className="px-3 py-2 text-right font-medium text-slate-900" data-testid={`${testId}-cpu`}>
        {data.cost_per_unit == null ? <span className="text-slate-400">—</span> : <Money value={data.cost_per_unit} />}
      </td>
    </tr>
  );
}

export function CostPerUnitTable({ data }) {
  return (
    <div className="overflow-auto rounded-lg border border-slate-200" data-testid="cost-per-unit-table">
      <table className="w-full border-collapse text-left text-[13px]">
        <thead className="bg-slate-100">
          <tr>
            {["Product", "Quantity produced", "Total production cost", "Cost per unit"].map((h, i) => (
              <th key={h} className={`px-3 py-2.5 text-xs font-semibold uppercase tracking-wider text-slate-500 ${i ? "text-right" : ""}`}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white">
          {data.products.length === 0 && (
            <tr><td colSpan={4} className="px-3 py-4 text-center text-slate-500" data-testid="cost-per-unit-empty">No finished goods in this period</td></tr>
          )}
          {data.products.map((p) => (
            <Row key={p.product} label={p.product} data={p} testId={`cpu-row-${p.product.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`} />
          ))}
          <Row label="Overall" data={data.overall} testId="cpu-row-overall" total />
        </tbody>
      </table>
    </div>
  );
}
