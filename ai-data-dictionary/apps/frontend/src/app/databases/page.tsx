"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Database,
  Plus,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  Trash2,
  Edit,
} from "lucide-react";
import Button from "../../components/ui/Button";
import { apiClient } from "../../lib/api-client";
import { AuthStore } from "../../lib/auth-store";

interface DatabaseConnection {
  id: number;
  name: string;
  db_type: string;
  description?: string;
  host?: string;
  port?: number;
  database_name?: string;
  last_sync_at?: string;
  sync_status: string;
  sync_error?: string;
  created_at: string;
  updated_at: string;
}

interface ConnectionStatus {
  connected: boolean;
  message: string;
  status: string;
}

export default function DatabasesPage() {
  const router = useRouter();
  const [databases, setDatabases] = useState<DatabaseConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingConnection, setTestingConnection] = useState<number | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    try {
      setLoading(true);
      const token = AuthStore.getToken();
      if (!token) {
        router.push("/");
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

  const testConnection = async (databaseId: number) => {
    try {
      setTestingConnection(databaseId);
      const token = AuthStore.getToken();
      if (!token) return;

      const result = await apiClient.post<ConnectionStatus>(
        `/databases/${databaseId}/test`,
        {},
        token
      );

      // Refresh the databases list to show updated status
      await loadDatabases();

      return result;
    } catch (error) {
      console.error("Connection test failed:", error);
    } finally {
      setTestingConnection(null);
    }
  };

  const deleteDatabase = async (databaseId: number) => {
    if (!confirm("Are you sure you want to delete this database connection?")) {
      return;
    }

    try {
      const token = AuthStore.getToken();
      if (!token) return;

      await apiClient.delete(`/databases/${databaseId}`, token);
      await loadDatabases();
    } catch (error) {
      console.error("Failed to delete database:", error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "error":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "connected":
        return "Connected";
      case "error":
        return "Error";
      case "pending":
        return "Pending";
      default:
        return "Unknown";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "bg-green-100 text-green-800 border-green-200";
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      case "pending":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="mx-auto max-w-7xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-[var(--color-text)]">
            Database Connections
          </h2>
          <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
            Manage your database connections and test connectivity
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => router.push("/databases/new")}
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Database
        </Button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-[var(--color-primary)]" />
        </div>
      ) : databases.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-[var(--color-border)] bg-[var(--color-surface)] p-12 text-center">
          <Database className="mx-auto h-12 w-12 text-[var(--color-text-secondary)]" />
          <h3 className="mt-4 text-lg font-medium text-[var(--color-text)]">
            No databases connected
          </h3>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
            Get started by adding your first database connection
          </p>
          <Button
            variant="primary"
            className="mt-6"
            onClick={() => router.push("/databases/new")}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Database
          </Button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {databases.map((db) => (
            <div
              key={db.id}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="mb-4 flex items-start justify-between">
                <div className="flex items-center">
                  <Database className="h-8 w-8 text-[var(--color-primary)]" />
                  <div className="ml-3">
                    <h3 className="font-semibold text-[var(--color-text)]">
                      {db.name}
                    </h3>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      {db.db_type}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-4 space-y-2">
                {db.description && (
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    {db.description}
                  </p>
                )}
                {db.host && (
                  <p className="text-sm text-[var(--color-text-secondary)]">
                    {db.host}:{db.port}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[var(--color-text-secondary)]">
                    Status:
                  </span>
                  <span
                    className={`flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-medium ${getStatusColor(
                      db.sync_status
                    )}`}
                  >
                    {getStatusIcon(db.sync_status)}
                    {getStatusText(db.sync_status)}
                  </span>
                </div>
                {db.sync_error && (
                  <p className="text-xs text-red-600">
                    Error: {db.sync_error}
                  </p>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  className="flex-1"
                  onClick={() => testConnection(db.id)}
                  disabled={testingConnection === db.id}
                >
                  {testingConnection === db.id ? (
                    <RefreshCw className="mr-2 h-3 w-3 animate-spin" />
                  ) : (
                    <RefreshCw className="mr-2 h-3 w-3" />
                  )}
                  Test
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => router.push(`/databases/${db.id}`)}
                >
                  <Edit className="h-3 w-3" />
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => deleteDatabase(db.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
