import { sql } from "@/lib/database";

import type { BandName } from "@/components/Band";

export type QueueRow = {
  memberId: number;
  accountNumber: string;
  site: string;
  band: BandName;
  joinedOn: string;
  tenureDays: number;
  tenureMonths: number;
  monthlyPrice: number;
  reason: string;
};

export type SiteCount = { id: number; name: string; atRisk: number };

/**
 * Worst band first, and inside a band the most expensive membership first.
 *
 * The specification bands members rather than ranking them on a raw score, because
 * an operations team works a queue and not a leaderboard, and orders within a band
 * by monthly price. Both are fixed here rather than offered as a sort, since the
 * order is the argument.
 */
const BANDED = `
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select r.member_id,
       m.account_number,
       s.name as site,
       r.band,
       m.joined_on,
       m.monthly_price,
       r.reason,
       latest.scored_on
from risk_scores r
join members m on m.id = r.member_id
join sites s on s.id = m.site_id,
     latest
where r.scored_on = latest.scored_on
  and r.band <> 'unflagged'
  and ($1::int is null or m.site_id = $1::int)
order by case r.band when 'high' then 0 when 'medium' then 1 else 2 end,
         m.monthly_price desc,
         m.account_number
`;

const SITE_COUNTS = `
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select s.id,
       s.name,
       count(r.member_id) filter (where r.band <> 'unflagged') as at_risk
from sites s
left join members m on m.site_id = s.id
left join risk_scores r on r.member_id = m.id
     and r.scored_on = (select scored_on from latest)
group by s.id, s.name
order by s.name
`;

/** Every banded member, optionally narrowed to one site. */
export async function queueRows(siteId: number | null): Promise<QueueRow[]> {
  const rows = await sql.query(BANDED, [siteId]);
  return rows.map(toQueueRow);
}

/** Each site with how many members it has in a band, so a filter says what it will show. */
export async function siteCounts(): Promise<SiteCount[]> {
  const rows = await sql.query(SITE_COUNTS);
  return rows.map((row) => ({
    id: Number(row.id),
    name: String(row.name),
    atRisk: Number(row.at_risk),
  }));
}

function toQueueRow(row: Record<string, unknown>): QueueRow {
  const joinedOn = String(row.joined_on);
  return {
    memberId: Number(row.member_id),
    accountNumber: String(row.account_number),
    site: String(row.site),
    band: row.band as BandName,
    joinedOn,
    tenureDays: daysBetween(joinedOn, String(row.scored_on)),
    tenureMonths: monthsBetween(joinedOn, String(row.scored_on)),
    monthlyPrice: Number(row.monthly_price),
    reason: String(row.reason),
  };
}

/**
 * Tenure is measured to the scoring date rather than to today, so it agrees with
 * the reading beside it instead of drifting a day at a time after a run.
 */
function daysBetween(joinedOn: string, scoredOn: string): number {
  const day = 24 * 60 * 60 * 1000;
  return Math.round((new Date(scoredOn).getTime() - new Date(joinedOn).getTime()) / day);
}

function monthsBetween(joinedOn: string, scoredOn: string): number {
  const joined = new Date(joinedOn);
  const scored = new Date(scoredOn);
  const months =
    (scored.getUTCFullYear() - joined.getUTCFullYear()) * 12 +
    (scored.getUTCMonth() - joined.getUTCMonth());
  return scored.getUTCDate() < joined.getUTCDate() ? months - 1 : months;
}
