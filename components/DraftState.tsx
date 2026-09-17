export type DraftStatus = "not drafted" | "drafting" | "drafted" | "failed";

/** Why a call did not produce a message. Which one it was decides what to offer. */
export type Failure = "unreachable" | "no credit" | "daily limit";

/** Shared with the briefing, so the three messages exist once. */
export const FAILURE: Record<Failure, { heading: string; detail: string; fault: boolean }> = {
  unreachable: {
    heading: "Could not reach the model",
    detail: "Transient. Worth trying again.",
    fault: true,
  },
  "no credit": {
    heading: "No credit remaining",
    detail: "Trying again will not help. The account needs topping up first.",
    fault: true,
  },
  "daily limit": {
    heading: "Daily limit reached",
    detail: "The cap on model calls for today is spent. It resets tomorrow.",
    fault: false,
  },
};

/**
 * Where a row in the queue has got to.
 *
 * The daily limit is styled as a limit rather than a fault, because it is the cap
 * working as designed. Dressing it in the same red as a broken call would report a
 * deliberate constraint as a malfunction.
 */
export default function DraftState({
  status,
  failure,
}: {
  status: DraftStatus;
  failure?: Failure;
}) {
  if (status === "not drafted") {
    return <span className="text-ink-dim text-xs">No message yet</span>;
  }

  if (status === "drafting") {
    return (
      <span className="text-ink-dim inline-flex items-center gap-2 text-xs" aria-live="polite">
        <span className="bg-accent h-1.5 w-1.5 animate-pulse" aria-hidden />
        Drafting
      </span>
    );
  }

  if (status === "drafted") {
    return <span className="text-accent text-xs font-medium">Drafted, not sent</span>;
  }

  const { heading, detail, fault } = FAILURE[failure ?? "unreachable"];
  return (
    <span className="block text-xs" role={fault ? "alert" : undefined}>
      <span className={fault ? "text-high font-medium" : "text-ink font-medium"}>{heading}</span>
      <span className="text-ink-dim mt-0.5 block">{detail}</span>
    </span>
  );
}
