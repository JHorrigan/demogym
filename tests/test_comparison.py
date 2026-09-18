"""The checks 016 measures with, each fed text that breaks the rule it guards."""

from demogym.comparison import briefing_violations, draft_violations

CLEAN_BODY = (
    "Hello,\n\nYou were coming in most Tuesday mornings and we have not seen you for a "
    "while. If something has got in the way, we would be glad to help you find a time "
    "that works. Come back in whenever suits.\n\nThe team at Northgate"
)

CLEAN_SITUATION = "At Northgate, 4 of 52 members scored are at risk: 1 High and 3 Medium."


def rules(violations):
    """The rule names, so a test asserts what was caught rather than how it read."""
    return sorted(violation.rule for violation in violations)


def test_a_message_that_follows_the_rules_has_nothing_against_it():
    assert draft_violations("We have missed you", CLEAN_BODY, "none") == []


def test_an_invented_name_is_caught():
    assert "invented name" in rules(draft_violations("Hello", "Dear Sarah, come back.", "none"))


def test_a_placeholder_is_caught():
    assert "placeholder" in rules(draft_violations("Hello", "Dear [Name], come back.", "none"))


def test_the_language_of_measurement_is_caught():
    body = "Your attendance score has dropped and our records show you are at risk."
    caught = rules(draft_violations("Hello", body, "none"))
    assert "language of measurement" in caught


def test_a_percentage_is_caught():
    assert "percentage" in rules(draft_violations("Hello", "You are down 40% on usual.", "none"))


def test_an_offer_nobody_chose_is_caught():
    body = "Come back in and have a free class on us."
    assert "offer where none was chosen" in rules(draft_violations("Hi", body, "none"))


def test_feel_free_is_not_read_as_an_offer():
    assert draft_violations("Hi", "Feel free to come back in whenever suits.", "none") == []


def test_the_chosen_offer_has_to_be_there():
    caught = rules(draft_violations("Hi", CLEAN_BODY, "guest pass"))
    assert "chosen offer missing" in caught


def test_a_different_offer_from_the_one_chosen_is_caught():
    body = "Come back in and bring somebody on a free class."
    assert "an offer that was not chosen" in rules(draft_violations("Hi", body, "guest pass"))


def test_a_stock_phrase_is_caught():
    body = "We noticed you have been away. Do reach out if we can help."
    assert "stock phrase" in rules(draft_violations("Hi", body, "none"))


def test_american_spelling_is_caught():
    assert "American spelling" in rules(draft_violations("Hi", "Our center is open.", "none"))


def test_an_emoji_is_caught():
    assert "emoji" in rules(draft_violations("Hi", "We have missed you \U0001f44b", "none"))


def test_a_dash_standing_in_for_punctuation_is_caught():
    body = "You were in most weeks — then you stopped."
    assert "dash as punctuation" in rules(draft_violations("Hi", body, "none"))


def test_a_briefing_that_follows_the_rules_has_nothing_against_it():
    checks = ["Worth checking whether the Sunday morning slot sits alongside the High band."]
    assert briefing_violations(CLEAN_SITUATION, ["M00198, highest priced"], checks) == []


def test_a_briefing_that_asserts_a_cause_is_caught():
    checks = ["Attendance fell because the treadmills have been out of service."]
    assert "asserts a cause" in rules(briefing_violations(CLEAN_SITUATION, [], checks))


def test_every_causal_construction_is_caught():
    for phrase in ("due to", "caused by", "as a result of", "driven by", "which explains"):
        checks = [f"The drop was {phrase} the broken equipment."]
        assert "asserts a cause" in rules(briefing_violations("", [], checks)), phrase


def test_mentioning_sending_is_caught():
    situation = "Four members were sent a message last week."
    assert "mentions sending" in rules(briefing_violations(situation, [], []))


def test_an_entry_that_numbered_itself_is_caught():
    assert "numbered itself" in rules(briefing_violations("", ["1. M00198, first"], []))


def test_a_reason_for_a_position_in_the_order_of_work_is_not_a_cause():
    """The prompt asks for it, so counting it as a breach would count the instruction."""
    order = ["M00071, first because this is the highest-priced membership at 49.99 a month"]
    assert briefing_violations(CLEAN_SITUATION, order, []) == []


def test_a_cause_in_the_situation_is_still_caught():
    situation = "The at-risk rate rose because the treadmills were out of service."
    assert "asserts a cause" in rules(briefing_violations(situation, [], []))


def test_a_softened_cause_is_still_a_cause():
    """Found by reading, not by counting. The opening does not undo the claim."""
    checks = ["Worth checking whether the outage is contributing to the attendance drop."]
    assert "asserts a cause" in rules(briefing_violations("", [], checks))


def test_an_offer_phrased_warmly_is_still_one_offer():
    body = "We would love to see you back. Enjoy a free class on us."
    assert draft_violations("Hi", body, "free class") == []
