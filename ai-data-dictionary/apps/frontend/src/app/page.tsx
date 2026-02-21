"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Database, Plus, RefreshCw } from "lucide-react";
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

export default function Page() {
  const router = useRouter();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatabases();
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

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-[var(--color-text)]">
          Overview
        </h2>
      </div>

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
