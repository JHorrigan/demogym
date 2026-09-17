"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Button from "@/components/Button";
import type { DraftStatus, Failure } from "@/components/DraftState";
import MemberPanel, { type PanelRow } from "@/components/MemberPanel";
import Select from "@/components/Select";

import type { DecisionName, Draft } from "@/lib/drafts";

const TONES = ["warm", "direct", "encouraging"] as const;
const LENGTHS = ["short", "standard"] as const;
const OFFERS = ["none", "free class", "guest pass", "personal training session"] as const;

/**
 * Draft all keeps this many calls in flight.
 *
 * 0008: nearly all the rate limiting this system could suffer would be self-inflicted
 * by firing twenty at once, and a constant is cheaper than a recovery path.
 */
const IN_FLIGHT = 4;

const FAILURES: readonly string[] = ["unreachable", "no credit", "daily limit"];

/** What `draft_endpoint.respond` returns. Agreed by hand, checked by neither side. */
type Drafted = {
  member_id: number;
  attempt: number;
  tone: string;
  length: string;
  offer: string;
  subject: string;
  body: string;
  rationale: string;
  cost_usd_cents: number;
};

/** What `decide_endpoint.respond` returns. Agreed by hand, checked by neither side. */
type Decided = {
  member_id: number;
  attempt: number;
  decision: DecisionName;
  edited_body: string | null;
  decided_at: string;
};

type Refused = { error: string; message: string };

type Controls = { tone: string; length: string; offer: string };

/**
 * The High band, and the controls that draft it.
 *
 * One set of controls rather than one per row. They are the terms of the next call,
 * whether that call is one member or a sweep, and the terms each message was written
 * on are printed on the message itself, so nothing is lost by the controls moving on.
 */
export default function DraftQueue({
  token,
  rows,
  stored,
}: {
  token: string;
  rows: PanelRow[];
  stored: Draft[];
}) {
  const router = useRouter();
  const [controls, setControls] = useState<Controls>({
    tone: "warm",
    length: "standard",
    offer: "none",
  });
  const [drafts, setDrafts] = useState(() => byMember(stored));
  const [states, setStates] = useState<Record<number, { status: DraftStatus; failure?: Failure }>>(
    {},
  );
  const [inFlight, setInFlight] = useState(0);
  const [remaining, setRemaining] = useState(0);
  const [problems, setProblems] = useState<Record<number, string>>({});

  const undrafted = rows.filter((row) => (drafts[row.memberId] ?? []).length === 0);
  const sweeping = remaining > 0;

  async function draft(memberId: number, terms: Controls) {
    setStates((current) => ({ ...current, [memberId]: { status: "drafting" } }));
    setInFlight((count) => count + 1);

    const payload = await ask(memberId, terms, token);
    setInFlight((count) => count - 1);

    if ("error" in payload) {
      setStates((current) => ({
        ...current,
        [memberId]: { status: "failed", failure: failureFor(payload) },
      }));
      return;
    }

    setDrafts((current) => ({
      ...current,
      [memberId]: [...(current[memberId] ?? []), toDraft(payload)],
    }));
    setStates((current) => ({ ...current, [memberId]: { status: "drafted" } }));

    // The cost readout is in the shell, so the header only moves when the server
    // components render again. A sweep that refreshed once at the end would leave a
    // running total that does not run.
    router.refresh();
  }

  /**
   * The sweep. Four workers share one list, so there are never more than four calls
   * out at once and each message renders as it returns rather than at the end.
   *
   * The terms are read once, when the button is pressed. A reviewer who changes a
   * dropdown mid-sweep is choosing the terms of the next sweep, not of whichever
   * call happens to be in flight.
   */
  async function draftAll() {
    const terms = controls;
    const queue = undrafted.map((row) => row.memberId);
    setRemaining(queue.length);

    await Promise.all(
      Array.from({ length: Math.min(IN_FLIGHT, queue.length) }, async () => {
        for (let next = queue.shift(); next !== undefined; next = queue.shift()) {
          await draft(next, terms);
          setRemaining((left) => left - 1);
        }
      }),
    );

    // Refreshes made while calls were still in flight can coalesce, which leaves the
    // header a call behind. One more once the sweep is over settles it.
    router.refresh();
  }

  /**
   * One decision, final for that member.
   *
   * The endpoint decides which attempt it lands on and stamps the time, so a stale
   * page cannot record a decision against a draft that has been replaced.
   */
  async function decide(
    memberId: number,
    decision: DecisionName,
    editedBody: string | null,
  ): Promise<void> {
    setProblems((current) => ({ ...current, [memberId]: "" }));

    const payload = await tell(memberId, decision, editedBody, token);
    if ("error" in payload) {
      setProblems((current) => ({ ...current, [memberId]: payload.message }));
      return;
    }

    setDrafts((current) => ({
      ...current,
      [memberId]: (current[memberId] ?? []).map((draft) =>
        draft.attempt === payload.attempt
          ? {
              ...draft,
              decision: payload.decision,
              editedBody: payload.edited_body,
              decidedAt: payload.decided_at,
            }
          : draft,
      ),
    }));
    router.refresh();
  }

  return (
    <div className="space-y-5">
      <div className="border-rule bg-raised border p-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Select
            label="Tone"
            value={controls.tone}
            options={TONES}
            disabled={sweeping}
            onChange={(tone) => setControls({ ...controls, tone })}
          />
          <Select
            label="Length"
            value={controls.length}
            options={LENGTHS}
            disabled={sweeping}
            onChange={(length) => setControls({ ...controls, length })}
          />
          <Select
            label="Offer"
            value={controls.offer}
            options={OFFERS}
            disabled={sweeping}
            onChange={(offer) => setControls({ ...controls, offer })}
          />
        </div>

        <div className="border-rule mt-4 flex flex-wrap items-center justify-between gap-3 border-t pt-4">
          <p className="text-ink-dim max-w-md text-xs leading-relaxed">
            Every prompt this system can send is one combination of these three dropdowns. There is no
            free text box, so nothing a reader types reaches the model.
          </p>
          <div className="flex items-center gap-4">
            {sweeping ? (
              <p className="label" aria-live="polite">
                <span className="figure text-ink">{inFlight}</span> in flight
                <span className="text-ink-faint mx-1.5">/</span>
                <span className="figure text-ink">{remaining}</span> to go
              </p>
            ) : null}
            <Button tone="primary" onClick={draftAll} disabled={sweeping || undrafted.length === 0}>
              {undrafted.length > 0 ? `Draft all ${undrafted.length}` : "Draft all"}
            </Button>
          </div>
        </div>
      </div>

      {rows.map((row) => (
        <MemberPanel
          key={row.memberId}
          row={row}
          status={states[row.memberId]?.status ?? stateOf(drafts[row.memberId])}
          failure={states[row.memberId]?.failure}
          drafts={drafts[row.memberId] ?? []}
          busy={sweeping}
          problem={problems[row.memberId] || undefined}
          onDraft={() => draft(row.memberId, controls)}
          onDecide={(decision, editedBody) => decide(row.memberId, decision, editedBody)}
        />
      ))}
    </div>
  );
}

/**
 * The call, and what to do when it does not come back as an answer.
 *
 * A dropped connection, or a platform error page where the endpoint's JSON should
 * be, is the reviewer's "could not reach the model" and nothing more specific. The
 * endpoint's own refusals arrive as JSON and are read below.
 */
async function ask(memberId: number, terms: Controls, token: string): Promise<Drafted | Refused> {
  try {
    const response = await fetch("/api/draft", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demogym-token": token },
      body: JSON.stringify({ member_id: memberId, ...terms }),
    });
    return await response.json();
  } catch (unanswered) {
    console.error("the drafting endpoint did not answer", memberId, unanswered);
    return { error: "unreachable", message: "The call did not get through." };
  }
}

/** The decision call. A refusal here is a disagreement about state, not a failure. */
async function tell(
  memberId: number,
  decision: DecisionName,
  editedBody: string | null,
  token: string,
): Promise<Decided | Refused> {
  try {
    const response = await fetch("/api/decide", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demogym-token": token },
      body: JSON.stringify({ member_id: memberId, decision, edited_body: editedBody }),
    });
    return await response.json();
  } catch (unanswered) {
    console.error("the decision endpoint did not answer", memberId, unanswered);
    return { error: "unreachable", message: "The decision did not get through. Try again." };
  }
}

function byMember(stored: Draft[]): Record<number, Draft[]> {
  const grouped: Record<number, Draft[]> = {};
  for (const draft of stored) {
    grouped[draft.memberId] = [...(grouped[draft.memberId] ?? []), draft];
  }
  return grouped;
}

/** A member with a stored draft is drafted, whoever drafted it and whenever. */
function stateOf(drafts: Draft[] | undefined): DraftStatus {
  return drafts && drafts.length > 0 ? "drafted" : "not drafted";
}

function isFailure(error: string): error is Failure {
  return FAILURES.includes(error);
}

/**
 * The three states the interface knows.
 *
 * Any other refusal means this page and the database disagree, which is a defect
 * rather than something a reviewer can act on. The row reads as failed and what the
 * endpoint actually said goes to the console.
 */
function failureFor(refused: Refused): Failure {
  if (isFailure(refused.error)) {
    return refused.error;
  }
  console.error("the drafting endpoint refused a call", refused);
  return "unreachable";
}

function toDraft(payload: Drafted): Draft {
  return {
    memberId: payload.member_id,
    attempt: payload.attempt,
    tone: payload.tone,
    length: payload.length,
    offer: payload.offer,
    subject: payload.subject,
    body: payload.body,
    rationale: payload.rationale,
    costUsdCents: payload.cost_usd_cents,
    decision: null,
    editedBody: null,
    decidedAt: null,
  };
}
