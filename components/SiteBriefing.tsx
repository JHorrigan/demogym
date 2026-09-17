"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import Button from "@/components/Button";
import { FAILURE, type Failure } from "@/components/DraftState";

import type { SiteBriefingRow } from "@/lib/briefings";

const FAILURES: readonly string[] = ["unreachable", "no credit", "daily limit"];

/** What `briefing_endpoint.respond` returns. Agreed by hand, checked by neither side. */
type Written = {
  site_id: number;
  site: string;
  generated_on: string;
  body: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cost_usd_cents: number;
};

type Refused = { error: string; message: string };

/** The estate's own clock, so a date reads the same on the server and here. */
const WHEN = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "long",
  timeZone: "Europe/London",
});

/**
 * One site's briefing, written when somebody asks.
 *
 * It starts empty, exactly as the queue does. The prose is rendered as it was
 * stored, headings and all, because what is on the screen should be what the row
 * holds rather than a reading of it.
 */
export default function SiteBriefing({
  token,
  siteId,
  siteName,
  stored,
}: {
  token: string;
  siteId: number;
  siteName: string;
  stored: SiteBriefingRow | null;
}) {
  const router = useRouter();
  const [briefing, setBriefing] = useState(stored);
  const [writing, setWriting] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [problem, setProblem] = useState<string | null>(null);

  async function write() {
    setWriting(true);
    setFailure(null);
    setProblem(null);

    const payload = await ask(siteId, token);
    setWriting(false);

    if ("error" in payload) {
      if (isFailure(payload.error)) {
        setFailure(payload.error);
      } else {
        console.error("the briefing endpoint refused a call", payload);
        setProblem(payload.message);
      }
      return;
    }

    setBriefing({
      siteId: payload.site_id,
      generatedOn: payload.generated_on,
      body: payload.body,
      model: payload.model,
      inputTokens: payload.input_tokens,
      outputTokens: payload.output_tokens,
      costUsdCents: payload.cost_usd_cents,
    });

    // The cost readout is in the shell, so it only moves when the server components
    // render again. A briefing is a billed call and belongs in the running total.
    router.refresh();
  }

  return (
    <section className="border-rule bg-raised border">
      <header className="border-rule flex flex-wrap items-center justify-between gap-3 border-b px-4 py-3">
        <div>
          <p className="label">Site briefing</p>
          <p className="text-ink-dim mt-1 text-xs">
            {briefing
              ? `Written on ${WHEN.format(new Date(briefing.generatedOn))} from the figures above`
              : `Written on request from ${siteName}'s own figures. Nothing until somebody asks.`}
          </p>
        </div>
        <Button tone={briefing ? "quiet" : "primary"} disabled={writing} onClick={write}>
          {briefing ? "Write it again" : "Write the briefing"}
        </Button>
      </header>

      {writing ? (
        <p className="text-ink-dim flex items-center gap-2 px-4 py-4 text-xs" aria-live="polite">
          <span className="bg-accent h-1.5 w-1.5 animate-pulse" aria-hidden />
          Writing the briefing
        </p>
      ) : null}

      {failure ? (
        <p
          className="block px-4 py-4 text-xs"
          role={FAILURE[failure].fault ? "alert" : undefined}
        >
          <span className={FAILURE[failure].fault ? "text-high font-medium" : "text-ink font-medium"}>
            {FAILURE[failure].heading}
          </span>
          <span className="text-ink-dim mt-0.5 block">{FAILURE[failure].detail}</span>
        </p>
      ) : null}

      {problem ? (
        <p className="text-high px-4 py-4 text-xs" role="alert">
          {problem}
        </p>
      ) : null}

      {briefing ? (
        <div className="px-4 py-4">
          <p className="max-w-prose text-sm leading-relaxed whitespace-pre-line">{briefing.body}</p>
          <p className="text-ink-dim border-rule mt-4 border-t pt-3 text-xs">
            <span className="figure">{briefing.model}</span>
            <span className="text-ink-faint mx-2">/</span>
            <span className="figure">{briefing.inputTokens}</span> in,{" "}
            <span className="figure">{briefing.outputTokens}</span> out,{" "}
            <span className="figure">{briefing.costUsdCents.toFixed(4)}</span> US cents
          </p>
        </div>
      ) : null}
    </section>
  );
}

async function ask(siteId: number, token: string): Promise<Written | Refused> {
  try {
    const response = await fetch("/api/briefing", {
      method: "POST",
      headers: { "content-type": "application/json", "x-demogym-token": token },
      body: JSON.stringify({ site_id: siteId }),
    });
    return await response.json();
  } catch (unanswered) {
    console.error("the briefing endpoint did not answer", siteId, unanswered);
    return { error: "unreachable", message: "The call did not get through." };
  }
}

function isFailure(error: string): error is Failure {
  return FAILURES.includes(error);
}
