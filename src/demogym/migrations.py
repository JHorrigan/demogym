"""Discovers migration files and puts them in the order they must be applied."""

import re
from dataclasses import dataclass
from pathlib import Path

FILENAME = re.compile(r"^(\d+)_([a-z0-9_]+)\.sql$")


@dataclass(frozen=True)
class Migration:
    """One numbered migration file and the SQL it holds."""

    number: int
    name: str
    sql: str


def load(directory: Path) -> list[Migration]:
    """Reads every migration in a directory, ordered by number.

    Numeric order rather than filename order, so 10 follows 9 rather than 1.
    """
    migrations = [_read(path) for path in directory.iterdir() if FILENAME.match(path.name)]
    _reject_repeated_numbers(migrations)
    return sorted(migrations, key=lambda migration: migration.number)


def pending(migrations: list[Migration], applied: set[int]) -> list[Migration]:
    """Returns the migrations not yet applied, in order."""
    return [migration for migration in migrations if migration.number not in applied]


def _read(path: Path) -> Migration:
    match = FILENAME.match(path.name)
    assert match is not None
    return Migration(number=int(match.group(1)), name=match.group(2), sql=path.read_text())


def _reject_repeated_numbers(migrations: list[Migration]) -> None:
    """Two migrations sharing a number have no defined order between them."""
    seen: dict[int, str] = {}
    for migration in sorted(migrations, key=lambda migration: migration.name):
        if migration.number in seen:
            raise ValueError(
                f"migration number {migration.number} is used twice: "
                f"{seen[migration.number]} and {migration.name}"
            )
        seen[migration.number] = migration.name
