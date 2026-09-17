---
slice: 004
title: Generate and seed the estate
status: backlog
depends_on: [003]
decisions: [0003, 0005]
---

# 004 - Generate and seed the estate

## Goal

Six sites, around three hundred members, and six months of entry records in Neon, produced by a committed generator that anyone reading the repository can inspect.

## Why now

This is the data every later slice reads. It is also the hardest data work in the project, because the attendance patterns have to be varied enough that scoring them produces a meaningful spread rather than everyone landing in one band.

## In scope

- A generator producing sites, members with join and leave dates, plans and monthly prices, and six months of entries.
- Attendance patterns that vary by member: regulars, occasional attenders, weekday-morning types, and a population whose attendance decays over the window.
- Loading via `COPY` rather than row-by-row inserts.
- Tests asserting invariants, not exact values: no entry before a member joined or after they left, every member attached to a site, every entry attached to a member, counts within stated ranges.
- A fixed seed so two runs produce the same estate.

## Not in scope

- Equipment. 005 does that.
- Any scoring. 006 does that, and it is where the spread gets tuned.
- A label marking which members were made to decay. 0005 rules that out: asserting the scorer recovers a pattern the generator injected proves the code ran, not that it is right.

## Done when

- The command runs against a migrated database and reports what it wrote.
- Row counts land in the specified ranges: 6 sites, around 300 members, around 12,000 entries.
- Every invariant test passes, and each fails if the corresponding rule is deliberately broken in the generator.
- Running twice with the same seed produces identical data.
- A hand-check of three members shows attendance that reads as a plausible pattern rather than noise.

## Evidence

## Outcome
