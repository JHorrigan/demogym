"""The HTTP glue every deployed endpoint shares.

Vercel's Python runtime wants a class named `handler` in each file under `api/`, and
what those handlers do is identical: read a JSON body, pass it and the link token to
the package, write a JSON answer. Only `answer` differs, so only `answer` is written
twice.
"""

import json
from http.server import BaseHTTPRequestHandler

TOKEN_HEADER = "x-demogym-token"


class JsonEndpoint(BaseHTTPRequestHandler):
    """Reads a JSON request and writes a JSON response. Subclasses supply `answer`."""

    def answer(self, token: str | None, payload: object) -> tuple[int, dict]:
        """The status and body this endpoint replies with."""
        raise NotImplementedError

    def do_POST(self) -> None:  # noqa: N802
        size = int(self.headers.get("content-length") or 0)
        status, body = self.answer(self.headers.get(TOKEN_HEADER), _payload(self.rfile.read(size)))
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
