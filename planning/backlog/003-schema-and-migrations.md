---
slice: 003
title: Create the schema and the migration runner
status: backlog
depends_on: [001]
decisions: [0002, 0003]
---

# 003 - Create the schema and the migration runner

## Goal

The seven tables exist in Neon, created by numbered SQL applied in order by a committed tool.

## Why now

Everything after this writes rows. 0003 puts migrations in the local tool rather than in the deploy, so the tool has to exist before any data does.

## In scope

- Numbered SQL migration files for `sites`, `members`, `entries`, `equipment`, `risk_scores`, `drafts`, `briefings`, as specified.
- A Python command that applies pending migrations in order and records which have been applied.
- Connection by environment variable, `.env` locally, already covered by `.gitignore`.
- Indexes the queries in the specification will need, chosen from the specification rather than guessed.

## Not in scope

- Any data. 004 and 005 seed it.
- Rollback or down-migrations. 0001 applies: they solve a problem this project does not have.
- The application reading any of it.

## Done when

- Running the command against an empty database creates all seven tables.
- Running it a second time applies nothing and says so.
- Every column in the specification's SQL sketch exists with a sensible type, and the uniqueness constraints on `risk_scores` and `drafts` are in place.
- A test proves the runner applies files in numeric order rather than lexical or filesystem order.

## Evidence

## Outcome
