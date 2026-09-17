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
};

export type Spend = { calls: number; cents: number };

const STORED = `
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select d.member_id, d.attempt, d.tone, d.length, d.offer,
       d.subject, d.body, d.rationale, d.cost_usd_cents
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
  }));
}

/** What has been spent so far, measured from the token counts the API returned. */
export async function spend(): Promise<Spend> {
  const [row] = await sql.query(SPEND);
  return { calls: Number(row.calls), cents: Number(row.cents) };
}
