"""What a decision has to be, and what the endpoint answers when it is not."""

import pytest

from demogym.decide_endpoint import BAD_REQUEST, FORBIDDEN, STATUS, respond
from demogym.decisions import ACTIONS, MAXIMUM_EDIT, Decision, parse

TOKEN = "a-long-random-string"

APPROVE = {"member_id": 42, "decision": "approved"}
EDIT = {"member_id": 42, "decision": "edited", "edited_body": "Something a person wrote."}


def refuses(payload: object) -> str:
    with pytest.raises(ValueError) as refusal:
        parse(payload)
    return str(refusal.value)


def test_an_approval_parses_to_a_member_and_an_action():
    assert parse(APPROVE) == Decision(42, "approved", None)


def test_an_edit_carries_the_body_the_reviewer_wrote():
    assert parse(EDIT) == Decision(42, "edited", "Something a person wrote.")


def test_the_three_actions_are_the_ones_the_column_allows():
    """`drafts.decision` checks against these three. Nothing checks the two agree."""
    assert ACTIONS == ("approved", "edited", "rejected")


def test_a_body_that_is_not_an_object_is_refused():
    assert "JSON object" in refuses(None)


def test_a_member_id_must_be_a_positive_integer():
    assert "member_id" in refuses(APPROVE | {"member_id": "42"})
    assert "member_id" in refuses(APPROVE | {"member_id": 0})
    assert "member_id" in refuses({"decision": "approved"})


def test_the_action_must_be_one_of_the_three():
    assert "decision" in refuses(APPROVE | {"decision": "maybe"})
    assert "decision" in refuses({"member_id": 42})


def test_an_approval_cannot_carry_an_edit():
    """Otherwise a row would say approved and hold a rewrite nobody agreed to."""
    assert "belongs to an edit" in refuses(APPROVE | {"edited_body": "a rewrite"})
    assert "belongs to an edit" in refuses(
        {"member_id": 42, "decision": "rejected", "edited_body": "a rewrite"}
    )


def test_an_edit_needs_a_body():
    assert "needs an edited_body" in refuses({"member_id": 42, "decision": "edited"})
    assert "needs an edited_body" in refuses(EDIT | {"edited_body": "   "})
    assert "needs an edited_body" in refuses(EDIT | {"edited_body": 7})


def test_an_edit_is_bounded():
    assert "longer than" in refuses(EDIT | {"edited_body": "x" * (MAXIMUM_EDIT + 1)})
    assert parse(EDIT | {"edited_body": "x" * MAXIMUM_EDIT}).edited_body


def unreachable_database():
    raise AssertionError("a refused decision must not open a database connection")


def test_the_wrong_token_is_refused_by_the_endpoint_itself(monkeypatch):
    monkeypatch.setenv("DEMOGYM_ACCESS_TOKEN", TOKEN)
    status, body = respond("not-the-token", APPROVE, unreachable_database)
    assert status == 401
    assert body["error"] == FORBIDDEN


def test_a_refused_decision_never_reaches_the_database(monkeypatch):
    monkeypatch.setenv("DEMOGYM_ACCESS_TOKEN", TOKEN)
    status, body = respond(TOKEN, APPROVE | {"decision": "maybe"}, unreachable_database)
    assert status == 400
    assert body["error"] == BAD_REQUEST
    assert "decision" in body["message"]


def test_no_token_configured_is_a_fault_rather_than_an_open_door(monkeypatch):
    monkeypatch.delenv("DEMOGYM_ACCESS_TOKEN", raising=False)
    with pytest.raises(KeyError):
        respond(TOKEN, APPROVE, unreachable_database)


def test_a_decision_that_cannot_be_recorded_is_never_a_server_fault():
    assert max(STATUS.values()) < 500
