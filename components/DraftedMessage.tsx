import type { Draft } from "@/lib/drafts";

/**
 * One drafted message, with the settings that produced it.
 *
 * The settings are on the message rather than in a tooltip, because a redraft sits
 * directly beneath the draft it replaced and the only useful comparison is between
 * the terms each was written on.
 *
 * The rationale is addressed to the reviewer and not to the member, so it is set
 * apart from the message rather than beneath it as though it were a sign-off.
 */
export default function DraftedMessage({ draft }: { draft: Draft }) {
  return (
    <article className="border-rule border-t pt-4">
      <p className="label">
        Attempt {draft.attempt} <Dot /> {draft.tone} <Dot /> {draft.length} <Dot />{" "}
        {draft.offer === "none" ? "no offer" : draft.offer}
      </p>

      <p className="mt-3 text-sm font-semibold">{draft.subject}</p>
      <p className="mt-2 max-w-prose text-sm leading-relaxed whitespace-pre-line">{draft.body}</p>

      <div className="bg-paper border-rule mt-4 max-w-prose border-l-2 px-3 py-2">
        <p className="label">Why it was written this way</p>
        <p className="text-ink-dim mt-1.5 text-xs leading-relaxed">{draft.rationale}</p>
      </div>
    </article>
  );
}

function Dot() {
  return <span className="text-ink-faint mx-1">/</span>;
}
