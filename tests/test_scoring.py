from datetime import date, timedelta

from demogym.score import is_active, scoring_dates
from demogym.scoring import (
    BASELINE_WEEKS,
    MINIMUM_BASELINE,
    UNFLAGGED,
    band,
    baseline_window,
    score,
)

SCORED_ON = date(2026, 9, 17)
SETTLED = SCORED_ON - timedelta(weeks=60)

# Any baseline at or above the guard, so the decay reading governs.
COMPARABLE = 4.0


def week_starts(scored_on: date = SCORED_ON) -> list[date]:
    """The first day of each of the twelve weeks the baseline window covers."""
    end = scored_on + timedelta(days=1)
    start = end - timedelta(weeks=BASELINE_WEEKS)
    return [start + timedelta(weeks=week) for week in range(BASELINE_WEEKS)]


def visits_in_weeks(counts: list[int], scored_on: date = SCORED_ON) -> list[date]:
    """Visits placed week by week, `counts[n]` of them in the nth week of the window."""
    visits = []
    for start, count in zip(week_starts(scored_on), counts, strict=True):
        visits.extend(start + timedelta(days=offset) for offset in range(count))
    return visits


def every(days: int, count: int, ending: date) -> list[date]:
    """`count` visits `days` apart, the most recent of them on `ending`."""
    return [ending - timedelta(days=days * step) for step in range(count)]


# The six cut points in the band table. Each pair fails if its threshold moves.


def test_decay_at_the_high_threshold_bands_high() -> None:
    assert band(0.25, None, COMPARABLE) == "high"


def test_decay_just_above_the_high_threshold_bands_medium() -> None:
    assert band(0.26, None, COMPARABLE) == "medium"


def test_decay_at_the_medium_threshold_bands_medium() -> None:
    assert band(0.45, None, COMPARABLE) == "medium"


def test_decay_just_above_the_medium_threshold_bands_low() -> None:
    assert band(0.46, None, COMPARABLE) == "low"


def test_decay_at_the_low_threshold_bands_low() -> None:
    assert band(0.65, None, COMPARABLE) == "low"


def test_decay_just_above_the_low_threshold_is_not_flagged() -> None:
    assert band(0.66, None, COMPARABLE) == UNFLAGGED


def test_gap_multiple_at_the_high_threshold_bands_high() -> None:
    assert band(None, 4.0, COMPARABLE) == "high"


def test_gap_multiple_just_below_the_high_threshold_bands_medium() -> None:
    assert band(None, 3.99, COMPARABLE) == "medium"


def test_gap_multiple_at_the_medium_threshold_bands_medium() -> None:
    assert band(None, 3.0, COMPARABLE) == "medium"


def test_gap_multiple_just_below_the_medium_threshold_bands_low() -> None:
    assert band(None, 2.99, COMPARABLE) == "low"


def test_gap_multiple_at_the_low_threshold_bands_low() -> None:
    assert band(None, 2.0, COMPARABLE) == "low"


def test_gap_multiple_just_below_the_low_threshold_is_not_flagged() -> None:
    assert band(None, 1.99, COMPARABLE) == UNFLAGGED


def test_a_member_takes_the_worse_of_the_two_readings() -> None:
    # A long silence alone, with a rate that is not flagged at all.
    assert band(0.66, 4.0, COMPARABLE) == "high"
    # A sharp drop alone, with a gap well inside the usual rhythm.
    assert band(0.25, 1.0, COMPARABLE) == "high"
    # Two readings, one worse than the other.
    assert band(0.5, 3.0, COMPARABLE) == "medium"
    assert band(0.45, 2.0, COMPARABLE) == "medium"


# The minimum-baseline guard.


def test_the_guard_keeps_a_rate_drop_on_a_low_baseline_out_of_the_band() -> None:
    """Baselines spelt out rather than taken from the constant, so moving the guard
    does not move the test along with it."""
    assert band(0.0, None, 0.5) == UNFLAGGED


def test_the_same_drop_on_a_comparable_baseline_bands_high() -> None:
    """The guard is what makes the difference, not the ratio."""
    assert band(0.0, None, 1.0) == "high"


def test_a_fortnightly_attender_silent_for_nine_days_is_behaving_normally() -> None:
    """Half of the specification's paired example. The other half is below.

    A global rule on days since the last visit flags this member and misses the
    one below, which is precisely backwards.
    """
    scored = score(every(14, 12, SCORED_ON - timedelta(days=9)), SETTLED, SCORED_ON)

    assert scored.baseline < MINIMUM_BASELINE
    assert scored.typical_gap == 14.0
    assert scored.band == UNFLAGGED


def test_a_four_times_a_week_member_silent_for_nine_days_is_in_trouble() -> None:
    visits = [
        day
        for day in (SCORED_ON - timedelta(days=offset) for offset in range(9, 200))
        if day.weekday() in (0, 1, 3, 4)
    ]
    scored = score(visits, SETTLED, SCORED_ON)

    assert scored.baseline == COMPARABLE
    # The rate reading alone would not flag them. The silence is what does it.
    assert scored.decay > 0.45
    assert scored.band == "high"


def test_the_same_four_times_a_week_member_is_not_flagged_after_three_days() -> None:
    visits = [
        day
        for day in (SCORED_ON - timedelta(days=offset) for offset in range(3, 200))
        if day.weekday() in (0, 1, 3, 4)
    ]

    assert score(visits, SETTLED, SCORED_ON).band == UNFLAGGED


# Tenure and the baseline windows.


def test_a_member_inside_their_first_four_weeks_is_not_scored() -> None:
    joined = SCORED_ON - timedelta(days=27)

    assert baseline_window(joined, SCORED_ON) is None
    assert score(every(2, 10, SCORED_ON), joined, SCORED_ON) is None


def test_a_member_at_exactly_four_weeks_is_scored() -> None:
    joined = SCORED_ON - timedelta(days=28)

    assert baseline_window(joined, SCORED_ON) is not None


def test_a_member_between_four_and_twelve_weeks_uses_their_own_first_four_weeks() -> None:
    joined = SCORED_ON - timedelta(days=60)
    window = baseline_window(joined, SCORED_ON)

    assert window.start == joined
    assert window.weeks == 4

    # Eight visits inside those first four weeks, and none after.
    scored = score([joined + timedelta(days=day * 2) for day in range(8)], joined, SCORED_ON)

    assert scored.baseline == 2.0


def test_a_member_past_twelve_weeks_uses_the_trailing_twelve_weeks() -> None:
    window = baseline_window(SETTLED, SCORED_ON)

    assert window.weeks == BASELINE_WEEKS
    assert window.end == SCORED_ON + timedelta(days=1)


def test_the_baseline_is_a_median_so_one_holiday_does_not_move_it() -> None:
    """Eleven weeks at three visits and one week away. The mean would say 2.75."""
    scored = score(visits_in_weeks([3] * 11 + [0]), SETTLED, SCORED_ON)

    assert scored.baseline == 3.0


def test_the_baseline_median_takes_the_middle_of_an_uneven_history() -> None:
    scored = score(visits_in_weeks([0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]), SETTLED, SCORED_ON)

    assert scored.baseline == 2.5


# No visits at all.


def test_no_visits_in_the_baseline_window_bands_high() -> None:
    scored = score([], SETTLED, SCORED_ON)

    assert scored.band == "high"
    assert scored.baseline == 0.0


def test_no_visits_in_the_window_says_so_without_quoting_a_ratio() -> None:
    scored = score([], SETTLED, SCORED_ON)

    assert scored.reason == "No visits at all in the last 12 weeks."
    assert scored.decay is None
    assert scored.gap_multiple is None


def test_no_visits_in_the_window_still_says_when_they_last_came() -> None:
    """A joiner can have nothing in their first four weeks and have come since.

    The window sentence alone reads as never, and a message drafted from it sits
    beside a last visit the member certainly made.
    """
    joined = SCORED_ON - timedelta(weeks=9)
    scored = score([SCORED_ON - timedelta(days=19)], joined, SCORED_ON)

    assert scored.reason == "No visits at all in their first four weeks. Last came 19 days ago."


def test_a_member_whose_visits_all_predate_the_window_bands_high() -> None:
    scored = score(every(3, 20, SCORED_ON - timedelta(weeks=20)), SETTLED, SCORED_ON)

    assert scored.band == "high"


# The readings themselves.


def test_the_recent_rate_covers_three_weeks() -> None:
    scored = score(visits_in_weeks([0] * 9 + [2, 2, 2]), SETTLED, SCORED_ON)

    assert scored.recent_rate == 2.0


def test_the_typical_gap_is_the_median_of_consecutive_gaps() -> None:
    """Gaps of 1, 1, 1 and 10 days. The mean would say 3.25."""
    start = week_starts()[0]
    visits = [start + timedelta(days=offset) for offset in (0, 1, 2, 3, 13)]
    scored = score(visits, SETTLED, SCORED_ON)

    assert scored.typical_gap == 1.0


def test_the_typical_gap_is_unknown_below_two_visits() -> None:
    scored = score([SCORED_ON - timedelta(days=3)], SETTLED, SCORED_ON)

    assert scored.typical_gap is None
    assert scored.gap_multiple is None


def test_decay_is_unknown_when_the_baseline_is_zero() -> None:
    """Two visits in twelve weeks gives a median weekly count of zero."""
    scored = score(
        [SCORED_ON - timedelta(days=80), SCORED_ON - timedelta(days=40)], SETTLED, SCORED_ON
    )

    assert scored.baseline == 0.0
    assert scored.decay is None


def test_the_gap_multiple_counts_from_the_last_visit_even_outside_the_window() -> None:
    """A joiner's baseline window is their first four weeks, long past by now.

    Days since the last visit has to count the visit they made last week, not the
    last one inside that window, or a current member reads as months silent.
    """
    joined = SCORED_ON - timedelta(days=60)
    visits = [joined + timedelta(days=day * 2) for day in range(8)]
    visits.append(SCORED_ON - timedelta(days=5))
    scored = score(visits, joined, SCORED_ON)

    assert scored.typical_gap == 2.0
    assert scored.gap_multiple == 2.5


# Reason strings.


def test_the_reason_names_the_gap_when_the_silence_drove_the_band() -> None:
    scored = score(every(2, 40, SCORED_ON - timedelta(days=10)), SETTLED, SCORED_ON)

    assert scored.band == "high"
    assert "Last came 10 days ago" in scored.reason
    assert "usual gap of 2 days" in scored.reason


def test_the_reason_names_the_rate_when_the_drop_drove_the_band() -> None:
    scored = score(visits_in_weeks([4] * 9 + [1, 0, 0]), SETTLED, SCORED_ON)

    assert scored.band == "high"
    assert "Visits down from 4 to 0.3 a week" in scored.reason


def test_the_numbers_in_a_gap_reason_divide_the_way_it_claims() -> None:
    """The multiple has to equal the days over the gap, or the string is not checkable."""
    scored = score(every(3, 40, SCORED_ON - timedelta(days=12)), SETTLED, SCORED_ON)

    assert scored.band == "high"
    assert "Last came 12 days ago, 4.0 times their usual gap of 3 days" in scored.reason
    assert scored.gap_multiple == 12 / 3


def test_a_joiner_reason_does_not_claim_a_twelve_week_history() -> None:
    joined = SCORED_ON - timedelta(days=60)
    scored = score([joined + timedelta(days=day) for day in range(0, 28, 2)], joined, SCORED_ON)

    assert "their first four weeks" in scored.reason
    assert "12 weeks" not in scored.reason


def test_every_score_carries_a_reason() -> None:
    for visits in ([], every(2, 40, SCORED_ON), every(30, 4, SCORED_ON - timedelta(days=40))):
        scored = score(visits, SETTLED, SCORED_ON)

        assert scored.reason
        assert scored.reason.endswith(".")


# The weekly sweep across twelve dates.


def test_the_sweep_covers_twelve_weekly_dates_ending_on_the_scoring_date() -> None:
    dates = scoring_dates(SCORED_ON)

    assert len(dates) == 12
    assert dates[-1] == SCORED_ON
    assert dates[0] == SCORED_ON - timedelta(weeks=11)
    assert all(
        (later - earlier).days == 7 for earlier, later in zip(dates, dates[1:], strict=False)
    )


def test_a_member_who_had_not_joined_yet_is_not_active() -> None:
    assert not is_active(SCORED_ON + timedelta(days=1), None, SCORED_ON)


def test_a_member_who_joined_on_the_scoring_date_is_active() -> None:
    assert is_active(SCORED_ON, None, SCORED_ON)


def test_a_member_who_left_before_the_scoring_date_is_not_active() -> None:
    assert not is_active(SETTLED, SCORED_ON - timedelta(days=1), SCORED_ON)


def test_a_member_who_leaves_after_the_scoring_date_is_still_active_on_it() -> None:
    assert is_active(SETTLED, SCORED_ON + timedelta(days=1), SCORED_ON)


def test_a_member_who_left_on_the_scoring_date_is_no_longer_active() -> None:
    assert not is_active(SETTLED, SCORED_ON, SCORED_ON)


# Reason strings are read by people, so they have to read like English.


def test_a_gap_of_one_day_reads_as_one_day() -> None:
    """A row saying "their usual gap of 1 days" undermines the string's whole job."""
    scored = score(every(1, 40, SCORED_ON - timedelta(days=5)), SETTLED, SCORED_ON)

    assert scored.typical_gap == 1.0
    assert "gap of 1 day." in scored.reason
    assert "1 days" not in scored.reason


def test_a_weekly_rate_of_one_reads_as_once_a_week() -> None:
    """The offsets are taken from a real row that read "Attends 1 times a week"."""
    visits = [SCORED_ON - timedelta(days=offset) for offset in (90, 89, 76, 13, 9, 2)]
    scored = score(visits, SETTLED, SCORED_ON)

    assert scored.recent_rate == 1.0
    assert "once a week" in scored.reason
    assert "1 times a week" not in scored.reason


def test_a_visit_yesterday_reads_as_one_day_ago() -> None:
    visits = [*visits_in_weeks([5] * 11 + [0]), SCORED_ON - timedelta(days=1)]
    scored = score(visits, SETTLED, SCORED_ON)

    assert "last came 1 day ago" in scored.reason
    assert "1 days ago" not in scored.reason


def test_a_visit_today_reads_as_today() -> None:
    """ "Last came 0 days ago" reads as an assembled sentence rather than a written one."""
    visits = [*visits_in_weeks([5] * 11 + [0]), SCORED_ON]
    scored = score(visits, SETTLED, SCORED_ON)

    assert "last came today" in scored.reason
    assert "0 days ago" not in scored.reason
