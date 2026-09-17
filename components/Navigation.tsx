"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type Destination = { href: string; label: string };

/**
 * The three screens, as an underlined rail rather than tabs.
 *
 * A client component because it reads the current path to mark where you are. The
 * token stays in every href, since it is a real route segment.
 */
export default function Navigation({ token }: { token: string }) {
  const pathname = usePathname();

  const destinations: Destination[] = [
    { href: `/${token}`, label: "Estate" },
    { href: `/${token}/queue`, label: "At-risk queue" },
    { href: `/${token}/real-data`, label: "Running this on real data" },
  ];

  return (
    <nav aria-label="Screens" className="-mb-px flex gap-6 overflow-x-auto">
      {destinations.map(({ href, label }) => {
        const here = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            aria-current={here ? "page" : undefined}
            className={`border-b-2 pb-3 text-sm whitespace-nowrap transition-colors ${
              here
                ? "border-accent text-ink font-medium"
                : "text-ink-dim hover:border-edge hover:text-ink border-transparent"
            }`}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
