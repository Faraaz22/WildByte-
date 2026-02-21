"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  Table2,
  GitBranch,
  Settings,
} from "lucide-react";
import { clsx } from "clsx";

const navItems = [
  { href: "/", label: "Home", icon: LayoutDashboard },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/tables", label: "Tables", icon: Table2 },
  { href: "/lineage", label: "Lineage", icon: GitBranch },
  { href: "/settings", label: "Settings", icon: Settings },
];

function NavItem({
  href,
  label,
  icon: Icon,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const pathname = usePathname();
  const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <Link
      href={href}
      className={clsx(
        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors min-h-[44px]",
        isActive
          ? "bg-primary/10 text-primary"
          : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)] hover:text-[var(--color-text)]"
      )}
      aria-current={isActive ? "page" : undefined}
    >
      <Icon className="h-5 w-5 shrink-0" aria-hidden />
      {label}
    </Link>
  );
}

export default function Sidebar() {
  return (
    <aside
      className="hidden w-64 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-bg)] md:block"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="flex h-full flex-col p-4">
        <div className="mb-6 text-lg font-semibold text-[var(--color-text)]">
          AI Data Dictionary
        </div>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <NavItem
              key={item.href}
              href={item.href}
              label={item.label}
              icon={item.icon}
            />
          ))}
        </nav>
      </div>
    </aside>
  );
}
