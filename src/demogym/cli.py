"""The command-line entry point for the local tooling."""

import argparse
from datetime import date
from pathlib import Path

from demogym.database import connect
from demogym.migrate import run
from demogym.score import run as run_scoring
from demogym.seed import SEED, existing_counts, replace

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


def main() -> None:
    """Parses the command and runs it."""
    parser = argparse.ArgumentParser(prog="demogym", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="apply pending migrations")

    seed = commands.add_parser("seed", help="replace the estate with a generated one")
    seed.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    seed.add_argument("--seed", type=int, default=SEED)

    scoring = commands.add_parser("score", help="score the estate at twelve weekly dates")
    scoring.add_argument("--as-of", type=date.fromisoformat, default=date.today())

    arguments = parser.parse_args()
    if arguments.command == "migrate":
        migrate()
    elif arguments.command == "seed":
        seed_estate(arguments.as_of, arguments.seed)
    else:
        score_estate(arguments.as_of)


def migrate() -> None:
    """Applies pending migrations and reports what happened."""
    with connect() as connection:
        applied = run(connection, MIGRATIONS)

    if not applied:
        print("No pending migrations.")
        return

    for migration in applied:
        print(f"Applied {migration.number:03d} {migration.name}")


def seed_estate(as_of: date, seed: int) -> None:
    """Replaces the estate and reports what it removed and what it wrote."""
    with connect() as connection:
        existing = existing_counts(connection)
        if any(existing.values()):
            print(
                f"Replacing {existing['sites']} sites, {existing['members']} members, "
                f"{existing['equipment']} equipment units and {existing['entries']} entries."
            )
        written = replace(connection, as_of, seed)

    print(f"Wrote {written.sites} sites.")
    print(f"Wrote {written.members} members.")
    print(f"Wrote {written.equipment} equipment units.")
    print(f"Wrote {written.entries} entries as of {as_of.isoformat()}, seed {seed}.")


def score_estate(as_of: date) -> None:
    """Scores the estate and reports how the most recent date came out."""
    with connect() as connection:
        scored = run_scoring(connection, as_of)

    print(f"Wrote {scored.rows} scores across {scored.dates} weekly dates to {as_of.isoformat()}.")
    for band in ("high", "medium", "low", "unflagged"):
        print(f"  {band:10} {scored.latest.get(band, 0)}")
