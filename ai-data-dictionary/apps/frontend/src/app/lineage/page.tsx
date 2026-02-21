"use client";

import { useState, useEffect } from "react";
import { GitBranch, Table2, Loader2, ArrowRight, ChevronDown, ChevronRight } from "lucide-react";
import { getFullLineage, type LineageNode, type LineageEdge } from "../../lib/api/lineage";
import { listDatabases, type DatabaseResponse } from "../../lib/api/databases";

function nodeLabel(n: LineageNode) {
  return n.schema_name ? `${n.schema_name}.${n.name}` : n.name;
}

export default function LineagePage() {
  const [nodes, setNodes] = useState<LineageNode[]>([]);
  const [edges, setEdges] = useState<LineageEdge[]>([]);
  const [databases, setDatabases] = useState<DatabaseResponse[]>([]);
  const [databaseId, setDatabaseId] = useState<number | "">("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedEdge, setExpandedEdge] = useState<number | null>(null);

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
  // onlyUpstream: pure source nodes — no parents of their own, but feed into others (= root/upstream)
  const onlyUpstream = nodes.filter(
    (n) =>
      !(upstreamByTarget.get(n.id)?.length ?? 0) &&
      (downstreamBySource.get(n.id)?.length ?? 0) > 0
  );
  // onlyDownstream: pure sink nodes — fed by others but produce nothing (= leaf/downstream)
  const onlyDownstream = nodes.filter(
    (n) =>
      (upstreamByTarget.get(n.id)?.length ?? 0) > 0 &&
      !(downstreamBySource.get(n.id)?.length ?? 0)
  );

  return (
    <div className="mx-auto max-w-7xl">
      <h2 className="mb-2 text-2xl font-semibold text-[var(--color-text)]">
        Lineage
      </h2>
      <p className="mb-6 text-sm text-[var(--color-text-secondary)]">
        Table dependencies from <strong>foreign keys</strong> (referenced table → referencing table). Column-level links are shown in the relationships table. Re-sync your database after schema changes to refresh.
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
            No lineage data. Connect a PostgreSQL database in Settings, then <strong>Sync</strong> to extract schemas and foreign keys.
          </p>
        </div>
      ) : (
        <>
          {/* Summary cards */}
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">Tables</p>
              <p className="text-xl font-semibold text-[var(--color-text)]">{nodes.length}</p>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">Relationships (FK)</p>
              <p className="text-xl font-semibold text-[var(--color-text)]">{edges.length}</p>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-3">
              <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">Source tables (no refs)</p>
              <p className="text-xl font-semibold text-[var(--color-text)]">{roots.length + onlyUpstream.length}</p>
            </div>
          </div>

          {/* Relationships table: precise FK info */}
          {edges.length > 0 && (
            <div className="mb-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
              <h3 className="border-b border-[var(--color-border)] px-4 py-3 text-sm font-semibold text-[var(--color-text)]">
                Relationships (foreign keys)
              </h3>
              <div className="divide-y divide-[var(--color-border)]">
                {edges.map((e, idx) => {
                  const src = nodeById.get(e.source);
                  const tgt = nodeById.get(e.target);
                  const srcLabel = src ? nodeLabel(src) : `Table ${e.source}`;
                  const tgtLabel = tgt ? nodeLabel(tgt) : `Table ${e.target}`;
                  const pairs = e.column_mapping && e.column_mapping.length > 0
                    ? e.column_mapping
                    : null;
                  const isExpanded = expandedEdge === idx;
                  return (
                    <div key={`${e.source}-${e.target}-${idx}`} className="px-4 py-2">
                      <button
                        type="button"
                        onClick={() => setExpandedEdge(isExpanded ? null : idx)}
                        className="flex w-full items-center gap-2 text-left text-sm"
                      >
                        {isExpanded ? (
                          <ChevronDown className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                        ) : (
                          <ChevronRight className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                        )}
                        <span className="font-medium text-[var(--color-text)]">{srcLabel}</span>
                        <ArrowRight className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                        <span className="font-medium text-[var(--color-text)]">{tgtLabel}</span>
                        {e.cardinality && (
                          <span
                            className="rounded px-1.5 py-0.5 text-xs font-medium"
                            title={e.cardinality}
                            style={{
                              backgroundColor:
                                e.cardinality === "one_to_one"
                                  ? "var(--color-bg-secondary)"
                                  : e.cardinality === "many_to_many"
                                    ? "hsl(var(--color-primary) / 0.2)"
                                    : "var(--color-bg-secondary)",
                            }}
                          >
                            {e.cardinality === "one_to_one"
                              ? "1∶1"
                              : e.cardinality === "one_to_many"
                                ? "1∶N"
                                : "N∶N"}
                          </span>
                        )}
                        {e.is_join_table && (
                          <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-xs text-amber-700 dark:text-amber-300" title="Join table">
                            join
                          </span>
                        )}
                        {pairs && (
                          <span className="rounded bg-primary/10 px-1.5 py-0.5 text-xs text-primary">
                            {pairs.length} col{pairs.length !== 1 ? "s" : ""}
                          </span>
                        )}
                      </button>
                      {isExpanded && (
                        <div className="mt-2 ml-6 space-y-1 border-l-2 border-[var(--color-border)] pl-3 text-xs">
                          {pairs ? (
                            pairs.map((p, i) => (
                              <div key={i} className="text-[var(--color-text-secondary)]">
                                <span className="font-mono text-[var(--color-text)]">
                                  {(p as { referenced_column?: string }).referenced_column ?? "?"}
                                </span>
                                <span className="mx-1">→</span>
                                <span className="font-mono text-[var(--color-text)]">
                                  {(p as { referencing_column?: string }).referencing_column ?? "?"}
                                </span>
                              </div>
                            ))
                          ) : (
                            <p className="text-[var(--color-text-secondary)]">
                              No column mapping (re-sync database to extract FK column names).
                            </p>
                          )}
                          {e.label && (
                            <p className="pt-1 text-[var(--color-text-secondary)]">{e.label}</p>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Visual buckets */}
          <div className="overflow-auto rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-6 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-[var(--color-text)]">Table groups</h3>
            <div className="flex flex-wrap items-start justify-center gap-6 md:gap-10">
              {(onlyUpstream.length > 0 || roots.length > 0) && (
                <>
                  <div className="flex flex-col gap-2">
                    <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                      Upstream / Roots
                    </p>
                    {(onlyUpstream.length > 0 ? onlyUpstream : roots).map((n) => (
                      <div
                        key={n.id}
                        className="flex min-w-[160px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-3 py-2"
                        title={`${n.schema_name}.${n.name} (${n.table_type})`}
                      >
                        <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                        <span className="truncate text-sm font-medium text-[var(--color-text)]">
                          {nodeLabel(n)}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
                    <ArrowRight className="h-5 w-5" />
                  </div>
                </>
              )}

              {(middle.length > 0 || roots.length > 0) && (
                <>
                  <div className="flex flex-col gap-2">
                    <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                      Core
                    </p>
                    {(middle.length > 0 ? middle : roots).slice(0, 15).map((n) => (
                      <div
                        key={n.id}
                        className="flex min-w-[160px] items-center gap-2 rounded-lg border-2 border-primary bg-primary/10 px-3 py-2"
                        title={`${n.schema_name}.${n.name} (${n.table_type})`}
                      >
                        <Table2 className="h-4 w-4 shrink-0 text-primary" />
                        <span className="truncate text-sm font-medium text-[var(--color-text)]">
                          {nodeLabel(n)}
                        </span>
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center text-[var(--color-text-secondary)]" aria-hidden>
                    <ArrowRight className="h-5 w-5" />
                  </div>
                </>
              )}

              {(onlyDownstream.length > 0 || leaves.length > 0) && (
                <div className="flex flex-col gap-2">
                  <p className="text-center text-xs font-medium uppercase tracking-wider text-[var(--color-text-secondary)]">
                    Downstream / Leaves
                  </p>
                  {(onlyDownstream.length > 0 ? onlyDownstream : leaves).slice(0, 15).map((n) => (
                    <div
                      key={n.id}
                      className="flex min-w-[160px] items-center gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg-secondary)] px-3 py-2"
                      title={`${n.schema_name}.${n.name} (${n.table_type})`}
                    >
                      <Table2 className="h-4 w-4 shrink-0 text-[var(--color-text-secondary)]" />
                      <span className="truncate text-sm font-medium text-[var(--color-text)]">
                        {nodeLabel(n)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <GitBranch className="h-4 w-4" />
              <span>
                {nodes.length} tables, {edges.length} foreign key relationship{edges.length !== 1 ? "s" : ""}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
