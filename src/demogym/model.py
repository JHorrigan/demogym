"""The one model call this project makes, and what it costs when it works.

The model ID is pinned, so a run is reproducible and a cost figure means something.
Token counts come back on the response and are stored as they arrived. Nothing here
estimates. See 0007.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

from openai import APIStatusError, OpenAI, OpenAIError
from pydantic import BaseModel

MODEL = "gpt-5.6-luna"

# Published prices per million tokens, from 0007.
INPUT_USD_PER_MILLION = Decimal("0.20")
OUTPUT_USD_PER_MILLION = Decimal("1.20")

# A standard draft is about 120 words. This is a long way above that, so hitting it
# means something went wrong rather than that the message was ambitious.
MAX_OUTPUT_TOKENS = 2000

UNREACHABLE = "unreachable"
NO_CREDIT = "no credit"

REFUSED = {
    UNREACHABLE: "The model could not be reached. Worth trying again.",
    NO_CREDIT: "The account has no credit left. Trying again will not help.",
}

TRUNCATED = "The message stopped before it was finished and was discarded. Worth another try."

log = logging.getLogger(__name__)

# OpenAI returns 429 for both rate limiting and an exhausted balance, and retrying a
# billing refusal will not restore access. The status code cannot tell them apart, so
# the error body does.
BILLING_CODES = frozenset({"insufficient_quota", "billing_hard_limit_reached"})


class Message(BaseModel):
    """What the model returns: the message, and why it was written that way."""

    subject: str
    body: str
    rationale: str


@dataclass(frozen=True)
class Generated:
    """One message and what the call that produced it cost."""

    message: Message
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd_cents: Decimal


class ModelFailed(Exception):
    """A call that produced no message, carrying the state the row should show."""

    def __init__(self, state: str, detail: str) -> None:
        super().__init__(detail)
        self.state = state
        self.detail = detail


def generate(client: OpenAI, instructions: str, facts: str) -> Generated:
    """Calls the pinned model once, or raises ModelFailed saying which state it is.

    No retry is added here. The installed client already retries connection errors,
    408, 409, 429 and 5xx twice with backoff, honours `Retry-After` up to two minutes,
    and obeys an `x-should-retry: false` header. A second retry budget on top of that
    one would multiply rather than help.
    """
    try:
        response = client.responses.parse(
            model=MODEL,
            instructions=instructions,
            input=facts,
            text_format=Message,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
    except OpenAIError as error:
        # The provider's own words go to the log, where whoever ran this can read
        # them. They do not go in the response, because an upstream error body is
        # the provider's business and the reviewer can act on none of it.
        log.warning("the model refused a call: %s", error)
        state = classify(error)
        raise ModelFailed(state, REFUSED[state]) from error

    if response.status == "incomplete":
        raise ModelFailed(UNREACHABLE, TRUNCATED)

    usage = response.usage
    return Generated(
        message=response.output_parsed,
        model=response.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd_cents=cost_in_cents(usage.input_tokens, usage.output_tokens),
    )


def classify(error: OpenAIError) -> str:
    """Which of the two model failure states a raised error is.

    A billing refusal is the only one worth telling apart, because it is the only one
    where trying again is pointless and the interface should say so.
    """
    if isinstance(error, APIStatusError) and error.code in BILLING_CODES:
        return NO_CREDIT
    return UNREACHABLE


def cost_in_cents(input_tokens: int, output_tokens: int) -> Decimal:
    """What a call cost in US cents, to the four places the column stores."""
    usd = (input_tokens * INPUT_USD_PER_MILLION + output_tokens * OUTPUT_USD_PER_MILLION) / Decimal(
        1_000_000
    )
    return (usd * 100).quantize(Decimal("0.0001"))
