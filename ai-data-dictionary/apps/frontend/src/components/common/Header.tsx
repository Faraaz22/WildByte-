"use client";

import { useRouter } from "next/navigation";
import { Search, LogOut, User } from "lucide-react";
import { AuthStore } from "../../lib/auth-store";
import { useState } from "react";

export default function Header() {
  const router = useRouter();
  const [showMenu, setShowMenu] = useState(false);
  const user = AuthStore.getUser();

  const handleLogout = () => {
    AuthStore.clearAuth();
    router.push("/login");
  };

  return (
    <header
      className="flex w-full items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-bg)] px-4 py-3 md:px-6"
      role="banner"
    >
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-[var(--color-text)]">
          AI Data Dictionary
        </h1>
        <p className="hidden text-sm text-[var(--color-text-secondary)] sm:inline">
          Insights &amp; schema explorer
        </p>
      </div>
      <div className="flex items-center gap-3">
        <label className="relative hidden md:block">
          <span className="sr-only">Search tables, columns, models</span>
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-secondary)]"
            aria-hidden
          />
          <input
            type="search"
            aria-label="Search tables, columns, models"
            placeholder="Search tables, columns, models..."
            className="w-64 rounded-md border border-[var(--color-border)] bg-[var(--color-bg-secondary)] py-2 pl-9 pr-3 text-sm text-[var(--color-text)] placeholder:text-[var(--color-text-secondary)] focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </label>
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowMenu(!showMenu)}
            className="flex h-10 w-10 min-h-[44px] min-w-[44px] items-center justify-center rounded-full bg-[var(--color-bg-secondary)] text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-border)] focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
            aria-label="Open user menu"
            title={user?.email || "User menu"}
          >
            {user?.username?.charAt(0).toUpperCase() || "U"}
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-lg">
              <div className="border-b border-[var(--color-border)] px-4 py-3">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-[var(--color-text-secondary)]" />
                  <div>
                    <p className="text-sm font-medium text-[var(--color-text)]">
                      {user?.full_name || user?.username || "User"}
                    </p>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      {user?.email}
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-2 px-4 py-3 text-sm text-[var(--color-text)] hover:bg-[var(--color-bg)]"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

