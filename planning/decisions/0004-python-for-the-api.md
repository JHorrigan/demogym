---
adr: 0004
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0004 - Write the deployed API in Python so the generation rules have one implementation

## Context

0002 puts a Next.js application written in TypeScript and a set of API endpoints on Vercel. 0003 says the rules that produce the data must exist as importable code rather than as a script, because two callers need them: the local tool that builds the dataset, and the deployed endpoint that advances it by one step.

The local tool is Python. Building a dataset is data work rather than web work, and nothing about a command-line program that writes rows to Postgres is better served by TypeScript.

The deployed endpoint could be either. It is a web request handler, which is TypeScript's home ground, and the application calling it is already TypeScript. Writing it as a Next.js route handler would mean one runtime, one dependency set, and request and response types shared with the frontend at compile time.

That option has one problem, and it is the whole decision. The endpoint applies the same rules the local tool applies. Written in TypeScript, those rules exist twice, in two languages, maintained by hand. They will drift, because two implementations of the same arithmetic always do. Once they drift, a row written by the advance endpoint is no longer built the same way as a row written by the seed, and the dataset quietly stops being internally consistent. Nothing would fail. The numbers would just stop meaning one thing.

Vercel runs Python as a first-class function alongside a Next.js application, from the same repository and the same deploy. Entrypoints are found at `app.py`, `index.py`, `server.py`, `main.py`, `wsgi.py` or `asgi.py` in the project root or in `src/`, `app/` or `api/`. WSGI and ASGI are named entrypoints, so a framework such as FastAPI is supported directly rather than through a shim. Dependencies install from `pyproject.toml` with uv, which is already the package manager here, so there is no parallel dependency file to keep in step.

## Decision

The deployed API is Python, in this repository, deployed with the application. It imports the same package the local tool imports, so the rules that produce a row have one implementation and one set of tests.

What goes through it is scoped deliberately:

| Work | Where it runs |
|---|---|
| Applying the rules: building rows, advancing a step, calling a model | Python endpoint |
| Reading stored rows for display | The Next.js application, querying Postgres directly |

Rules are applied when data is written and their results are stored. Nothing derives a rule-based value while a page is rendering. That is the same principle 0003 applies to bulk work, carried down a level: compute ahead of time, then read plainly.

The consequence for the API surface is that it stays small. An endpoint exists where a request has to apply a rule or call a model. Reading does neither.

## Alternatives considered

**TypeScript route handlers for everything.** One runtime, no second dependency set, no second cold-start profile, and request and response types checked across the boundary at compile time. This is the option with the lowest deployment cost and it is genuinely attractive. Rejected because it puts the generation rules in two languages, which is the failure described above. Every other cost in this decision is paid to avoid that one.

**Python for the whole API surface, including reads.** Consistent, one language owns all data access, and the Next.js application becomes a pure view layer. Rejected because reads apply no rules. Routing them through Python adds a serialisation boundary and a second set of response shapes to keep in step, in exchange for nothing, and it puts a network hop between the page and a query the page could have made itself.

**Write everything in TypeScript, including the local tool, and drop Python entirely.** One language across the project, one toolchain, one test runner. A real option rather than a straw man. Rejected because the generation work and any modelling that follows it are better served by Python's ecosystem, and because a command-line program that writes rows to a database gains nothing from being TypeScript. The cost of this choice is the one below.

**A separate Python service deployed somewhere else.** Railway, Fly, or a Lambda behind its own URL. This is what you would do if Vercel could not run Python, and it is the standard shape for a polyglot system at any size. Rejected because Vercel can, and a second deployment means a second URL, a second set of secrets, cross-origin configuration, and two things to deploy in the right order. 0002 chose one deployment for the same reason.

## Consequences

The rules that produce a row exist once. The seed and the advance cannot disagree, because there is nothing for them to disagree about.

There is no type checking across the language boundary. The request and response shapes of each endpoint are agreed by hand between Python and TypeScript, and nothing catches a mismatch at build time. This is the real price of the decision, and the mitigation is that the surface is small enough to hold in your head. If it stops being small, a generated schema becomes worth the machinery, and that would need its own ADR.

Two runtimes ship in one deployment, with the second dependency set and second cold-start profile 0002 already records. The Python version the project pins is constrained by what the Vercel runtime offers.

Most of what the endpoint does is covered by the package's own tests, because the endpoint is a thin wrapper around it. What is left to test at the endpoint itself is narrow: input validation, the rate cap, and the shape of an error. None of it needs a database or a deployment. How that is tested, and what is deliberately not tested, is decided in 0005.

Anyone reading the repository can see the same function that produced the seed being called by the endpoint that advances it. That is easier to verify than a claim in a document, which is part of why the rules live in one place.
