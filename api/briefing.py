"""The deployed briefing endpoint. One site per call."""

from openai import OpenAI

from demogym.briefing_endpoint import respond
from demogym.database import connect
from demogym.json_endpoint import JsonEndpoint


class handler(JsonEndpoint):  # noqa: N801
    """Writes the briefing for one site."""

    def answer(self, token: str | None, payload: object) -> tuple[int, dict]:
        return respond(token, payload, connect, OpenAI)
