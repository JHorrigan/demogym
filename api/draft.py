"""The deployed drafting endpoint. One member per call.

Vercel's Python runtime treats each file under `api/` as a function and looks for a
class named `handler`. Everything this does beyond reading and writing HTTP lives in
the package, which is the same package the local tooling imports. See 0004.
"""

from openai import OpenAI

from demogym.database import connect
from demogym.draft_endpoint import respond
from demogym.json_endpoint import JsonEndpoint


class handler(JsonEndpoint):  # noqa: N801
    """Drafts the message to one member at risk."""

    def answer(self, token: str | None, payload: object) -> tuple[int, dict]:
        return respond(token, payload, connect, OpenAI)
