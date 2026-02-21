"use client";

import { Database, Key, Bell, Palette } from "lucide-react";

const sections = [
  {
    icon: Database,
    title: "Connections",
    desc: "Manage database connections and sync schedule",
    items: ["olist (PostgreSQL) — Connected", "warehouse_pg (PostgreSQL) — Connected"],
  },
  {
    icon: Key,
    title: "API & Keys",
    desc: "OpenAI API key and optional Ollama endpoint",
    items: ["OpenAI: configured", "Ollama: not set"],
  },
  {
    icon: Bell,
    title: "Notifications",
    desc: "Alerts for sync failures and quality violations",
    items: ["Email: off", "Slack: not connected"],
  },
  {
    icon: Palette,
    title: "Appearance",
    desc: "Theme and display options",
    items: ["Theme: System", "Compact mode: off"],
  },
];

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Settings
      </h2>
      <p className="mb-8 text-sm text-[var(--color-text-secondary)]">
        Application and connection settings (mockup).
      </p>

      <div className="space-y-6">
        {sections.map((section) => (
          <section
            key={section.title}
            className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--color-bg-secondary)]">
                <section.icon className="h-5 w-5 text-[var(--color-text-secondary)]" />
              </div>
              <div>
                <h3 className="font-semibold text-[var(--color-text)]">
                  {section.title}
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)]">
                  {section.desc}
                </p>
              </div>
            </div>
            <ul className="space-y-2 text-sm text-[var(--color-text)]">
              {section.items.map((item, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between rounded-md bg-[var(--color-bg-secondary)] px-3 py-2"
                >
                  {item}
                  <button
                    type="button"
                    className="text-primary text-xs font-medium hover:underline"
                  >
                    Edit
                  </button>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
