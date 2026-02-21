"use client";

import type { ReactNode } from "react";

export interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export default function EmptyState({
  icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-8 text-center"
      role="status"
      aria-label={`${title}. ${description}`}
    >
      <div
        className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] [&>svg]:h-7 [&>svg]:w-7"
        aria-hidden
      >
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-[var(--color-text)]">
        {title}
      </h3>
      <p className="mt-2 max-w-sm text-sm text-[var(--color-text-secondary)]">
        {description}
      </p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
