"use client";

import { MessageSquare, Send, Sparkles } from "lucide-react";
import { useState } from "react";

const mockMessages = [
  { role: "user" as const, text: "Which tables contain customer information?" },
  {
    role: "assistant" as const,
    text: "Tables with customer-related data:\n\n• **customers** — customer_id, zip_code, city, state\n• **orders** — links to customers via customer_id\n• **order_reviews** — review scores per order/customer\n\nI can show column details or sample queries for any of these.",
  },
  { role: "user" as const, text: "Show me the schema for orders" },
  {
    role: "assistant" as const,
    text: "The **orders** table has 8 columns: order_id (uuid), customer_id (uuid), order_status (varchar), order_purchase_timestamp (timestamp), order_approved_at (timestamp), order_delivered_carrier_date (date), order_delivered_customer_date (date), order_estimated_delivery_date (date). It references **customers** and is referenced by **order_items**, **order_payments**, and **order_reviews**.",
  },
];

const suggestedQuestions = [
  "List all tables in the public schema",
  "What is the relationship between orders and order_items?",
  "Generate SQL for total revenue by month",
];

export default function ChatPage() {
  const [input, setInput] = useState("");

  return (
    <div className="mx-auto flex max-w-4xl flex-col">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Chat
      </h2>

      <div className="flex min-h-[480px] flex-col rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        {/* Messages area */}
        <div className="flex-1 overflow-auto p-6">
          <div className="flex items-center gap-2 rounded-lg bg-secondary/10 p-3 text-sm text-[var(--color-text-secondary)]">
            <Sparkles className="h-4 w-4 text-secondary" />
            <span>Ask about tables, columns, lineage, or request SQL. (Mockup — replies are static.)</span>
          </div>
          <ul className="mt-4 space-y-6">
            {mockMessages.map((msg, i) => (
              <li
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-white"
                      : "bg-[var(--color-bg-secondary)] text-[var(--color-text)]"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="whitespace-pre-wrap">{msg.text}</div>
                  ) : (
                    msg.text
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Suggested questions */}
        <div className="border-t border-[var(--color-border)] px-6 py-3">
          <p className="mb-2 text-xs font-medium text-[var(--color-text-secondary)]">
            Suggested
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setInput(q)}
                className="rounded-full border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-1.5 text-xs text-[var(--color-text)] hover:bg-[var(--color-bg-secondary)]"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-[var(--color-border)] p-4">
          <div className="flex gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-2 focus-within:ring-1 focus-within:ring-primary">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your data..."
              className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-[var(--color-text-secondary)]"
              aria-label="Chat message"
            />
            <button
              type="button"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary text-white hover:opacity-90"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
