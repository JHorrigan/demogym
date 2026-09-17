"""Applies pending migrations to the database and records what it applied."""

from pathlib import Path

import psycopg

from demogym.migrations import Migration, load, pending

LEDGER = """
create table if not exists schema_migrations (
    number integer primary key,
    name text not null,
    applied_at timestamptz not null default now()
)
"""


def run(connection: psycopg.Connection, directory: Path) -> list[Migration]:
    """Applies every pending migration in order and returns those it applied.

    Each migration and its ledger row are written in one transaction, so a
    failure leaves nothing half applied.
    """
    with connection.transaction():
        connection.execute(LEDGER)

    outstanding = pending(load(directory), _applied(connection))
    for migration in outstanding:
        with connection.transaction():
            connection.execute(migration.sql)
            connection.execute(
                "insert into schema_migrations (number, name) values (%s, %s)",
                (migration.number, migration.name),
            )
    return outstanding


def _applied(connection: psycopg.Connection) -> set[int]:
    rows = connection.execute("select number from schema_migrations").fetchall()
    return {row[0] for row in rows}
