import { sql } from "@/lib/database";

/**
 * A drafted message as it is stored, which is also the shape the endpoint returns.
 *
 * Nothing typechecks across the Python and TypeScript boundary, so this type and
 * `draft_endpoint.respond` are agreed by hand. 0005 records that as the sharpest
 * edge in the project.
 */
export type Draft = {
  memberId: number;
  attempt: number;
  tone: string;
  length: string;
  offer: string;
  subject: string;
  body: string;
  rationale: string;
  costUsdCents: number;
  decision: DecisionName | null;
  editedBody: string | null;
  decidedAt: string | null;
};

/** The three the `drafts.decision` column allows. Agreed by hand with `decisions.py`. */
export type DecisionName = "approved" | "edited" | "rejected";

export type Spend = { calls: number; cents: number };

/**
 * How many approvals needed an edit, out of how many approvals.
 *
 * The only honest quality measure this project can produce. 0005 rules out accuracy
 * against the generator's own labels, because that would measure whether the scorer
 * recovered a pattern the generator injected.
 */
export type Approvals = { approved: number; edited: number };

const STORED = `
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select d.member_id, d.attempt, d.tone, d.length, d.offer,
       d.subject, d.body, d.rationale, d.cost_usd_cents,
       d.decision, d.edited_body, d.decided_at
from drafts d, latest
where d.scored_on = latest.scored_on
order by d.member_id, d.attempt
`;

/**
 * Every call the account has been billed for, drafts and briefings together.
 *
 * Costs are stored in US cents because that is the currency the API bills in, and
 * summing them is not arithmetic on a reading: it is adding up receipts.
 */
const APPROVALS = `
select count(*) filter (where decision in ('approved', 'edited')) as approved,
       count(*) filter (where decision = 'edited') as edited
from drafts
`;

const SPEND = `
select count(*) as calls, coalesce(sum(cost_usd_cents), 0) as cents
from (
    select cost_usd_cents from drafts
    union all
    select cost_usd_cents from briefings
) as billed
`;

/** Drafts already written at the current scoring date, oldest attempt first. */
export async function storedDrafts(): Promise<Draft[]> {
  const rows = await sql.query(STORED);
  return rows.map((row) => ({
    memberId: Number(row.member_id),
    attempt: Number(row.attempt),
    tone: String(row.tone),
    length: String(row.length),
    offer: String(row.offer),
    subject: String(row.subject),
    body: String(row.body),
    rationale: String(row.rationale),
    costUsdCents: Number(row.cost_usd_cents),
    decision: decisionOf(row.decision),
    editedBody: row.edited_body === null ? null : String(row.edited_body),
    decidedAt: row.decided_at === null ? null : new Date(String(row.decided_at)).toISOString(),
  }));
}

/**
 * The stored decision, narrowed at the boundary rather than asserted through it.
 *
 * The column checks the same three names, and nothing checks that this list and that
 * constraint agree, so an unrecognised value reads as no decision rather than as a
 * decision nobody can render.
 */
function decisionOf(value: unknown): DecisionName | null {
  const name = value === null || value === undefined ? "" : String(value);
  return isDecision(name) ? name : null;
}

function isDecision(value: string): value is DecisionName {
  const names: readonly string[] = ["approved", "edited", "rejected"];
  return names.includes(value);
}

/** Approvals and how many of them were edited, counted in the database. */
export async function approvals(): Promise<Approvals> {
  const [row] = await sql.query(APPROVALS);
  return { approved: Number(row.approved), edited: Number(row.edited) };
}

/** What has been spent so far, measured from the token counts the API returned. */
export async function spend(): Promise<Spend> {
  const [row] = await sql.query(SPEND);
  return { calls: Number(row.calls), cents: Number(row.cents) };
}
