"""The one model call this project makes, and what it costs when it works.

The model ID is pinned, so a run is reproducible and a cost figure means something.
Token counts come back on the response and are stored as they arrived. Nothing here
estimates. See 0007.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

from openai import APIStatusError, OpenAI, OpenAIError
from pydantic import BaseModel, ValidationError

MODEL = "gpt-5.6-luna"

# Published prices per million tokens, input then output, from 0007. The incumbent and
# the two candidates 016 measures it against. A model with no price here cannot be
# costed, and a cost this project calls measured is never estimated.
PRICES = {
    "gpt-5-nano": (Decimal("0.05"), Decimal("0.40")),
    "gpt-5.6-luna": (Decimal("0.20"), Decimal("1.20")),
    "gpt-5-mini": (Decimal("0.25"), Decimal("2.00")),
}

INPUT_USD_PER_MILLION, OUTPUT_USD_PER_MILLION = PRICES[MODEL]

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


@dataclass(frozen=True)
class Generated[T: BaseModel]:
    """What one call produced and what it cost.

    The shape of `output` belongs to the feature that asked for it, so a draft and a
    briefing share the call, the pricing and the failure states without sharing a
    response type.
    """

    output: T
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


def generate[T: BaseModel](
    client: OpenAI,
    instructions: str,
    facts: str,
    shape: type[T],
    model: str = MODEL,
    ceiling: int = MAX_OUTPUT_TOKENS,
) -> Generated[T]:
    """Calls the pinned model once, or raises ModelFailed saying which state it is.

    No retry is added here. The installed client already retries connection errors,
    408, 409, 429 and 5xx twice with backoff, honours `Retry-After` up to two minutes,
    and obeys an `x-should-retry: false` header. A second retry budget on top of that
    one would multiply rather than help.
    """
    try:
        response = client.responses.parse(
            model=model,
            instructions=instructions,
            input=facts,
            text_format=shape,
            max_output_tokens=ceiling,
        )
    except OpenAIError as error:
        # The provider's own words go to the log, where whoever ran this can read
        # them. They do not go in the response, because an upstream error body is
        # the provider's business and the reviewer can act on none of it.
        log.warning("the model refused a call: %s", error)
        state = classify(error)
        raise ModelFailed(state, REFUSED[state]) from error
    except ValidationError as unparsable:
        # A structured answer cut off at the ceiling is parsed before its status can
        # be read, so truncation arrives as a parse failure and never reaches the
        # check below. The SDK documents this: invalid JSON still raises. 016 found it
        # by running a model that spent its whole budget reasoning.
        log.warning("the model returned an answer that would not parse: %s", unparsable)
        raise ModelFailed(UNREACHABLE, TRUNCATED) from unparsable

    if response.status == "incomplete":
        raise ModelFailed(UNREACHABLE, TRUNCATED)

    usage = response.usage
    return Generated(
        output=response.output_parsed,
        model=response.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd_cents=cost_in_cents(usage.input_tokens, usage.output_tokens, model),
    )


def classify(error: OpenAIError) -> str:
    """Which of the two model failure states a raised error is.

    A billing refusal is the only one worth telling apart, because it is the only one
    where trying again is pointless and the interface should say so.
    """
    if isinstance(error, APIStatusError) and error.code in BILLING_CODES:
        return NO_CREDIT
    return UNREACHABLE


def cost_in_cents(input_tokens: int, output_tokens: int, model: str = MODEL) -> Decimal:
    """What a call cost in US cents, to the four places the column stores.

    Priced against the model that was asked for rather than the snapshot that answered,
    so the figure matches a published price a reader can look up.
    """
    price_in, price_out = PRICES[model]
    usd = (input_tokens * price_in + output_tokens * price_out) / Decimal(1_000_000)
    return (usd * 100).quantize(Decimal("0.0001"))
