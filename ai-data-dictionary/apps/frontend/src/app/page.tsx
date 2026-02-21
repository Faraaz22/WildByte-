"use client";

import { useState } from "react";
import {
  Database,
  Table2,
  BarChart3,
  TrendingUp,
  Activity,
} from "lucide-react";
import Button from "../components/ui/Button";
import EmptyState from "../components/common/EmptyState";
import Link from "next/link";

const mockActivity = [
  { text: "Schema sync completed: olist (8 tables)", time: "2m ago" },
  { text: "AI documentation generated for orders", time: "15m ago" },
  { text: "Quality check: order_items — 98% complete", time: "1h ago" },
  { text: "New database connected: warehouse_pg", time: "Yesterday" },
];

const mockTables = [
  { name: "orders", schema: "public", rows: "99.441", updated: "2h ago", docs: true },
  { name: "order_items", schema: "public", rows: "112.650", updated: "2h ago", docs: true },
  { name: "customers", schema: "public", rows: "99.096", updated: "2h ago", docs: true },
  { name: "products", schema: "public", rows: "32.951", updated: "2h ago", docs: true },
  { name: "sellers", schema: "public", rows: "3.095", updated: "2h ago", docs: false },
];

export default function Page() {
  const [showMockup, setShowMockup] = useState(false);
  const [showAddDbModal, setShowAddDbModal] = useState(false);

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-[var(--color-text)]">
          Overview
        </h2>
        <Button variant="secondary" onClick={() => setShowMockup(!showMockup)}>
          {showMockup ? "Show empty state" : "View full mockup"}
        </Button>
      </div>

      {!showMockup ? (
        <EmptyState
          icon={<Database />}
          title="No databases connected"
          description="Connect your first database to start generating documentation and exploring schemas."
          action={
            <Button variant="primary" onClick={() => setShowAddDbModal(true)}>
              Add Database
            </Button>
          }
        />
      ) : (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4 shadow-sm">
              <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                <Table2 className="h-4 w-4" />
                <span className="text-sm font-medium">Tables</span>
              </div>
              <p className="mt-2 text-2xl font-semibold text-[var(--color-text)]">128</p>
              <p className="mt-1 text-xs text-[var(--color-text-secondary)]">Across 3 schemas</p>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4 shadow-sm">
              <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                <Database className="h-4 w-4" />
                <span className="text-sm font-medium">Databases</span>
              </div>
              <p className="mt-2 text-2xl font-semibold text-[var(--color-text)]">2</p>
              <p className="mt-1 text-xs text-[var(--color-text-secondary)]">olist, warehouse_pg</p>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4 shadow-sm">
              <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                <BarChart3 className="h-4 w-4" />
                <span className="text-sm font-medium">Documented</span>
              </div>
              <p className="mt-2 text-2xl font-semibold text-[var(--color-success)]">118</p>
              <p className="mt-1 text-xs text-[var(--color-text-secondary)]">92% with AI docs</p>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-4 shadow-sm">
              <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm font-medium">Last sync</span>
              </div>
              <p className="mt-2 text-2xl font-semibold text-[var(--color-text)]">2h ago</p>
              <p className="mt-1 text-xs text-[var(--color-text-secondary)]">Incremental</p>
            </div>
          </div>

          <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm lg:col-span-2">
              <h3 className="text-lg font-semibold text-[var(--color-text)]">Table growth (mockup)</h3>
              <p className="mt-1 text-sm text-[var(--color-text-secondary)]">Documented vs total tables over time</p>
              <div className="mt-6 flex h-48 items-center justify-center rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
                <BarChart3 className="h-12 w-12 text-[var(--color-text-secondary)]" />
                <span className="ml-2 text-sm text-[var(--color-text-secondary)]">Chart placeholder</span>
              </div>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-[var(--color-text-secondary)]" />
                <h3 className="font-semibold text-[var(--color-text)]">Recent activity</h3>
              </div>
              <ul className="mt-4 space-y-3">
                {mockActivity.map((item, i) => (
                  <li key={i} className="flex justify-between gap-2 border-b border-[var(--color-border)] pb-3 text-sm last:border-0 last:pb-0">
                    <span className="text-[var(--color-text)]">{item.text}</span>
                    <span className="shrink-0 text-[var(--color-text-secondary)]">{item.time}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
            <div className="flex items-center justify-between border-b border-[var(--color-border)] px-6 py-4">
              <div className="flex items-center gap-2">
                <Table2 className="h-5 w-5 text-[var(--color-text-secondary)]" />
                <h3 className="text-lg font-semibold text-[var(--color-text)]">Tables</h3>
              </div>
              <Link href="/tables">
                <Button variant="ghost" size="sm">View all</Button>
              </Link>
            </div>
            <div className="overflow-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
                    <th className="p-3 font-medium text-[var(--color-text-secondary)]">Table</th>
                    <th className="p-3 font-medium text-[var(--color-text-secondary)]">Schema</th>
                    <th className="p-3 font-medium text-[var(--color-text-secondary)]">Rows</th>
                    <th className="p-3 font-medium text-[var(--color-text-secondary)]">Updated</th>
                    <th className="p-3 font-medium text-[var(--color-text-secondary)]">Docs</th>
                  </tr>
                </thead>
                <tbody className="text-[var(--color-text)]">
                  {mockTables.map((row, i) => (
                    <tr key={row.name} className={`border-b border-[var(--color-border)] ${i % 2 === 1 ? "bg-[var(--color-bg-secondary)]" : ""}`}>
                      <td className="p-3">
                        <Link href={`/tables/${row.name}`} className="font-medium text-primary hover:underline">{row.name}</Link>
                      </td>
                      <td className="p-3 text-[var(--color-text-secondary)]">{row.schema}</td>
                      <td className="p-3">{row.rows}</td>
                      <td className="p-3 text-[var(--color-text-secondary)]">{row.updated}</td>
                      <td className="p-3">
                        {row.docs ? (
                          <span className="rounded bg-[var(--color-success)]/15 px-2 py-0.5 text-xs font-medium text-[var(--color-success)]">Yes</span>
                        ) : (
                          <span className="text-[var(--color-text-secondary)]">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      {showAddDbModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-labelledby="add-db-title">
          <div className="w-full max-w-lg rounded-xl border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-xl">
            <div className="mb-6 flex items-center justify-between">
              <h3 id="add-db-title" className="text-lg font-semibold text-[var(--color-text)]">Add Database</h3>
              <button type="button" onClick={() => setShowAddDbModal(false)} className="rounded p-1 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text)]" aria-label="Close">Close</button>
            </div>
            <p className="mb-4 text-sm text-[var(--color-text-secondary)]">Connect a read-only database to extract schema and generate documentation. (Mockup.)</p>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--color-text)]">Name</label>
                <input type="text" placeholder="e.g. Production PostgreSQL" className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm" readOnly />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--color-text)]">Type</label>
                <select className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm" disabled aria-label="Database type">
                  <option>PostgreSQL</option>
                  <option>Snowflake</option>
                  <option>SQL Server</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-[var(--color-text)]">Host</label>
                <input type="text" placeholder="host.example.com" className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm" readOnly />
              </div>
              <div className="flex gap-2 pt-2">
                <Button variant="primary" onClick={() => setShowAddDbModal(false)}>Connect (mockup)</Button>
                <Button variant="secondary" onClick={() => setShowAddDbModal(false)}>Cancel</Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
