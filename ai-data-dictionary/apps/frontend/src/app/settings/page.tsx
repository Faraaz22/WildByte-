"use client";

import { useState, useEffect } from "react";
import { Database, Loader2, Check, AlertCircle } from "lucide-react";
import {
  listDatabases,
  testConnection,
  createDatabaseFromUri,
  type DatabaseResponse,
  type TestConnectionResponse,
} from "../../lib/api/databases";

type ConnectionStatus = "idle" | "connecting" | "connected" | "error";

export default function SettingsPage() {
  const [databases, setDatabases] = useState<DatabaseResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [uri, setUri] = useState("");
  const [name, setName] = useState("");
  const [testStatus, setTestStatus] = useState<ConnectionStatus>("idle");
  const [testMessage, setTestMessage] = useState("");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "done" | "error">("idle");
  const [saveError, setSaveError] = useState("");

  const loadDatabases = async () => {
    try {
      const res = await listDatabases();
      setDatabases(res.data);
    } catch (e) {
      setDatabases([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatabases();
  }, []);

  const handleTest = async () => {
    const u = uri.trim();
    if (!u) return;
    setTestStatus("connecting");
    setTestMessage("");
    try {
      const res: TestConnectionResponse = await testConnection(u);
      if (res.connected) {
        setTestStatus("connected");
        setTestMessage(res.message ?? "Connected");
      } else {
        setTestStatus("error");
        setTestMessage(res.message ?? "Connection failed");
      }
    } catch (e) {
      setTestStatus("error");
      setTestMessage(e instanceof Error ? e.message : "Connection failed");
    }
  };

  const handleSave = async () => {
    const u = uri.trim();
    const n = name.trim();
    if (!u || !n) {
      setSaveError("Name and connection URI are required.");
      setSaveStatus("error");
      return;
    }
    setSaveStatus("saving");
    setSaveError("");
    try {
      await createDatabaseFromUri(n, u);
      setSaveStatus("done");
      setUri("");
      setName("");
      setTestStatus("idle");
      setTestMessage("");
      await loadDatabases();
    } catch (e) {
      setSaveStatus("error");
      setSaveError(e instanceof Error ? e.message : "Failed to save connection");
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Settings
      </h2>
      <p className="mb-8 text-sm text-[var(--color-text-secondary)]">
        Connect a PostgreSQL database by entering its URI. Test the connection, then save to extract schemas and tables.
      </p>

      {/* Connections: add new */}
      <section className="mb-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--color-bg-secondary)]">
            <Database className="h-5 w-5 text-[var(--color-text-secondary)]" />
          </div>
          <div>
            <h3 className="font-semibold text-[var(--color-text)]">Connections</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">
              Add a PostgreSQL database (URI). We will show &quot;Connecting…&quot; then &quot;Connected&quot; when ready.
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-[var(--color-text)]">
              Connection name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. My Warehouse"
              className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-3 py-2 text-sm text-[var(--color-text)] placeholder:text-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-[var(--color-text)]">
              PostgreSQL URI
            </label>
            <input
              type="password"
              value={uri}
              onChange={(e) => setUri(e.target.value)}
              placeholder="postgresql://user:password@host:5432/dbname"
              className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-3 py-2 text-sm text-[var(--color-text)] placeholder:text-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleTest}
              disabled={!uri.trim() || testStatus === "connecting"}
              className="flex items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-4 py-2 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-border)] disabled:opacity-50"
            >
              {testStatus === "connecting" ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Connecting…
                </>
              ) : (
                "Test connection"
              )}
            </button>
            {testStatus === "connected" && (
              <span className="flex items-center gap-1 text-sm text-[var(--color-success)]">
                <Check className="h-4 w-4" />
                Connected
              </span>
            )}
            {testStatus === "error" && testMessage && (
              <span className="flex items-center gap-1 text-sm text-[var(--color-error)]">
                <AlertCircle className="h-4 w-4" />
                {testMessage}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleSave}
              disabled={saveStatus === "saving"}
              className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
            >
              {saveStatus === "saving" ? (
                <>
                  <Loader2 className="mr-2 inline h-4 w-4 animate-spin" />
                  Saving &amp; extracting schemas…
                </>
              ) : (
                "Save Connection"
              )}
            </button>
            {saveStatus === "done" && (
              <span className="text-sm text-[var(--color-success)]">Saved. Schemas extracted.</span>
            )}
            {saveStatus === "error" && saveError && (
              <span className="text-sm text-[var(--color-error)]">{saveError}</span>
            )}
          </div>
        </div>

        {/* Saved connections */}
        <div className="mt-6 border-t border-[var(--color-border)] pt-4">
          <h4 className="mb-2 text-sm font-medium text-[var(--color-text)]">Saved connections</h4>
          {loading ? (
            <p className="text-sm text-[var(--color-text-secondary)]">Loading…</p>
          ) : databases.length === 0 ? (
            <p className="text-sm text-[var(--color-text-secondary)]">No connections yet. Add one above.</p>
          ) : (
            <ul className="space-y-2">
              {databases.map((db) => (
                <li
                  key={db.id}
                  className="flex items-center justify-between rounded-md bg-[var(--color-bg-secondary)] px-3 py-2 text-sm"
                >
                  <span className="text-[var(--color-text)]">
                    {db.name} ({db.db_type}) — {db.sync_status}
                    {db.sync_error ? `: ${db.sync_error}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
