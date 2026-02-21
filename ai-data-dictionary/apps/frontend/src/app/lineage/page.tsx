"use client";

import { GitBranch, Table2 } from "lucide-react";

const upstream = ["geolocation", "customers", "sellers", "products"];
const middle = ["orders"];
const downstream = ["order_items", "order_payments", "order_reviews"];

export default function LineagePage() {
  return (
    <div className="mx-auto max-w-7xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Lineage
      </h2>
      <p className="mb-6 text-sm text-[var(--color-text-secondary)]">
        Table dependencies — upstream to downstream (mockup).
      </p>

      <div className="overflow-auto rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-8 shadow-sm">
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {/* Upstream */}
          <div className="flex flex-col gap-3">
            <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
              Upstream
            </p>
            {upstream.map((id) => (
              <div
                key={id}
                className="flex min-w-[140px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-4 py-3"
              >
                <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                <span className="truncate text-sm font-medium text-[var(--color-text)]">
                  {id}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
            <span className="text-2xl">→</span>
          </div>

          {/* Core */}
          <div className="flex flex-col gap-3">
            <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
              Core
            </p>
            <div className="flex min-w-[140px] items-center gap-2 rounded-lg border-2 border-primary bg-primary/10 px-4 py-3">
              <Table2 className="h-4 w-4 shrink-0 text-primary" />
              <span className="truncate text-sm font-medium text-[var(--color-text)]">
                orders
              </span>
            </div>
          </div>

          <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
            <span className="text-2xl">→</span>
          </div>

          {/* Downstream */}
          <div className="flex flex-col gap-3">
            <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
              Downstream
            </p>
            {downstream.map((id) => (
              <div
                key={id}
                className="flex min-w-[140px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-4 py-3"
              >
                <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                <span className="truncate text-sm font-medium text-[var(--color-text)]">
                  {id}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-sm text-[var(--color-text-secondary)]">
          <GitBranch className="h-4 w-4" />
          <span>Connect a database to see real lineage graph.</span>
        </div>
      </div>
    </div>
  );
}
