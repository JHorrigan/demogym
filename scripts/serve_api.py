"""Runs the deployed handler on a local port, so the pages can call it in development.

`next dev` serves the pages and nothing else. On Vercel the Python function is part of
the same deployment; here it is a second process, and `next.config.ts` proxies `/api`
to this port. It loads the same file Vercel loads, so there is one handler rather than
a real one and a development one.

Threaded, because Vercel runs each request in its own invocation. A single-threaded
server would serialise the four calls Draft all keeps in flight and make a sweep look
four times slower than it is.

    make api
"""

import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

PORT = 5328

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from draft import handler  # noqa: E402

if __name__ == "__main__":
    print(f"The drafting endpoint is on http://127.0.0.1:{PORT}/api/draft")
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()
