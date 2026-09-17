"""The facts about one member that the drafting prompt is allowed to see.

Every field here was derived by arithmetic from a stored row. The model never sees
an entry, so a draft that says the member usually came on Tuesday mornings is
repeating a count rather than making an inference.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime

from demogym.scoring import baseline_window

MORNING_ENDS = 12
AFTERNOON_ENDS = 17


@dataclass(frozen=True)
class Facts:
    """One member at one scoring date, as the prompt describes them."""

    account_number: str
    site: str
    band: str
    reason: str
    plan: str
    monthly_price: float
    tenure_months: int
    baseline: float
    last_visit: date | None
    usual_day: str | None
    usual_time: str | None


def build(
    account_number: str,
    site: str,
    band: str,
    reason: str,
    plan: str,
    monthly_price: float,
    baseline: float,
    joined_on: date,
    scored_on: date,
    visits: list[datetime],
) -> Facts:
    """Assembles the facts for one member, counting their visits for the two habits."""
    window = baseline_window(joined_on, scored_on)
    established = [
        visit for visit in visits if window and window.start <= visit.date() < window.end
    ]
    past = [visit for visit in visits if visit.date() <= scored_on]

    return Facts(
        account_number=account_number,
        site=site,
        band=band,
        reason=reason,
        plan=plan,
        monthly_price=monthly_price,
        tenure_months=months_between(joined_on, scored_on),
        baseline=baseline,
        last_visit=max(past).date() if past else None,
        usual_day=usual_day(established),
        usual_time=usual_time(established),
    )


def usual_day(visits: list[datetime]) -> str | None:
    """The weekday they came on most often, or None if they did not come.

    Most often rather than usually. A member whose visits are spread evenly still has
    a modal day, and calling it their usual one would overstate what the count says.
    """
    if not visits:
        return None
    counts = Counter(visit.strftime("%A") for visit in visits)
    return max(counts, key=lambda day: (counts[day], -_WEEKDAYS.index(day)))


def usual_time(visits: list[datetime]) -> str | None:
    """The part of the day they came in most often, or None if they did not come."""
    if not visits:
        return None
    counts = Counter(part_of_day(visit) for visit in visits)
    return max(counts, key=lambda part: (counts[part], -_PARTS.index(part)))


def months_between(joined_on: date, scored_on: date) -> int:
    """Whole months of membership at the scoring date, not at today."""
    months = (scored_on.year - joined_on.year) * 12 + scored_on.month - joined_on.month
    return months - 1 if scored_on.day < joined_on.day else months


_WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

_PARTS = ["morning", "afternoon", "evening"]


def part_of_day(visit: datetime) -> str:
    """Morning, afternoon or evening, split at noon and five."""
    if visit.hour < MORNING_ENDS:
        return "morning"
    return "afternoon" if visit.hour < AFTERNOON_ENDS else "evening"
