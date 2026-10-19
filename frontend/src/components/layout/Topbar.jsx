import { useNavigate } from "react-router-dom";
import { CalendarDays, LogOut, Menu, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { formatDate, todayMuscat } from "@/lib/format";

export function Topbar({ onMenu }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-slate-200 bg-white/90 px-8 backdrop-blur">
      <div className="flex items-center gap-2 text-sm text-slate-500" data-testid="topbar-date">
        <Button variant="outline" size="icon" className="mr-2 h-8 w-8 xl:hidden" onClick={onMenu} data-testid="sidebar-toggle">
          <Menu className="h-4 w-4" />
        </Button>
        <CalendarDays className="h-4 w-4" />
        <span>{formatDate(todayMuscat())}</span>
        <span className="text-slate-300">·</span>
        <span>Asia/Muscat</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600" data-testid="topbar-user">
          <UserRound className="h-3.5 w-3.5" /> {user?.email}
        </span>
        <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="logout-button" className="text-slate-600">
          <LogOut className="mr-1.5 h-4 w-4" /> Logout
        </Button>
      </div>
    </header>
  );
}
