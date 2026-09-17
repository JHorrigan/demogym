"""Writes a generated estate to the database with COPY."""

from dataclasses import dataclass
from datetime import date
from random import Random

import psycopg

from demogym.attendance import entries
from demogym.members import Member, generate
from demogym.sites import SITES

SEED = 20260917

# Every table, because everything else is computed from the estate. A score, a draft
# or a briefing held over a replacement would describe members that no longer exist.
CLEARED_ON_RESEED = (
    "entries",
    "drafts",
    "briefings",
    "risk_scores",
    "equipment",
    "members",
    "sites",
)


@dataclass(frozen=True)
class Written:
    """How many rows of each kind the seed wrote."""

    sites: int
    members: int
    entries: int


def existing_counts(connection: psycopg.Connection) -> dict[str, int]:
    """Counts what is already there, so a replacement says what it replaced."""
    return {
        table: connection.execute(f"select count(*) from {table}").fetchone()[0]  # noqa: S608
        for table in ("sites", "members", "entries")
    }


def replace(connection: psycopg.Connection, as_of: date, seed: int = SEED) -> Written:
    """Clears the estate and writes a freshly generated one in its place."""
    members = generate(as_of, Random(seed))

    with connection.transaction():
        connection.execute(f"truncate {', '.join(CLEARED_ON_RESEED)}")
        site_ids = _write_sites(connection)
        member_ids = _write_members(connection, members, site_ids)
        written = _write_entries(connection, members, member_ids, site_ids, as_of, Random(seed))

    return Written(sites=len(site_ids), members=len(member_ids), entries=written)


def _write_sites(connection: psycopg.Connection) -> dict[str, int]:
    with connection.cursor().copy("copy sites (name, region, opened_on) from stdin") as copy:
        for site in SITES:
            copy.write_row((site.name, site.region, site.opened_on))

    rows = connection.execute("select name, id from sites").fetchall()
    return dict(rows)


def _write_members(
    connection: psycopg.Connection, members: list[Member], site_ids: dict[str, int]
) -> dict[str, int]:
    with connection.cursor().copy(
        "copy members (site_id, account_number, joined_on, left_on, plan, monthly_price) from stdin"
    ) as copy:
        for member in members:
            copy.write_row(
                (
                    site_ids[member.site.name],
                    member.account_number,
                    member.joined_on,
                    member.left_on,
                    member.plan,
                    member.monthly_price,
                )
            )

    rows = connection.execute("select account_number, id from members").fetchall()
    return dict(rows)


def _write_entries(
    connection: psycopg.Connection,
    members: list[Member],
    member_ids: dict[str, int],
    site_ids: dict[str, int],
    as_of: date,
    random: Random,
) -> int:
    written = 0
    with connection.cursor().copy(
        "copy entries (member_id, site_id, entered_at) from stdin"
    ) as copy:
        for member in members:
            member_id = member_ids[member.account_number]
            site_id = site_ids[member.site.name]
            for arrival in entries(member, as_of, random):
                copy.write_row((member_id, site_id, arrival))
                written += 1
    return written
