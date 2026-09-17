"""The command-line entry point for the local tooling."""

import argparse
from pathlib import Path

from demogym.database import connect
from demogym.migrate import run

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


def main() -> None:
    """Parses the command and runs it."""
    parser = argparse.ArgumentParser(prog="demogym", description=__doc__)
    parser.add_argument("command", choices=["migrate"])
    parser.parse_args()
    migrate()


def migrate() -> None:
    """Applies pending migrations and reports what happened."""
    with connect() as connection:
        applied = run(connection, MIGRATIONS)

    if not applied:
        print("No pending migrations.")
        return

    for migration in applied:
        print(f"Applied {migration.number:03d} {migration.name}")
