"""The daily cap across every model call, enforced server side.

0003 calls this the only thing between a public control and unbounded writes. It
counts requests the endpoint accepts rather than rows written, because a call that
fails has still been made and still cost the account something.
"""

from datetime import date

import psycopg

# A full sweep is about forty-six calls, so this is a long way above a day's honest
# use and still a ceiling.
DAILY_CALL_LIMIT = 200

DAILY_LIMIT = "daily limit"

# One statement, so two requests arriving together cannot both read the count below
# the cap and both go on to spend it. The insert path covers the first call of the
# day; the where clause governs every one after it.
RESERVE = """
insert into model_calls (day, calls) values (%s, 1)
on conflict (day) do update set calls = model_calls.calls + 1
where model_calls.calls < %s
returning calls
"""


def reserve(connection: psycopg.Connection, day: date, limit: int = DAILY_CALL_LIMIT) -> int | None:
    """Counts one accepted request against the day, or returns None if the cap is spent."""
    row = connection.execute(RESERVE, (day, limit)).fetchone()
    return row[0] if row else None


def calls_on(connection: psycopg.Connection, day: date) -> int:
    """How many calls the day has counted so far."""
    row = connection.execute("select calls from model_calls where day = %s", (day,)).fetchone()
    return row[0] if row else 0
