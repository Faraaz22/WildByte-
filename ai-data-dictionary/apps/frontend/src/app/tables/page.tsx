"use client";

import { useState, useEffect } from "react";
import { Search, Table2, Filter, ChevronRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { listTables, type TableResponse } from "../../lib/api/tables";
import { listSchemas, type SchemaResponse } from "../../lib/api/schemas";

export default function TablesPage() {
  const [tables, setTables] = useState<TableResponse[]>([]);
  const [schemas, setSchemas] = useState<SchemaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [schemaFilter, setSchemaFilter] = useState<number | "all">("all");
  const [search, setSearch] = useState("");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [tablesRes, schemasRes] = await Promise.all([
          listTables({
            page: 1,
            page_size: 100,
            schema_id: schemaFilter === "all" ? undefined : schemaFilter,
            search: search || undefined,
          }),
          listSchemas(),
        ]);
        if (!cancelled) {
          setTables(tablesRes.data);
          setTotal(tablesRes.total);
          setSchemas(schemasRes);
        }
      } catch (_e) {
        if (!cancelled) {
          setTables([]);
          setSchemas([]);
          setTotal(0);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [schemaFilter, search]);

  const schemaNameById = Object.fromEntries(schemas.map((s) => [s.id, s.name]));

  return (
    <div className="mx-auto max-w-7xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Tables
      </h2>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <span className="sr-only">Search tables</span>
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-secondary)]" />
          <input
            type="search"
            placeholder="Search tables, columns..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] py-2.5 pl-10 pr-4 text-sm placeholder:text-[var(--color-text-secondary)] focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            aria-label="Search tables"
          />
        </label>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-[var(--color-text-secondary)]" />
          <select
            value={schemaFilter === "all" ? "all" : schemaFilter}
            onChange={(e) =>
              setSchemaFilter(e.target.value === "all" ? "all" : Number(e.target.value))
            }
            className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-2.5 text-sm font-medium text-[var(--color-text)]"
            aria-label="Filter by schema"
          >
            <option value="all">Schema: All</option>
            {schemas.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        <div className="border-b border-[var(--color-border)] px-6 py-4">
          <div className="flex items-center gap-2">
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin text-[var(--color-text-secondary)]" />
            ) : (
              <Table2 className="h-5 w-5 text-[var(--color-text-secondary)]" />
            )}
            <span className="font-medium text-[var(--color-text)]">
              {loading ? "Loading…" : `${total} tables`}
            </span>
          </div>
        </div>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-[var(--color-text-secondary)]" />
          </div>
        ) : tables.length === 0 ? (
          <div className="px-6 py-12 text-center text-sm text-[var(--color-text-secondary)]">
            No tables found. Connect a database in Settings and run sync to extract schemas.
          </div>
        ) : (
          <ul className="divide-y divide-[var(--color-border)]">
            {tables.map((t) => (
              <li key={t.id}>
                <Link
                  href={`/tables/${t.id}`}
                  className="flex flex-wrap items-center gap-4 px-6 py-4 transition-colors hover:bg-[var(--color-bg-secondary)] sm:flex-nowrap"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-[var(--color-text)]">{t.name}</p>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      {schemaNameById[t.schema_id] ?? "—"} · {t.row_count != null ? t.row_count.toLocaleString() : "—"} rows
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-[var(--color-text-secondary)]">
                      {t.updated_at ? new Date(t.updated_at).toLocaleDateString() : "—"}
                    </span>
                    {t.ai_generated_description ? (
                      <span className="rounded bg-[var(--color-success)]/15 px-2 py-0.5 text-xs font-medium text-[var(--color-success)]">
                        Documented
                      </span>
                    ) : (
                      <span className="text-[var(--color-text-secondary)]">—</span>
                    )}
                    <ChevronRight className="h-4 w-4 text-[var(--color-text-secondary)]" />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
