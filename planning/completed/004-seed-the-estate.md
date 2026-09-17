---
slice: 004
title: Generate and seed the estate
status: complete
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

Generation was measured against a throwaway `postgres:17` container and then run against Neon. 0005
keeps Docker out of `make check` and it stays out.

**The command runs against a migrated database and reports what it wrote.** Against Neon:

```
$ uv run --env-file .env demogym seed --as-of 2026-09-17
Wrote 6 sites.
Wrote 300 members.
Wrote 12110 entries as of 2026-09-17, seed 20260917.
```

Run over an existing estate it says what it is replacing first:

```
Replacing 6 sites, 300 members and 12107 entries.
```

**Row counts land in the specified ranges.** 6 sites, 300 members, 12,110 entries. The specification
asks for 6, around 300 and around 12,000.

```
Northgate       North West         68 members   2651 entries
Kingsway        West Midlands      57 members   2435 entries
Riverside       Yorkshire          52 members   2139 entries
Parkhead        Scotland           46 members   1993 entries
Castle Street   South West         41 members   1712 entries
Meadowbank      East of England    36 members   1180 entries
```

Sizes are deliberately uneven, so the estate screen has something to rank and a bigger site cannot be
mistaken for a site in trouble. 24 members have already left and are not scored.

**Invariants hold in the database as well as in the tests.** Queried against Neon after seeding:

```
entries before join:        0
entries on or after leave:  0
members with no site:       0
entries with no member:     0
```

**Every invariant test fails when the rule it guards is broken.** Fourteen tests, and each one was
checked by breaking the corresponding rule in the generator, running that test alone, and confirming it
failed. The generator was then restored and confirmed byte-identical to before.

| Rule broken | Test that failed |
|---|---|
| Entries may start before the member joined | `no_entry_falls_before_a_member_joined` |
| The leaving date is attendable again | `no_entry_falls_on_or_after_the_date_a_member_left` |
| The window reaches back 40 weeks | `every_entry_falls_inside_the_window` |
| A member is attached to a site not in the estate | `every_member_belongs_to_one_of_the_six_sites` |
| Joining is not clamped to the site opening | `no_member_joined_before_their_site_opened` |
| Site populations are halved | `each_site_gets_the_population_it_asks_for`, `the_population_is_about_three_hundred` |
| Attendance rates are doubled | `the_estate_produces_about_twelve_thousand_entries` |
| Every account number is the same | `every_account_number_is_unique` |
| Arrivals drift to three in the morning | `arrivals_land_within_plausible_opening_hours` |
| Stopping is ignored | `a_member_who_stopped_has_no_entries_after_stopping` |
| Fading is ignored | `a_fading_member_attends_less_in_the_recent_weeks_than_earlier` |
| Generation reads the unseeded global random | `the_same_seed_produces_the_same_estate` |
| The seed is ignored entirely | `a_different_seed_produces_a_different_estate` |

**One real bug was found this way rather than by reading.** The first seeded estate had 7 entries on
members' leaving dates, because the day range was inclusive at both ends. A member who left on a date did
not attend on it, so the last generated day is the one before. The test now fails if that is reverted.

**Running twice with the same seed produces identical data.** A checksum over every member field and
every entry timestamp:

```
run one:    71a0f818ffc7f79500eacb2dad71473d
run two:    71a0f818ffc7f79500eacb2dad71473d
seed 999:   8f92ea4dd355bfea89164fd5815e0329
back again: 71a0f818ffc7f79500eacb2dad71473d
```

**A hand-check of four members reads as a pattern rather than noise.** Weekly visit counts, one line per
week across the window.

A regular who is still coming, steady between two and six visits a week for six months:

```
M00021  joined 2022-09-14  87 visits  last came 2026-09-17
  2026-08-10  ****
  2026-08-17  ****
  2026-08-24  ******
  2026-08-31  *****
  2026-09-07  **
  2026-09-14  **
```

A member who stopped outright. Four visits a week until late July, then nothing for seven weeks:

```
M00224  joined 2021-12-01  59 visits  last came 2026-07-26
  2026-07-06  **
  2026-07-13  *****
  2026-07-20  ****
  (nothing after this)
```

A gradual fader, which is the pattern a global "no visit in fourteen days" rule would miss entirely. Four
or five visits a week through the spring, one or two a week from mid-July, and still attending:

```
M00274  79 visits before the last three weeks, 3 since
  2026-06-08  *****
  2026-06-15  *****
  2026-06-22  *
  2026-06-29  ******
  2026-07-06  ****
  2026-07-13  *
  2026-07-20  ****
  2026-08-03  ***
  2026-08-10  *
  2026-08-17  **
  2026-08-24  **
  2026-08-31  **
```

**The population as a whole has the right shape.** Visits per member are bimodal, a cluster of low
attenders and a separate cluster of regulars, rather than a single hump:

```
up to  10 visits:  65 members
up to  20 visits:  49 members
up to  30 visits:  41 members
up to  40 visits:  12 members
up to  50 visits:  14 members
up to  60 visits:  16 members
up to  70 visits:  27 members
up to  80 visits:  29 members
up to  90 visits:  26 members
up to 100 visits:  16 members
up to 110 visits:   4 members
up to 120 visits:   1 member
```

Arrivals cluster into a morning peak and an evening peak, with nothing overnight:

```
05:00  377    16:00  185
06:00  1577   17:00  826
07:00  1824   18:00  1032
08:00  1886   19:00  1274
09:00  1589   20:00  926
10:00  393    21:00  221
```

Weekly totals across the estate sit near 460 with no trend, apart from the first and last weeks which the
window truncates. The decline is inside individual members rather than in the estate total, which is what
makes scoring against each member's own pattern the thing that finds it.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      23 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

Six sites, 300 members and 12,110 entries over six months are in Neon, written by `demogym seed` from a
generator anyone reading the repository can inspect.

The generator is four modules. `sites.py` holds the six sites as a fixed list rather than random names,
because invented place names chosen once are more legible than names assembled at runtime.
`members.py` builds the population and the attendance habit behind each member. `attendance.py` turns a
habit into arrival times. `seed.py` writes with `COPY` and returns what it wrote. The habit never reaches
the database, which is what 0005 requires: there is no label for the scorer to be graded against.

Five habits, weighted: regular at 26 per cent, weekday morning at 14, occasional at 38, fading at 14 and
stopped at 8. The last two are what give the scorer something to find, and 006 tunes those weights
against the band thresholds.

Six decisions the slice left open, settled here.

Arrival times are generated in Europe/London and stored as `timestamptz`, so an arrival written at seven
in the morning is seven in the morning in both halves of the year. Anything computing a usual hour has to
convert back to that zone rather than reading UTC.

`--as-of` defaults to today and is recorded in the command's output. Determinism is therefore a property
of the seed and the date together, not the seed alone. Anchoring the window to a date rather than to
today is what makes a run reproducible tomorrow.

Seeding replaces rather than appends, and truncates all seven tables. A score, a draft or a briefing held
over a replaced estate would describe members that no longer exist. The command prints the counts it is
about to replace before it does it.

Site and member ids are read back from the database after insertion rather than assigned by the
generator, because the identity columns are `generated always` and a generator that assigns its own ids
would have to override them.

A member attends the days they favour most of the time and other days 12 per cent of the time, so a
weekday-morning regular still looks like a person rather than a schedule.

Attendance rates were not tuned beyond landing the total near 12,000. The band spread is 006's job, and
the backlog already records that 004 and 006 will be revisited together.

One thing changing the generator costs: any edit to the draw order reshuffles the whole estate, because
every member draws from one shared random stream. Fixing the leaving-date bug moved the entry count from
12,107 to 12,110 even though it only removed rows. Reproducibility holds for a given version of the code,
not across versions.

## Amended by 006

The backlog said 004 and 006 would be revisited together, and they were. 006 changed the attendance
model in `members.py` and reran every invariant test, which still pass.

The habit weights moved from regular 26, weekday morning 14, occasional 38, fading 14, stopped 8 to
regular 25, weekday morning 13, occasional 52, fading 7, stopped 3. The first mix put 58 members in the
High band against a target of around twenty.

The larger change was to how a member picks their days. Every habit now trains on a small set of days
spaced across the week, chosen once per member, rather than by an independent draw each morning. Drawing
each day independently clusters visits onto consecutive days, which made the median gap one day for
thirty-two members and turned an ordinary two-day break into twice their usual gap. Spacing the days is
both a better model of how people train and what makes the gap reading mean anything. The finding is
recorded under `Still open` in the specification.

A fading member's final share moved from 0.05 to 0.4 up to 0.15 to 0.6, so the depth of a fade spreads
across all three bands rather than bunching every fading member into High.

The entry count moved from 12,110 to 12,195, and the invariant range of 10,000 to 14,000 still holds.
Measured across twelve seeds the mean is 11,328 and the range 10,604 to 12,230.
