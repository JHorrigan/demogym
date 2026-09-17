"""Runs the deployed handlers on a local port, so the pages can call them in development.

`next dev` serves the pages and nothing else. On Vercel each file under `api/` is its
own function; here they are one process routing by path, and `next.config.ts` proxies
`/api` to this port. It loads the same files Vercel loads, so there is one handler per
endpoint rather than a real one and a development one.

Threaded, because Vercel runs each request in its own invocation. A single-threaded
server would serialise the four calls Draft all keeps in flight and make a sweep look
four times slower than it is.

    make api
"""

import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

from demogym.json_endpoint import JsonEndpoint

PORT = 5328

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from briefing import handler as briefing  # noqa: E402
from decide import handler as decide  # noqa: E402
from draft import handler as draft  # noqa: E402

ROUTES = {"/api/draft": draft, "/api/decide": decide, "/api/briefing": briefing}


class router(JsonEndpoint):  # noqa: N801
    """Answers each path with the handler Vercel would give its own function."""

    def answer(self, token: str | None, payload: object) -> tuple[int, dict]:
        endpoint = ROUTES.get(self.path)
        if endpoint is None:
            return 404, {"error": "not found", "message": f"nothing is served at {self.path}"}
        return endpoint.answer(self, token, payload)


if __name__ == "__main__":
    for path in ROUTES:
        print(f"http://127.0.0.1:{PORT}{path}")
    ThreadingHTTPServer(("127.0.0.1", PORT), router).serve_forever()
