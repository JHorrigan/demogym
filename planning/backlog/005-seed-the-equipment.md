---
slice: 005
title: Generate and seed the equipment
status: backlog
depends_on: [003]
decisions: [0003]
---

# 005 - Generate and seed the equipment

## Goal

Around a hundred equipment units spread across the six sites, with install dates going back a few years and a handful currently out of service.

## Why now

The briefing in 013 is the only consumer of this data, and it cannot be written until the data exists. It is independent of the member data and much smaller, so it does not belong inside 004.

## In scope

- A fixture of forty to fifty equipment types with a name and a category: cardio, selectorised strength, plate-loaded, racks and benches, free weights, functional.
- A generator placing units at sites. Not every site holds every type, and some hold several of a type.
- Install dates spread across the last few years rather than clustered on one date.
- A status per unit, with a small number out of service carrying a `down_since` date in the past.
- Invariant tests: every unit attached to a site, every unit a type that exists, no install date in the future, no `down_since` on a unit that is in service.

## Not in scope

- Generating the type catalogue with a model. 0003 rules it out: rule-written reference data is reproducible and checkable, model-written data is neither, and this is fifty rows.
- Fault history, capex planning, and any link between equipment and members. All three are recorded under deliberately absent in the specification.

## Done when

- Around a hundred units exist across six sites, and no two sites hold an identical inventory.
- Every invariant test passes, and each fails when the corresponding rule is deliberately broken.
- At least one unit has been out of service long enough that a briefing mentioning it would be saying something.
- Running twice with the same seed produces identical data.

## Evidence

## Outcome
