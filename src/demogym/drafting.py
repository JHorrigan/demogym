"""What the reviewer asked for, and whether the request is one the endpoint accepts.

Three dropdowns and a member. Nothing here is free text, so the set of prompts this
system can produce is finite and every one of them is a combination somebody chose
from a list. See 0008.
"""

from dataclasses import dataclass

TONES = ("warm", "direct", "encouraging")
LENGTHS = ("short", "standard")
OFFERS = ("none", "free class", "guest pass", "personal training session")

# One redraft per member. The count comes from the stored rows, so a call that fails
# never spends one.
MAXIMUM_ATTEMPTS = 2

WORDS = {"short": 40, "standard": 120}


@dataclass(frozen=True)
class Controls:
    """The three settings a reviewer chose before the call."""

    tone: str
    length: str
    offer: str


@dataclass(frozen=True)
class Request:
    """One accepted request: which member, and on what terms."""

    member_id: int
    controls: Controls


def parse(payload: object) -> Request:
    """Reads a request body, or raises ValueError naming the field that is wrong.

    This is the boundary, so it is the one place that does not trust its input.
    """
    if not isinstance(payload, dict):
        raise ValueError("the request body must be a JSON object")

    return Request(
        member_id=_member_id(payload.get("member_id")),
        controls=Controls(
            tone=_option("tone", payload.get("tone"), TONES),
            length=_option("length", payload.get("length"), LENGTHS),
            offer=_option("offer", payload.get("offer"), OFFERS),
        ),
    )


def _member_id(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("member_id must be a positive integer")
    return value


def _option(field: str, value: object, allowed: tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{field} must be one of: {', '.join(allowed)}")
    return value
