"""The deployed drafting endpoint. One member per call.

Vercel's Python runtime treats each file under `api/` as a function and looks for a
class named `handler`. Everything this does beyond reading and writing HTTP lives in
the package, which is the same package the local tooling imports. See 0004.
"""

import json
from http.server import BaseHTTPRequestHandler

from openai import OpenAI

from demogym.database import connect
from demogym.draft_endpoint import TOKEN_HEADER, respond


class handler(BaseHTTPRequestHandler):  # noqa: N801
    """Drafts the message to one member at risk."""

    def do_POST(self) -> None:  # noqa: N802
        size = int(self.headers.get("content-length") or 0)
        status, body = respond(
            self.headers.get(TOKEN_HEADER), _payload(self.rfile.read(size)), connect, OpenAI
        )
        self._reply(status, body)

    def _reply(self, status: int, body: dict) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def _payload(raw: bytes) -> object:
    """A body that is not JSON is a bad request rather than a crash."""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
