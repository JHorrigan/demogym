"""Turns a member's attendance rule into the entry records it would have produced."""

from datetime import date, datetime, timedelta
from random import Random
from zoneinfo import ZoneInfo

from demogym.members import Member

WINDOW_WEEKS = 26
LOCAL = ZoneInfo("Europe/London")

# A member favours certain days, but not exclusively. This is the chance that a
# visit lands on a day they do not usually come.
OFF_DAY_SHARE = 0.12


def entries(member: Member, as_of: date, random: Random) -> list[datetime]:
    """Returns the arrival times for one member over the trailing window.

    Local London times, so an arrival generated at seven in the morning is seven in
    the morning in both halves of the year.
    """
    arrivals = []
    for day in _days(member, as_of):
        rate = _rate_on(member, day, as_of)
        if rate <= 0:
            continue
        if random.random() < _chance(member, day, rate):
            arrivals.append(_arrival(member, day, random))
    return arrivals


def _days(member: Member, as_of: date) -> list[date]:
    """Every day in the window the member was actually a member.

    A member who left on a date did not attend on it, so the last day is the one
    before. Without that, a leaver's final visit lands on their leaving date.
    """
    start = max(as_of - timedelta(weeks=WINDOW_WEEKS), member.joined_on)
    last_day = member.left_on - timedelta(days=1) if member.left_on else as_of
    end = min(as_of, last_day)
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def _rate_on(member: Member, day: date, as_of: date) -> float:
    """The member's visits per week on a given day, after any decline.

    A fading member's rate falls in a straight line from their full rate at
    `fade_from` to `final_share` of it on the scoring date.
    """
    attendance = member.attendance

    if attendance.stopped_on and day >= attendance.stopped_on:
        return 0.0

    if attendance.fade_from is None or day <= attendance.fade_from:
        return attendance.visits_per_week

    elapsed = (day - attendance.fade_from).days
    total = max((as_of - attendance.fade_from).days, 1)
    progress = min(elapsed / total, 1.0)
    share = 1.0 - progress * (1.0 - attendance.final_share)
    return attendance.visits_per_week * share


def _chance(member: Member, day: date, rate: float) -> float:
    """The chance of a visit on one day, spread across the days they favour."""
    favoured = day.weekday() in member.attendance.days
    share = (1.0 - OFF_DAY_SHARE) if favoured else OFF_DAY_SHARE
    spread = len(member.attendance.days) if favoured else 7 - len(member.attendance.days)
    return min(rate * share / spread, 1.0)


def _arrival(member: Member, day: date, random: Random) -> datetime:
    """An arrival near the member's usual hour, with a little drift."""
    hour = member.attendance.hour + random.choice((-1, 0, 0, 0, 1))
    hour = min(max(hour, 5), 22)
    return datetime(day.year, day.month, day.day, hour, random.randint(0, 59), tzinfo=LOCAL)
