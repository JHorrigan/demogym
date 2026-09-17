"""What the decision endpoint answers, for any request that reaches it.

No model, no cap. A decision costs nothing to record, and the only thing it can
spend is the one decision a member gets.
"""

import os
from collections.abc import Callable

import psycopg

from demogym.decisions import EDITED, parse
from demogym.drafts import latest_draft, record

FORBIDDEN = "forbidden"
BAD_REQUEST = "bad request"
NOTHING_DRAFTED = "nothing drafted"
ALREADY_DECIDED = "already decided"
EDIT_UNCHANGED = "edit unchanged"

STATUS = {
    FORBIDDEN: 401,
    BAD_REQUEST: 400,
    NOTHING_DRAFTED: 404,
    ALREADY_DECIDED: 409,
    EDIT_UNCHANGED: 409,
}


def respond(
    token: str | None,
    payload: object,
    connect: Callable[[], psycopg.Connection],
) -> tuple[int, dict]:
    """Records one decision, or says why it did not."""
    expected = os.environ["DEMOGYM_ACCESS_TOKEN"]
    if token != expected:
        return _refuse(FORBIDDEN, "This endpoint is reached with the link token.")

    try:
        decision = parse(payload)
    except ValueError as invalid:
        return _refuse(BAD_REQUEST, str(invalid))

    with connect() as connection:
        latest = latest_draft(connection, decision.member_id)
        if latest is None:
            return _refuse(
                NOTHING_DRAFTED,
                f"Member {decision.member_id} has no draft at the most recent scoring date.",
            )
        if latest.decided:
            return _refuse(
                ALREADY_DECIDED,
                f"Member {decision.member_id} has already been decided. A decision is final.",
            )
        if decision.action == EDITED and decision.edited_body == latest.body:
            return _refuse(
                EDIT_UNCHANGED,
                "The edit matches what the model wrote, so it is an approval rather than an edit.",
            )

        decided_at = record(
            connection, decision.member_id, latest, decision.action, decision.edited_body
        )

    return 200, {
        "member_id": decision.member_id,
        "scored_on": latest.scored_on.isoformat(),
        "attempt": latest.attempt,
        "decision": decision.action,
        "edited_body": decision.edited_body,
        "decided_at": decided_at.isoformat(),
    }


def _refuse(state: str, message: str) -> tuple[int, dict]:
    """The same error shape the drafting endpoint uses."""
    return STATUS[state], {"error": state, "message": message}
