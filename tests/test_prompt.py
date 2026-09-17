"""What reaches the model, and what cannot."""

from datetime import date

from demogym.drafting import Controls
from demogym.facts import Facts
from demogym.prompt import system, user

SCORED_ON = date(2026, 9, 17)

FACTS = Facts(
    account_number="M00042",
    site="Northgate",
    band="high",
    reason="Last came 21 days ago, 5.2 times their usual gap of 4 days.",
    plan="standard",
    monthly_price=34.99,
    tenure_months=32,
    baseline=3.0,
    last_visit=date(2026, 8, 27),
    usual_day="Tuesday",
    usual_time="morning",
)

CONTROLS = Controls("warm", "standard", "free class")


def test_every_fact_in_the_prompt_is_one_the_row_carries():
    prompt = user(FACTS, CONTROLS, SCORED_ON)
    assert FACTS.reason in prompt
    assert "M00042" in prompt
    assert "Northgate" in prompt
    assert "standard, 34.99 pounds a month" in prompt
    assert "2 years" in prompt
    assert "3.0 visits a week" in prompt
    assert "2026-08-27" in prompt
    assert "most often on a Tuesday, most often in the morning" in prompt


def test_the_terms_the_reviewer_set_are_named_in_the_words_they_chose():
    prompt = user(FACTS, CONTROLS, SCORED_ON)
    assert "Tone: warm" in prompt
    assert "about 120 words" in prompt
    assert "Offer: a free class" in prompt


def test_a_short_draft_asks_for_forty_words():
    assert "about 40 words" in user(FACTS, Controls("direct", "short", "none"), SCORED_ON)


def test_no_offer_says_to_offer_nothing_rather_than_leaving_it_open():
    prompt = user(FACTS, Controls("direct", "short", "none"), SCORED_ON)
    assert "Offer: none, do not offer anything" in prompt


def test_a_member_with_no_habits_gets_no_line_about_them():
    prompt = user(
        Facts(**{**vars(FACTS), "usual_day": None, "usual_time": None}), CONTROLS, SCORED_ON
    )
    assert "most often" not in prompt


def test_a_member_who_never_came_says_so_rather_than_carrying_a_blank():
    prompt = user(Facts(**{**vars(FACTS), "last_visit": None}), CONTROLS, SCORED_ON)
    assert "Last visit: no visit on record" in prompt


def test_the_prompt_never_names_the_band_or_the_score():
    """The member is not told they were flagged. The model is not told either."""
    prompt = user(FACTS, CONTROLS, SCORED_ON)
    assert "high" not in prompt.lower()
    assert "band" not in prompt.lower()


def test_the_rules_forbid_inventing_a_name_and_a_cause():
    assert "Do not invent one" in system()
    assert "Never state why they stopped coming" in system()
