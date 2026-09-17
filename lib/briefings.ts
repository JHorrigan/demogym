import { sql } from "@/lib/database";

/** One site's briefing as it is stored. The body is prose, exactly as it was written. */
export type SiteBriefingRow = {
  siteId: number;
  generatedOn: string;
  body: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  costUsdCents: number;
};

const LATEST = `
select site_id, generated_on, body, model, input_tokens, output_tokens, cost_usd_cents
from briefings
where site_id = $1
order by generated_on desc
limit 1
`;

/** The most recent briefing for one site, or null if nobody has asked for one. */
export async function latestBriefing(siteId: number): Promise<SiteBriefingRow | null> {
  const [row] = await sql.query(LATEST, [siteId]);
  if (!row) {
    return null;
  }
  return {
    siteId: Number(row.site_id),
    generatedOn: String(row.generated_on),
    body: String(row.body),
    model: String(row.model),
    inputTokens: Number(row.input_tokens),
    outputTokens: Number(row.output_tokens),
    costUsdCents: Number(row.cost_usd_cents),
  };
}
