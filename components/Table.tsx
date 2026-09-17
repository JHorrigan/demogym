import type { ReactNode } from "react";

/**
 * A table that scrolls sideways inside itself rather than pushing the page wide.
 *
 * Hairline rules and no striping. `caption` is read by a screen reader and hidden
 * on screen, because the heading above the table already says what it holds.
 */
export function Table({ caption, children }: { caption: string; children: ReactNode }) {
  return (
    <div className="relative">
      {/* A region you can scroll has to be reachable by keyboard, which is also what
          gives it a focus ring and so signals that it moves. */}
      <div
        tabIndex={0}
        role="region"
        aria-label={caption}
        className="border-rule bg-raised overflow-x-auto border"
      >
        <table className="w-full min-w-max border-collapse text-sm">
          <caption className="sr-only">{caption}</caption>
          {children}
        </table>
      </div>
      {/* At phone width a dense table always runs past the edge, and a column cut
          off mid-word reads as broken rather than as scrollable. */}
      <div
        aria-hidden
        className="from-raised pointer-events-none absolute inset-y-px right-px w-8 bg-gradient-to-l to-transparent sm:hidden"
      />
    </div>
  );
}

export function HeaderCell({
  children,
  numeric = false,
}: {
  children: ReactNode;
  numeric?: boolean;
}) {
  return (
    <th
      scope="col"
      className={`label border-rule border-b px-3 py-3 whitespace-nowrap ${
        numeric ? "text-right" : "text-left"
      }`}
    >
      {children}
    </th>
  );
}

export function Row({ children }: { children: ReactNode }) {
  return <tr className="border-rule border-b last:border-0">{children}</tr>;
}

export function Cell({
  children,
  numeric = false,
  wrap = false,
}: {
  children: ReactNode;
  numeric?: boolean;
  wrap?: boolean;
}) {
  return (
    <td
      className={`px-3 py-3 align-top ${numeric ? "figure text-right" : ""} ${
        wrap ? "min-w-[22rem] whitespace-normal" : "whitespace-nowrap"
      }`}
    >
      {children}
    </td>
  );
}
