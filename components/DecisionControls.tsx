"use client";

import { useState } from "react";

import Button from "@/components/Button";

import type { DecisionName } from "@/lib/drafts";

/**
 * Approve, Edit and Reject, on the latest draft.
 *
 * The names are the ones the equivalent production tool would use, because a
 * prototype that renames them to soften what they do is describing a different
 * workflow from the one it is arguing for.
 */
export default function DecisionControls({
  body,
  busy,
  problem,
  onDecide,
}: {
  body: string;
  busy: boolean;
  problem?: string;
  onDecide: (decision: DecisionName, editedBody: string | null) => void;
}) {
  const [editing, setEditing] = useState<string | null>(null);

  if (editing !== null) {
    return (
      <div className="border-rule border-t px-4 py-4">
        <label className="block">
          <span className="label mb-2 block">Edit the message</span>
          <textarea
            value={editing}
            rows={14}
            onChange={(event) => setEditing(event.target.value)}
            className="border-edge bg-raised text-ink w-full max-w-prose border px-3 py-2 text-sm leading-relaxed"
          />
        </label>
        <p className="text-ink-dim mt-2 max-w-prose text-xs leading-relaxed">
          The edit is stored beside what the model wrote, never over it, and the interface shows one
          against the other. How often a person has to rewrite a draft is the only quality figure this
          project can honestly produce.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button
            tone="primary"
            disabled={busy || editing.trim() === "" || editing === body}
            onClick={() => onDecide("edited", editing)}
          >
            Approve this edit
          </Button>
          <Button disabled={busy} onClick={() => setEditing(null)}>
            Cancel
          </Button>
        </div>
        {editing === body ? (
          <p className="text-ink-dim mt-2 text-xs">
            Nothing has changed yet. Approve it as it stands instead.
          </p>
        ) : null}
      </div>
    );
  }

  return (
    <div className="border-rule border-t px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <Button tone="primary" disabled={busy} onClick={() => onDecide("approved", null)}>
          Approve
        </Button>
        <Button disabled={busy} onClick={() => setEditing(body)}>
          Edit
        </Button>
        <Button disabled={busy} onClick={() => onDecide("rejected", null)}>
          Reject
        </Button>
        <span className="text-ink-dim ml-1 text-xs">
          Approving records a decision. It does not send anything.
        </span>
      </div>
      {problem ? (
        <p className="text-high mt-2 text-xs" role="alert">
          {problem}
        </p>
      ) : null}
    </div>
  );
}
