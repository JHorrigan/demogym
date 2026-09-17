import Band from "@/components/Band";
import DraftQueue from "@/components/DraftQueue";
import type { PanelRow } from "@/components/MemberPanel";
import SiteFilter from "@/components/SiteFilter";
import { Cell, HeaderCell, Row, Table } from "@/components/Table";
import { Empty } from "@/components/States";
import { storedDrafts } from "@/lib/drafts";
import { queueRows, siteCounts, type QueueRow } from "@/lib/queue";

export const dynamic = "force-dynamic";

const MONEY = new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" });

export default async function Queue({
  params,
  searchParams,
}: {
  params: Promise<{ token: string }>;
  searchParams: Promise<{ site?: string }>;
}) {
  const { token } = await params;
  const { site } = await searchParams;

  const sites = await siteCounts();
  const selected = selectedSite(site, sites.map((option) => option.id));
  const rows = await queueRows(selected);
  const stored = await storedDrafts();

  const high = rows.filter((row) => row.band === "high");
  const rest = rows.filter((row) => row.band !== "high");
  const counts = {
    high: high.length,
    medium: rows.filter((row) => row.band === "medium").length,
    low: rows.filter((row) => row.band === "low").length,
  };
  const siteName = sites.find((option) => option.id === selected)?.name;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">At-risk queue</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          Every member in a band at the most recent scoring date, worst first, and inside a band the
          most expensive membership first. Each row carries the reason that put them there, generated
          from the arithmetic rather than written by anything.
        </p>
      </div>

      <SiteFilter
        token={token}
        sites={sites}
        selected={selected}
        total={sites.reduce((sum, option) => sum + option.atRisk, 0)}
      />

      {rows.length === 0 ? (
        <Empty heading={`Nobody at ${siteName ?? "any site"} is in a band`}>
          Every member scored at this site is attending close enough to their own established pattern
          that the arithmetic does not flag them. That is the queue working, not a gap in the data.
        </Empty>
      ) : (
        <>
          <p className="text-ink-dim text-sm">
            <span className="figure text-ink font-medium">{rows.length}</span> members
            {siteName ? ` at ${siteName}` : " across the estate"}:{" "}
            <span className="figure">{counts.high}</span> High,{" "}
            <span className="figure">{counts.medium}</span> Medium,{" "}
            <span className="figure">{counts.low}</span> Low.
          </p>

          <section className="space-y-4 pt-2">
            <div>
              <h2 className="text-lg font-semibold tracking-tight">High band</h2>
              <p className="text-ink-dim mt-1.5 max-w-2xl text-sm leading-relaxed">
                The only members a message is drafted for. Nothing is written until somebody asks, and
                nothing here is sent to anybody: a message that is approved is recorded as a decision
                and goes no further.
              </p>
            </div>

            {high.length === 0 ? (
              <Empty heading={`Nobody at ${siteName ?? "any site"} is in the High band`}>
                There are members in a lower band below, and those carry a reason without a drafted
                message. A message for a Low-band member is work nobody will do today.
              </Empty>
            ) : (
              <DraftQueue token={token} rows={high.map(toPanelRow)} stored={stored} />
            )}
          </section>

          {rest.length > 0 ? (
            <section className="space-y-4 pt-4">
              <div>
                <h2 className="text-lg font-semibold tracking-tight">Medium and Low</h2>
                <p className="text-ink-dim mt-1.5 max-w-2xl text-sm leading-relaxed">
                  A band and a reason, and no drafted message. These are the rows worth watching rather
                  than working.
                </p>
              </div>

              <Table caption="Members in the Medium and Low bands, worst first">
                <thead>
                  <tr>
                    <HeaderCell>Member</HeaderCell>
                    <HeaderCell>Band</HeaderCell>
                    <HeaderCell>Site</HeaderCell>
                    <HeaderCell numeric>Monthly</HeaderCell>
                    <HeaderCell numeric>Tenure</HeaderCell>
                    <HeaderCell>Why</HeaderCell>
                  </tr>
                </thead>
                <tbody>
                  {rest.map((row) => (
                    <Row key={row.memberId}>
                      <Cell>
                        <span className="figure">{row.accountNumber}</span>
                      </Cell>
                      <Cell>
                        <Band band={row.band} />
                      </Cell>
                      <Cell>{row.site}</Cell>
                      <Cell numeric>{MONEY.format(row.monthlyPrice)}</Cell>
                      <Cell numeric>{tenure(row.tenureDays, row.tenureMonths)}</Cell>
                      <Cell wrap>{row.reason}</Cell>
                    </Row>
                  ))}
                </tbody>
              </Table>
            </section>
          ) : null}

          <p className="text-ink-dim max-w-3xl text-xs leading-relaxed">
            The cost in the header is measured from the token counts the API returns on each call, in the
            currency it bills in, and it is never estimated. Approve, Edit and Reject arrive in 012.
          </p>
        </>
      )}
    </div>
  );
}

/** Formatting happens here, so nothing in the browser reaches for the data layer. */
function toPanelRow(row: QueueRow): PanelRow {
  return {
    memberId: row.memberId,
    accountNumber: row.accountNumber,
    site: row.site,
    price: MONEY.format(row.monthlyPrice),
    tenure: tenure(row.tenureDays, row.tenureMonths),
    reason: row.reason,
  };
}

/**
 * Tenure as a person would say it.
 *
 * Weeks below two months, because a member scored at four weeks and a day is "0
 * months" in whole months, which reads as missing data rather than as new.
 */
function tenure(days: number, months: number): string {
  if (months < 2) {
    const weeks = Math.floor(days / 7);
    return `${weeks} ${weeks === 1 ? "week" : "weeks"}`;
  }
  if (months < 24) {
    return `${months} months`;
  }
  return `${Math.floor(months / 12)} years`;
}

function selectedSite(site: string | undefined, known: number[]): number | null {
  const id = Number(site);
  return site && Number.isInteger(id) && known.includes(id) ? id : null;
}
