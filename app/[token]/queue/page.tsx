import Band from "@/components/Band";
import SiteFilter from "@/components/SiteFilter";
import { Cell, HeaderCell, Row, Table } from "@/components/Table";
import { Empty } from "@/components/States";
import { queueRows, siteCounts } from "@/lib/queue";

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

  const counts = {
    high: rows.filter((row) => row.band === "high").length,
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

          <Table caption="Members in a band, worst first">
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
              {rows.map((row) => (
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

          <p className="text-ink-dim max-w-3xl text-xs leading-relaxed">
            High rows will carry the drafting controls in 011 and the Approve, Edit and Reject actions
            in 012. Nothing has been drafted and nothing has been sent. Medium and Low rows carry a
            band and a reason and will not carry a drafted message: a message for a Low-band member is
            work nobody will do today.
          </p>
        </>
      )}
    </div>
  );
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
