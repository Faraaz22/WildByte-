"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Table2,
  ArrowLeft,
  FileText,
  Database,
  Type,
  Loader2,
} from "lucide-react";
import { getTable, type TableDetailResponse } from "../../../lib/api/tables";

export default function TableDetailPage() {
  const params = useParams();
  const idParam = params?.id as string | undefined;
  const id = idParam ? parseInt(idParam, 10) : NaN;
  const [table, setTable] = useState<TableDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!idParam || !Number.isInteger(id) || id < 1) {
      setLoading(false);
      setError("Invalid table ID");
      return;
    }
    let cancelled = false;
    getTable(id)
      .then((data) => {
        if (!cancelled) setTable(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load table");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id, idParam]);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[var(--color-text-secondary)]" />
        </div>
      </div>
    );
  }

  if (error || !table) {
    return (
      <div className="mx-auto max-w-7xl">
        <Link
          href="/tables"
          className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-primary"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to tables
        </Link>
        <p className="text-[var(--color-error)]">{error ?? "Table not found"}</p>
      </div>
    );
  }

  const rowLabel = table.row_count != null ? table.row_count.toLocaleString() : "—";

  return (
    <div className="mx-auto max-w-7xl">
      <Link
        href="/tables"
        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to tables
      </Link>

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <Table2 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-[var(--color-text)]">
              {table.name}
            </h1>
            <p className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <Database className="h-4 w-4" />
              schema {table.schema_id} · {rowLabel} rows · Updated{" "}
              {table.updated_at ? new Date(table.updated_at).toLocaleDateString() : "—"}
            </p>
          </div>
        </div>
        {table.ai_generated_description && (
          <span className="rounded-lg bg-[var(--color-success)]/15 px-3 py-1.5 text-sm font-medium text-[var(--color-success)]">
            AI documented
          </span>
        )}
      </div>

      {(table.description || table.ai_generated_description) && (
        <div className="mb-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm">
          <div className="mb-2 flex items-center gap-2">
            <FileText className="h-5 w-5 text-[var(--color-text-secondary)]" />
            <h3 className="font-semibold text-[var(--color-text)]">Description</h3>
          </div>
          <p className="text-sm text-[var(--color-text)]">
            {table.ai_generated_description ?? table.description ?? "—"}
          </p>
        </div>
      )}

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        <div className="border-b border-[var(--color-border)] px-6 py-4">
          <h3 className="font-semibold text-[var(--color-text)]">Columns</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {table.columns?.length ?? 0} columns
          </p>
        </div>
        {table.columns && table.columns.length > 0 ? (
          <div className="overflow-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
                  <th className="p-3 font-medium text-[var(--color-text-secondary)]">Column</th>
                  <th className="p-3 font-medium text-[var(--color-text-secondary)]">Type</th>
                  <th className="p-3 font-medium text-[var(--color-text-secondary)]">Nullable</th>
                  <th className="p-3 font-medium text-[var(--color-text-secondary)]">Description</th>
                </tr>
              </thead>
              <tbody>
                {table.columns.map((col) => (
                  <tr key={col.id} className="border-b border-[var(--color-border)]">
                    <td className="p-3 font-medium text-[var(--color-text)]">{col.name}</td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 rounded bg-[var(--color-bg-secondary)] px-2 py-0.5 font-mono text-xs">
                        <Type className="h-3 w-3" />
                        {col.data_type}
                      </span>
                    </td>
                    <td className="p-3 text-[var(--color-text-secondary)]">
                      {col.is_nullable ? "Yes" : "No"}
                    </td>
                    <td className="p-3 text-[var(--color-text-secondary)]">
                      {col.is_primary_key ? "PK" : ""}
                      {col.is_foreign_key ? " FK" : ""}
                      {(col as { description?: string }).description ?? ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="px-6 py-4 text-sm text-[var(--color-text-secondary)]">
            No column metadata.
          </div>
        )}
      </section>
    </div>
  );
}
