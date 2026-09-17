"""What a reviewer decided about a drafted message.

Three actions, and one of them carries text. That text is the only free input this
project accepts anywhere, and it never reaches a model: it is stored beside the
draft, shown against it, and nothing else happens to it.
"""

from dataclasses import dataclass

APPROVED = "approved"
EDITED = "edited"
REJECTED = "rejected"

ACTIONS = (APPROVED, EDITED, REJECTED)

# Long enough for any rewrite of a hundred-and-twenty-word message, and a bound
# rather than no bound, because this arrives from a public request.
MAXIMUM_EDIT = 4000


@dataclass(frozen=True)
class Decision:
    """One decision about one member's latest draft."""

    member_id: int
    action: str
    edited_body: str | None


def parse(payload: object) -> Decision:
    """Reads a request body, or raises ValueError naming the field that is wrong."""
    if not isinstance(payload, dict):
        raise ValueError("the request body must be a JSON object")

    member_id = payload.get("member_id")
    if not isinstance(member_id, int) or isinstance(member_id, bool) or member_id <= 0:
        raise ValueError("member_id must be a positive integer")

    action = payload.get("decision")
    if not isinstance(action, str) or action not in ACTIONS:
        raise ValueError(f"decision must be one of: {', '.join(ACTIONS)}")

    return Decision(
        member_id=member_id, action=action, edited_body=_edit(action, payload.get("edited_body"))
    )


def _edit(action: str, edited_body: object) -> str | None:
    """The edit, which belongs to exactly one of the three actions."""
    if action != EDITED:
        if edited_body is not None:
            raise ValueError(f"edited_body belongs to an edit, not to {action}")
        return None

    if not isinstance(edited_body, str) or not edited_body.strip():
        raise ValueError("an edit needs an edited_body")
    if len(edited_body) > MAXIMUM_EDIT:
        raise ValueError(f"edited_body is longer than {MAXIMUM_EDIT} characters")
    return edited_body
