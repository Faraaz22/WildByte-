"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, getCurrentUser } from "../../lib/api/auth";
import { AuthStore } from "../../lib/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokenRes = await login({ username, password });
      AuthStore.setToken(tokenRes.access_token);
      const user = await getCurrentUser(tokenRes.access_token);
      AuthStore.setUser(user);
      // Full reload so AuthLayout sees the token on mount (avoids stuck "Signing in…")
      if (typeof window !== "undefined") window.location.href = "/";
      return;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-screen items-center justify-center"
      style={{
        background: "var(--color-bg-secondary)",
        color: "var(--color-text)",
      }}
    >
      <div className="w-full max-w-sm rounded-lg border p-6 shadow-sm" style={{ background: "var(--color-bg)", borderColor: "var(--color-border)" }}>
        <h1 className="mb-6 text-center text-xl font-semibold">Sign in</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <p className="rounded border border-[var(--color-error)] bg-red-50 px-3 py-2 text-sm text-[var(--color-error)]">
              {error}
            </p>
          )}
          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              className="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
              placeholder="admin"
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="w-full rounded border px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{ borderColor: "var(--color-border)", background: "var(--color-bg-secondary)" }}
              placeholder="••••••••"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded py-2 text-sm font-medium text-white focus:outline-none focus:ring-2 disabled:opacity-70"
            style={{ background: "var(--color-primary)" }}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="mt-4 text-center text-xs" style={{ color: "var(--color-text-secondary)" }}>
          Seeded user: admin / admin 123
        </p>
      </div>
    </div>
  );
}
