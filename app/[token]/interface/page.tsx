import Band from "@/components/Band";
import Button from "@/components/Button";
import DraftState from "@/components/DraftState";
import { Cell, HeaderCell, Row, Table } from "@/components/Table";
import { Empty, Failed, Loading } from "@/components/States";

/** Every primitive and every state, rendered, so the design language is inspectable. */
export default function Interface() {
  return (
    <div className="space-y-12">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Interface states</h1>
        <p className="text-ink-dim mt-2 max-w-2xl text-sm leading-relaxed">
          The pieces every screen is built from, with invented values. This page exists so the
          states can be looked at rather than described.
        </p>
      </div>

      <Section title="Bands">
        <div className="flex flex-wrap gap-3">
          <Band band="high" />
          <Band band="medium" />
          <Band band="low" />
          <Band band="unflagged" />
        </div>
      </Section>

      <Section title="Buttons">
        <div className="flex flex-wrap items-center gap-3">
          <Button tone="primary">Draft all</Button>
          <Button>Draft</Button>
          <Button disabled>Redraft</Button>
        </div>
      </Section>

      <Section title="Row states">
        <Table caption="The four states a row in the queue can be in">
          <thead>
            <tr>
              <HeaderCell>Member</HeaderCell>
              <HeaderCell>Band</HeaderCell>
              <HeaderCell numeric>Monthly</HeaderCell>
              <HeaderCell>State</HeaderCell>
            </tr>
          </thead>
          <tbody>
            {(
              [
                ["M00248", "high", "49.99", { status: "not drafted" }],
                ["M00291", "high", "34.99", { status: "drafting" }],
                ["M00022", "high", "34.99", { status: "drafted" }],
                ["M00104", "high", "24.99", { status: "failed", failure: "unreachable" }],
                ["M00187", "high", "24.99", { status: "failed", failure: "no credit" }],
                ["M00203", "medium", "49.99", { status: "failed", failure: "daily limit" }],
              ] as const
            ).map(([account, band, price, state]) => (
              <Row key={account}>
                <Cell>
                  <span className="figure">{account}</span>
                </Cell>
                <Cell>
                  <Band band={band} />
                </Cell>
                <Cell numeric>£{price}</Cell>
                <Cell wrap>
                  <DraftState {...state} />
                </Cell>
              </Row>
            ))}
          </tbody>
        </Table>
      </Section>

      <Section title="Reason strings">
        <Table caption="Reasons as the scorer writes them">
          <thead>
            <tr>
              <HeaderCell>Member</HeaderCell>
              <HeaderCell>Reason</HeaderCell>
              <HeaderCell numeric>Baseline</HeaderCell>
              <HeaderCell numeric>Gap</HeaderCell>
            </tr>
          </thead>
          <tbody>
            {(
              [
                [
                  "M00248",
                  "Last came 25 days ago, 3.6 times their usual gap of 7 days. Usually attends 0.5 times a week.",
                  "0.50",
                  "7.00",
                ],
                [
                  "M00022",
                  "Visits down from 1.2 to 0.3 a week, 27% of their rate over their first four weeks. Last came 7 days ago.",
                  "1.25",
                  "3.00",
                ],
                ["M00311", "No visits at all in the last 12 weeks.", "0.00", "—"],
              ] as const
            ).map(([account, reason, baseline, gap]) => (
              <Row key={account}>
                <Cell>
                  <span className="figure">{account}</span>
                </Cell>
                <Cell wrap>{reason}</Cell>
                <Cell numeric>{baseline}</Cell>
                <Cell numeric>{gap}</Cell>
              </Row>
            ))}
          </tbody>
        </Table>
      </Section>

      <Section title="Empty">
        <Empty heading="No messages drafted" action={<Button tone="primary">Draft all</Button>}>
          The queue opens with nothing in it. Drafting costs money per press, so nothing is written
          until somebody asks for it.
        </Empty>
      </Section>

      <Section title="Loading">
        <Loading rows={3} label="Loading the queue" />
      </Section>

      <Section title="Failed">
        <div className="space-y-4">
          <Failed heading="Could not reach the model" action={<Button>Try again</Button>}>
            The call did not get through. Nothing was written and nothing was billed.
          </Failed>
          <Failed heading="No credit remaining">
            The account has no credit left, so trying again will not help. Top it up and the queue
            picks up where it stopped.
          </Failed>
        </div>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="label border-rule border-b pb-2">{title}</h2>
      {children}
    </section>
  );
}
