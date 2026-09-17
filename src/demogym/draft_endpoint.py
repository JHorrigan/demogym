"""What the drafting endpoint answers, for any request that reaches it.

A status and a body, and nothing about HTTP beyond that, so the same decisions can be
run in a test without a server. The connection and the model client arrive as
arguments, which is what lets a refused request prove it touched neither.
"""

import os
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg
from openai import OpenAI

from demogym.cap import DAILY_LIMIT, reserve
from demogym.drafting import MAXIMUM_ATTEMPTS, parse
from demogym.drafts import LOCAL, candidate, store
from demogym.model import NO_CREDIT, UNREACHABLE, ModelFailed, generate
from demogym.prompt import system, user

TOKEN_HEADER = "x-demogym-token"

FORBIDDEN = "forbidden"
BAD_REQUEST = "bad request"
UNKNOWN_MEMBER = "unknown member"
NOT_AT_RISK = "not at risk"
NO_DRAFTS_LEFT = "no drafts left"

STATUS = {
    FORBIDDEN: 401,
    BAD_REQUEST: 400,
    UNKNOWN_MEMBER: 404,
    NOT_AT_RISK: 409,
    NO_DRAFTS_LEFT: 409,
    DAILY_LIMIT: 429,
    NO_CREDIT: 402,
    UNREACHABLE: 503,
}


def respond(
    token: str | None,
    payload: object,
    connect: Callable[[], psycopg.Connection],
    make_client: Callable[[], OpenAI],
) -> tuple[int, dict]:
    """Drafts one member, or says why it did not."""
    expected = os.environ["DEMOGYM_ACCESS_TOKEN"]
    if token != expected:
        return _refuse(FORBIDDEN, "This endpoint is reached with the link token.")

    try:
        request = parse(payload)
    except ValueError as invalid:
        return _refuse(BAD_REQUEST, str(invalid))

    with connect() as connection:
        found = candidate(connection, request.member_id)
        if found is None:
            return _refuse(
                UNKNOWN_MEMBER,
                f"No member {request.member_id} was scored at the most recent scoring date.",
            )
        if found.facts.band != "high":
            return _refuse(
                NOT_AT_RISK,
                f"Member {request.member_id} is {found.facts.band} band. "
                "Only the High band is drafted for.",
            )
        if found.attempts >= MAXIMUM_ATTEMPTS:
            return _refuse(
                NO_DRAFTS_LEFT,
                f"Member {request.member_id} has had a draft and a redraft.",
            )

        if reserve(connection, datetime.now(ZoneInfo(LOCAL)).date()) is None:
            return _refuse(
                DAILY_LIMIT,
                "The cap on model calls for today is spent. It resets tomorrow.",
            )
        # The call counts against the day before it is made, so a model that fails
        # every time is still a bounded amount of spending.
        connection.commit()

        try:
            generated = generate(
                make_client(),
                system(),
                user(found.facts, request.controls, found.scored_on),
            )
        except ModelFailed as failed:
            return _refuse(failed.state, failed.detail)

        attempt = found.attempts + 1
        store(connection, request.member_id, found.scored_on, attempt, request.controls, generated)

    return 200, {
        "member_id": request.member_id,
        "scored_on": found.scored_on.isoformat(),
        "attempt": attempt,
        "tone": request.controls.tone,
        "length": request.controls.length,
        "offer": request.controls.offer,
        "subject": generated.message.subject,
        "body": generated.message.body,
        "rationale": generated.message.rationale,
        "model": generated.model,
        "input_tokens": generated.input_tokens,
        "output_tokens": generated.output_tokens,
        "cost_usd_cents": float(generated.cost_usd_cents),
    }


def _refuse(state: str, message: str) -> tuple[int, dict]:
    """The one error shape, so a caller reads the state rather than the status code."""
    return STATUS[state], {"error": state, "message": message}
