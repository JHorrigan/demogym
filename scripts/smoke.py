"""Checks that the deployed application is alive and rendering.

`make check` typechecks, and a typecheck is not a render: a page that compiles can
still come back blank, and a query that fails on the deployment fails nowhere else.
This is the check 0005 and `standards/nextjs.md` both name as the first one to add.

It reads the database only to find out what should be on the screens. It writes
nothing, and the endpoint probes send an empty body, which is refused before any model
call is made.

    make smoke
    uv run --env-file .env python scripts/smoke.py http://localhost:3000
"""

import json
import os
import sys
import urllib.error
import urllib.request

from demogym.database import connect

DEPLOYED = "https://demogym-ten.vercel.app"

# On every page, because the honesty rules put them there and a screen without them is
# a screen that should not have shipped.
EVERYWHERE = ["Synthetic data", "Inference cost"]

ENDPOINTS = {
    "draft": "member_id must be a positive integer",
    "briefing": "site_id must be a positive integer",
    "decide": "member_id must be a positive integer",
}


def expected():
    """What should be on the screens, read from the database rather than assumed."""
    with connect() as connection:
        sites = [row[0] for row in connection.execute("select name from sites order by id")]
        banded = connection.execute(
            "select account_number from members join risk_scores on members.id = member_id "
            "where band = 'high' and scored_on = (select max(scored_on) from risk_scores) "
            "order by account_number limit 1"
        ).fetchone()
    return sites, banded[0]


def fetch(url, token=None, body=None):
    """One request, returning the status and the text, with no exception for a refusal."""
    data = json.dumps(body).encode() if body is not None else None
    headers = {"content-type": "application/json"} if data else {}
    if token:
        headers["x-demogym-token"] = token
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as refused:
        return refused.code, refused.read().decode()


class Checks:
    """Every check, its result, and whether anything failed."""

    def __init__(self):
        self.failures = 0

    def that(self, what, ok, detail=""):
        print(f"  {'ok  ' if ok else 'FAIL'}  {what}{'  ' + detail if detail and not ok else ''}")
        self.failures += not ok

    def page(self, name, url, status, markers):
        code, text = fetch(url)
        self.that(f"{name} answers {status}", code == status, f"answered {code}")
        for marker in markers:
            self.that(f"{name} carries {marker!r}", marker in text)


def main(base):
    token = os.environ["DEMOGYM_ACCESS_TOKEN"]
    sites, account = expected()
    checks = Checks()

    print(f"{base}\n")
    checks.page("estate", f"{base}/{token}", 200, [*EVERYWHERE, "Estate", sites[0], sites[-1]])
    checks.page(
        "queue", f"{base}/{token}/queue", 200, [*EVERYWHERE, "At-risk queue", account, sites[0]]
    )
    checks.page(
        "real data",
        f"{base}/{token}/real-data",
        200,
        [*EVERYWHERE, "Running this on real data", 'id="regulatory-position"'],
    )
    checks.page("refusal", f"{base}/nope", 401, ["Synthetic data", "This link is not valid"])

    code, robots = fetch(f"{base}/robots.txt")
    checks.that("robots.txt answers 200", code == 200, f"answered {code}")
    checks.that("robots.txt does not name the token", token not in robots)

    for endpoint, message in ENDPOINTS.items():
        code, text = fetch(f"{base}/api/{endpoint}", token, {})
        checks.that(f"{endpoint} endpoint is alive", code == 400 and message in text, text[:70])
        code, _ = fetch(f"{base}/api/{endpoint}", "not-the-token", {})
        checks.that(f"{endpoint} endpoint checks the token", code == 401, f"answered {code}")

    print(f"\n{checks.failures} failed" if checks.failures else "\neverything passed")
    return 1 if checks.failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEPLOYED))
