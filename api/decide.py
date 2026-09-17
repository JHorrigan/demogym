"""The deployed decision endpoint. One member per call.

No model is called here, so there is no client to build and nothing to cap. The only
thing a decision can spend is the one decision a member gets.
"""

from demogym.database import connect
from demogym.decide_endpoint import respond
from demogym.json_endpoint import JsonEndpoint


class handler(JsonEndpoint):  # noqa: N801
    """Records what a reviewer decided about one member's draft."""

    def answer(self, token: str | None, payload: object) -> tuple[int, dict]:
        return respond(token, payload, connect)
