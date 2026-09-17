"""Scores every eligible member at twelve weekly dates and stores the result."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

import psycopg

from demogym.scoring import score

SCORING_DATES = 12

# Entries are stored as instants. A visit belongs to the local day it happened on,
# so the estate's own clock decides the date rather than UTC.
LOCAL = "Europe/London"


@dataclass(frozen=True)
class Scored:
    """How many rows were written, and how the most recent date came out."""

    rows: int
    dates: int
    latest: dict[str, int]


def scoring_dates(as_of: date) -> list[date]:
    """Twelve weekly dates, oldest first, ending on the scoring date."""
    return [as_of - timedelta(weeks=week) for week in reversed(range(SCORING_DATES))]


def run(connection: psycopg.Connection, as_of: date) -> Scored:
    """Replaces every score with a fresh sweep over the twelve dates."""
    members = _members(connection)
    visits = _visits(connection)
    dates = scoring_dates(as_of)

    with connection.transaction():
        connection.execute("truncate drafts, risk_scores")
        rows = _write(connection, members, visits, dates)

    return Scored(rows=rows, dates=len(dates), latest=_bands_on(connection, dates[-1]))


def _members(connection: psycopg.Connection) -> list[tuple[int, date, date | None]]:
    return connection.execute("select id, joined_on, left_on from members order by id").fetchall()


def _visits(connection: psycopg.Connection) -> dict[int, list[date]]:
    """Every member's visit dates, in the estate's own timezone."""
    rows = connection.execute(
        f"select member_id, (entered_at at time zone '{LOCAL}')::date from entries"  # noqa: S608
    ).fetchall()

    visits = defaultdict(list)
    for member_id, day in rows:
        visits[member_id].append(day)
    return visits


def _write(
    connection: psycopg.Connection,
    members: list[tuple[int, date, date | None]],
    visits: dict[int, list[date]],
    dates: list[date],
) -> int:
    written = 0
    with connection.cursor().copy(
        "copy risk_scores (member_id, scored_on, band, reason, baseline, recent_rate, "
        "decay, typical_gap, gap_multiple) from stdin"
    ) as copy:
        for scored_on in dates:
            for member_id, joined_on, left_on in members:
                if not is_active(joined_on, left_on, scored_on):
                    continue
                scored = score(visits.get(member_id, []), joined_on, scored_on)
                if scored is None:
                    continue
                copy.write_row(
                    (
                        member_id,
                        scored_on,
                        scored.band,
                        scored.reason,
                        round(scored.baseline, 2),
                        round(scored.recent_rate, 2),
                        _rounded(scored.decay),
                        _rounded(scored.typical_gap),
                        _rounded(scored.gap_multiple),
                    )
                )
                written += 1
    return written


def is_active(joined_on: date, left_on: date | None, scored_on: date) -> bool:
    """Joined and not left, which is who the specification scores."""
    return joined_on <= scored_on and (left_on is None or left_on > scored_on)


def _rounded(value: float | None) -> float | None:
    """The column keeps two decimal places, so the stored value is the rounded one."""
    return None if value is None else round(value, 2)


def _bands_on(connection: psycopg.Connection, scored_on: date) -> dict[str, int]:
    rows = connection.execute(
        "select band, count(*) from risk_scores where scored_on = %s group by band",
        (scored_on,),
    ).fetchall()
    return dict(rows)
