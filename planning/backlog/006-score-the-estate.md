---
slice: 006
title: Score the estate
status: backlog
depends_on: [004]
decisions: [0004, 0005]
---

# 006 - Score the estate

## Goal

`risk_scores` populated at twelve weekly dates, with the most recent holding around twenty High-band members, each carrying a reason a person can read and check against the stored numbers.

## Why now

Both screens and both model features read this table. It is the arithmetic the entire project rests on, and 0005 puts the weight of the testing here because this is the part where being wrong is silent.

## In scope

- Baseline, recent rate and typical gap, computed per the specification.
- `decay` and `gap_multiple`, both stored alongside the band rather than discarded.
- The joiner rule for members between four and twelve weeks, the exclusion under four weeks, the minimum-baseline guard, and the no-visits-in-window rule.
- Band assignment taking the worse of the two readings.
- Reason strings generated from the arithmetic, naming the reading that drove the band and the numbers behind it.
- Scoring at twelve weekly dates across the trailing twelve weeks.
- Tuning: either the thresholds here or the attendance mix in 004, so the High band lands around twenty. Expect to revisit 004.

## Not in scope

- Any model. Scoring is arithmetic and the specification says so in terms.
- Any label from the generator marking who was made to decay. 0005 rules it out.
- The estate-level aggregates the briefing consumes. Those are queries over this table rather than new arithmetic, and they land with 013.

## Done when

- Twelve weekly rows exist per eligible member, and none for members inside their first four weeks at that date.
- The most recent scoring date holds between fifteen and twenty-five High-band members.
- A boundary test exists for every cut point in the band table, and each fails when its threshold is moved by one step.
- A test shows the minimum-baseline guard keeping a twice-a-month attender out of the queue while a four-times-a-week attender reaches High at about day seven.
- Three rows picked at random can be checked by hand: the reason string agrees with the stored readings, and the readings agree with the entries.

## Evidence

## Outcome
