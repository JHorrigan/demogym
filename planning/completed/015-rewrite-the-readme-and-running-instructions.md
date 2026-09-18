---
slice: 015
title: Rewrite the README and write the running instructions
status: complete
depends_on: [014]
decisions: [0001, 0002, 0003, 0006, 0007]
---

# 015 - Rewrite the README and write the running instructions

## Goal

A front door that says what this is and what it is not, and instructions someone else can follow to
run the whole thing on their own database and their own API key.

## Why now

The README still says the specification is being written. Everything is built, and the first file
anyone opens describes a project that no longer exists.

It comes after 014 because the front door points at the running-on-real-data page for the limitations
rather than repeating them, and there was no sense writing the pointer before the page.

## In scope

- Rewrite `README.md`. What this is, the synthetic-data statement before anything else, the two model
  features and where the boundary between arithmetic and the model sits, the three screens, the
  stack, and where the specification and the slices live.
- The running instructions: what has to be installed, the three environment variables, and the
  commands in order from a clean clone to a working application with data in it.
- The local development path, which is two processes rather than one, and why.
- Fix the token mismatch those instructions expose. `next dev` reads `.env.local` over `.env` and
  `make api` reads `.env` alone, so the token that opens a page is refused by the endpoint and
  nothing can be drafted locally. Proved before this slice was written.

## Not in scope

- Any change to the application, the scoring, the prompts or the screens.
- Repeating the limitations in the README. They are on the running-on-real-data page and in the
  specification, and a third copy is a third thing to keep true.
- Instructions for deploying someone else's copy to Vercel. The README says what the deployment needs
  set and stops there, because the rest is Vercel's documentation and it changes.
- Any change to the specification.

## Done when

- `README.md` says all data is synthetic before it says anything else, and names no real operator.
- Every command in the instructions has been run and its output recorded, including from a clean
  clone into an empty directory. `seed` and `score` are the exception: they replace the live estate,
  and their output is recorded in 004 and 006 rather than produced again here.
- The local path works end to end: the same token opens a page and is accepted by the endpoint, and
  a draft is produced from the browser against `make api`.
- Every path the README refers to exists.
- The writing rules hold: no dashes standing in for punctuation, no stock phrasing, British spelling,
  no emoji.
- `make check` passes, on the working copy and on the clean clone.

## Evidence

**The token mismatch, proved before it was fixed.** `next dev` and `make api` were started as the
Makefile and the README describe. The token that opens a page was refused by the endpoint:

```
token from .env.local   page gate 200    draft endpoint 401  This endpoint is reached with the link token.
token from .env         page gate 401    draft endpoint 400  member_id must be a positive integer
```

Neither token worked for both. The 400 on the second line is the endpoint accepting the token and then
rejecting an empty body, which is how the probe tells "past the gate" from "refused at it" without
making a model call.

The cause is that the two files hold different values for the same variable:

```
.env         DEMOGYM_ACCESS_TOKEN set(32)  DATABASE_URL set(149)  OPENAI_API_KEY set(164)
.env.local   DEMOGYM_ACCESS_TOKEN set(28)  DATABASE_URL absent    OPENAI_API_KEY absent
```

`.env.local` exists to give development a different token from the deployment's, and Next.js reads it
over `.env`. `make api` read `.env` alone, so the two processes disagreed by construction. It now
passes both files in the same order Next.js reads them, and uv gives the later file precedence:

```
uv run --env-file .env --env-file .env.local  ->  token length 28
uv run --env-file .env.local --env-file .env  ->  token length 32
```

Afterwards, one token opens the page and every endpoint accepts it:

```
page gate: 200
draft     400 {"error": "bad request", "message": "member_id must be a positive integer"}
briefing  400 {"error": "bad request", "message": "site_id must be a positive integer"}
decide    400 {"error": "bad request", "message": "member_id must be a positive integer"}
```

The first attempt at this fix appeared not to work. The old server was still bound to 5328 and the new
one had exited with `OSError: [Errno 98] Address already in use`, so the probe was still answered by the
process loading the old environment. The fix was right and the measurement was reading a stale process.

**The local path, end to end, from a browser.** The queue opened under the development token, a Draft
button was clicked, and the request went through `next dev` to `make api` to the model and back:

```
127.0.0.1 - - [18/Sep/2026 09:03:47] "POST /api/draft HTTP/1.1" 200 -

member 1820  attempt 1  gpt-5.6-luna  in 540  out 642  cost 0.0878 cents
subject: We've missed seeing you at Northgate
body:    Hello, You're usually in with us several times a week, and Friday mornings have often bee...
```

The cost divides out by hand: `540 x 0.20 + 642 x 1.20` per million is `0.0008784` dollars, which is
`0.0878` cents. The row was deleted afterwards, so the deployment still opens with nothing drafted:

```
drafts now: 0    briefings now: 0    High at latest: 18
```

**Every documented command, run.**

```
$ uv sync
Resolved 26 packages       Checked 23 packages

$ npm ci
found 0 vulnerabilities

$ uv run --env-file .env demogym migrate
No pending migrations.

$ uv run --env-file .env demogym seed --help
usage: demogym seed [-h] [--as-of AS_OF] [--seed SEED]

$ uv run --env-file .env demogym score --help
usage: demogym score [-h] [--as-of AS_OF]
```

`seed` and `score` were not run. Both replace the live estate, and reseeding as of today would move
every figure quoted in 006, 013 and 014 away from what the deployment shows, for no gain. Their full
output is recorded in those slices. The flags above are read off the commands the README documents, so
the instructions match the tooling.

**From a clean clone into an empty directory**, with this slice's changes applied so the gate covers
what ships:

```
$ git clone <this repository> clean-clone
dddcd25 Retire slice 014

$ uv sync
 + typing-extensions==4.16.0
 + typing-inspection==0.4.4

$ npm ci
found 0 vulnerabilities

$ make check
161 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**Every claim in the README checked against the repository.**

```
CREATE TABLE statements in migrations/:   8
  sites  members  equipment  risk_scores  drafts  entries  briefings  model_calls
```

The first draft of the README said nine tables, counting the nine migration files. There are nine
migrations and eight tables: 008 widens a column rather than creating anything, and the ledger is
written by the runner rather than by a migration. Corrected before it shipped.

Every path the README names exists:

```
ok  planning/README.md   ok  planning/specification.md   ok  AGENTS.md   ok  standards
ok  LICENSE              ok  proxy.ts                    ok  .env.example  ok  api
```

`LICENSE` is MIT. Next 16.3.5 and React 19.2.8 are what `package.json` pins, CI runs Node 24, and
`.python-version` is 3.13.

**The writing rules.**

```
dashes standing in for punctuation:  0
stock phrasing:                      0
American spellings:                  0
emoji:                               0
```

The one hit on the American-spelling sweep is the `LICENSE` filename, which is the file's actual name.
The heading above it is spelled Licence.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      161 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

The README is the project rather than its plan. It opens with the synthetic-data statement, says what
the system does and where the line between arithmetic and the model sits, lists the three screens and
the stack, and then gives the commands from a clean clone to a working application with data in it. It
points at the running-on-real-data screen for the limitations instead of repeating them.

Two decisions the slice left open, settled here.

**The limitations are named and not listed.** The README says there is no holdout group, no
suppression, no seasonality, no authentication beyond the token and no observability, then sends the
reader to the screen and the specification. A third copy of that list would be a third thing to keep
true, and the one on the screen is the one a reader of the deployment sees.

**Deploying a copy is out of scope.** The README says which three variables a deployment needs set and
stops. The rest is Vercel's documentation, it changes, and a stale copy of it here would be worse than
a pointer.

Three things came out different from the plan.

**Writing the instructions found a bug in them.** The documented local path did not work. `next dev`
reads `.env.local` over `.env` and `make api` read `.env` alone, so the token that opened a page was
refused by the endpoint and nothing could be drafted locally. Neither token worked for both. `make api`
now passes both files in the order Next.js reads them, which makes the two processes agree by
construction rather than by somebody keeping two files in step. This is the value of the slice: the
instructions were written by running them, and running them is what found it.

**A stale process made the fix look wrong.** The first probe after the change still returned 401,
because the old server held port 5328 and the new one had exited with `Address already in use`. The fix
was right and the measurement was reading the wrong process. That is the second time in two slices that
a check has been wrong before the thing it checked was.

**The README claimed nine tables.** There are nine migrations and eight tables: one widens a column,
and the ledger is written by the runner rather than by a migration. Counting files rather than tables
is the kind of error a README accumulates, and it was caught by checking the claim against
`migrations/` rather than by reading it back.

One thing this slice does not do. `seed` and `score` were not run, because both replace the live estate
and reseeding as of today would move every figure quoted in 006, 013 and 014 away from what the
deployment shows. Their output is recorded in those slices, and the flags the README documents were
read off the commands themselves.
