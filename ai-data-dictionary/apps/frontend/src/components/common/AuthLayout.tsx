"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import { AuthStore } from "../../lib/auth-store";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const isLogin = pathname === "/login";
  const authenticated = mounted && AuthStore.isAuthenticated();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (isLogin) return;
    if (!AuthStore.isAuthenticated()) {
      router.replace("/login");
    }
  }, [mounted, isLogin, router]);

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "var(--color-bg-secondary)" }}>
        <p style={{ color: "var(--color-text-secondary)" }}>Loading…</p>
      </div>
    );
  }

  if (isLogin) {
    return <>{children}</>;
  }

  if (!authenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center" style={{ background: "var(--color-bg-secondary)" }}>
        <p style={{ color: "var(--color-text-secondary)" }}>Redirecting to login…</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
