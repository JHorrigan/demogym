"""Generates the member population and the attendance habit behind each member."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import StrEnum
from random import Random

from demogym.sites import SITES, Site

PLANS = (
    ("off-peak", Decimal("24.99")),
    ("standard", Decimal("34.99")),
    ("premium", Decimal("49.99")),
)

MORNING_HOURS = (6, 7, 8, 9)
EVENING_HOURS = (17, 18, 19, 20)
WEEKDAYS = (0, 1, 2, 3, 4)
ALL_DAYS = (0, 1, 2, 3, 4, 5, 6)


class Habit(StrEnum):
    """How a member attends. Never stored, so nothing can score against it."""

    REGULAR = "regular"
    WEEKDAY_MORNING = "weekday morning"
    OCCASIONAL = "occasional"
    FADING = "fading"
    STOPPED = "stopped"


# Weights across the population. The fading and stopped shares are what give the
# scorer something to find; 006 tunes them against the band thresholds.
HABIT_WEIGHTS = (
    (Habit.REGULAR, 25),
    (Habit.WEEKDAY_MORNING, 13),
    (Habit.OCCASIONAL, 52),
    (Habit.FADING, 7),
    (Habit.STOPPED, 3),
)


@dataclass(frozen=True)
class Attendance:
    """The rule a member's entries are drawn from.

    `visits_per_week` is the rate before any decline. `days` are the weekdays they
    favour and `hour` the hour they usually arrive. A fading member's rate falls
    linearly from `fade_from` to `final_share` of the original by the scoring date.
    A stopped member's entries end at `stopped_on`.
    """

    habit: Habit
    visits_per_week: float
    days: tuple[int, ...]
    hour: int
    fade_from: date | None
    final_share: float
    stopped_on: date | None


@dataclass(frozen=True)
class Member:
    """One member, with the attendance rule that produces their entries.

    `attendance` is generation input and is never written to the database.
    """

    account_number: str
    site: Site
    joined_on: date
    left_on: date | None
    plan: str
    monthly_price: Decimal
    attendance: Attendance


def generate(as_of: date, random: Random) -> list[Member]:
    """Builds the whole population, site by site, in a stable order."""
    members = []
    for site in SITES:
        for _ in range(site.members):
            members.append(_member(site, len(members) + 1, as_of, random))
    return members


def _member(site: Site, number: int, as_of: date, random: Random) -> Member:
    joined_on = _joined_on(site, as_of, random)
    plan, monthly_price = random.choice(PLANS)
    return Member(
        account_number=f"M{number:05d}",
        site=site,
        joined_on=joined_on,
        left_on=_left_on(joined_on, as_of, random),
        plan=plan,
        monthly_price=monthly_price,
        attendance=_attendance(as_of, random),
    )


def _joined_on(site: Site, as_of: date, random: Random) -> date:
    """Mostly long tenure, with enough recent joiners to exercise both baseline rules.

    Below 4 weeks nobody is scored at all, and between 4 and 12 weeks the baseline
    comes from a member's own first four weeks rather than a 12-week median.
    """
    roll = random.random()
    if roll < 0.08:
        weeks_ago = random.uniform(0.5, 4)
    elif roll < 0.20:
        weeks_ago = random.uniform(4, 12)
    else:
        weeks_ago = random.uniform(13, 300)

    joined_on = as_of - timedelta(weeks=weeks_ago)
    return max(joined_on, site.opened_on)


def _left_on(joined_on: date, as_of: date, random: Random) -> date | None:
    """A small share have already gone. They are not scored and not in the queue."""
    if random.random() >= 0.06:
        return None
    earliest = max(joined_on + timedelta(weeks=8), as_of - timedelta(weeks=24))
    if earliest >= as_of:
        return None
    days = (as_of - earliest).days
    return earliest + timedelta(days=random.randint(0, days))


def _spread(count: int, among: tuple[int, ...], random: Random) -> tuple[int, ...]:
    """`count` days spaced as evenly across `among` as it allows.

    Days drawn independently cluster, which puts consecutive-day visits in the
    majority and makes the median gap one day. A member who trains four times a
    week goes every other day, so an ordinary two-day break is not twice their
    usual gap. This is what keeps the gap reading meaningful.
    """
    start = random.randrange(len(among))
    picked = {
        among[(start + round(step * len(among) / count)) % len(among)] for step in range(count)
    }
    return tuple(sorted(picked))


def _attendance(as_of: date, random: Random) -> Attendance:
    habit = random.choices(
        [habit for habit, _ in HABIT_WEIGHTS],
        weights=[weight for _, weight in HABIT_WEIGHTS],
    )[0]

    if habit is Habit.REGULAR:
        rate = random.uniform(2.6, 4.3)
        return Attendance(
            habit=habit,
            visits_per_week=rate,
            days=_spread(round(rate), ALL_DAYS, random),
            hour=random.choice(MORNING_HOURS + EVENING_HOURS),
            fade_from=None,
            final_share=1.0,
            stopped_on=None,
        )

    if habit is Habit.WEEKDAY_MORNING:
        rate = random.uniform(1.9, 3.1)
        return Attendance(
            habit=habit,
            visits_per_week=rate,
            days=_spread(round(rate), WEEKDAYS, random),
            hour=random.choice(MORNING_HOURS),
            fade_from=None,
            final_share=1.0,
            stopped_on=None,
        )

    if habit is Habit.OCCASIONAL:
        return Attendance(
            habit=habit,
            visits_per_week=random.uniform(0.25, 1.0),
            # One or two days they favour rather than any day of the week. A
            # fortnightly attender goes on alternate Saturdays; they do not roll a
            # die every morning. Spread across all seven days their visits arrive in
            # bursts, and a median gap taken over two or three of them says nothing.
            days=_spread(random.randint(1, 2), ALL_DAYS, random),
            hour=random.choice(MORNING_HOURS + EVENING_HOURS),
            fade_from=None,
            final_share=1.0,
            stopped_on=None,
        )

    if habit is Habit.FADING:
        rate = random.uniform(2.2, 4.4)
        return Attendance(
            habit=habit,
            visits_per_week=rate,
            days=_spread(round(rate), ALL_DAYS, random),
            hour=random.choice(MORNING_HOURS + EVENING_HOURS),
            fade_from=as_of - timedelta(weeks=random.uniform(6, 14)),
            # How far the fade goes decides the band, so the range spans all three
            # rather than bunching every fading member into High.
            final_share=random.uniform(0.15, 0.6),
            stopped_on=None,
        )

    rate = random.uniform(1.6, 4.2)
    return Attendance(
        habit=habit,
        visits_per_week=rate,
        days=_spread(round(rate), ALL_DAYS, random),
        hour=random.choice(MORNING_HOURS + EVENING_HOURS),
        fade_from=None,
        final_share=1.0,
        stopped_on=as_of - timedelta(days=random.randint(9, 70)),
    )
