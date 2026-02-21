"use client";

import { Search, Table2, Filter, ChevronRight } from "lucide-react";
import Link from "next/link";

const mockTables = [
  { name: "orders", schema: "public", rows: "99,441", updated: "2h ago", docs: true },
  { name: "order_items", schema: "public", rows: "112,650", updated: "2h ago", docs: true },
  { name: "customers", schema: "public", rows: "99,096", updated: "2h ago", docs: true },
  { name: "products", schema: "public", rows: "32,951", updated: "2h ago", docs: true },
  { name: "sellers", schema: "public", rows: "3,095", updated: "2h ago", docs: false },
  { name: "order_reviews", schema: "public", rows: "99,324", updated: "2h ago", docs: true },
  { name: "order_payments", schema: "public", rows: "103,886", updated: "2h ago", docs: true },
  { name: "geolocation", schema: "public", rows: "8,009", updated: "2h ago", docs: false },
];

export default function TablesPage() {
  return (
    <div className="mx-auto max-w-7xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Tables
      </h2>

      {/* Search and filters mockup */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center">
        <label className="relative flex-1">
          <span className="sr-only">Search tables</span>
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-secondary)]" />
          <input
            type="search"
            placeholder="Search tables, columns..."
            className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] py-2.5 pl-10 pr-4 text-sm placeholder:text-[var(--color-text-secondary)] focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            aria-label="Search tables"
          />
        </label>
        <button
          type="button"
          className="flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-2.5 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-bg-secondary)]"
          aria-label="Filter"
        >
          <Filter className="h-4 w-4" />
          Schema: All
        </button>
      </div>

      {/* Table list mockup */}
      <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        <div className="border-b border-[var(--color-border)] px-6 py-4">
          <div className="flex items-center gap-2">
            <Table2 className="h-5 w-5 text-[var(--color-text-secondary)]" />
            <span className="font-medium text-[var(--color-text)]">
              {mockTables.length} tables
            </span>
          </div>
        </div>
        <ul className="divide-y divide-[var(--color-border)]">
          {mockTables.map((t) => (
            <li key={t.name}>
              <Link
                href={`/tables/${t.name}`}
                className="flex flex-wrap items-center gap-4 px-6 py-4 transition-colors hover:bg-[var(--color-bg-secondary)] sm:flex-nowrap"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-[var(--color-text)]">{t.name}</p>
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    {t.schema} · {t.rows} rows
                  </p>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-[var(--color-text-secondary)]">
                    Updated {t.updated}
                  </span>
                  {t.docs ? (
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
      </div>
    </div>
  );
}
