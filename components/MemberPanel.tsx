import Band from "@/components/Band";
import Button from "@/components/Button";
import Decision from "@/components/Decision";
import DecisionControls from "@/components/DecisionControls";
import DraftState, { type DraftStatus, type Failure } from "@/components/DraftState";
import DraftedMessage from "@/components/DraftedMessage";

import type { DecisionName, Draft } from "@/lib/drafts";

/**
 * One High-band member, with everything already formatted.
 *
 * Numbers are formatted where they are read, on the server, so nothing in the
 * client bundle has to reach for the data layer to say what a tenure is.
 */
export type PanelRow = {
  memberId: number;
  accountNumber: string;
  site: string;
  price: string;
  tenure: string;
  reason: string;
};

/** Only a transient failure is worth pressing again. The other two say so instead. */
const RETRYABLE: Failure = "unreachable";

/**
 * A member in the High band, as a panel rather than a table row.
 *
 * A hundred and twenty words does not fit in a table cell, and the High band is
 * worked one member at a time rather than scanned down a column. Medium and Low
 * keep the table, because scanning is exactly what they are for.
 */
export default function MemberPanel({
  row,
  status,
  failure,
  drafts,
  busy,
  problem,
  onDraft,
  onDecide,
}: {
  row: PanelRow;
  status: DraftStatus;
  failure?: Failure;
  drafts: Draft[];
  busy: boolean;
  problem?: string;
  onDraft: () => void;
  onDecide: (decision: DecisionName, editedBody: string | null) => void;
}) {
  const latest = drafts.at(-1);
  const decided = drafts.find((draft) => draft.decision !== null);
  const action = decided ? null : label(status, failure, drafts.length);

  return (
    <section className="border-rule bg-raised border">
      <header className="flex flex-wrap items-baseline gap-x-4 gap-y-2 px-4 pt-4">
        <span className="figure text-sm font-medium">{row.accountNumber}</span>
        <Band band="high" />
        <span className="text-ink-dim text-sm">{row.site}</span>
        <span className="text-ink-dim ml-auto text-xs">
          <span className="figure text-ink">{row.price}</span> a month
          <span className="text-ink-faint mx-2">/</span>
          member for <span className="figure text-ink">{row.tenure}</span>
        </span>
      </header>

      <p className="text-ink-dim mt-3 max-w-prose px-4 text-sm leading-relaxed">{row.reason}</p>

      <div className="border-rule mt-4 flex flex-wrap items-start justify-between gap-3 border-t px-4 py-3">
        {decided?.decision && decided.decidedAt ? (
          <Decision decision={decided.decision} decidedAt={decided.decidedAt} />
        ) : (
          <DraftState status={status} failure={failure} />
        )}
        {action ? (
          <Button onClick={onDraft} disabled={busy || status === "drafting"}>
            {action}
          </Button>
        ) : null}
      </div>

      {drafts.length > 0 ? (
        <div className="space-y-5 px-4 pb-5">
          {drafts.map((draft) => (
            <DraftedMessage key={draft.attempt} draft={draft} />
          ))}
        </div>
      ) : null}

      {latest && !decided && status !== "drafting" ? (
        <DecisionControls
          body={latest.body}
          busy={busy}
          problem={problem}
          onDecide={onDecide}
        />
      ) : null}
    </section>
  );
}

/**
 * What the button offers, or nothing at all.
 *
 * A member with a draft and a redraft has had both, and an enabled button that the
 * endpoint would refuse is worse than no button.
 */
function label(status: DraftStatus, failure: Failure | undefined, attempts: number): string | null {
  if (status === "failed") {
    return failure === RETRYABLE ? "Try again" : null;
  }
  if (attempts === 0) {
    return "Draft";
  }
  return attempts === 1 ? "Redraft" : null;
}
