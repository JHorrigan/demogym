from datetime import date, timedelta
from random import Random

from demogym.attendance import WINDOW_WEEKS, entries
from demogym.members import Member, generate
from demogym.seed import SEED
from demogym.sites import SITES

AS_OF = date(2026, 9, 17)
WINDOW_START = AS_OF - timedelta(weeks=WINDOW_WEEKS)


def estate(seed: int = SEED) -> list[tuple[Member, list[date]]]:
    """The whole estate as members paired with the dates they attended."""
    random = Random(seed)
    return [
        (member, [arrival.date() for arrival in entries(member, AS_OF, random)])
        for member in generate(AS_OF, Random(seed))
    ]


def test_no_entry_falls_before_a_member_joined() -> None:
    for member, days in estate():
        assert all(day >= member.joined_on for day in days), member.account_number


def test_no_entry_falls_on_or_after_the_date_a_member_left() -> None:
    for member, days in estate():
        if member.left_on:
            assert all(day < member.left_on for day in days), member.account_number


def test_every_entry_falls_inside_the_window() -> None:
    for member, days in estate():
        assert all(WINDOW_START <= day <= AS_OF for day in days), member.account_number


def test_every_member_belongs_to_one_of_the_six_sites() -> None:
    for member, _ in estate():
        assert member.site in SITES


def test_no_member_joined_before_their_site_opened() -> None:
    for member, _ in estate():
        assert member.joined_on >= member.site.opened_on, member.account_number


def test_each_site_gets_the_population_it_asks_for() -> None:
    counted = dict.fromkeys(SITES, 0)
    for member, _ in estate():
        counted[member.site] += 1

    assert counted == {site: site.members for site in SITES}


def test_the_population_is_about_three_hundred() -> None:
    assert 280 <= len(estate()) <= 320


def test_the_estate_produces_about_twelve_thousand_entries() -> None:
    total = sum(len(days) for _, days in estate())

    assert 10_000 <= total <= 14_000


def test_every_account_number_is_unique() -> None:
    accounts = [member.account_number for member, _ in estate()]

    assert len(set(accounts)) == len(accounts)


def test_arrivals_land_within_plausible_opening_hours() -> None:
    random = Random(SEED)
    for member in generate(AS_OF, Random(SEED)):
        for arrival in entries(member, AS_OF, random):
            assert 5 <= arrival.hour <= 22, member.account_number


def test_a_member_who_stopped_has_no_entries_after_stopping() -> None:
    stopped = [(member, days) for member, days in estate() if member.attendance.stopped_on and days]

    assert stopped, "the population should contain members who stopped attending"
    for member, days in stopped:
        assert max(days) < member.attendance.stopped_on, member.account_number


def test_a_fading_member_attends_less_in_the_recent_weeks_than_earlier() -> None:
    """The decline has to be visible in the counts, or there is nothing to score."""
    recent_start = AS_OF - timedelta(weeks=3)
    fading = [
        (member, days)
        for member, days in estate()
        if member.attendance.fade_from and member.left_on is None and len(days) > 40
    ]

    assert fading, "the population should contain members whose attendance fades"
    faded = 0
    for _, days in fading:
        recent = len([day for day in days if day >= recent_start]) / 3
        earlier = len([day for day in days if day < recent_start]) / (WINDOW_WEEKS - 3)
        if recent < earlier:
            faded += 1

    assert faded >= len(fading) * 0.9


def test_the_same_seed_produces_the_same_estate() -> None:
    assert estate(SEED) == estate(SEED)


def test_a_different_seed_produces_a_different_estate() -> None:
    assert estate(SEED) != estate(SEED + 1)
