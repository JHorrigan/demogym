---
slice: 002
title: Deploy the application behind a link token
status: backlog
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

## Outcome
