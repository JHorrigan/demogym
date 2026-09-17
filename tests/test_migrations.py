from pathlib import Path

import pytest

from demogym.cli import MIGRATIONS
from demogym.migrations import load, pending


def write(directory: Path, names: list[str]) -> None:
    for name in names:
        (directory / name).write_text(f"-- {name}\n")


def test_load_orders_by_number_rather_than_by_filename(tmp_path: Path) -> None:
    write(tmp_path, ["10_tenth.sql", "2_second.sql", "1_first.sql"])

    assert [migration.number for migration in load(tmp_path)] == [1, 2, 10]


def test_load_reads_the_sql_and_the_name(tmp_path: Path) -> None:
    write(tmp_path, ["3_create_entries.sql"])

    migration = load(tmp_path)[0]

    assert migration.name == "create_entries"
    assert migration.sql == "-- 3_create_entries.sql\n"


def test_load_ignores_files_that_are_not_numbered_sql(tmp_path: Path) -> None:
    write(tmp_path, ["1_first.sql", "README.md", "notes.sql", "2_second.sql.bak"])

    assert [migration.name for migration in load(tmp_path)] == ["first"]


def test_load_rejects_two_migrations_sharing_a_number(tmp_path: Path) -> None:
    write(tmp_path, ["4_one_way.sql", "4_another_way.sql"])

    with pytest.raises(ValueError, match="number 4 is used twice"):
        load(tmp_path)


def test_pending_returns_only_what_has_not_been_applied(tmp_path: Path) -> None:
    write(tmp_path, ["1_first.sql", "2_second.sql", "3_third.sql"])
    migrations = load(tmp_path)

    assert [migration.number for migration in pending(migrations, {1, 3})] == [2]


def test_pending_returns_nothing_once_everything_is_applied(tmp_path: Path) -> None:
    write(tmp_path, ["1_first.sql", "2_second.sql"])
    migrations = load(tmp_path)

    assert pending(migrations, {1, 2}) == []


def test_the_committed_migrations_are_numbered_from_one_without_gaps() -> None:
    numbers = [migration.number for migration in load(MIGRATIONS)]

    assert numbers == list(range(1, len(numbers) + 1))


def test_the_committed_migrations_create_the_seven_specified_tables() -> None:
    sql = "\n".join(migration.sql for migration in load(MIGRATIONS))

    for table in (
        "sites",
        "members",
        "entries",
        "equipment",
        "risk_scores",
        "drafts",
        "briefings",
    ):
        assert f"create table {table} (" in sql
