"""The facts the prompt is allowed to see, and the counts behind them."""

from datetime import date, datetime

from demogym.facts import build, months_between, usual_day, usual_time


def at(day: str, hour: int) -> datetime:
    return datetime.fromisoformat(day).replace(hour=hour)


def test_the_usual_day_is_the_one_they_came_on_most_often():
    visits = [at("2026-09-01", 7), at("2026-09-08", 7), at("2026-09-09", 7)]
    assert usual_day(visits) == "Tuesday"


def test_a_tie_on_days_takes_the_earlier_one_in_the_week():
    visits = [at("2026-09-07", 7), at("2026-09-08", 7)]
    assert usual_day(visits) == "Monday"


def test_a_member_with_no_visits_has_no_usual_day_or_time():
    assert usual_day([]) is None
    assert usual_time([]) is None


def test_the_usual_time_splits_the_day_at_noon_and_five():
    assert usual_time([at("2026-09-08", 11)]) == "morning"
    assert usual_time([at("2026-09-08", 12)]) == "afternoon"
    assert usual_time([at("2026-09-08", 16)]) == "afternoon"
    assert usual_time([at("2026-09-08", 17)]) == "evening"


def test_tenure_counts_whole_months_to_the_scoring_date():
    assert months_between(date(2026, 3, 17), date(2026, 9, 17)) == 6
    assert months_between(date(2026, 3, 18), date(2026, 9, 17)) == 5


def facts_for(visits: list[datetime]):
    return build(
        account_number="M00042",
        site="Northgate",
        band="high",
        reason="Last came 21 days ago.",
        plan="standard",
        monthly_price=34.99,
        baseline=3.0,
        joined_on=date(2024, 1, 10),
        scored_on=date(2026, 9, 17),
        visits=visits,
    )


def test_the_habits_are_counted_over_the_baseline_window_only():
    old = [at("2025-01-07", 7)] * 5
    recent = [at("2026-08-05", 19)]
    assert facts_for(old + recent).usual_day == "Wednesday"
    assert facts_for(old + recent).usual_time == "evening"


def test_the_last_visit_is_the_most_recent_one_on_or_before_the_scoring_date():
    visits = [at("2026-08-05", 19), at("2026-09-20", 19)]
    assert facts_for(visits).last_visit == date(2026, 8, 5)


def test_a_member_with_no_visits_in_the_window_carries_no_habits():
    facts = facts_for([])
    assert facts.usual_day is None
    assert facts.usual_time is None
    assert facts.last_visit is None
