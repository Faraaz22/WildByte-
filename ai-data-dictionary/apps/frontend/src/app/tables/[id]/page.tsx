"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Table2,
  ArrowLeft,
  FileText,
  Database,
  Hash,
  Calendar,
  Type,
} from "lucide-react";

const mockColumns = [
  { name: "order_id", type: "uuid", nullable: false, description: "Unique order identifier" },
  { name: "customer_id", type: "uuid", nullable: false, description: "FK to customers" },
  { name: "order_status", type: "varchar(32)", nullable: false, description: "pending, delivered, etc." },
  { name: "order_purchase_timestamp", type: "timestamp", nullable: false, description: "When order was placed" },
  { name: "order_approved_at", type: "timestamp", nullable: true, description: "Payment approval time" },
  { name: "order_delivered_carrier_date", type: "date", nullable: true, description: "Handoff to carrier" },
  { name: "order_delivered_customer_date", type: "date", nullable: true, description: "Delivery to customer" },
  { name: "order_estimated_delivery_date", type: "date", nullable: false, description: "Estimated delivery" },
];

const mockSample = [
  { order_id: "e481f51c...", order_status: "delivered", order_purchase_timestamp: "2018-01-10 10:32" },
  { order_id: "53cdb2fc...", order_status: "delivered", order_purchase_timestamp: "2018-01-11 19:45" },
  { order_id: "47770eb4...", order_status: "delivered", order_purchase_timestamp: "2018-01-12 08:23" },
];

export default function TableDetailPage() {
  const params = useParams();
  const id = (params?.id as string) || "orders";

  return (
    <div className="mx-auto max-w-7xl">
      <Link
        href="/tables"
        className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to tables
      </Link>

      {/* Header */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
            <Table2 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-[var(--color-text)]">
              {id}
            </h1>
            <p className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <Database className="h-4 w-4" />
              public · 99,441 rows · Updated 2h ago
            </p>
          </div>
        </div>
        <span className="rounded-lg bg-[var(--color-success)]/15 px-3 py-1.5 text-sm font-medium text-[var(--color-success)]">
          AI documented
        </span>
      </div>

      {/* Description mockup */}
      <div className="mb-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <FileText className="h-5 w-5 text-[var(--color-text-secondary)]" />
          <h3 className="font-semibold text-[var(--color-text)]">
            Description
          </h3>
        </div>
        <p className="text-sm text-[var(--color-text)]">
          Contains one row per order. Links to customers (customer_id), and is
          referenced by order_items, order_payments, and order_reviews. Key dates
          include purchase, approval, carrier handoff, and delivery.
        </p>
      </div>

      {/* Columns */}
      <section className="mb-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        <div className="border-b border-[var(--color-border)] px-6 py-4">
          <h3 className="font-semibold text-[var(--color-text)]">Columns</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {mockColumns.length} columns
          </p>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  Column
                </th>
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  Type
                </th>
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  Nullable
                </th>
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  Description
                </th>
              </tr>
            </thead>
            <tbody>
              {mockColumns.map((col) => (
                <tr
                  key={col.name}
                  className="border-b border-[var(--color-border)]"
                >
                  <td className="p-3 font-medium text-[var(--color-text)]">
                    {col.name}
                  </td>
                  <td className="p-3">
                    <span className="inline-flex items-center gap-1 rounded bg-[var(--color-bg-secondary)] px-2 py-0.5 font-mono text-xs">
                      <Type className="h-3 w-3" />
                      {col.type}
                    </span>
                  </td>
                  <td className="p-3 text-[var(--color-text-secondary)]">
                    {col.nullable ? "Yes" : "No"}
                  </td>
                  <td className="p-3 text-[var(--color-text-secondary)]">
                    {col.description}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Sample data mockup */}
      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        <div className="border-b border-[var(--color-border)] px-6 py-4">
          <h3 className="font-semibold text-[var(--color-text)]">
            Sample data (mockup)
          </h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            First 3 rows
          </p>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-left text-sm font-mono">
            <thead>
              <tr className="border-b border-[var(--color-border)] bg-[var(--color-bg-secondary)]">
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  order_id
                </th>
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  order_status
                </th>
                <th className="p-3 font-medium text-[var(--color-text-secondary)]">
                  order_purchase_timestamp
                </th>
              </tr>
            </thead>
            <tbody>
              {mockSample.map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-[var(--color-border)]"
                >
                  <td className="p-3 text-[var(--color-text)]">{row.order_id}</td>
                  <td className="p-3 text-[var(--color-text)]">
                    {row.order_status}
                  </td>
                  <td className="p-3 text-[var(--color-text-secondary)]">
                    {row.order_purchase_timestamp}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
