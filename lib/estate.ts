import { sql } from "@/lib/database";

export type SiteRow = {
  id: number;
  name: string;
  region: string;
  active: number;
  scored: number;
  high: number;
  medium: number;
  low: number;
  atRisk: number;
  atRiskRate: number;
  revenueAtRisk: number;
  outOfService: number;
  trend: number[];
  changeOnLastWeek: number | null;
};

/**
 * One query for the whole screen.
 *
 * `scored` is the denominator of the at-risk rate rather than `active`, because a
 * member inside their first four weeks is not scored at all and counting them as
 * not at risk would report a site as calmer than it is. Both are on screen so the
 * division can be checked by hand.
 */
const ESTATE = `
with latest as (
    select max(scored_on) as scored_on from risk_scores
),
per_date as (
    select m.site_id,
           r.scored_on,
           count(*) as scored,
           count(*) filter (where r.band <> 'unflagged') as at_risk
    from risk_scores r
    join members m on m.id = r.member_id
    group by m.site_id, r.scored_on
),
trend as (
    select site_id,
           array_agg(at_risk::numeric / scored order by scored_on) as rates
    from per_date
    group by site_id
),
current as (
    select p.site_id, p.scored, p.at_risk
    from per_date p, latest
    where p.scored_on = latest.scored_on
),
bands as (
    select m.site_id,
           count(*) filter (where r.band = 'high') as high,
           count(*) filter (where r.band = 'medium') as medium,
           count(*) filter (where r.band = 'low') as low,
           coalesce(sum(m.monthly_price) filter (where r.band <> 'unflagged'), 0) as revenue
    from risk_scores r
    join members m on m.id = r.member_id,
         latest
    where r.scored_on = latest.scored_on
    group by m.site_id
),
active as (
    select m.site_id, count(*) as active
    from members m, latest
    where m.joined_on <= latest.scored_on
      and (m.left_on is null or m.left_on > latest.scored_on)
    group by m.site_id
),
down as (
    select site_id, count(*) as out_of_service
    from equipment
    where status = 'out of service'
    group by site_id
)
select s.id,
       s.name,
       s.region,
       coalesce(a.active, 0) as active,
       coalesce(c.scored, 0) as scored,
       coalesce(b.high, 0) as high,
       coalesce(b.medium, 0) as medium,
       coalesce(b.low, 0) as low,
       coalesce(c.at_risk, 0) as at_risk,
       coalesce(b.revenue, 0) as revenue,
       coalesce(d.out_of_service, 0) as out_of_service,
       coalesce(t.rates, array[]::numeric[]) as rates
from sites s
left join active a on a.site_id = s.id
left join current c on c.site_id = s.id
left join bands b on b.site_id = s.id
left join down d on d.site_id = s.id
left join trend t on t.site_id = s.id
order by case when coalesce(c.scored, 0) = 0 then 0
              else c.at_risk::numeric / c.scored end desc,
         s.name
`;

/**
 * Every site, worst at-risk rate first.
 *
 * Ordering on the rate rather than the count, because a site with twice the
 * members will always have more members at risk, and ranking on the count reports
 * which site is biggest rather than which is in trouble.
 */
export async function siteRows(): Promise<SiteRow[]> {
  const rows = await sql.query(ESTATE);
  return rows.map(toSiteRow);
}

function toSiteRow(row: Record<string, unknown>): SiteRow {
  const scored = Number(row.scored);
  const atRisk = Number(row.at_risk);
  const trend = (row.rates as string[]).map(Number);

  return {
    id: Number(row.id),
    name: String(row.name),
    region: String(row.region),
    active: Number(row.active),
    scored,
    high: Number(row.high),
    medium: Number(row.medium),
    low: Number(row.low),
    atRisk,
    atRiskRate: scored === 0 ? 0 : atRisk / scored,
    revenueAtRisk: Number(row.revenue),
    outOfService: Number(row.out_of_service),
    trend,
    changeOnLastWeek: changeOnLastWeek(trend),
  };
}

/**
 * The move in percentage points since the previous scoring date.
 *
 * Null with fewer than two dates, because there is nothing to compare against and
 * a zero would read as steady rather than as unknown.
 */
function changeOnLastWeek(trend: number[]): number | null {
  if (trend.length < 2) {
    return null;
  }
  return trend[trend.length - 1] - trend[trend.length - 2];
}
