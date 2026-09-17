---
slice: 006
title: Score the estate
status: complete
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

**Twelve weekly rows per eligible member, and none for anyone who should not be there.** In Neon:

```
scoring dates: 12
rows:          3010

12 dates: 228 members      6 dates:   7 members
11 dates:   3 members      5 dates:   7 members
10 dates:   1 members      4 dates:   4 members
 9 dates:   2 members      3 dates:   2 members
 8 dates:   5 members      2 dates:   8 members
 7 dates:   8 members      1 dates:   2 members

rows for a member inside their first four weeks at that date:  0
rows for a member who had left by that date:                   0
rows for a member before they joined:                          0
```

228 members carry all twelve. The rest carry fewer because they crossed the four-week threshold or left
partway through the window, which is the rule working rather than rows going missing.

**The most recent date holds nineteen in the High band.**

```
$ uv run --env-file .env demogym score --as-of 2026-09-17
Wrote 3010 scores across 12 weekly dates to 2026-09-17.
  high       19
  medium     15
  low        12
  unflagged  217
```

The twelve dates show the at-risk count climbing, which gives the estate screen's trend something real
rather than a flat line:

```
2026-07-02  high   9  medium  17  low   7  scored 238
2026-07-30  high  13  medium   8  low   9  scored 245
2026-08-27  high  19  medium  30  low  11  scored 260
2026-09-17  high  19  medium  15  low  12  scored 263
```

**Every cut point in the band table has a test, and each fails when its threshold moves.** Twelve
thresholds, each checked in both directions by moving it and running that test alone.

| Threshold moved | Test that failed |
|---|---|
| High decay 0.25 to 0.24 | `decay_at_the_high_threshold_bands_high` |
| High decay 0.25 to 0.26 | `decay_just_above_the_high_threshold_bands_medium` |
| Medium decay 0.45 to 0.44 | `decay_at_the_medium_threshold_bands_medium` |
| Medium decay 0.45 to 0.46 | `decay_just_above_the_medium_threshold_bands_low` |
| Low decay 0.65 to 0.64 | `decay_at_the_low_threshold_bands_low` |
| Low decay 0.65 to 0.66 | `decay_just_above_the_low_threshold_is_not_flagged` |
| High gap 4.0 to 4.01 | `gap_multiple_at_the_high_threshold_bands_high` |
| High gap 4.0 to 3.99 | `gap_multiple_just_below_the_high_threshold_bands_medium` |
| Medium gap 3.0 to 3.01 | `gap_multiple_at_the_medium_threshold_bands_medium` |
| Medium gap 3.0 to 2.99 | `gap_multiple_just_below_the_medium_threshold_bands_low` |
| Low gap 2.0 to 2.01 | `gap_multiple_at_the_low_threshold_bands_low` |
| Low gap 2.0 to 1.99 | `gap_multiple_just_below_the_low_threshold_is_not_flagged` |

Every other rule was checked the same way:

| Rule broken | Test that failed |
|---|---|
| Guard 1.0 to 0.4 | `the_guard_keeps_a_rate_drop_on_a_low_baseline_out_of_the_band` |
| Guard 1.0 to 1.5 | `the_same_drop_on_a_comparable_baseline_bands_high` |
| Not-scored cut 4 to 3 weeks | `a_member_inside_their_first_four_weeks_is_not_scored` |
| Not-scored cut 4 to 5 weeks | `a_member_at_exactly_four_weeks_is_scored` |
| Joiner cut 12 to 8 weeks | `a_member_between_four_and_twelve_weeks_uses_their_own_first_four_weeks` |
| Baseline a mean not a median | `the_baseline_is_a_median_so_one_holiday_does_not_move_it` |
| Recent window 3 to 4 weeks | `the_recent_rate_covers_three_weeks` |
| Typical gap a mean not a median | `the_typical_gap_is_the_median_of_consecutive_gaps` |
| Gap needs one visit rather than two | `the_typical_gap_is_unknown_below_two_visits` |
| Last visit limited to the window | `the_gap_multiple_counts_from_the_last_visit_even_outside_the_window` |
| The no-visits rule removed | `no_visits_in_the_baseline_window_bands_high` |
| Worse of two becomes better of two | `a_member_takes_the_worse_of_the_two_readings` |

**The minimum-baseline guard is shown both ways.** `band(0.0, None, 0.5)` is not flagged and
`band(0.0, None, 1.0)` is High, so the guard rather than the ratio is what makes the difference. The
specification's paired example is tested directly: a fortnightly attender silent for nine days is not
flagged, with a baseline of 0.5 and a typical gap of 14 days, while a four-times-a-week attender silent
for the same nine days is High. The same four-times-a-week member is not flagged after three days. A
global rule on days since the last visit flags the first and misses the second, which is precisely
backwards.

**Three rows checked by hand.** Each recomputed from the entries in SQL, independently of the Python
that wrote the row.

```
M00248, band medium
  reason:      Last came 25 days ago, 3.6 times their usual gap of 7 days. Usually attends 0.5 times a week.
  stored:      baseline 0.50  recent 0.00  gap 7.00  multiple 3.57
  weekly:      [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0]  median 0.5
  recomputed:  baseline 0.5   recent 0.00  gap 7     days since 25, so 25 / 7 = 3.57

M00291, band low
  reason:      Last came 15 days ago, 2.1 times their usual gap of 7 days. Usually attends 0.5 times a week.
  stored:      baseline 0.50  recent 0.67  gap 7.00  multiple 2.14
  weekly:      [1, 0, 0, 1, 0, 2, 1, 0, 2, 2, 0, 0]  median 0.5
  recomputed:  baseline 0.5   recent 0.67  gap 7     days since 15, so 15 / 7 = 2.14
```

The third is a joiner, and the check caught its own mistake. M00022 joined 46 days before the scoring
date, so their baseline comes from their own first four weeks rather than the trailing twelve, which the
reason string says in as many words. Recomputed against the right window:

```
M00022, joined 2026-08-02, band medium
  reason:      Visits down from 1.2 to 0.3 a week, 27% of their rate over their first four weeks.
               Last came 7 days ago.
  visits in the first four weeks: 13, 17, 24, 25 and 27 August, so gaps of 4, 7, 1 and 2 days
  recomputed:  baseline 5 / 4 = 1.25, typical gap median([4, 7, 1, 2]) = 3.0
  stored:      baseline 1.25  gap 3.00  decay 0.27  multiple 2.33
  and 0.33 / 1.25 = 0.26, 7 / 3 = 2.33
```

Display rounds to one decimal place where the column keeps two, so a reason quoting 1.2 sits behind a
stored 1.25.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      87 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

`risk_scores` holds 3,010 rows across twelve weekly dates, with nineteen in the High band at the most
recent, each carrying a reason a person can read and check against the stored numbers.

`scoring.py` is the arithmetic and takes no database. `score.py` reads the entries, sweeps the twelve
dates and writes with `COPY`. `band(decay, gap_multiple, baseline)` is public, which is what lets the
boundary tests hit each cut point exactly rather than trying to construct a member whose readings land
on 0.45.

Three decisions the slice left open, settled here.

**A row exists for every eligible member at every date, not only for banded ones.** The slice asks for
twelve rows per eligible member and the specification's volume of around 3,600 is 300 members by twelve
weeks, so a member whose readings do not reach Low needs a value rather than no row. Migration 008
widens the check constraint to admit `unflagged`. The queue selects the three real bands and ignores it;
the estate screen divides the banded count by the active members.

**Reason strings quote numbers that divide.** The first version rendered a gap of 1.5 days as "2", so a
row read "9 days ago, 6.0 times their usual gap of 2 days" and the arithmetic in the sentence did not
work. A string whose whole job is being checkable cannot round to a different number than the one it
divides by.

**A joiner's reason names their own first four weeks** rather than saying "the last 12 weeks", because a
member of six weeks' standing has no twelve-week history and a reason claiming one is unauditable.

Two findings came out of running the rule rather than reading it, and both mattered.

**The gap reading has no minimum-data guard.** Member 464 had two visits in the twelve-week window, one
day apart. That single gap became a median of one day, so 37 days of silence read as 37 times their usual
gap. The minimum-baseline guard exists to stop exactly this on the decay side and there is no equivalent
on the gap side. The thresholds are the specification's and were left alone; the case is recorded under
`Still open` with the two options for real data. What removed it here was the generator change below,
which took the number of High rows resting on fewer than four visits from many to one.

**Independent daily draws do not produce habits.** The first attendance model rolled for every member on
every day, which clusters visits onto consecutive days and gave thirty-two members a median gap of one
day. A member who trains four times a week goes every other day, so an ordinary two-day break is not
twice their usual gap. Every habit now trains on a small set of spaced days chosen once per member. This
is what made the gap reading mean anything, and it is recorded as an amendment on 004.

Tuning took four rounds and the first three were measured against a single database run, which was a
mistake: the band count is a draw from a population of 300 and moves by six either way on reshuffling
alone. Sweeping twelve seeds in memory showed the distribution rather than a point, and the mix was
chosen against that. The committed seed gives nineteen High and 12,195 entries. Across twelve seeds the
High band runs 19 to 26 with a mean of 22, and entries 10,604 to 12,230 with a mean of 11,328. A single
run would have had me tuning against noise, and for three rounds it did.

One thing this slice does not establish. The tests assert the rules hold and the readings agree with the
entries. They say nothing about whether the rule finds members a real gym would want called, and they
cannot, because the data was made by the same project. 0005 records that, and the accuracy figure this
project deliberately does not produce is the same point.

## Amended after 011

011 put a reason string next to a message drafted from it, and the pair read as a contradiction: M00141
at Riverside said "No visits at all in their first four weeks" while the draft named a visit on 29
August the member had certainly made. Both were true. The rule behind them was not.

**What was wrong.** The specification said no visits in the baseline window bands High without further
calculation. For a member with a full history that window is the trailing twelve weeks, so an empty one
means they have stopped coming. For a member between four and twelve weeks the window is their own first
four weeks, which is a stretch of the past: emptying it says nothing about whether they are still coming.
Sixteen rows across the twelve scoring dates were banded High on an empty joiner window while the member
had attended since, two of them at the most recent date. M00106 was High for an empty first four weeks
and had last come four days earlier.

**What changed.** Two things, and the second is what makes the first work.

The no-visits rule now fires on an observed period rather than the baseline window: the trailing twelve
weeks, or since they joined if that is more recent. It always runs up to the scoring date, so "no visits
at all" means what it says. `Observed` in `scoring.py` carries it, with the phrase a reason uses for it,
so a member who has never come reads "No visits at all since they joined" and a member who stopped
twelve weeks ago still reads "in the last 12 weeks".

The typical gap is now measured over that same observed period rather than over the baseline window.
Without this the fix has a hole: a joiner with an empty first four weeks has no gap at all, so a month of
silence after a run of visits would band unflagged, which is the opposite mistake. For a member with a
full history the two periods are identical, so nothing about a settled member moved.

**What it moved.** Rescoring changed 29 rows out of 3,010, of which 24 changed band.

```
bands at the most recent date
  high         19 ->   18
  medium       15 ->   16
  low          12 ->   11
  unflagged   217 ->  218
```

Ten of the band moves are the misfire going away. The rest are joiners whose gap reading now counts the
visits they have made rather than only the ones inside their first four weeks. Three checked by hand
against the entries:

```
M00266  joined 2026-08-08, 5 weeks
  visits 13 Aug, 1 Sep, 2 Sep, 5 Sep    gaps 19, 1, 3    median 3    last came 12 days ago
  12 / 3 = 4.00                         stored gap 3.00, multiple 4.00    unflagged -> high
  The 5 September visit sat outside their first four weeks, so the old gap was 10 days and a
  twelve-day silence read as ordinary.

M00141  joined 2026-07-13, 9 weeks
  visits 15, 22, 28, 29 Aug             gaps 7, 6, 1     median 6    last came 19 days ago
  19 / 6 = 3.17                         stored gap 6.00, multiple 3.17    high -> medium

M00106  joined 2026-07-15, 9 weeks
  visits 13, 23, 26 Aug, 13 Sep         gaps 10, 3, 18   median 10   last came 4 days ago
  4 / 10 = 0.40                         stored gap 10.00, multiple 0.40   high -> unflagged
```

Neither of the last two claims a usual weekly rate any more, because their baseline is zero and saying
"usually attends 0 times a week" would be a number pretending to be a reading.

Three tests landed with it, written before the change and watched to fail against the old rule:

```
test_a_joiner_who_has_attended_since_their_empty_window_is_not_banded_high_for_it   FAIL
test_a_joiner_who_has_never_attended_still_bands_high                               FAIL
test_a_joiners_usual_gap_counts_the_visits_they_have_actually_made                  FAIL
```

The test 011 added for the last-visit clause moved to a member whose visits all predate the twelve-week
window, which is the case that still reaches that sentence.

This slice's own conditions still hold: the most recent date holds eighteen High-band members, inside the
fifteen to twenty-five the slice asked for, and every cut point in the band table is still tested.

The open question this raised in the specification is now closed, and the rule text and the typical-gap
definition were both rewritten to match.
