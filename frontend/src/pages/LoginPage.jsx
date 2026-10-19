import { useState } from "react";
import { Navigate } from "react-router-dom";
import { Factory, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/AuthContext";
import { errorMessage } from "@/lib/api";

export default function LoginPage() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    const fieldErrors = {};
    if (!email.trim()) fieldErrors.email = "Required";
    if (!password) fieldErrors.password = "Required";
    setErrors(fieldErrors);
    setError("");
    if (Object.keys(fieldErrors).length) return;
    setBusy(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.response?.status === 401 ? "Invalid email or password" : errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden bg-slate-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-blue-600"><Factory className="h-5 w-5" /></div>
          <span className="font-heading text-lg font-semibold">Factory P&amp;L</span>
        </div>
        <div className="max-w-md">
          <h1 className="text-4xl font-bold leading-tight tracking-tight">See gross, operating and net profit for any day or month.</h1>
          <p className="mt-4 text-slate-400">Record revenue, production costs and expenses, then read exact figures in OMR, to the baisa.</p>
        </div>
        <div className="num grid grid-cols-3 gap-4 border-t border-slate-800 pt-6 text-xs text-slate-400">
          <div><p className="text-slate-500">Net Revenue</p><p className="mt-1 text-sm text-white">− COGS</p></div>
          <div><p className="text-slate-500">Gross Profit</p><p className="mt-1 text-sm text-white">− OpEx</p></div>
          <div><p className="text-slate-500">Operating Profit</p><p className="mt-1 text-sm text-emerald-400">= Net Profit</p></div>
        </div>
      </div>
      <div className="flex items-center justify-center bg-slate-50 p-8">
        <form onSubmit={submit} noValidate className="w-full max-w-sm fade-up" data-testid="login-form">
          <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Admin sign in</h2>
          <p className="mt-1 text-sm text-slate-500">Use the administrator account for this factory.</p>
          <div className="mt-8 space-y-5">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} className="h-10 bg-white" data-testid="login-email-input" />
              {errors.email && <p className="text-xs text-rose-600" data-testid="login-email-error">{errors.email}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} className="h-10 bg-white" data-testid="login-password-input" />
              {errors.password && <p className="text-xs text-rose-600" data-testid="login-password-error">{errors.password}</p>}
            </div>
            {error && (
              <div className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700" data-testid="login-error">{error}</div>
            )}
            <Button type="submit" className="h-10 w-full bg-blue-700 hover:bg-blue-800" disabled={busy} data-testid="login-submit-button">
              {busy && <Loader2 className="mr-2 h-4 w-4 animate-spin" />} Sign in
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
