"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, LogIn, AlertCircle } from "lucide-react";
import Button from "../../components/ui/Button";
import { apiClient } from "../../lib/api-client";
import { AuthStore } from "../../lib/auth-store";

interface LoginFormData {
  email: string;
  password: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<LoginFormData>({
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);

      // Call the login endpoint
      const response = await apiClient.post<{
        access_token: string;
        refresh_token: string;
        token_type: string;
        user: {
          id: number;
          email: string;
          username: string;
          full_name?: string;
          role: string;
          is_active: boolean;
        };
      }>("/auth/login", formData);

      // Store authentication data
      AuthStore.setAuth({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        user: response.user,
      });

      // Redirect to home page
      router.push("/");
    } catch (err: any) {
      setError(
        err.message ||
          "Failed to login. Please check your credentials and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-[var(--color-background)]">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-[var(--color-primary)]/10">
            <Lock className="h-6 w-6 text-[var(--color-primary)]" />
          </div>
          <h1 className="text-3xl font-bold text-[var(--color-text)]">
            Welcome back
          </h1>
          <p className="mt-2 text-[var(--color-text-secondary)]">
            Sign in to your AI Data Dictionary account
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-sm"
        >
          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-5 w-5 text-red-600" />
                <div>
                  <h3 className="font-medium text-red-900">Error</h3>
                  <p className="mt-1 text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-[var(--color-text)]"
              >
                Email Address
              </label>
              <div className="mt-1 flex items-center gap-2">
                <Mail className="h-5 w-5 text-[var(--color-text-secondary)]" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  required
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                  placeholder="you@example.com"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-[var(--color-text)]"
              >
                Password
              </label>
              <div className="mt-1 flex items-center gap-2">
                <Lock className="h-5 w-5 text-[var(--color-text-secondary)]" />
                <input
                  type="password"
                  id="password"
                  name="password"
                  required
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full rounded-md border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
                  placeholder="••••••••"
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            className="mt-6 w-full"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Signing in...
              </>
            ) : (
              <>
                <LogIn className="mr-2 h-4 w-4" />
                Sign in
              </>
            )}
          </Button>

          <p className="mt-4 text-center text-sm text-[var(--color-text-secondary)]">
            For testing, use any email and password
          </p>
        </form>
      </div>
    </div>
  );
}
