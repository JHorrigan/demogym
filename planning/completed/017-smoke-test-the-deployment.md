---
slice: 017
title: Smoke test the deployment
status: complete
depends_on: [014, 016]
decisions: [0001, 0005, 0006]
---

# 017 - Smoke test the deployment

## Goal

One command that says whether the deployed thing is alive and rendering. `0005` and
`standards/nextjs.md` both name this in the same words as the cheapest useful addition and the first
one to make, and neither of them made it.

## Why now

Nothing in this project verifies that the deployed page renders. `make check` typechecks, and a
typecheck is not a render: a page that compiles can still come back blank, and a query that fails on
the deployment fails nowhere else. The whole prototype is shown to people through a link, so a blank
page would be found by whoever it was sent to rather than by the person who sent it.

Every screen exists now, so there is a fixed set of routes to check rather than a moving one.

## In scope

- `scripts/smoke.py`, run by `make smoke`, against the deployed URL by default and against any other
  base URL given as an argument, so the same check covers a local server.
- Per screen: the response code, the synthetic-data strip and the cost readout that the honesty rules
  put on every page, and a marker that proves the page rendered rather than returned a shell.
- Real content on the two screens that read the database, so a page that renders with a failed query
  is not reported as healthy.
- The refusal page, which is the only part of `0006` that a reader ever sees.
- `robots.txt`, which must not contain the token. The Next.js standard states that property and
  nothing checks it.
- The three endpoints, probed with an empty body, which answers before any model call is made. Free,
  and it proves each deployed function is alive rather than only the pages.
- A line in the README, under the running instructions.

## Not in scope

- Adding any of this to `make check`. `0005` keeps the gate free of secrets, credentials and network,
  and CI currently needs no secrets at all, which is worth more than running this automatically.
- A browser. The check is over HTTP, because a headless browser in the loop is a dependency and a
  second thing to keep working, and the failure this exists to catch shows up in the response body.
- Any assertion about numbers being correct. That is what the slices that built each screen did. This
  says the page rendered, not that it is right.
- Writing anything. No draft, no briefing, no model call, no row.
- Unit tests for the script. It fetches and looks for text, and there is no rule in it to get wrong.

## Done when

- `make smoke` passes against the deployment, and every check it made is named in its output rather
  than summarised as a count.
- It fails, loudly and specifically, when something is actually wrong. Proved by breaking each class of
  thing it checks and watching it fail: a wrong token, a route that does not exist, and a marker that
  is not on the page.
- Its exit code is non-zero on any failure, so it can be run by something other than a person.
- It passes against a local server as well, with the base URL given as an argument.
- The README documents it.
- `make check` still passes and still needs no network or credentials.

## Evidence

**Twenty-eight checks against the deployment**, each named rather than counted:

```
$ make smoke
https://demogym-ten.vercel.app

  ok    estate answers 200                      ok    refusal answers 401
  ok    estate carries 'Synthetic data'         ok    refusal carries 'Synthetic data'
  ok    estate carries 'Inference cost'         ok    refusal carries 'This link is not valid'
  ok    estate carries 'Estate'                 ok    robots.txt answers 200
  ok    estate carries 'Northgate'              ok    robots.txt does not name the token
  ok    estate carries 'Meadowbank'             ok    draft endpoint is alive
  ok    queue answers 200                       ok    draft endpoint checks the token
  ok    queue carries 'Synthetic data'          ok    briefing endpoint is alive
  ok    queue carries 'Inference cost'          ok    briefing endpoint checks the token
  ok    queue carries 'At-risk queue'           ok    decide endpoint is alive
  ok    queue carries 'M00020'                  ok    decide endpoint checks the token
  ok    queue carries 'Northgate'
  ok    real data answers 200
  ok    real data carries 'Synthetic data'
  ok    real data carries 'Inference cost'
  ok    real data carries 'Running this on real data'
  ok    real data carries 'id="regulatory-position"'

everything passed
EXIT=0
```

`Northgate`, `Meadowbank` and `M00020` are read out of the database at the start of the run rather than
written into the script, so a page that renders with a failed query fails rather than passing.

**Each class of failure, broken and watched.**

A token the deployment does not accept. Every page and every endpoint notices, and the refusal page and
its strip still pass, which is correct: that page is what a wrong token is supposed to produce.

```
FAIL  estate answers 200  answered 401          FAIL  real data answers 200  answered 401
FAIL  estate carries 'Inference cost'           FAIL  draft endpoint is alive  {"error": "forbidden"...
FAIL  estate carries 'Northgate'                FAIL  briefing endpoint is alive  {"error": "forbidden"...
FAIL  queue answers 200  answered 401           FAIL  decide endpoint is alive  {"error": "forbidden"...
17 failed
exit 1
```

A screen that is no longer deployed:

```
FAIL  real data answers 200  answered 404
FAIL  real data carries 'Synthetic data'
FAIL  real data carries 'Inference cost'
FAIL  real data carries 'Running this on real data'
FAIL  real data carries 'id="regulatory-position"'
5 failed
```

A marker that is not on the page, which is the shape a blank page would take:

```
FAIL  real data carries 'a phrase nobody wrote'
1 failed
```

Restored, everything passes again. The script exits 1 on any failure and `make` surfaces that as 2.

**Against a local server**, with the base URL as an argument:

```
$ uv run --env-file .env --env-file .env.local python scripts/smoke.py http://localhost:3000
28 checks, everything passed, EXIT=0
```

That run also re-proves 015: the token the pages are served under in development is the one the local
endpoints accept, which was the thing that was broken before that slice.

**The gate is unchanged and still needs nothing.** `make check` is `lint test typecheck lint-web`, and
none of them reads an environment file:

```
$ grep -n "env-file" Makefile
28:  uv run --env-file .env --env-file .env.local python scripts/serve_api.py   # make api
32:  uv run --env-file .env demogym migrate                                      # make migrate
37:  uv run --env-file .env python scripts/smoke.py                              # make smoke
```

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      184 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**Nothing was written.** The endpoint probes send an empty body, which is refused on validation before
any model call, so the run costs nothing and leaves no row.

## Outcome

`make smoke` fetches every screen, the refusal page, `robots.txt` and the three endpoints, and says which
of twenty-eight checks passed. It runs against the deployment by default and against any base URL given
as an argument. `0005` and `standards/nextjs.md` both named this as the first thing to add and neither of
them added it; it is added.

Four decisions the slice left open, settled here.

**It stays out of `make check`.** The gate needs no database, no key and no network, and CI needs no
secrets at all. That is worth more than running this automatically, and `0005` says so. The cost is that
somebody has to remember to run it after a deploy, which the README now tells them to do.

**It checks content read from the database, not just that a page answered 200.** A page that renders its
shell with a failed query answers 200 and looks healthy. The site names and the account number come out
of the database at the start of the run, so the check moves when the data does and cannot quietly pass
against an empty screen.

**It uses HTTP rather than a browser.** A headless browser would catch things this cannot, a page that
renders but throws on hydration among them. It is also a dependency and a second thing to keep working,
and the failure this exists to catch is visible in the response body. The screens that needed a browser
were measured in one when they were built.

**It covers the endpoints as well as the pages.** The gap `0005` names is the frontend, but the probe is
an empty body, which is refused on validation before any model call is made, so proving each deployed
function is alive costs nothing. A deployment where the pages render and the functions are gone is a
deployment that looks fine and cannot draft.

Two things came out different from the plan.

**The wrong-token run is not a total failure, and should not be.** Seventeen checks fail and three pass:
the refusal page answers 401, carries its strip, and says the link is not valid, which is exactly what a
wrong token should produce. Watching that run was what showed the refusal checks were asserting something
real rather than passing by accident.

**It doubles as a check on 015.** Run against a local server it only passes if the token the pages are
served under is the one the local endpoints accept, which is the thing that was broken until 015 fixed
it. That was not the intention and it is worth keeping.

What this does not do. It says the deployment renders and its functions answer. It says nothing about
whether any number on a screen is right, which is what the slice that built each screen established, and
nothing about behaviour that needs a browser.
