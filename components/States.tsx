import type { ReactNode } from "react";

/**
 * Empty, loading and failed, as pieces every screen shares.
 *
 * The empty state matters most. 0008 has the queue open with no messages in it, and
 * a reviewer drafting one at a time, so an empty queue is the normal starting
 * condition. It has to read as waiting for you rather than as broken.
 */
export function Empty({
  heading,
  children,
  action,
}: {
  heading: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="border-rule bg-raised border border-dashed px-6 py-12 text-center">
      <p className="text-base font-medium">{heading}</p>
      <p className="text-ink-dim mx-auto mt-2 max-w-md text-sm leading-relaxed">{children}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </div>
  );
}

/**
 * A skeleton shaped like the rows it stands in for, so the page does not jump when
 * the real ones arrive. The pulse is suppressed under prefers-reduced-motion by the
 * blanket guard in globals.css.
 */
export function Loading({ rows = 4, label }: { rows?: number; label: string }) {
  return (
    <div className="border-rule bg-raised border" aria-busy="true" aria-live="polite">
      <p className="sr-only">{label}</p>
      {Array.from({ length: rows }, (_, row) => (
        <div key={row} className="border-rule flex items-center gap-4 border-b px-3 py-4 last:border-0">
          <span className="bg-rule h-3 w-32 animate-pulse" />
          <span className="bg-rule h-3 w-20 animate-pulse" />
          <span className="bg-rule ml-auto h-3 w-14 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

/**
 * A failure says what happened and what to do next. It does not apologise, and it
 * does not invite a retry where retrying cannot help.
 */
export function Failed({
  heading,
  children,
  action,
}: {
  heading: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="border-high/40 bg-raised border-l-high border border-l-4 px-5 py-5" role="alert">
      <p className="text-high text-sm font-semibold">{heading}</p>
      <p className="mt-2 max-w-xl text-sm leading-relaxed">{children}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
