"""Which attendance slots at a site have thinned, by day of week and part of day.

Arithmetic only: the trailing three weeks against the nine before them.

The two windows do not overlap, which is where this differs from the decay ratio. For
a member the question is how now compares with their own long-run normal, and the
scorer answers it conservatively by leaving the recent weeks inside the baseline. For
a slot the question is whether it has changed, and a window that contains the change
it is measuring answers that one badly.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from demogym.facts import part_of_day
from demogym.scoring import BASELINE_WEEKS, RECENT_WEEKS

# The earlier of the two windows: the baseline twelve weeks with the recent three
# taken off the end.
BASELINE_WEEKS_BEFORE = BASELINE_WEEKS - RECENT_WEEKS

# Below this a slot has lost less than one visit a week, which at this size is one
# member changing their mind rather than a slot thinning.
MINIMUM_DROP = 1.0


@dataclass(frozen=True)
class Slot:
    """One day-and-part slot at one site, and how its rate has moved."""

    day: str
    part: str
    baseline: float
    recent: float

    @property
    def drop(self) -> float:
        """Visits a week the slot has lost."""
        return self.baseline - self.recent


def thinned(visits: list[datetime], scored_on: date, limit: int = 3) -> list[Slot]:
    """The slots that have lost the most visits a week, worst first.

    `visits` is every arrival at one site, in the estate's own timezone.
    """
    end = scored_on + timedelta(days=1)
    recent_from = end - timedelta(weeks=RECENT_WEEKS)
    baseline_from = end - timedelta(weeks=BASELINE_WEEKS)

    baseline = _counts(visits, baseline_from, recent_from)
    recent = _counts(visits, recent_from, end)

    slots = [
        Slot(
            day=day,
            part=part,
            baseline=count / BASELINE_WEEKS_BEFORE,
            recent=recent[(day, part)] / RECENT_WEEKS,
        )
        for (day, part), count in baseline.items()
    ]
    thinning = [slot for slot in slots if slot.drop >= MINIMUM_DROP]
    return sorted(thinning, key=lambda slot: (-slot.drop, slot.day, slot.part))[:limit]


def _counts(visits: list[datetime], start: date, end: date) -> Counter[tuple[str, str]]:
    return Counter(
        (visit.strftime("%A"), part_of_day(visit))
        for visit in visits
        if start <= visit.date() < end
    )
