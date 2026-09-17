"""Scores a member's attendance against their own established pattern.

Arithmetic only. No model is involved, and every number here can be checked by
hand against the entries that produced it.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import median

BASELINE_WEEKS = 12
RECENT_WEEKS = 3
JOINER_WEEKS = 4

# Below this baseline a decay ratio is built on one or two visits, so it is noise
# and the gap reading governs alone.
MINIMUM_BASELINE = 1.0

UNFLAGGED = "unflagged"

# Band, the decay at or below which it applies, and the gap multiple at or above.
# Ordered worst first, so the first match is the band.
BANDS = (
    ("high", 0.25, 4.0),
    ("medium", 0.45, 3.0),
    ("low", 0.65, 2.0),
)

SEVERITY = {UNFLAGGED: 0, "low": 1, "medium": 2, "high": 3}


@dataclass(frozen=True)
class Window:
    """The stretch a member's baseline is measured over, half open.

    `label` is the phrase the reason string uses, so a joiner's reason does not
    claim a twelve-week history they do not have.
    """

    start: date
    end: date
    weeks: int
    label: str


@dataclass(frozen=True)
class Score:
    """One member's band at one date, with the readings behind it."""

    band: str
    reason: str
    baseline: float
    recent_rate: float
    decay: float | None
    typical_gap: float | None
    gap_multiple: float | None


def baseline_window(joined_on: date, scored_on: date) -> Window | None:
    """The window a baseline is measured over, or None for a member too new to score.

    Under four weeks nobody can tell, so the member is not scored at all. Between
    four and twelve weeks the baseline comes from their own first four weeks rather
    than a twelve-week median they cannot fill.
    """
    tenure = (scored_on - joined_on).days
    if tenure < JOINER_WEEKS * 7:
        return None

    if tenure <= BASELINE_WEEKS * 7:
        start = joined_on
        return Window(
            start, start + timedelta(weeks=JOINER_WEEKS), JOINER_WEEKS, "their first four weeks"
        )

    end = scored_on + timedelta(days=1)
    return Window(end - timedelta(weeks=BASELINE_WEEKS), end, BASELINE_WEEKS, "the last 12 weeks")


def score(visits: list[date], joined_on: date, scored_on: date) -> Score | None:
    """Bands one member at one date, or returns None if they are too new to score.

    `visits` is every date the member attended, in any order.
    """
    window = baseline_window(joined_on, scored_on)
    if window is None:
        return None

    in_window = [visit for visit in visits if window.start <= visit < window.end]
    baseline = _baseline(in_window, window)
    recent_rate = _recent_rate(visits, scored_on)
    typical_gap = _typical_gap(in_window)
    days_since = _days_since_last_visit(visits, scored_on)

    decay = recent_rate / baseline if baseline > 0 else None
    gap_multiple = days_since / typical_gap if typical_gap and days_since is not None else None

    decay_band = _decay_band(decay, baseline)
    gap_band = _gap_band(gap_multiple)
    banded = "high" if not in_window else band(decay, gap_multiple, baseline)

    return Score(
        band=banded,
        reason=_reason(
            banded,
            decay_band,
            gap_band,
            window,
            in_window,
            baseline,
            recent_rate,
            decay,
            typical_gap,
            days_since,
        ),
        baseline=baseline,
        recent_rate=recent_rate,
        decay=decay,
        typical_gap=typical_gap,
        gap_multiple=gap_multiple,
    )


def band(decay: float | None, gap_multiple: float | None, baseline: float) -> str:
    """The band two readings give, taking the worse of them.

    A sharp drop in rate and a long silence are each sufficient alone.
    """
    return _worse(_decay_band(decay, baseline), _gap_band(gap_multiple))


def _baseline(in_window: list[date], window: Window) -> float:
    """The member's own established rate in visits per week.

    A median of the weekly counts for a full history, so one holiday does not move
    it. A plain rate for a joiner, who has only four weeks to average.
    """
    if window.weeks == JOINER_WEEKS:
        return len(in_window) / JOINER_WEEKS
    return float(median(_weekly_counts(in_window, window)))


def _weekly_counts(in_window: list[date], window: Window) -> list[int]:
    """One visit count per whole week of the window."""
    counts = []
    for week in range(window.weeks):
        start = window.start + timedelta(weeks=week)
        end = start + timedelta(weeks=1)
        counts.append(len([visit for visit in in_window if start <= visit < end]))
    return counts


def _recent_rate(visits: list[date], scored_on: date) -> float:
    """Visits per week over the trailing three weeks."""
    end = scored_on + timedelta(days=1)
    start = end - timedelta(weeks=RECENT_WEEKS)
    return len([visit for visit in visits if start <= visit < end]) / RECENT_WEEKS


def _typical_gap(in_window: list[date]) -> float | None:
    """The median days between consecutive visits, or None below two visits.

    Measured over distinct days, because a gap is a number of days and two entries
    on one day is not a gap of nothing.
    """
    days = sorted(set(in_window))
    if len(days) < 2:
        return None
    gaps = [(later - earlier).days for earlier, later in zip(days, days[1:], strict=False)]
    return float(median(gaps))


def _days_since_last_visit(visits: list[date], scored_on: date) -> int | None:
    """Days since the member last came, counting visits from any window."""
    past = [visit for visit in visits if visit <= scored_on]
    return (scored_on - max(past)).days if past else None


def _decay_band(decay: float | None, baseline: float) -> str:
    """The band the rate drop alone would give, under the minimum-baseline guard."""
    if decay is None or baseline < MINIMUM_BASELINE:
        return UNFLAGGED
    for name, threshold, _ in BANDS:
        if decay <= threshold:
            return name
    return UNFLAGGED


def _gap_band(gap_multiple: float | None) -> str:
    """The band the silence alone would give."""
    if gap_multiple is None:
        return UNFLAGGED
    for name, _, threshold in BANDS:
        if gap_multiple >= threshold:
            return name
    return UNFLAGGED


def _plain(value: float) -> str:
    """A number as a reader would write it, so the reason agrees with the stored value.

    A gap of 1.5 days shown as 2 makes the multiple beside it fail to divide, which
    reads as a contradiction in a string whose whole job is being checkable.
    """
    return f"{value:.0f}" if value == int(value) else f"{value:.1f}"


def _days(value: float) -> str:
    """A number of days, singular where it is one. These strings are read by people."""
    return "1 day" if value == 1 else f"{_plain(value)} days"


def _last_came(days: int) -> str:
    """When they last came, as a person would say it.

    Zero days is today. "Last came 0 days ago" is the kind of phrase that tells a
    reader the sentence was assembled rather than written.
    """
    if days == 0:
        return "today"
    return "1 day ago" if days == 1 else f"{days} days ago"


def _a_week(rate: float) -> str:
    """A weekly rate as a person would say it."""
    return "once a week" if rate == 1 else f"{_plain(rate)} times a week"


def _worse(left: str, right: str) -> str:
    """A member takes the worse of the two readings."""
    return left if SEVERITY[left] >= SEVERITY[right] else right


def _reason(
    banded: str,
    decay_band: str,
    gap_band: str,
    window: Window,
    in_window: list[date],
    baseline: float,
    recent_rate: float,
    decay: float | None,
    typical_gap: float | None,
    days_since: int | None,
) -> str:
    """Names the reading that drove the band, with the numbers behind it."""
    if not in_window:
        # A joiner can have nothing in their first four weeks and have come since.
        # The window sentence on its own reads as never, which is a different claim.
        since = f" Last came {_last_came(days_since)}." if days_since is not None else ""
        return f"No visits at all in {window.label}.{since}"

    if banded == UNFLAGGED:
        return _steady_reason(baseline, recent_rate, decay, days_since, window)

    if SEVERITY[gap_band] > SEVERITY[decay_band]:
        return _gap_reason(days_since, typical_gap, baseline)

    return _decay_reason(baseline, recent_rate, decay, window, days_since)


def _decay_reason(
    baseline: float, recent_rate: float, decay: float | None, window: Window, days_since: int | None
) -> str:
    since = f" Last came {_last_came(days_since)}." if days_since is not None else ""
    return (
        f"Visits down from {_plain(baseline)} to {_plain(recent_rate)} a week, "
        f"{decay:.0%} of their rate over {window.label}.{since}"
    )


def _gap_reason(days_since: int | None, typical_gap: float | None, baseline: float) -> str:
    rate = f" Usually attends {_a_week(baseline)}." if baseline > 0 else ""
    return (
        f"Last came {_days(days_since)} ago, {days_since / typical_gap:.1f} times "
        f"their usual gap of {_days(typical_gap)}.{rate}"
    )


def _steady_reason(
    baseline: float, recent_rate: float, decay: float | None, days_since: int | None, window: Window
) -> str:
    since = f", last came {_last_came(days_since)}" if days_since is not None else ""
    if decay is None:
        return (
            f"Attends {_a_week(recent_rate)}{since}. Too few visits in {window.label} to compare."
        )
    return f"Attending at {decay:.0%} of their usual {_plain(baseline)} a week{since}."
