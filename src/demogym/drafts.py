"""Reading what a draft needs from the database, and writing the row it produced.

The scoring date is taken from the database rather than from the request, so a caller
cannot ask for a draft against a week that is no longer current.
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


@dataclass(frozen=True)
class Candidate:
    """A member as the drafting endpoint sees them, at the current scoring date."""

    facts: Facts
    scored_on: date
    attempts: int


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
    return Candidate(
        facts=facts, scored_on=scored_on, attempts=_attempts(connection, member_id, scored_on)
    )


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


def _attempts(connection: psycopg.Connection, member_id: int, scored_on: date) -> int:
    row = connection.execute(
        "select count(*) from drafts where member_id = %s and scored_on = %s",
        (member_id, scored_on),
    ).fetchone()
    return row[0]
