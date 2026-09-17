---
slice: 002
title: Deploy the application behind a link token
status: in progress
depends_on: [001]
decisions: [0002, 0005, 0006]
---

# 002 - Deploy the application behind a link token

## Goal

A URL that loads a placeholder page for someone holding the link, refuses everyone else with a page rather than a bare error, and stays out of search engines. The deployment pipeline exists and works before there is anything to deploy.

## Why now

The thing most likely to go wrong late is deployment, and finding that out with three screens built is worse than finding it out with none. 0006 decides the access gate and nothing enforces it yet. This slice also completes the `make check` gate that 001 half built.

It is also where TypeScript enters the project, and `AGENTS.md` requires a language to get its standard in the same commit as the decision that brings it in. 0002 chose the stack and no standard was written, so the repository currently contradicts its own instruction file.

## In scope

- Next.js App Router with TypeScript and Tailwind, one placeholder page.
- `standards/nextjs.md`, covering the same ground `standards/python.md` covers for Python, and referenced from `AGENTS.md`.
- Middleware enforcing the token from the URL path against an environment variable.
- A refusal page for a missing or wrong token. Plain, but a page, not a bare 401 body.
- `noindex` on every response, no sitemap, and the token absent from `robots.txt`.
- `Referrer-Policy: no-referrer`.
- A Vercel project deploying on push, with the token set as an environment variable.
- Extend `make check` to run `tsc` and `eslint` after ruff and pytest.

## Not in scope

- Any database connection, any data, any real screen.
- Any Python function. 010 deploys the first one.
- The visual design. 007 owns that, and it restyles the refusal page along with everything else.

## Done when

- The deployed URL with the token returns the placeholder page.
- The same URL with a missing token and with a wrong token returns the refusal page.
- `curl -I` on the deployed URL shows the `noindex` and `Referrer-Policy` headers.
- `/robots.txt` and `/sitemap.xml` do not reveal the token or the protected path.
- `make check` runs four steps in order and exits zero.
- A push to main produces a deployment with no manual step.
- `standards/nextjs.md` exists and `AGENTS.md` points at it.

## Evidence

Everything below was run against `next start` on the built application at `127.0.0.1:3117`, with
`DEMOGYM_ACCESS_TOKEN=local-dev-token-not-a-secret` in `.env.local`. The deployed conditions are still
open and are listed at the end.

**The stack.** Next.js 16.3.5, React 19.2.8, Tailwind 4, TypeScript 5, ESLint 9 flat config, scaffolded
with `create-next-app` and then reduced to what this slice needs. `npm run build` compiles and reports
the routes the gate depends on:

```
Route (app)
┌ ○ /_not-found
├ ƒ /[token]
├ ○ /refused
└ ○ /robots.txt

ƒ Proxy (Middleware)
```

**The gate admits the token and refuses everything else.**

```
with token     /local-dev-token-not-a-secret   status=200   placeholder, synthetic-data label present
root, no token /                               status=401   refusal page
wrong token    /wrong-token                    status=401   refusal page
```

The refusal is a rendered page at 401, not a bare body.

**Headers are on every response**, set in `next.config.ts` against `source: "/:path*"` so no page has to
remember. `curl -I` on the protected page and on the refusal:

```
HTTP/1.1 200 OK                    HTTP/1.1 401 Unauthorized
X-Robots-Tag: noindex, nofollow    X-Robots-Tag: noindex, nofollow
Referrer-Policy: no-referrer       Referrer-Policy: no-referrer
```

The document also carries `<meta name="robots" content="noindex, nofollow"/>` from the layout's
metadata, so the instruction survives for a client reading the markup rather than the headers.

**`robots.txt` does not name the token.** `app/robots.ts` returns a blanket disallow, and the path is
excluded from the proxy matcher so it is served rather than refused:

```
User-Agent: *
Disallow: /
```

`/sitemap.xml` returns 401. No sitemap is published and nothing advertises one.

**The gate fails closed and loudly when the token is not configured.** Started with
`DEMOGYM_ACCESS_TOKEN=` empty, a request returned 500 and the log carried
`DEMOGYM_ACCESS_TOKEN is not set, so no request can be admitted`. A misconfigured deployment refuses
everyone rather than admitting everyone.

**`make check` runs four steps in order and exits zero.**

```
uv run ruff format --check .
uv run ruff check .
uv run pytest
npx tsc --noEmit
npx eslint
EXIT=0
```

Both new steps were checked against a deliberate fault. A `const broken: number = "not a number"` in
`app/refused/page.tsx` stopped the gate at `typecheck` with `error TS2322` and
`make: *** [Makefile:13: typecheck] Error 2`. A `let` that is never reassigned passed `tsc` and stopped
the gate at `lint-web` with `prefer-const` and `make: *** [Makefile:16: lint-web] Error 1`. Removing each
returned it to exit zero.

The CI workflow gained `actions/setup-node@v7` at Node 24 with npm caching, and `npm ci` before
`make check`.

**`standards/nextjs.md` exists** and covers the same ground `standards/python.md` covers: tooling,
layout, components, names, types, errors, styling, copy and tests. `AGENTS.md` lists it under coding
standards. It records two things worth finding in writing rather than by surprise: that nothing formats
TypeScript, and that the frontend does no arithmetic because every number on screen has to trace back to
a stored row.

**Still open, both needing the Vercel project.** The deployed URL with and without the token, the
headers and `robots.txt` on that URL, and a push to main producing a deployment with no manual step.

## Outcome
