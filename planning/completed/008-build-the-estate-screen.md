---
slice: 008
title: Build the estate screen
status: complete
depends_on: [006, 007]
decisions: [0002, 0004, 0005]
---

# 008 - Build the estate screen

## Goal

Six sites on one screen, ranked by the share of members at risk, each row carrying its counts by band,
its revenue at risk, its equipment out of service, and a twelve-point trend beside the change against
last week.

## Why now

It is the first screen, and it puts computed data in front of someone before any model is involved. When
010 lands, the only new thing is the model.

It is also where the application reads the database for the first time. 0004 has the frontend querying
Postgres directly for anything that applies no rule, and nothing has exercised that yet, so the read
path and the driver choice land here rather than being discovered under a screen that also has a model
in it.

## In scope

- A read layer in the application, querying Neon directly. 0004 routes reads this way rather than through
  Python, because reading applies no rule.
- One query for the screen rather than one per row.
- The estate table: site, active members, members scored, counts by High, Medium and Low, at-risk rate,
  monthly revenue at risk, and equipment currently out of service.
- A twelve-point trend of the at-risk rate per site, and the change in percentage points against last
  week, shown beside each other.
- Default sort on at-risk rate descending.
- Selecting a site opens its queue filtered to that site.
- The empty state from 007 where the estate has been seeded but not yet scored.

## Not in scope

- The briefing, and the button that generates one. 013 owns both.
- The queue itself. 009 builds it; this slice only links to it.
- Any model call, and any change to the cost readout.
- Sorting by anything else, or any other interaction on the table. The default order is the argument the
  specification makes, and a sortable column is a feature nobody has asked for yet.

## Done when

- The deployed estate screen shows six rows read from Neon, not from fixtures.
- The rows are ordered by at-risk rate descending, and the order is not the same as ordering by member
  count, so the ranking demonstrably reports trouble rather than size.
- Every number on a row can be traced by hand: a query run separately against the database reproduces
  each figure in that row.
- The trend shows twelve points, and the change against last week agrees with the last two of them.
- The at-risk rate names its own denominator on screen, because members inside their first four weeks
  are not scored and a rate that hides them overstates how settled a site is.
- Selecting a site reaches the queue with that site applied.
- No horizontal page scroll at 320px and 390px.
- `make check` passes.

## Evidence

Measured against the built application reading the live Neon database, and in headless Chrome over the
DevTools protocol.

**Six rows, read from Neon rather than from fixtures.**

```
SITE           AT RISK    ON LAST WEEK   HIGH  MED  LOW  REVENUE  DOWN  ACTIVE  SCORED
Meadowbank      26.5%        +5.9 pp        4    2    3    £325     —      35      34
Northgate       19.3%        -4.4 pp        4    7    0    £410     1      63      57
Parkhead        19.0%        -4.8 pp        3    3    2    £305     1      44      42
Kingsway        15.4%        -5.8 pp        5    1    2    £240     1      54      52
Riverside       14.0%        -8.8 pp        2    1    3    £235     1      45      43
Castle Street   11.4%        -5.2 pp        1    1    2    £125     2      36      35
```

**The ranking reports trouble rather than size.** Meadowbank is the smallest site in the estate at 35
active members and sits first at 26.5%. Northgate is the largest at 63 and sits second at 19.3%. Ordering
on the count would put Northgate first and Meadowbank last, which is the inversion the specification
argues against, so the ordering demonstrably is not a proxy for size.

**Every number on a row traces by hand.** Queried separately against the database, outside the
application:

```
latest scoring date: 2026-09-17

Meadowbank (site 42)              on screen
  active at that date      35         35
  scored at that date      34         34
  high / medium / low    4/2/3      4/2/3
  at risk (any band)        9      9 of 34
  revenue at risk      324.91       £325
  equipment out             0          —
  change on last week   +5.9pp    +5.9 pp
  twelve rates: 6.7, 13.3, 13.3, 13.3, 17.2, 20.7, 20.0, 13.3, 25.8, 16.1, 20.6, 26.5

Northgate (site 37)               on screen
  active at that date      63         63
  scored at that date      57         57
  high / medium / low    4/7/0      4/7/0
  at risk (any band)       11     11 of 57
  revenue at risk      409.89       £410
  equipment out             1          1
  change on last week   -4.4pp    -4.4 pp
  twelve rates: 15.1, 15.1, 20.4, 20.4, 12.7, 14.0, 16.1, 13.8, 22.4, 25.9, 23.7, 19.3
```

9 of 34 is 26.47%, shown as 26.5%. 11 of 57 is 19.30%, shown as 19.3%. Revenue is rounded to the pound
on screen and the unrounded sums are above.

**The trend shows twelve points and the change agrees with the last two of them.** Meadowbank's last two
readings are 20.6% and 26.5%, a rise of 5.9 percentage points, which is what the column says. Northgate's
are 23.7% and 19.3%, a fall of 4.4.

**The rate names its own denominator.** Both `Active` and `Scored` are columns, the rate cell carries
`9 of 34` under it, and the note under the table says why the denominator is the scored count: nobody
inside their first four weeks is scored, and counting them as not at risk would report a site as calmer
than it is. Meadowbank has 35 active and 34 scored, so the choice changes the figure.

**Selecting a site reaches the queue with that site named.**

```
first site link:  /local-dev-token-not-a-secret/queue?site=42
that page shows:  Meadowbank,  No messages drafted
an unknown site:  status=200
```

The queue reads the parameter and names the site. It does not filter rows by it, because 009 has not
built any rows to filter. That is the honest limit of what this slice can show.

**No horizontal page scroll.**

```
320px: scrollWidth 320 vs viewport 320
390px: scrollWidth 390 vs viewport 390
768px: scrollWidth 768 vs viewport 768
```

The table is wider than a phone and scrolls inside its own container, which 007 built for exactly this.

**Two things looking at the render changed.**

The sparklines were anchored at zero and read as nearly flat, while the column beside them reported moves
of nine percentage points. A band running from a tenth to a third of the members compresses into the top
of a 30px box. The scale now spans the readings across the whole estate, 4.3% to 29.3%, and that band is
named under the table. Truncating a value scale usually misleads, and three things stop it here: the rate
and the move are both on the row as numbers, and the scale is identical on every row, so the shape
supports a comparison between rows rather than a reading of level.

The first column order put `Active` and `Scored` immediately after the site name, so at phone width a
reader saw two context figures and had to scroll to reach the rate the table is ranked by. The rate, the
change and the trend now come first and sit together, which is what the specification asks for anyway.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      87 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployed screen reads Neon.** Commit `b17d2fc`, CI green, `DATABASE_URL` added as a Vercel project
environment variable. All six rows on the deployed page, with the twelve readings from each accessible
label:

```
Meadowbank     26.5%   9 of 34   +5.9 pp   6.7, 13.3, 13.3, 13.3, 17.2, 20.7, 20.0, 13.3, 25.8, 16.1, 20.6, 26.5
Northgate      19.3%  11 of 57   -4.4 pp   15.1, 15.1, 20.4, 20.4, 12.7, 14.0, 16.1, 13.8, 22.4, 25.9, 23.7, 19.3
Parkhead       19.0%   8 of 42   -4.8 pp   18.9, 18.9, 16.2, 18.9, 15.4, 15.0, 22.5, 27.5, 29.3, 28.6, 23.8, 19.0
Kingsway       15.4%   8 of 52   -5.8 pp   11.9, 16.7, 9.5, 4.8, 4.5, 4.3, 10.2, 17.3, 21.2, 23.5, 21.2, 15.4
Riverside      14.0%   6 of 43   -8.8 pp   15.8, 12.8, 20.5, 17.9, 10.0, 25.0, 21.4, 21.4, 23.8, 14.6, 22.7, 14.0
Castle Street  11.4%   4 of 35   -5.2 pp   13.2, 16.2, 8.1, 5.4, 15.8, 13.2, 24.3, 25.0, 16.7, 13.9, 16.7, 11.4
```

Those readings cross-check the shared scale: Kingsway's 4.3% is the floor and Parkhead's 29.3% the
ceiling, which is the band the note under the table names. Six polylines rendered, the site links carry
the deployed token, `?site=42` reaches the queue and it says Meadowbank.

The gate and the headers from 002 still hold over the new routes: `x-robots-tag: noindex, nofollow` and
`referrer-policy: no-referrer` on the estate screen, and the root without a token still returns 401.

## Outcome

Six sites on one screen, read from Neon in one query, ranked by the share of scored members at risk, each
row carrying its bands, its revenue at risk, its equipment out of service and a twelve-point trend beside
the change against last week.

`lib/database.ts` holds the read connection and `lib/estate.ts` the query and the row type.
`components/Sparkline.tsx` is the trend. The screen is a Server Component that awaits one query, which is
what 0004 asks for: reads apply no rule, so they do not go through Python.

Five decisions the slice left open, settled here.

**`@neondatabase/serverless` over HTTPS, not a pooled client.** Queries are stateless request-response, so
there is no pool to exhaust and nothing held open between invocations, which is the failure mode a
connection pool has in a serverless runtime. One read per screen is exactly the shape it suits. This is
the first dependency the application has taken on beyond the framework, and it is recorded here rather
than in an ADR because it implements 0004 rather than deciding anything 0004 left open.

**One query for the screen, not one per row.** Six sites would otherwise be seven round trips. The query
is long, and it is one thing, so it lives as one named constant.

**The at-risk rate divides by scored, not active.** A member inside their first four weeks cannot be at
risk by construction, and putting them in the denominator reports a site as more settled than it is. Both
counts are columns so the division is checkable.

**The sparklines share one scale and it does not start at zero.** Reasoning above, in the evidence.

**`force-dynamic`, no caching.** The data changes only when the seed or the scoring run changes, and a
page cache on top of that would be a second staleness to explain. The specification already says the data
is only as fresh as the last run.

Two things this slice does not do. Nothing tests any of it, per 0005: the screen renders values that were
computed and stored elsewhere, and `tsc` plus `eslint` catch the three things that can go wrong in it. And
the numbers above were checked by hand, once, rather than by anything that will run again.
