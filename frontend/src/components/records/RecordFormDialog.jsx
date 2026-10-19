import { useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, errorMessage } from "@/lib/api";
import { todayMuscat } from "@/lib/format";
import { validateRecord } from "@/lib/validate";
import { cn } from "@/lib/utils";

function initialValues(category, record) {
  return Object.fromEntries(
    category.fields.map((f) => {
      if (record) return [f.key, record.values[f.key] ?? ""];
      if (f.type === "date") return [f.key, todayMuscat()];
      if (f.type === "month") return [f.key, todayMuscat().slice(0, 7)];
      return [f.key, ""];
    })
  );
}

function FieldInput({ field, value, onChange, invalid }) {
  const base = cn("h-10 bg-white", invalid && "border-rose-400 focus-visible:ring-rose-400");
  const testId = `field-${field.key}-input`;
  if (field.type === "select") {
    return (
      <select value={value} onChange={(e) => onChange(e.target.value)} data-testid={testId}
        className={cn("flex w-full rounded-md border border-input px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring", base)}>
        <option value="">Select…</option>
        {field.options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    );
  }
  const numeric = field.type === "money" || field.type === "quantity";
  const type = numeric ? "number" : field.type === "date" ? "date" : field.type === "month" ? "month" : "text";
  return (
    <Input type={type} step={numeric ? "any" : undefined} inputMode={numeric ? "decimal" : undefined}
      value={value} onChange={(e) => onChange(e.target.value)} className={cn(base, numeric && "num")} data-testid={testId} />
  );
}

export function RecordFormDialog({ category, record, onClose, onSaved }) {
  const [values, setValues] = useState(() => initialValues(category, record));
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    const found = validateRecord(category.fields, values);
    setErrors(found);
    if (Object.keys(found).length) return;
    setSaving(true);
    try {
      if (record) await api.put(`/records/${category.slug}/${record.id}`, values);
      else await api.post(`/records/${category.slug}`, values);
      toast.success(record ? "Record updated" : "Record saved");
      onSaved();
    } catch (err) {
      const serverErrors = err.response?.data?.detail?.errors;
      if (serverErrors) setErrors(serverErrors);
      else toast.error(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-lg" data-testid="record-form-dialog">
        <DialogHeader>
          <DialogTitle className="font-heading">{record ? "Edit" : "Add"} {category.label.toLowerCase()} record</DialogTitle>
          <DialogDescription>All fields are required. Amounts are in OMR (3 decimals).</DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} noValidate className="space-y-4" data-testid="record-form">
          {category.fields.map((f) => (
            <div key={f.key} className="space-y-1.5">
              <Label className="text-slate-700">{f.label}{f.type === "money" && <span className="ml-1 text-xs font-normal text-slate-400">(OMR)</span>}</Label>
              <FieldInput field={f} value={values[f.key]} invalid={!!errors[f.key]}
                onChange={(v) => setValues((s) => ({ ...s, [f.key]: v }))} />
              {errors[f.key] && <p className="text-xs text-rose-600" data-testid={`field-${f.key}-error`}>{errors[f.key]}</p>}
            </div>
          ))}
          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={onClose} data-testid="record-form-cancel">Cancel</Button>
            <Button type="submit" disabled={saving} className="bg-blue-700 hover:bg-blue-800" data-testid="record-form-submit">
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} {record ? "Save changes" : "Save record"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
