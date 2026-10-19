import { useState } from "react";
import { Outlet } from "react-router-dom";
import { CategoriesProvider } from "@/context/CategoriesContext";
import { Sidebar } from "@/components/layout/Sidebar";
import { Topbar } from "@/components/layout/Topbar";

export function AppLayout() {
  const [navOpen, setNavOpen] = useState(false);
  return (
    <CategoriesProvider>
      <div className="min-h-screen bg-slate-50">
        <Sidebar open={navOpen} onClose={() => setNavOpen(false)} />
        <div className="xl:pl-[240px]">
          <Topbar onMenu={() => setNavOpen(true)} />
          <main className="px-8 py-8" data-testid="main-content">
            <div className="mx-auto max-w-[1400px]">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </CategoriesProvider>
  );
}
