import { Money } from "@/components/Money";

const COLS = [
  { key: "net_revenue", label: "Net Revenue" },
  { key: "cogs", label: "COGS" },
  { key: "gross_profit", label: "Gross Profit", signed: true },
  { key: "opex", label: "Operating Expenses" },
  { key: "operating_profit", label: "Operating Profit", signed: true },
  { key: "other", label: "Other" },
  { key: "net_profit", label: "Net Profit", signed: true },
];

function Row({ row, label, testId, total }) {
  return (
    <tr className={total ? "border-t-2 border-slate-300 bg-slate-50 font-semibold" : "border-b border-slate-100 hover:bg-slate-50/70"} data-testid={testId}>
      <td className="whitespace-nowrap px-2 py-2 text-slate-700">{label}</td>
      {COLS.map((c) => (
        <td key={c.key} className="px-2 py-2 text-right" data-testid={`${testId}-${c.key}`}>
          <Money value={row[c.key]} signed={c.signed} className={`tracking-tight ${c.signed ? "" : "text-slate-700"}`} />
        </td>
      ))}
    </tr>
  );
}

export function PnlTable({ rows, total, daily }) {
  return (
    <div className={`overflow-auto rounded-lg border border-slate-200 ${daily ? "max-h-[520px]" : ""}`} data-testid="pnl-table">
      <table className="w-full border-collapse text-left text-xs">
        <thead className="sticky top-0 z-10 bg-slate-100">
          <tr>
            <th className="px-2 py-2.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{daily ? "Day" : "Month"}</th>
            {COLS.map((c) => (
              <th key={c.key} className="px-2 py-2.5 text-right text-[11px] font-semibold uppercase tracking-wide text-slate-500">{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white">
          {rows.map((r) => <Row key={r.period} row={r} label={r.label} testId={`pnl-row-${r.period}`} />)}
          <Row row={total} label="Total" testId="pnl-row-total" total />
        </tbody>
      </table>
    </div>
  );
}
