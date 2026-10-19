import { NavLink } from "react-router-dom";
import { BarChart3, Factory, LayoutDashboard, Settings } from "lucide-react";
import { useCategories } from "@/context/CategoriesContext";
import { cn } from "@/lib/utils";

const GROUP_DOT = { revenue: "bg-sky-400", cogs: "bg-rose-400", opex: "bg-amber-400", other: "bg-violet-400" };

const linkClass = ({ isActive }) =>
  cn(
    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors duration-150",
    isActive ? "bg-blue-600 font-medium text-white shadow-sm" : "text-slate-300 hover:bg-slate-800 hover:text-white"
  );

const subLinkClass = ({ isActive }) =>
  cn(
    "flex items-center gap-2.5 rounded-md px-3 py-1.5 text-[13px] transition-colors duration-150",
    isActive ? "bg-blue-600 font-medium text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"
  );

function CategoryGroup({ group, categories }) {
  return (
    <div className="mt-3" data-testid={`nav-group-${group.key}`}>
      <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">{group.label}</p>
      {categories.map((c) => (
        <NavLink key={c.slug} to={`/entry/${c.slug}`} className={subLinkClass} data-testid={`nav-category-${c.slug}`}>
          <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", GROUP_DOT[group.key])} />
          <span className="truncate">{c.label}</span>
        </NavLink>
      ))}
    </div>
  );
}

export function Sidebar({ open, onClose }) {
  const config = useCategories();
  return (
    <>
    {open && <div className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm xl:hidden" onClick={onClose} data-testid="sidebar-backdrop" />}
    <aside
      onClick={(e) => e.target.closest("a") && onClose()}
      className={cn(
        "sidebar-scroll fixed left-0 top-0 z-50 flex h-screen w-[240px] flex-col overflow-y-auto border-r border-slate-800 bg-slate-900 transition-transform duration-200 xl:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full"
      )}
      data-testid="sidebar"
    >
      <div className="flex items-center gap-3 border-b border-slate-800 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-blue-600 text-white">
          <Factory className="h-5 w-5" />
        </div>
        <div>
          <p className="font-heading text-base font-semibold leading-tight text-white">Factory P&amp;L</p>
          <p className="text-[11px] text-slate-400">Profit &amp; Loss panel · OMR</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        <NavLink to="/" end className={linkClass} data-testid="nav-dashboard-link">
          <LayoutDashboard className="h-4 w-4" /> Dashboard
        </NavLink>
        <p className="px-3 pb-1 pt-5 text-[11px] font-bold uppercase tracking-[0.16em] text-slate-400">Data entry</p>
        {config?.groups.map((g) => (
          <CategoryGroup key={g.key} group={g} categories={config.categories.filter((c) => c.group === g.key)} />
        ))}
        <div className="pt-5 space-y-1">
          <NavLink to="/reports" className={linkClass} data-testid="nav-reports-link">
            <BarChart3 className="h-4 w-4" /> Reports
          </NavLink>
          <NavLink to="/settings" className={linkClass} data-testid="nav-settings-link">
            <Settings className="h-4 w-4" /> Settings
          </NavLink>
        </div>
      </nav>
    </aside>
    </>
  );
}
