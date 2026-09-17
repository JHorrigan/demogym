"""What the briefing endpoint accepts, and how the prose is assembled."""

import pytest

from demogym.briefing_endpoint import BAD_REQUEST, FORBIDDEN, STATUS, respond
from demogym.briefing_prompt import Briefing, body, system

TOKEN = "a-long-random-string"

VALID = {"site_id": 40}


def unreachable_database():
    raise AssertionError("a refused briefing must not open a database connection")


def unreachable_model():
    raise AssertionError("a refused briefing must not build a model client")


def test_the_wrong_token_is_refused_by_the_endpoint_itself(monkeypatch):
    monkeypatch.setenv("DEMOGYM_ACCESS_TOKEN", TOKEN)
    status, refused = respond("not-the-token", VALID, unreachable_database, unreachable_model)
    assert status == 401
    assert refused["error"] == FORBIDDEN


def test_a_site_id_must_be_a_positive_integer(monkeypatch):
    monkeypatch.setenv("DEMOGYM_ACCESS_TOKEN", TOKEN)
    for payload in (None, [40], {}, {"site_id": "40"}, {"site_id": 0}, {"site_id": True}):
        status, refused = respond(TOKEN, payload, unreachable_database, unreachable_model)
        assert status == 400
        assert refused["error"] == BAD_REQUEST


def test_no_token_configured_is_a_fault_rather_than_an_open_door(monkeypatch):
    monkeypatch.delenv("DEMOGYM_ACCESS_TOKEN", raising=False)
    with pytest.raises(KeyError):
        respond(TOKEN, VALID, unreachable_database, unreachable_model)


def test_the_failure_states_are_spelled_as_the_interface_spells_them():
    assert {"unreachable", "no credit", "daily limit"} <= STATUS.keys()
    assert STATUS["daily limit"] == 429


def test_the_prose_carries_the_three_parts_under_headings():
    written = body(
        Briefing(
            situation="Northgate is steady.",
            contact_first=["M00020, first because they have not come for five days."],
            worth_checking=["Worth checking whether the air bike matters."],
        )
    )

    assert written.startswith("Northgate is steady.")
    assert "Who to contact first\n1. M00020, first because" in written
    assert "Worth checking\n- Worth checking whether the air bike" in written


def test_an_entry_the_model_numbered_itself_is_not_numbered_twice():
    """The prompt asks it not to. It sometimes does anyway."""
    written = body(
        Briefing(situation="Steady.", contact_first=["1. M00020, first."], worth_checking=[])
    )

    assert "1. M00020, first." in written
    assert "1. 1." not in written


def test_nothing_worth_checking_says_so_rather_than_leaving_a_heading_empty():
    written = body(Briefing(situation="Steady.", contact_first=["M00020."], worth_checking=[]))

    assert written.endswith("- Nothing in these figures stands out as worth checking.")


def test_the_rules_forbid_claiming_a_cause():
    """The one constraint 0007 says to stress hardest is carried in the prompt."""
    rules = system()
    assert "may not say, imply or\n  suggest that one caused the other" in rules
    assert "no evidence about cause" in rules
    assert "do not mention\n  sending at all" in rules
