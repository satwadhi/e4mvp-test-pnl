import { AlertTriangle, Pencil, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Money } from "@/components/Money";
import { formatDate, formatMonth, formatQty } from "@/lib/format";
import { isNumericField } from "@/lib/validate";

function Cell({ field, value }) {
  if (value == null) return <span className="text-slate-400">—</span>;
  if (field.type === "money") return <Money value={value} />;
  if (field.type === "quantity") return <span className="num">{formatQty(value)}</span>;
  if (field.type === "date") return <span className="whitespace-nowrap">{formatDate(value)}</span>;
  if (field.type === "month") return <span className="whitespace-nowrap">{formatMonth(value)}</span>;
  return <span>{value}</span>;
}

function DeleteButton({ record, onDelete }) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-rose-600" data-testid={`delete-record-${record.id}`}>
          <Trash2 className="h-4 w-4" />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent data-testid="delete-confirm-dialog">
        <AlertDialogHeader>
          <AlertDialogTitle>Delete this record?</AlertDialogTitle>
          <AlertDialogDescription>It will be removed from this list and from every total. This cannot be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel data-testid="delete-cancel-button">Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => onDelete(record)} className="bg-rose-600 hover:bg-rose-700" data-testid="delete-confirm-button">Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

export function RecordsTable({ category, items, onEdit, onDelete }) {
  const cols = [...category.fields, ...category.computed];
  const right = (f) => isNumericField(f);
  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm fade-up" data-testid="records-table">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              {cols.map((f) => (
                <th key={f.key} className={`whitespace-nowrap px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-500 ${right(f) ? "text-right" : ""}`}>{f.label}</th>
              ))}
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items === null && (
              <tr><td colSpan={cols.length + 1} className="px-4 py-10 text-center text-slate-400">Loading…</td></tr>
            )}
            {items?.length === 0 && (
              <tr><td colSpan={cols.length + 1} className="px-4 py-10 text-center text-slate-500" data-testid="records-empty">No records yet. Click “Add record” to create the first one.</td></tr>
            )}
            {items?.map((r) => (
              <tr key={r.id} className="border-b border-slate-100 transition-colors hover:bg-slate-50/80" data-testid={`record-row-${r.id}`}>
                {category.fields.map((f) => (
                  <td key={f.key} className={`px-4 py-2.5 text-slate-700 ${right(f) ? "text-right" : ""}`}>
                    <Cell field={f} value={r.values[f.key]} />
                  </td>
                ))}
                {category.computed.map((f) => (
                  <td key={f.key} className="px-4 py-2.5 text-right font-medium text-slate-900" data-testid={`record-${f.key}-${r.id}`}>
                    <Cell field={f} value={r.computed[f.key]} />
                    {f.key === "value" && r.computed.warning && (
                      <div className="mt-1 flex items-center justify-end gap-1 text-xs font-normal text-amber-700" data-testid={`record-warning-${r.id}`}>
                        <AlertTriangle className="h-3 w-3" /> {r.computed.warning}
                      </div>
                    )}
                  </td>
                ))}
                <td className="whitespace-nowrap px-4 py-2 text-right">
                  {r.is_sample && <Badge variant="outline" className="mr-2 border-slate-200 text-[10px] font-normal text-slate-400">sample</Badge>}
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-500 hover:text-blue-700" onClick={() => onEdit(r)} data-testid={`edit-record-${r.id}`}>
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <DeleteButton record={r} onDelete={onDelete} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
