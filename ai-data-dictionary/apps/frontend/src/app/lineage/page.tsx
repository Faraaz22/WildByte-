"use client";

import { useState, useEffect } from "react";
import { GitBranch, Table2, Loader2 } from "lucide-react";
import { getFullLineage, listDatabases, type LineageNode, type LineageEdge } from "../../lib/api/lineage";
import type { DatabaseResponse } from "../../lib/api/databases";

export default function LineagePage() {
  const [nodes, setNodes] = useState<LineageNode[]>([]);
  const [edges, setEdges] = useState<LineageEdge[]>([]);
  const [databases, setDatabases] = useState<DatabaseResponse[]>([]);
  const [databaseId, setDatabaseId] = useState<number | "">("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getFullLineage(databaseId === "" ? undefined : databaseId)
      .then((res) => {
        if (!cancelled) {
          setNodes(res.nodes);
          setEdges(res.edges);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load lineage");
          setNodes([]);
          setEdges([]);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [databaseId]);

  useEffect(() => {
    listDatabases()
      .then((res) => setDatabases(res.data))
      .catch(() => setDatabases([]));
  }, []);

  const nodeById = new Map(nodes.map((n) => [n.id, n]));
  const upstreamByTarget = new Map<number, number[]>();
  const downstreamBySource = new Map<number, number[]>();
  for (const e of edges) {
    if (!upstreamByTarget.has(e.target)) upstreamByTarget.set(e.target, []);
    upstreamByTarget.get(e.target)!.push(e.source);
    if (!downstreamBySource.has(e.source)) downstreamBySource.set(e.source, []);
    downstreamBySource.get(e.source)!.push(e.target);
  }

  const roots = nodes.filter((n) => !(upstreamByTarget.get(n.id)?.length));
  const leaves = nodes.filter((n) => !(downstreamBySource.get(n.id)?.length));
  const middle = nodes.filter(
    (n) =>
      (upstreamByTarget.get(n.id)?.length ?? 0) > 0 &&
      (downstreamBySource.get(n.id)?.length ?? 0) > 0
  );
  const onlyUpstream = nodes.filter(
    (n) =>
      (upstreamByTarget.get(n.id)?.length ?? 0) > 0 &&
      !(downstreamBySource.get(n.id)?.length ?? 0)
  );
  const onlyDownstream = nodes.filter(
    (n) =>
      !(upstreamByTarget.get(n.id)?.length ?? 0) &&
      (downstreamBySource.get(n.id)?.length ?? 0) > 0
  );

  return (
    <div className="mx-auto max-w-7xl">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Lineage
      </h2>
      <p className="mb-6 text-sm text-[var(--color-text-secondary)]">
        Table dependencies (upstream → downstream) from foreign keys. Connect a database in Settings and sync to see lineage.
      </p>

      {databases.length > 0 && (
        <div className="mb-4 flex items-center gap-2">
          <label className="text-sm font-medium text-[var(--color-text)]">Database:</label>
          <select
            value={databaseId}
            onChange={(e) => setDatabaseId(e.target.value === "" ? "" : Number(e.target.value))}
            className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-2 text-sm text-[var(--color-text)]"
          >
            <option value="">All</option>
            {databases.map((db) => (
              <option key={db.id} value={db.id}>
                {db.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] py-12">
          <Loader2 className="h-6 w-6 animate-spin text-[var(--color-text-secondary)]" />
          <span className="text-sm text-[var(--color-text-secondary)]">Loading lineage…</span>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 text-[var(--color-error)]">
          {error}
        </div>
      ) : nodes.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] py-12 text-center">
          <GitBranch className="h-10 w-10 text-[var(--color-text-secondary)]" />
          <p className="text-sm text-[var(--color-text-secondary)]">
            No lineage data. Connect a PostgreSQL database in Settings, then save to extract schemas and foreign keys.
          </p>
        </div>
      ) : (
        <div className="overflow-auto rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-8 shadow-sm">
          <div className="flex flex-wrap items-start justify-center gap-8 md:gap-12">
            {/* Upstream (sources only) */}
            {(onlyUpstream.length > 0 || roots.length > 0) && (
              <>
                <div className="flex flex-col gap-3">
                  <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                    Upstream
                  </p>
                  {(onlyUpstream.length > 0 ? onlyUpstream : roots).map((n) => (
                    <div
                      key={n.id}
                      className="flex min-w-[140px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-4 py-3"
                    >
                      <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                      <span className="truncate text-sm font-medium text-[var(--color-text)]">
                        {n.schema_name}.{n.name}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
                  <span className="text-2xl">→</span>
                </div>
              </>
            )}

            {/* Middle / Core */}
            {(middle.length > 0 || roots.length > 0) && (
              <>
                <div className="flex flex-col gap-3">
                  <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                    Core
                  </p>
                  {(middle.length > 0 ? middle : roots).slice(0, 12).map((n) => (
                    <div
                      key={n.id}
                      className="flex min-w-[140px] items-center gap-2 rounded-lg border-2 border-[var(--color-primary)] bg-[var(--color-primary)]/10 px-4 py-3"
                    >
                      <Table2 className="h-4 w-4 shrink-0 text-[var(--color-primary)]" />
                      <span className="truncate text-sm font-medium text-[var(--color-text)]">
                        {n.schema_name}.{n.name}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
                  <span className="text-2xl">→</span>
                </div>
              </>
            )}

            {/* Downstream (targets only) */}
            {(onlyDownstream.length > 0 || leaves.length > 0) && (
              <div className="flex flex-col gap-3">
                <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                  Downstream
                </p>
                {(onlyDownstream.length > 0 ? onlyDownstream : leaves).slice(0, 12).map((n) => (
                  <div
                    key={n.id}
                    className="flex min-w-[140px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-4 py-3"
                  >
                    <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                    <span className="truncate text-sm font-medium text-[var(--color-text)]">
                      {n.schema_name}.{n.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-[var(--color-text-secondary)]">
            <GitBranch className="h-4 w-4" />
            <span>
              {nodes.length} tables, {edges.length} relationships (from foreign keys)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
