import type { ReactNode } from "react";

import CostReadout from "@/components/CostReadout";
import Navigation from "@/components/Navigation";
import SyntheticDataStrip from "@/components/SyntheticDataStrip";

/**
 * The shell every screen renders inside. The strip and the cost readout sit here
 * rather than on each page, so no screen can ship without them.
 */
export default async function Shell({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;

  return (
    <div className="flex min-h-dvh flex-col">
      <SyntheticDataStrip />

      <header className="border-rule bg-raised border-b">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="flex items-start justify-between gap-4 pt-5 pb-4">
            <div>
              <p className="text-lg leading-none font-semibold tracking-tight">demogym</p>
              <p className="text-ink-dim mt-1.5 text-xs">
                Member retention across six sites
              </p>
            </div>
            <CostReadout calls={0} pence={0} />
          </div>
          <Navigation token={token} />
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">{children}</main>

      <footer className="border-rule mt-auto border-t">
        <div className="text-ink-dim mx-auto flex max-w-7xl flex-wrap justify-between gap-2 px-4 py-4 text-xs sm:px-6">
          <p>A prototype on invented data. Nothing here is sent to anybody.</p>
          <a href={`/${token}/interface`} className="hover:text-ink underline">
            Interface states
          </a>
        </div>
      </footer>
    </div>
  );
}
