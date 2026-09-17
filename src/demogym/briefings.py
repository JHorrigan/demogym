"""The `briefings` table: one briefing per site per day, and what it cost.

Asking again on the same day replaces the prose and adds to the spend. The body is
the briefing that exists; the token counts are everything spent on this site today,
so the running total counts calls that were billed rather than only the one whose
words survived. The arithmetic still divides out by hand, because price times tokens
is linear and a sum of calls is a sum of costs.
"""

from dataclasses import dataclass
from datetime import date

import psycopg

from demogym.briefing_prompt import Briefing
from demogym.model import Generated

STORE = """
insert into briefings (site_id, generated_on, body, model,
                       input_tokens, output_tokens, cost_usd_cents)
values (%s, %s, %s, %s, %s, %s, %s)
on conflict (site_id, generated_on) do update
set body = excluded.body,
    model = excluded.model,
    input_tokens = briefings.input_tokens + excluded.input_tokens,
    output_tokens = briefings.output_tokens + excluded.output_tokens,
    cost_usd_cents = briefings.cost_usd_cents + excluded.cost_usd_cents
returning input_tokens, output_tokens, cost_usd_cents
"""


@dataclass(frozen=True)
class Stored:
    """What the row holds after the write, which may be more than this one call."""

    input_tokens: int
    output_tokens: int
    cost_usd_cents: float


def store(
    connection: psycopg.Connection,
    site_id: int,
    generated_on: date,
    body: str,
    generated: Generated[Briefing],
) -> Stored:
    """Writes the briefing from the response, before the endpoint returns."""
    row = connection.execute(
        STORE,
        (
            site_id,
            generated_on,
            body,
            generated.model,
            generated.input_tokens,
            generated.output_tokens,
            generated.cost_usd_cents,
        ),
    ).fetchone()
    return Stored(input_tokens=row[0], output_tokens=row[1], cost_usd_cents=float(row[2]))
