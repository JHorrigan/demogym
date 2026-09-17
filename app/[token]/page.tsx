import Link from "next/link";

import Sparkline from "@/components/Sparkline";
import { Cell, HeaderCell, Row, Table } from "@/components/Table";
import { Empty } from "@/components/States";
import { siteRows } from "@/lib/estate";

/** The seed and the scoring run are the only things that change this, so never cache it. */
export const dynamic = "force-dynamic";

const RATE = new Intl.NumberFormat("en-GB", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const MONEY = new Intl.NumberFormat("en-GB", {
  style: "currency",
  currency: "GBP",
  maximumFractionDigits: 0,
});

export default async function Estate({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const sites = await siteRows();

  if (sites.every((site) => site.scored === 0)) {
    return (
      <Screen>
        <Empty heading="Nothing has been scored yet">
          The estate is seeded but `demogym score` has not been run against it, so there are no
          bands to rank the sites by.
        </Empty>
      </Screen>
    );
  }

  // One scale across every row, so the shapes in the trend column are comparable.
  const readings = sites.flatMap((site) => site.trend);
  const floor = Math.min(...readings);
  const ceiling = Math.max(...readings);

  return (
    <Screen>
      <Table caption="Every site, ranked by the share of scored members at risk">
        <thead>
          <tr>
            <HeaderCell>Site</HeaderCell>
            <HeaderCell numeric>At risk</HeaderCell>
            <HeaderCell numeric>On last week</HeaderCell>
            <HeaderCell>Twelve weeks</HeaderCell>
            <HeaderCell numeric>High</HeaderCell>
            <HeaderCell numeric>Medium</HeaderCell>
            <HeaderCell numeric>Low</HeaderCell>
            <HeaderCell numeric>Revenue at risk</HeaderCell>
            <HeaderCell numeric>Equipment down</HeaderCell>
            <HeaderCell numeric>Active</HeaderCell>
            <HeaderCell numeric>Scored</HeaderCell>
          </tr>
        </thead>
        <tbody>
          {sites.map((site) => (
            <Row key={site.id}>
              <Cell>
                <Link href={`/${token}/queue?site=${site.id}`} className="hover:text-accent underline">
                  {site.name}
                </Link>
                <span className="text-ink-dim mt-0.5 block text-xs">{site.region}</span>
              </Cell>
              <Cell numeric>
                <span className="font-medium">{RATE.format(site.atRiskRate)}</span>
                <span className="text-ink-dim mt-0.5 block text-xs">
                  {site.atRisk} of {site.scored}
                </span>
              </Cell>
              <Cell numeric>
                <Change points={site.changeOnLastWeek} />
              </Cell>
              <Cell>
                <Sparkline
                  values={site.trend}
                  floor={floor}
                  ceiling={ceiling}
                  label={trendLabel(site.name, site.trend)}
                />
              </Cell>
              <Cell numeric>{site.high}</Cell>
              <Cell numeric>{site.medium}</Cell>
              <Cell numeric>{site.low}</Cell>
              <Cell numeric>{MONEY.format(site.revenueAtRisk)}</Cell>
              <Cell numeric>{site.outOfService === 0 ? "—" : site.outOfService}</Cell>
              <Cell numeric>{site.active}</Cell>
              <Cell numeric>{site.scored}</Cell>
            </Row>
          ))}
        </tbody>
      </Table>

      <p className="text-ink-dim max-w-3xl text-xs leading-relaxed">
        The at-risk rate divides by members scored rather than members active, because nobody inside
        their first four weeks is scored at all and counting them as settled would read as calmer
        than the site is. Both counts are in the table so the division can be checked. The trend and
        the change are shown together: the change says what moved this week, the trend says whether
        it has been moving for a while, and only the pair separates a site in decline from one that
        had a bad week. Every sparkline shares one scale, running from {RATE.format(floor)} to{" "}
        {RATE.format(ceiling)}, which is the lowest and highest reading anywhere in the estate over
        the twelve weeks. The shapes are therefore comparable between rows; the level itself is the
        number in the at-risk column, not the height of the line.
      </p>
    </Screen>
  );
}

/** Up is worse here, so a rise is the warning colour and a fall is the good one. */
function Change({ points }: { points: number | null }) {
  if (points === null) {
    return <span className="text-ink-faint">—</span>;
  }

  const percentagePoints = points * 100;
  const rounded = Math.abs(percentagePoints) < 0.05 ? 0 : percentagePoints;
  const tone =
    rounded > 0 ? "text-high" : rounded < 0 ? "text-accent" : "text-ink-dim";
  const sign = rounded > 0 ? "+" : "";

  return (
    <span className={tone}>
      {sign}
      {rounded.toFixed(1)} pp
    </span>
  );
}

function trendLabel(name: string, trend: number[]): string {
  const readings = trend.map((rate) => RATE.format(rate)).join(", ");
  return `${name}, at-risk rate over ${trend.length} weekly dates, oldest first: ${readings}`;
}

function Screen({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Estate</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          One row per site, worst at-risk rate first. Ranking on the rate rather than the count,
          because a site with twice the members will always have more of them at risk.
        </p>
      </div>
      {children}
    </div>
  );
}
