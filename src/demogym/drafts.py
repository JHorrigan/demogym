"""The `drafts` table: what a draft needs, the row it produced, and what was decided.

The scoring date is taken from the database rather than from the request, so a caller
cannot ask for a draft against a week that is no longer current. The attempt a
decision lands on is taken the same way.
"""

from dataclasses import dataclass
from datetime import date, datetime

import psycopg

from demogym.drafting import Controls
from demogym.facts import Facts, build
from demogym.model import Generated

LOCAL = "Europe/London"

CANDIDATE = """
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select m.account_number,
       s.name,
       r.band,
       r.reason,
       m.plan,
       m.monthly_price,
       r.baseline,
       m.joined_on,
       latest.scored_on
from risk_scores r
join members m on m.id = r.member_id
join sites s on s.id = m.site_id,
     latest
where r.scored_on = latest.scored_on
  and r.member_id = %s
"""

VISITS = f"""
select (entered_at at time zone '{LOCAL}')
from entries
where member_id = %s
order by 1
"""  # noqa: S608

STORE = """
insert into drafts (member_id, scored_on, attempt, tone, length, offer,
                    subject, body, rationale,
                    model, input_tokens, output_tokens, cost_usd_cents)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


LATEST_DRAFT = """
with latest as (
    select max(scored_on) as scored_on from risk_scores
)
select d.scored_on, d.attempt, d.body, d.decision
from drafts d, latest
where d.scored_on = latest.scored_on
  and d.member_id = %s
order by d.attempt desc
"""

DECIDE = """
update drafts
set decision = %s, edited_body = %s, decided_at = now()
where member_id = %s and scored_on = %s and attempt = %s
returning decided_at
"""


@dataclass(frozen=True)
class Candidate:
    """A member as the drafting endpoint sees them, at the current scoring date."""

    facts: Facts
    scored_on: date
    attempts: int
    decided: bool


def candidate(connection: psycopg.Connection, member_id: int) -> Candidate | None:
    """The facts for one member, or None if they were not scored at the current date."""
    row = connection.execute(CANDIDATE, (member_id,)).fetchone()
    if row is None:
        return None

    account_number, site, band, reason, plan, monthly_price, baseline, joined_on, scored_on = row
    visits = _visits(connection, member_id)
    facts = build(
        account_number=account_number,
        site=site,
        band=band,
        reason=reason,
        plan=plan,
        monthly_price=float(monthly_price),
        baseline=float(baseline),
        joined_on=joined_on,
        scored_on=scored_on,
        visits=visits,
    )
    latest = latest_draft(connection, member_id)
    return Candidate(
        facts=facts,
        scored_on=scored_on,
        # Attempts run 1 then 2, so the newest attempt number is how many there are.
        attempts=latest.attempt if latest else 0,
        decided=latest.decided if latest else False,
    )


@dataclass(frozen=True)
class Latest:
    """The most recent draft for one member, and whether anything was decided.

    `decided` covers every attempt, not just this one: a decision is about the member
    and there is only ever one.
    """

    scored_on: date
    attempt: int
    body: str
    decided: bool


def latest_draft(connection: psycopg.Connection, member_id: int) -> Latest | None:
    """The member's newest draft at the current scoring date, or None if they have none."""
    rows = connection.execute(LATEST_DRAFT, (member_id,)).fetchall()
    if not rows:
        return None

    scored_on, attempt, body, _ = rows[0]
    return Latest(
        scored_on=scored_on,
        attempt=attempt,
        body=body,
        decided=any(row[3] is not None for row in rows),
    )


def record(
    connection: psycopg.Connection,
    member_id: int,
    latest: Latest,
    action: str,
    edited_body: str | None,
) -> datetime:
    """Writes the decision and returns the moment the database stamped it."""
    row = connection.execute(
        DECIDE, (action, edited_body, member_id, latest.scored_on, latest.attempt)
    ).fetchone()
    return row[0]


def store(
    connection: psycopg.Connection,
    member_id: int,
    scored_on: date,
    attempt: int,
    controls: Controls,
    generated: Generated,
) -> None:
    """Writes the row from the response, before the endpoint returns."""
    connection.execute(
        STORE,
        (
            member_id,
            scored_on,
            attempt,
            controls.tone,
            controls.length,
            controls.offer,
            generated.message.subject,
            generated.message.body,
            generated.message.rationale,
            generated.model,
            generated.input_tokens,
            generated.output_tokens,
            generated.cost_usd_cents,
        ),
    )


def _visits(connection: psycopg.Connection, member_id: int) -> list[datetime]:
    return [row[0] for row in connection.execute(VISITS, (member_id,)).fetchall()]
