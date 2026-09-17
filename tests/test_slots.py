"""Which attendance slots have thinned, and by how much."""

from datetime import date, datetime, timedelta

from demogym.slots import BASELINE_WEEKS_BEFORE, MINIMUM_DROP, RECENT_WEEKS, thinned

SCORED_ON = date(2026, 9, 17)

# The Thursday inside the most recent week, so counting back in weeks stays on a
# Thursday and inside whichever window is intended.
THURSDAY = date(2026, 9, 17)


def visits(hour: int, weeks_ago: range, day: date = THURSDAY) -> list[datetime]:
    """One visit in that slot for each of those weeks."""
    return [
        datetime.combine(day - timedelta(weeks=week), datetime.min.time()).replace(hour=hour)
        for week in weeks_ago
    ]


def test_a_slot_that_stopped_shows_the_whole_rate_it_had():
    """One a week for the nine earlier weeks, none in the recent three."""
    slots = thinned(visits(9, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE)), SCORED_ON)

    assert [(slot.day, slot.part) for slot in slots] == [("Thursday", "morning")]
    assert slots[0].baseline == 1.0
    assert slots[0].recent == 0.0
    assert slots[0].drop == 1.0


def test_a_slot_that_kept_going_is_not_reported():
    every_week = visits(9, range(0, RECENT_WEEKS + BASELINE_WEEKS_BEFORE))

    assert thinned(every_week, SCORED_ON) == []


def test_a_drop_below_a_visit_a_week_is_not_reported():
    """One a week earlier and nothing recently is exactly the floor.

    A single visit in the recent window lifts the rate to a third and the drop to
    two thirds, which is under it, and the slot goes.
    """
    earlier = visits(9, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE))

    assert thinned(earlier, SCORED_ON)[0].drop == MINIMUM_DROP
    assert thinned(earlier + visits(9, range(0, 1)), SCORED_ON) == []


def test_the_windows_do_not_overlap():
    """The earlier rate is measured without the recent weeks in it.

    Two a week for the nine earlier weeks and one a week for the recent three is a
    rate of 2.0 falling to 1.0. A twelve-week window holding the recent three would
    count those three visits into the earlier rate as well and report 2.3 falling to
    1.0, which softens a decline by containing it.
    """
    earlier = visits(9, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE))
    earlier += visits(10, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE))
    recent = visits(9, range(0, RECENT_WEEKS))

    slot = thinned(earlier + recent, SCORED_ON)[0]

    assert slot.baseline == 2.0
    assert slot.recent == 1.0
    assert slot.drop == 1.0


def test_the_worst_slot_comes_first_and_the_list_is_bounded():
    friday = THURSDAY + timedelta(days=1)
    small = visits(9, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE))
    large = visits(19, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE), day=friday)
    large += visits(19, range(RECENT_WEEKS, RECENT_WEEKS + BASELINE_WEEKS_BEFORE), day=friday)

    slots = thinned(small + large, SCORED_ON, limit=1)

    assert [(slot.day, slot.part) for slot in slots] == [("Friday", "evening")]


def test_visits_before_the_twelve_weeks_are_outside_both_windows():
    long_ago = visits(9, range(20, 30))

    assert thinned(long_ago, SCORED_ON) == []
