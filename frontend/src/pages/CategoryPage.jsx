import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/PageHeader";
import { RecordsTable } from "@/components/records/RecordsTable";
import { RecordFormDialog } from "@/components/records/RecordFormDialog";
import { useCategories } from "@/context/CategoriesContext";
import { api, errorMessage } from "@/lib/api";

export default function CategoryPage() {
  const { slug } = useParams();
  const config = useCategories();
  const category = config?.bySlug[slug];
  const [items, setItems] = useState(null);
  const [editing, setEditing] = useState(null);

  const load = useCallback(() => {
    api.get(`/records/${slug}`).then((r) => setItems(r.data.items)).catch((e) => toast.error(errorMessage(e)));
  }, [slug]);

  useEffect(() => {
    setItems(null);
    load();
  }, [load]);

  if (!config) return null;
  if (!category) return <p className="text-slate-500" data-testid="unknown-category">Unknown category</p>;
  const group = config.groups.find((g) => g.key === category.group);

  const remove = async (record) => {
    try {
      await api.delete(`/records/${slug}/${record.id}`);
      toast.success("Record deleted");
      load();
    } catch (e) {
      toast.error(errorMessage(e));
    }
  };

  return (
    <div data-testid={`category-page-${slug}`}>
      <PageHeader
        eyebrow={`Data entry · ${group?.label}`}
        title={category.label}
        description={items ? `${items.length} record${items.length === 1 ? "" : "s"}` : "Loading…"}
        actions={
          <Button onClick={() => setEditing({})} className="bg-blue-700 hover:bg-blue-800" data-testid="add-record-button">
            <Plus className="mr-1.5 h-4 w-4" /> Add record
          </Button>
        }
      />
      <RecordsTable category={category} items={items} onEdit={setEditing} onDelete={remove} />
      {editing && (
        <RecordFormDialog
          key={`${slug}-${editing.id || "new"}`}
          category={category}
          record={editing.id ? editing : null}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null);
            load();
          }}
        />
      )}
    </div>
  );
}
