import { useCallback, useEffect, useState } from "react";
import { Database, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { PageHeader } from "@/components/PageHeader";
import { useAuth } from "@/context/AuthContext";
import { api, errorMessage } from "@/lib/api";

export default function SettingsPage() {
  const { user } = useAuth();
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    api.get("/settings/sample-data").then((r) => setStatus(r.data)).catch((e) => toast.error(errorMessage(e)));
  }, []);
  useEffect(load, [load]);

  const clear = async () => {
    setBusy(true);
    try {
      const { data } = await api.post("/settings/clear-sample-data");
      toast.success(`Deleted ${data.deleted} sample records`);
      load();
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-3xl" data-testid="settings-page">
      <PageHeader eyebrow="Administration" title="Settings" />
      <section className="mb-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm fade-up">
        <h2 className="text-lg font-semibold text-slate-900">Account</h2>
        <p className="mt-1 text-sm text-slate-500">Single administrator. There are no other users.</p>
        <p className="mt-3 text-sm text-slate-700" data-testid="settings-admin-email">{user?.email}</p>
      </section>
      <section className="rounded-xl border border-rose-200 bg-rose-50/40 p-6 fade-up" data-testid="sample-data-section">
        <div className="flex items-start gap-3">
          <Database className="mt-0.5 h-5 w-5 text-rose-600" />
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-slate-900">Sample data</h2>
            <p className="mt-1 text-sm text-slate-600">
              Sample records were loaded so you can explore the panel. Clearing removes every sample record in all 18 categories. Records you entered yourself are kept.
            </p>
            <div className="mt-4 flex gap-6 text-sm">
              <p>Sample records: <span className="num font-semibold" data-testid="sample-count">{status?.sample_records ?? "…"}</span></p>
              <p>Your records: <span className="num font-semibold" data-testid="user-count">{status?.user_records ?? "…"}</span></p>
            </div>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" className="mt-5" disabled={busy || !status?.sample_records} data-testid="clear-sample-data-button">
                  {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />} Clear sample data
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent data-testid="clear-sample-dialog">
                <AlertDialogHeader>
                  <AlertDialogTitle>Clear all sample data?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This permanently deletes {status?.sample_records} sample records across all categories. Your own records stay. This cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel data-testid="clear-sample-cancel">Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={clear} className="bg-rose-600 hover:bg-rose-700" data-testid="clear-sample-confirm">Yes, clear sample data</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </section>
    </div>
  );
}
