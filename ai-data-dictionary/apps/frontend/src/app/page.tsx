"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Database, Plus, RefreshCw, Table2, Layers } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import Button from "../components/ui/Button";
import EmptyState from "../components/common/EmptyState";
import Link from "next/link";
import { apiClient } from "../lib/api-client";
import { AuthStore } from "../lib/auth-store";

interface DatabaseConnection {
  id: number;
  name: string;
  db_type: string;
  description?: string;
  host?: string;
  port?: number;
  created_at: string;
  updated_at: string;
}

interface TablesPerDatabase {
  database_id: number;
  database_name: string;
  table_count: number;
}

interface Stats {
  total_databases: number;
  total_schemas: number;
  total_tables: number;
  tables_per_database?: TablesPerDatabase[];
}

export default function Page() {
  const router = useRouter();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatabases();
    loadStats();
  }, []);

  const loadDatabases = async () => {
    try {
      setLoading(true);
      const token = AuthStore.getToken();
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await apiClient.get<{
        data: DatabaseConnection[];
        total: number;
      }>("/databases", token);

      setDatabases(response.data);
    } catch (error) {
      console.error("Failed to load databases:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const token = AuthStore.getToken();
      if (!token) return;
      const data = await apiClient.get<Stats>("/stats", token);
      setStats(data);
    } catch {
      setStats(null);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-[var(--color-text)]">
          Overview
        </h2>
      </div>

      {stats && (stats.total_databases > 0 || stats.total_tables > 0) && (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Database className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-[var(--color-text)]">
                    {stats.total_databases}
                  </p>
                  <p className="text-xs font-medium text-[var(--color-text-secondary)]">
                    Databases
                  </p>
                </div>
              </div>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Layers className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-[var(--color-text)]">
                    {stats.total_schemas}
                  </p>
                  <p className="text-xs font-medium text-[var(--color-text-secondary)]">
                    Schemas
                  </p>
                </div>
              </div>
            </div>
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Table2 className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-[var(--color-text)]">
                    {stats.total_tables}
                  </p>
                  <p className="text-xs font-medium text-[var(--color-text-secondary)]">
                    Tables
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="mb-6 grid gap-6 lg:grid-cols-2">
            {stats.tables_per_database && stats.tables_per_database.length > 0 && (
              <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm">
                <h3 className="mb-3 text-sm font-semibold text-[var(--color-text)]">
                  Tables per database
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={stats.tables_per_database.map((d) => ({
                        name: d.database_name.length > 12 ? d.database_name.slice(0, 12) + "…" : d.database_name,
                        fullName: d.database_name,
                        tables: d.table_count,
                      }))}
                      margin={{ top: 8, right: 8, left: 0, bottom: 8 }}
                    >
                      <XAxis
                        dataKey="name"
                        tick={{ fontSize: 11 }}
                        stroke="var(--color-text-secondary)"
                      />
                      <YAxis tick={{ fontSize: 11 }} stroke="var(--color-text-secondary)" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--color-bg)",
                          border: "1px solid var(--color-border)",
                          borderRadius: "6px",
                        }}
                        labelFormatter={(_, payload) => payload[0]?.payload?.fullName}
                        formatter={(value: number) => [`${value} tables`, "Tables"]}
                      />
                      <Bar dataKey="tables" fill="var(--color-primary)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
            <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-sm">
              <h3 className="mb-3 text-sm font-semibold text-[var(--color-text)]">
                Overview
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: "Databases", value: stats.total_databases, color: "hsl(var(--color-primary))" },
                        { name: "Schemas", value: stats.total_schemas, color: "hsl(var(--color-primary) / 0.7)" },
                        { name: "Tables", value: stats.total_tables, color: "hsl(var(--color-primary) / 0.4)" },
                      ].filter((d) => d.value > 0)}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                      nameKey="name"
                      label={({ name, value }) => `${name}: ${value}`}
                      labelLine={{ stroke: "var(--color-text-secondary)" }}
                    >
                      {[
                        { name: "Databases", value: stats.total_databases, color: "hsl(var(--color-primary))" },
                        { name: "Schemas", value: stats.total_schemas, color: "hsl(var(--color-primary) / 0.7)" },
                        { name: "Tables", value: stats.total_tables, color: "hsl(var(--color-primary) / 0.4)" },
                      ]
                        .filter((d) => d.value > 0)
                        .map((entry) => (
                          <Cell key={entry.name} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "var(--color-bg)",
                        border: "1px solid var(--color-border)",
                        borderRadius: "6px",
                      }}
                      formatter={(value: number) => [value, ""]}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-[var(--color-primary)]" />
        </div>
      ) : databases.length === 0 ? (
        <EmptyState
          icon={<Database />}
          title="No databases connected"
          description="Connect your first database to start generating documentation and exploring schemas."
          action={
            <Button variant="primary" onClick={() => router.push("/databases/new")}>
              <Plus className="mr-2 h-4 w-4" />
              Add Database
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {databases.map((db) => (
            <Link key={db.id} href={`/databases/${db.id}`}>
              <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm transition-shadow hover:shadow-md cursor-pointer">
                <div className="flex items-start gap-3">
                  <Database className="h-8 w-8 text-[var(--color-primary)]" />
                  <div className="min-w-0">
                    <h3 className="font-semibold text-[var(--color-text)]">
                      {db.name}
                    </h3>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      {db.db_type}
                    </p>
                    {db.host && (
                      <p className="text-xs text-[var(--color-text-secondary)] mt-2">
                        {db.host}:{db.port}
                      </p>
                    )}
                    {db.description && (
                      <p className="text-xs text-[var(--color-text-secondary)] mt-1 line-clamp-2">
                        {db.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
