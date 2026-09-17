---
slice: 009
title: Build the at-risk queue
status: complete
depends_on: [006, 007, 008]
decisions: [0004, 0005]
---

# 009 - Build the at-risk queue

## Goal

Every member in a band at the most recent scoring date, High first and ordered by monthly price inside
each band, each row carrying the reason that put them there.

## Why now

It is the last screen with no model in it. After this, 010 lands and the only new thing is the model,
which is the sequencing the backlog was built around.

It also finishes what 008 started. The estate screen links to a site's queue and carries the site in the
URL, but nothing filters by it yet, so selecting a site currently arrives at a page that names the site
and does nothing with it.

## In scope

- Every member whose band at the most recent scoring date is High, Medium or Low. Nobody else.
- High first, then Medium, then Low. Inside a band, ordered by monthly price descending, because that is
  the order an operations team would work it.
- Each row: member, site, band, tenure, monthly price, and the reason string.
- A site filter, applying the `site` parameter 008 already links with, plus a way back to the whole
  estate. Server rendered, because a link needs no client state.
- Counts by band in the heading, and the same counts on each filter option, so the filter says what it
  will narrow to before it is pressed.
- The empty state from 007 where a site has nobody in a band.

## Not in scope

- The draft controls. 011 owns the tone, length and offer dropdowns, Draft all, redraft and the four row
  states. High rows carry no controls yet.
- Approve, Edit and Reject. 012 owns those.
- Sorting or filtering by anything other than site. The band order and the price order inside it are the
  specification's argument, not a default a reader should be able to override.
- Paging. Sixty rows fit on a page, and the estate is deliberately small enough that the queue is
  reviewable by one person.

## Done when

- The deployed queue lists every banded member at the most recent scoring date, and the number of rows in
  each band equals the band counts on the estate screen.
- No member whose band is `unflagged` appears, and no member from any earlier scoring date appears.
- Rows are High first, then Medium, then Low, and inside each band the monthly price never rises as you
  read down.
- Each row carries the member, the site, the band, the tenure, the monthly price and the reason.
- A reason on a row can be checked by hand against the readings stored for that member at that date.
- Selecting a site narrows the queue to that site, the row count matches that site's band counts on the
  estate screen, and there is a way back to all sites.
- A site with nobody in a band shows the empty state rather than an empty table.
- No horizontal page scroll at 320px and 390px.
- `make check` passes.

## Evidence

Measured against the built application reading the live Neon database.

**Forty-six members in a band, and the band counts match the estate screen.**

```
46 members across the estate: 19 High, 15 Medium, 12 Low
```

The estate screen's band columns sum to 19, 15 and 12, and the scoring run reported the same. Per site,
each filtered view against the counts queried straight from the database:

```
site             id  rows  high  med  low  database  only that site  match
Castle Street    41     4     1    1    2  (1, 1, 2)       yes            yes
Kingsway         38     8     5    1    2  (5, 1, 2)       yes            yes
Meadowbank       42     9     4    2    3  (4, 2, 3)       yes            yes
Northgate        37    11     4    7    0  (4, 7, 0)       yes            yes
Parkhead         40     8     3    3    2  (3, 3, 2)       yes            yes
Riverside        39     6     2    1    3  (2, 1, 3)       yes            yes

per-site rows sum to 46, all sites shows 46: match
```

Every filtered view holds only that site's members, and the six views partition the whole queue with
nothing lost or repeated.

**Nothing that should not be there is there.**

```
on screen: 46   banded at 2026-09-17: 46
  exactly the banded set:                  True
  unflagged members leaking through:       0
  members banded only at an earlier date:  105, of those on screen: 0
```

The last line is the one that matters: 105 members were in a band at some earlier scoring date and are
not in one now, and none of them appears.

**Order.** Read down the page the bands come in blocks, worst first, and inside each block the monthly
price never rises:

```
band order:  High x19  Medium x15  Low x12
High    [49.99 x5, 34.99 x5, 24.99 x9]
Medium  [49.99 x6, 34.99 x3, 24.99 x6]
Low     [49.99 x3, 34.99 x6, 24.99 x3]
```

**A reason checked by hand.** M00004, Medium, Northgate:

```
on screen:  Visits down from 1.5 to 0.7 a week, 44% of their rate over the last 12 weeks.
            Last came 15 days ago.
stored:     baseline 1.50  recent 0.67  decay 0.44  typical_gap 4.00  gap_multiple 3.75
```

0.67 divided by 1.50 is 0.447, shown as 44% and stored as 0.44. 15 divided by 4 is 3.75, which is the
stored multiple. The rendered string is character-for-character the stored one.

**The site filter is read, not hardcoded.** With Castle Street's four banded rows temporarily set to
`unflagged`, its filter option showed 0 and the all-sites option showed 42 rather than 46, and the site
showed the empty state rather than an empty table:

```
Nobody at Castle Street is in a band
Every member scored at this site is attending close enough to their own established pattern
that the arithmetic does not flag them. That is the queue working, not a gap in the data.
```

The estate was restored by rerunning `demogym score`, which is deterministic, and the counts returned to
19, 15 and 12.

An unrecognised `site` value falls back to the whole estate rather than to an empty page.

**No horizontal page scroll.**

```
320px (all)      scrollWidth 320 vs viewport 320
320px ?site=37   scrollWidth 320 vs viewport 320
390px (all)      scrollWidth 390 vs viewport 390
390px ?site=37   scrollWidth 390 vs viewport 390
```

**Four reason-string defects found by putting them on a screen.** All four had been written to the
database by 006 and read as machine-assembled the moment there were forty-six of them in a column:

| Was | Now | Rows affected |
|---|---|---|
| `their usual gap of 1 days` | `their usual gap of 1 day` | 4 |
| `Usually attends 1 times a week` | `Usually attends once a week` | 2 |
| `Last came 1 days ago` | `Last came 1 day ago` | several |
| `Last came 0 days ago` | `Last came today` | 8 |

Each landed with a test that fails without the fix, checked by reverting the helper and running the three
older ones alone:

```
test_a_gap_of_one_day_reads_as_one_day               FAIL
test_a_weekly_rate_of_one_reads_as_once_a_week       FAIL
test_a_visit_yesterday_reads_as_one_day_ago          FAIL
```

After rescoring, no row reads `1 days`, `1 times a week` or `came 0 days ago`, and 8 read `came today`.
The band counts are unchanged, because only the wording moved.

A fifth of the same kind was in this screen rather than in the scorer. A member scored at four weeks and
a day is zero whole months, and the tenure column read `0 months`, which looks like missing data rather
than like a new member. Tenure below two months is now in weeks. Every value now rendered:

```
4 weeks, 6 weeks, 2 months, 3 months, 4 months, 5 months, 10 months, 13 months,
16 months, 17 months, 19 months, 20 months, 23 months, 2 years, 3 years, 4 years, 5 years
```

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      91 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployed queue matches.** Commit `83235b3`:

```
deployed queue: 46 rows, 19 High, 15 Medium, 12 Low
bands in blocks, worst first: True
High / Medium / Low price never rises: True
no "1 days", no "1 times a week", no "came 0 days ago"
filter options: 8
```

The wording fixes are in the deployed rows, so the rescore reached the database the deployment reads.

## Outcome

Forty-six members in a band on one screen, worst first and by monthly price inside each band, each row
carrying the reason the arithmetic produced. The site filter applies the parameter 008 had only carried.

`lib/queue.ts` holds the two queries, `components/SiteFilter.tsx` the filter, and the screen is a Server
Component awaiting both.

Four decisions the slice left open, settled here.

**The filter is links, not a control.** No client state, the filter lives in the URL so a narrowed queue
can be sent to somebody, and each option shows the count it will narrow to before it is pressed. An
unrecognised site falls back to the whole estate rather than to an empty page.

**Band order and price order are fixed, not sortable.** The specification argues for both, and a column
a reader can re-sort turns an argument into a default.

**Tenure is measured to the scoring date, not to today**, so it agrees with the reading beside it instead
of drifting a day at a time after a run.

**The empty state says the queue is working.** A site with nobody in a band is the arithmetic finding
nothing, not a gap, and the copy says so.

The real work of this slice turned out to be the five wording defects. Four were in the scorer and had
been sitting in the database since 006, invisible while the strings were checked one at a time and
obvious the moment forty-six of them sat in a column. That is the argument for building the screen before
the model: reading "Last came 0 days ago" on a row is what makes it a bug, and no test I would have
thought to write in 006 would have caught it.

Two things this slice does not do. Nothing tests the screen, per 0005. And High rows carry no controls:
011 adds the drafting, 012 the decisions.
