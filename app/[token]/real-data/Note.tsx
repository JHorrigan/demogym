import type { ReactNode } from "react";

/** A statement that needs qualifying, marked down its left edge and then qualified. */
export default function Note({ statement, children }: { statement: string; children: ReactNode }) {
  return (
    <div className="border-l-edge border-l-2 pl-4">
      <p className="font-medium">{statement}</p>
      <p className="text-ink-dim mt-2 leading-relaxed">{children}</p>
    </div>
  );
}
