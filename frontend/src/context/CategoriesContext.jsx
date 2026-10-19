import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";

const CategoriesContext = createContext(null);

export function CategoriesProvider({ children }) {
  const [config, setConfig] = useState(null);

  useEffect(() => {
    api.get("/categories").then((r) => {
      const bySlug = Object.fromEntries(r.data.categories.map((c) => [c.slug, c]));
      setConfig({ ...r.data, bySlug });
    });
  }, []);

  return <CategoriesContext.Provider value={config}>{children}</CategoriesContext.Provider>;
}

export const useCategories = () => useContext(CategoriesContext);
