import type { DecisionName } from "@/lib/drafts";

const SAID: Record<DecisionName, string> = {
  approved: "Approved, not sent",
  edited: "Approved with an edit, not sent",
  rejected: "Rejected",
};

/** The estate's own clock, so the same moment reads the same on the server and here. */
const WHEN = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "Europe/London",
});

/**
 * What was decided, on the row rather than only in the header.
 *
 * A row is what gets cropped into a screenshot and travels without its header, and a
 * row reading only "Approved" beside a member's name and a message asserts something
 * that did not happen. Nothing in this project is sent to anybody.
 */
export default function Decision({
  decision,
  decidedAt,
}: {
  decision: DecisionName;
  decidedAt: string;
}) {
  return (
    <span className="block text-xs">
      <span className={`font-medium ${decision === "rejected" ? "text-ink-dim" : "text-accent"}`}>
        {SAID[decision]}
      </span>
      <span className="text-ink-dim mt-0.5 block">{WHEN.format(new Date(decidedAt))}</span>
    </span>
  );
}
