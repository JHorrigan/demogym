"""The call, what it costs, and what a failure is called."""

from decimal import Decimal
from types import SimpleNamespace

import httpx2
import pytest
from openai import APIConnectionError, APITimeoutError, AuthenticationError, RateLimitError
from pydantic import ValidationError

from demogym.model import (
    MODEL,
    NO_CREDIT,
    REFUSED,
    TRUNCATED,
    UNREACHABLE,
    ModelFailed,
    classify,
    cost_in_cents,
    generate,
)
from demogym.prompt import Message

REQUEST = httpx2.Request("POST", "https://api.openai.com/v1/responses")


def status_error(kind, code: str, status: int):
    return kind(
        "refused",
        response=httpx2.Response(status, request=REQUEST),
        body={"code": code, "type": code},
    )


def test_a_rate_limited_call_is_worth_trying_again():
    assert classify(status_error(RateLimitError, "rate_limit_exceeded", 429)) == UNREACHABLE


def test_an_exhausted_balance_is_not_worth_trying_again():
    """Both arrive as 429. Only the body tells them apart."""
    assert classify(status_error(RateLimitError, "insufficient_quota", 429)) == NO_CREDIT
    assert classify(status_error(RateLimitError, "billing_hard_limit_reached", 429)) == NO_CREDIT


def test_a_dropped_connection_or_a_timeout_reads_as_unreachable():
    assert classify(APIConnectionError(request=REQUEST)) == UNREACHABLE
    assert classify(APITimeoutError(request=REQUEST)) == UNREACHABLE


def test_a_bad_key_is_not_reported_as_an_empty_account():
    assert classify(status_error(AuthenticationError, "invalid_api_key", 401)) == UNREACHABLE


def test_cost_is_the_published_price_times_the_tokens_the_api_reported():
    # 1,000,000 input at $0.20 is 20 cents, 1,000,000 output at $1.20 is 120 cents.
    assert cost_in_cents(1_000_000, 0) == Decimal("20.0000")
    assert cost_in_cents(0, 1_000_000) == Decimal("120.0000")
    assert cost_in_cents(1_000_000, 1_000_000) == Decimal("140.0000")


def test_a_real_sized_draft_costs_a_fraction_of_a_cent():
    assert cost_in_cents(900, 200) == Decimal("0.0420")


def test_cost_is_stored_to_the_four_places_the_column_keeps():
    assert cost_in_cents(1, 0).as_tuple().exponent == -4


def fake_client(response) -> SimpleNamespace:
    """Stands in for the OpenAI client, which is the one genuine external edge here."""
    return SimpleNamespace(responses=SimpleNamespace(parse=lambda **_: response))


def completed_response() -> SimpleNamespace:
    return SimpleNamespace(
        status="completed",
        model=MODEL,
        output_parsed=Message(subject="A quiet fortnight", body="...", rationale="..."),
        usage=SimpleNamespace(input_tokens=900, output_tokens=200),
    )


def test_a_finished_message_carries_its_own_token_counts_and_cost():
    generated = generate(fake_client(completed_response()), "rules", "facts", Message)
    assert generated.output.subject == "A quiet fortnight"
    assert (generated.input_tokens, generated.output_tokens) == (900, 200)
    assert generated.cost_usd_cents == Decimal("0.0420")
    assert generated.model == MODEL


def test_a_message_that_stopped_at_the_ceiling_is_discarded():
    truncated = completed_response()
    truncated.status = "incomplete"
    with pytest.raises(ModelFailed) as failed:
        generate(fake_client(truncated), "rules", "facts", Message)
    assert failed.value.state == UNREACHABLE


def test_a_refused_call_raises_the_state_the_row_should_show():
    client = SimpleNamespace(
        responses=SimpleNamespace(
            parse=_raising(status_error(RateLimitError, "insufficient_quota", 429))
        )
    )
    with pytest.raises(ModelFailed) as failed:
        generate(client, "rules", "facts", Message)
    assert failed.value.state == NO_CREDIT


def test_a_refusal_does_not_repeat_the_provider_back_to_the_reader():
    """The provider's error body goes to the log. A reviewer can act on none of it."""
    error = status_error(AuthenticationError, "invalid_api_key", 401)
    client = SimpleNamespace(responses=SimpleNamespace(parse=_raising(error)))
    with pytest.raises(ModelFailed) as failed:
        generate(client, "rules", "facts", Message)
    assert failed.value.detail == REFUSED[UNREACHABLE]
    assert "invalid_api_key" not in failed.value.detail


def _raising(error):
    def parse(**_):
        raise error

    return parse


def test_an_answer_cut_off_mid_json_is_discarded_rather_than_raised():
    """The real shape of truncation for a structured answer.

    `responses.parse` validates before the caller can read `status`, so a message that
    stopped at the token ceiling arrives as a pydantic error rather than as an
    incomplete status. Without this, a reviewer gets a stack trace instead of a row
    that says the message was discarded.
    """
    with pytest.raises(ValidationError) as invalid:
        Message.model_validate_json('{"subject":"A quiet fortnig')

    client = SimpleNamespace(responses=SimpleNamespace(parse=_raising(invalid.value)))
    with pytest.raises(ModelFailed) as failed:
        generate(client, "rules", "facts", Message)
    assert failed.value.state == UNREACHABLE
    assert failed.value.detail == TRUNCATED
