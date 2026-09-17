import type { ReactNode } from "react";

import { SECTIONS } from "./sections";

/**
 * One numbered section, with its ordinal in a left gutter like a specification sheet.
 * The number and the title come from `sections.ts`, so the rail cannot drift from the page.
 */
export default function Section({ id, children }: { id: string; children: ReactNode }) {
  const index = SECTIONS.findIndex((section) => section.id === id);
  const { title } = SECTIONS[index];

  return (
    <section id={id} className="border-rule scroll-mt-4 border-t pt-6">
      <div className="sm:grid sm:grid-cols-[3rem_1fr] sm:gap-6">
        <p className="figure text-ink-faint text-sm leading-7">{String(index + 1).padStart(2, "0")}</p>
        <div className="max-w-3xl">
          <h2 className="text-lg leading-7 font-semibold tracking-tight">{title}</h2>
          <div className="mt-4 space-y-4 text-sm leading-relaxed">{children}</div>
        </div>
      </div>
    </section>
  );
}
