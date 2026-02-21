"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Database, CheckCircle2, XCircle, RefreshCw } from "lucide-react";
import Button from "../../../components/ui/Button";
import { apiClient } from "../../../lib/api-client";
import { AuthStore } from "../../../lib/auth-store";

interface DatabaseFormData {
  name: string;
  db_type: string;
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
  description: string;
}

export default function NewDatabasePage() {
  const router = useRouter();
  const [formData, setFormData] = useState<DatabaseFormData>({
    name: "",
    db_type: "postgresql",
    host: "localhost",
    port: 5432,
    database_name: "",
    username: "",
    password: "",
    description: "",
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    connected: boolean;
    message: string;
  } | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "port" ? parseInt(value) : value,
    }));
    setTestResult(null);
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      setError(null);
      const token = AuthStore.getToken();
      if (!token) {
        router.push("/");
        return;
      }

      const result = await apiClient.post<{
        connected: boolean;
        message: string;
      }>("/databases/test-new", formData, token);

      setTestResult(result);
    } catch (err: any) {
      setTestResult({
        connected: false,
        message: err.message || "Connection test failed",
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError(null);
      const token = AuthStore.getToken();
      if (!token) {
        router.push("/");
        return;
      }

      await apiClient.post("/databases", formData, token);
      router.push("/databases");
    } catch (err: any) {
      setError(err.message || "Failed to create database connection");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => router.back()}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <h2 className="text-2xl font-semibold text-[var(--color-text)]">
          Add Database Connection
        </h2>
        <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
          Connect a new database to start cataloging your data
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-sm"
      >
        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <div className="flex">
              <XCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {/* Database Name */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Connection Name *
            </label>
            <input
              type="text"
              id="name"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
              placeholder="My Production Database"
            />
          </div>

          {/* Database Type */}
          <div>
            <label
              htmlFor="db_type"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Database Type *
            </label>
            <select
              id="db_type"
              name="db_type"
              required
              value={formData.db_type}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="sqlserver">SQL Server</option>
              <option value="snowflake">Snowflake</option>
            </select>
          </div>

          {/* Host and Port */}
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <label
                htmlFor="host"
                className="block text-sm font-medium text-[var(--color-text)]"
              >
                Host *
              </label>
              <input
                type="text"
                id="host"
                name="host"
                required
                value={formData.host}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                placeholder="localhost"
              />
            </div>
            <div>
              <label
                htmlFor="port"
                className="block text-sm font-medium text-[var(--color-text)]"
              >
                Port *
              </label>
              <input
                type="number"
                id="port"
                name="port"
                required
                value={formData.port}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                placeholder="5432"
              />
            </div>
          </div>

          {/* Database Name */}
          <div>
            <label
              htmlFor="database_name"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Database Name *
            </label>
            <input
              type="text"
              id="database_name"
              name="database_name"
              required
              value={formData.database_name}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
              placeholder="my_database"
            />
          </div>

          {/* Username */}
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Username *
            </label>
            <input
              type="text"
              id="username"
              name="username"
              required
              value={formData.username}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
              placeholder="postgres"
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Password *
            </label>
            <input
              type="password"
              id="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
              placeholder="••••••••"
            />
          </div>

          {/* Description */}
          <div>
            <label
              htmlFor="description"
              className="block text-sm font-medium text-[var(--color-text)]"
            >
              Description (optional)
            </label>
            <textarea
              id="description"
              name="description"
              rows={3}
              value={formData.description}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
              placeholder="Optional description for this connection"
            />
          </div>
        </div>

        {/* Test Result */}
        {testResult && (
          <div
            className={`mt-4 rounded-md p-4 ${
              testResult.connected
                ? "bg-green-50 border border-green-200"
                : "bg-red-50 border border-red-200"
            }`}
          >
            <div className="flex">
              {testResult.connected ? (
                <CheckCircle2 className="h-5 w-5 text-green-400" />
              ) : (
                <XCircle className="h-5 w-5 text-red-400" />
              )}
              <div className="ml-3">
                <h3
                  className={`text-sm font-medium ${
                    testResult.connected ? "text-green-800" : "text-red-800"
                  }`}
                >
                  {testResult.connected
                    ? "Connection Successful"
                    : "Connection Failed"}
                </h3>
                <div
                  className={`mt-2 text-sm ${
                    testResult.connected ? "text-green-700" : "text-red-700"
                  }`}
                >
                  {testResult.message}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="mt-6 flex gap-3">
          <Button
            type="button"
            variant="secondary"
            onClick={handleTestConnection}
            disabled={testing}
          >
            {testing && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
            Test Connection
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={saving || !testResult?.connected}
            className="flex-1"
          >
            {saving ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Database className="mr-2 h-4 w-4" />
                Save Connection
              </>
            )}
          </Button>
        </div>

        <p className="mt-4 text-xs text-[var(--color-text-secondary)]">
          * Test the connection before saving. Credentials are encrypted before
          storage.
        </p>
      </form>
    </div>
  );
}
