"""What the briefing endpoint answers, for any request that reaches it.

The same shape as the drafting endpoint: one site per call, under the same daily cap,
returning the same three failure states. A briefing is a model call like any other and
is bounded like one.
"""

import os
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg
from openai import OpenAI

from demogym.briefing_facts import for_site
from demogym.briefing_prompt import Briefing, body, system, user
from demogym.briefings import store
from demogym.cap import DAILY_LIMIT, reserve
from demogym.drafts import LOCAL
from demogym.model import NO_CREDIT, UNREACHABLE, ModelFailed, generate

FORBIDDEN = "forbidden"
BAD_REQUEST = "bad request"
UNKNOWN_SITE = "unknown site"

STATUS = {
    FORBIDDEN: 401,
    BAD_REQUEST: 400,
    UNKNOWN_SITE: 404,
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
    """Writes one site's briefing, or says why it did not."""
    expected = os.environ["DEMOGYM_ACCESS_TOKEN"]
    if token != expected:
        return _refuse(FORBIDDEN, "This endpoint is reached with the link token.")

    if not isinstance(payload, dict):
        return _refuse(BAD_REQUEST, "the request body must be a JSON object")
    site_id = payload.get("site_id")
    if not isinstance(site_id, int) or isinstance(site_id, bool) or site_id <= 0:
        return _refuse(BAD_REQUEST, "site_id must be a positive integer")

    today = datetime.now(ZoneInfo(LOCAL)).date()

    with connect() as connection:
        facts = for_site(connection, site_id)
        if facts is None:
            return _refuse(UNKNOWN_SITE, f"There is no site {site_id}.")

        if reserve(connection, today) is None:
            return _refuse(
                DAILY_LIMIT, "The cap on model calls for today is spent. It resets tomorrow."
            )
        connection.commit()

        try:
            generated = generate(make_client(), system(), user(facts), Briefing)
        except ModelFailed as failed:
            return _refuse(failed.state, failed.detail)

        written = body(generated.output)
        stored = store(connection, site_id, today, written, generated)

    return 200, {
        "site_id": site_id,
        "site": facts.name,
        "generated_on": today.isoformat(),
        "body": written,
        "model": generated.model,
        "input_tokens": stored.input_tokens,
        "output_tokens": stored.output_tokens,
        "cost_usd_cents": stored.cost_usd_cents,
    }


def _refuse(state: str, message: str) -> tuple[int, dict]:
    """The same error shape the other two endpoints use."""
    return STATUS[state], {"error": state, "message": message}
