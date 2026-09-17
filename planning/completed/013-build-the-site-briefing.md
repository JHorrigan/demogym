---
slice: 013
title: Build the site briefing
status: complete
depends_on: [005, 008, 010, 011]
decisions: [0004, 0005, 0007, 0008]
---

# 013 - Build the site briefing

## Goal

A briefing per site, written on request from computed facts: the bands and how they moved, the
attendance slots that have thinned, the equipment out of service and for how long, and a projection of
what is at stake. It names the situation, orders who to contact first, and states any link between the
facts as a hypothesis to check rather than as a finding.

## Why now

It is the second feature and the last one. It is also the reason the equipment data exists: without a
second domain, a briefing narrates one number.

It is the harder of the two prompts, and 0007 says so in terms. Drafting writes a hundred and twenty
words from eight facts, which any current model does. A briefing has to synthesise several facts, order
a short list with a reason attached to each position, and hold a negative instruction across a whole
output. That last constraint is what 016 should stress hardest, and it cannot be stressed until it
exists.

## In scope

- The slot arithmetic: visits per week by day of week and part of day, over the trailing three weeks
  against the twelve-week baseline, per site, and which slots have thinned most. This is new arithmetic
  and it is where the tests go.
- The projection: the High band at the most recent scoring date, counted as likely to lapse within six
  weeks, and what those memberships are worth per month. The horizon is a stated assumption, not a
  measurement, and the briefing says so.
- The per-site facts assembled from stored rows: band counts, the move against the previous week, the
  direction across the twelve dates, the thinned slots, the equipment out of service with how long, and
  both revenue figures.
- The prompt, carrying the causation constraint explicitly rather than trusting the model's manners.
- `POST /api/briefing`, one site per call, under the daily cap and returning the same three failure
  states drafting does.
- The briefing stored with its model, both token counts and the measured cost, one row per site per day.
- A button on a site-filtered queue, and the briefing rendered where it was asked for.

## Not in scope

- Comparing models on the constraint. 016 owns that, and this slice exists so it has something to
  compare.
- Any change to scoring, drafting or the decision surface.
- A briefing for the whole estate. A briefing is written for whoever runs a site, and an estate-wide one
  is a different document for a different reader.
- Keeping more than one briefing per site per day. The primary key 003 chose is `(site_id,
  generated_on)`, and asking again on the same day replaces it.
- Any claim about whether a briefing is right. There is no holdout group and no outcome to score it
  against, which 0005 records and 014 writes down.

## Done when

- A `POST` to the deployed `/api/briefing` for each of the six sites returns a briefing and stores a row
  carrying the pinned model, both token counts and a cost that divides out by hand.
- The facts for one site can be checked by hand against the database: the band counts match the estate
  screen for that site, the equipment matches the equipment table, the thinned slots match a count over
  `entries`, and the projection equals the sum of the High band's monthly prices.
- All six briefings are read. None asserts that anything caused anything, and any link between
  attendance and equipment is stated as something to check. All six are quoted in the evidence.
- Asking twice on the same day replaces the row rather than adding one, and the cost readout counts both
  calls, because both were billed.
- The cap refuses a briefing once the day is spent, and the three failure states read the same as they do
  on a draft.
- The button appears on a site-filtered queue and not on the unfiltered one, because a briefing is for
  one site.
- No horizontal page scroll at 320px and 390px.
- `make check` passes.

## Evidence

Run against the live database and the real API, with the endpoint loaded from the same file Vercel runs.

**The facts one briefing is written from**, for Parkhead, and the prompt built round them:

```
Site
- Parkhead, Scotland
- Figures as of 2026-09-17

At risk now
- 3 High, 3 Medium, 2 Low, out of 42 members scored
- At-risk rate 19.1%, down 4.8 percentage points on last week
- The at-risk rate at each of the twelve weekly dates, oldest first: 18.9%, 18.9%, 16.2%,
  18.9%, 15.4%, 15.0%, 22.5%, 27.5%, 29.3%, 28.6%, 23.8%, 19.1%

What that is worth
- Every banded member's membership: 304.92 pounds a month
- The High band alone: 109.97 pounds a month. On current readings those 3 are the members
  counted as likely to lapse within 6 weeks.

The High band, most expensive membership first
- M00198, 49.99 a month: Last came 46 days ago, 7.1 times their usual gap of 6.5 days.
- M00183, 34.99 a month: Visits down from 1 to 0 a week, 0% of their rate over the last 12 weeks. Last came 38 days ago.
- M00212, 24.99 a month: Visits down from 3 to 0 a week, 0% of their rate over the last 12 weeks. Last came 25 days ago.

Attendance slots that have thinned, the last three weeks against the nine before
- Saturday evening: was 4.7 visits a week, now 2.3, down 2.3
- Wednesday evening: was 4.7 visits a week, now 2.7, down 2.0
- Sunday morning: was 4.4 visits a week, now 2.7, down 1.8

Equipment out of service
- Seated row (selectorised strength), out of service for 6 days
```

Every figure in it is a stored value or an arithmetic function of stored values. The band counts, the
rate and the change agree with the estate screen's row for Parkhead, which computes them separately in
SQL for the page. The equipment matches the `equipment` table. `109.97` is `49.99 + 34.99 + 24.99`.

**All six briefings, read for causation.** One run, one call each:

```
Castle Street  in  966  out  743  0.1085 cents  11.0s
Kingsway       in 1052  out  728  0.1084 cents   9.5s
Meadowbank     in 1072  out  737  0.1099 cents   9.6s
Northgate      in 1007  out  887  0.1266 cents  10.5s
Parkhead       in 1032  out  896  0.1282 cents  11.2s
Riverside      in  901  out 1200  0.1620 cents  13.6s
```

Every link any of them draws, quoted in full:

```
Castle Street  Worth checking whether the fall in the at-risk rate to 11.4%, down 5.2 percentage
               points on last week, sits alongside the thinner attendance slots, particularly
               Friday evening, now at 1.0 visit a week compared with 2.7.

Kingsway       Worth checking whether the non-attendance among the High band sits alongside thinner
               Sunday morning attendance, which was 3.0 visits a week and is now 1.7.
               Worth checking whether the High band's £119.96 a month sits alongside the chest press
               being out of service for 29 days.

Meadowbank     The 29.4% at-risk rate, up 8.8 percentage points on last week, sits alongside thinner
               Sunday morning attendance, down from 4.8 to 3.0 visits a week, and Saturday evening
               attendance, down from 2.7 to 1.3. It is worth checking whether the affected members
               attended either slot.
               Everything is in service, so no equipment pairing stands out.

Northgate      Worth checking whether the 19.3% at-risk rate sits alongside the Sunday morning
               attendance change from 11.8 to 10.7 visits a week.
               Worth checking whether any of the four High-band members' usual attendance overlaps
               with the air bike, which has been out of service for 3 days.

Parkhead       Worth checking whether any of the three High-band members used the Saturday evening,
               Wednesday evening or Sunday morning slots, which have fallen to 2.3, 2.7 and 2.7
               visits a week respectively.
               Worth checking whether the 19.1% at-risk rate sits alongside the seated row being out
               of service for 6 days.

Riverside      Worth checking whether M00153's visits down from 1 to 0 a week and last visit 61 days
               ago sit alongside Wednesday morning attendance, which was 6.9 visits a week and is
               now 5.7, down 1.2.
               Worth checking whether M00153's attendance record sits alongside the Arc trainer being
               out of service for 5 days.
```

Eleven links across six briefings, and not one of them says a cause. Every one is "worth checking
whether X sits alongside Y", and the figures quoted in them are the figures the prompt gave. Parkhead is
the hardest case in this dataset, with three evening and weekend slots thinning while a seated row sits
out of service, and it says the two sit together and stops there.

Each briefing also carries the horizon as an assumption where it mentions it. Kingsway: "those four
members are counted as likely to lapse within six weeks, although that six-week horizon is an
assumption this project has not measured."

**Two defects in the prompt, found by reading the output rather than the prompt.**

The first: every entry in the ordered list arrived numbered, and the heading numbers them too.

```
was:  1. 1. M00198, with a £49.99 monthly membership, last came 46 days ago ...
now:  1. M00198, first because this is the highest-priced High-band membership at 49.99 pounds ...
```

The prompt now asks the model not to number them, and the assembly drops a number it puts there
anyway, because it sometimes does.

The second: the instruction that nothing is sent was being repeated back as a sentence in the briefing.

```
was:  1. M00233, first and only listed contact: High band, last attendance 15 days ago ...
          Any approved message is recorded and goes no further.
```

It is now written as a constraint rather than a fact to quote, and none of the six mentions sending.

A third, smaller one: the hypothesis list padded itself with a figure compared against itself
("whether the £179.95 a month in the High band sits alongside the five members counted as likely to
lapse"). Each entry now has to join a fact about members or the at-risk figures to a fact about
attendance slots or equipment.

**The cost divides out for every row.**

```
Castle Street  2026-09-17 gpt-5.6-luna in  966 out  743 cost 0.1085 by hand 0.1085 match True
Kingsway       2026-09-17 gpt-5.6-luna in 1052 out  728 cost 0.1084 by hand 0.1084 match True
Meadowbank     2026-09-17 gpt-5.6-luna in 1072 out  737 cost 0.1099 by hand 0.1099 match True
Northgate      2026-09-17 gpt-5.6-luna in 1007 out  887 cost 0.1266 by hand 0.1266 match True
Parkhead       2026-09-17 gpt-5.6-luna in 1032 out  896 cost 0.1282 by hand 0.1282 match True
Riverside      2026-09-17 gpt-5.6-luna in  901 out 1200 cost 0.1620 by hand 0.1620 match True
```

**Asking twice on the same day replaces the prose and adds to the spend.** Riverside, written and then
written again from the screen:

```
before: 901 in, 780 out, 0.1116 cents, 1 row
after: 1802 in, 1448 out, 0.2098 cents, 1 row
cost divides out by hand: True
```

One row, as the primary key requires, holding what has been spent on that site's briefing today. The
arithmetic still checks because price times tokens is linear, so a sum of calls is a sum of costs.

**From the screen.** On a site-filtered queue, the panel starts empty and fills:

```
before:        SITE BRIEFING | Written on request from Riverside's own figures. Nothing until
               somebody asks. | Write the briefing
while writing: ... | Writing the briefing
after 10s:     SITE BRIEFING | Written on 17 September from the figures above | Write it again |
               At Riverside, Yorkshire, as of 2026-09-17, 5 of 43 scored members are currently at
               risk: 1 High, 2 Medium and 2 Low ...
```

The panel is on a site's queue and not on the unfiltered one:

```
on the unfiltered queue, a briefing panel: false
on a site's queue, a briefing panel:       true
```

**Every refusal, over HTTP.** None of these wrote anything:

```
no token                [401] forbidden      | This endpoint is reached with the link token.
not an object           [400] bad request    | the request body must be a JSON object
no site_id              [400] bad request    | site_id must be a positive integer
a site_id that is text  [400] bad request    | site_id must be a positive integer
an unknown site         [404] unknown site   | There is no site 999999.
the cap spent           [429] daily limit    | The cap on model calls for today is spent. It resets tomorrow.
```

**A defect the browser caught.** The panel did not refresh the shell, so writing a briefing left the
header's running cost unchanged until the next page load. It now refreshes as the drafting side does,
and the header lands on the database's own sum:

```
header after a briefing: 0.79 US cents, 6 calls
database:                6 rows, 0.7898
```

**Phone widths, with a briefing on the page.**

```
320px: page 305 vs viewport 320   nothing overflows its box
390px: page 375 vs viewport 390   nothing overflows its box
```

**Each new rule broken, and the test that noticed.**

```
the two slot windows do not overlap        test_the_windows_do_not_overlap                     FAIL
a slot under the floor is dropped          test_a_slot_that_kept_going_is_not_reported         FAIL
                                           test_a_drop_below_a_visit_a_week_is_not_reported    FAIL
the worst slot comes first                 test_the_worst_slot_comes_first_and_the_list...     FAIL
the endpoint checks the token itself       test_the_wrong_token_is_refused_by_the_endpoint...  FAIL
a site_id must be a positive integer       test_a_site_id_must_be_a_positive_integer           FAIL
a self-numbered entry is not numbered twice test_an_entry_the_model_numbered_itself_is_not...  FAIL
an empty list of checks says so            test_nothing_worth_checking_says_so_rather_than...  FAIL
```

The first of those passed on the first attempt, which meant the test was not testing its own name: it
used a slot with no recent visits, so overlapping the windows changed the count by nothing. Rewritten
with visits in both windows, it fails against the overlap and the rate it asserts is checkable by hand:
two a week for nine weeks against one a week for three is 2.0 falling to 1.0, where an overlapping
window would report 2.3.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      161 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployed endpoint and screen.** Commit `4668b21`, against `https://demogym-ten.vercel.app`.
Northgate, from a command:

```
Northgate  gpt-5.6-luna  in 1007  out 1056  cost 0.1469 cents  12.7s
```

Its two links, from the deployment rather than from a local run:

```
Sunday morning visits are now 10.7 a week, down 1.1 from 11.8, alongside 4 High and 7 Medium
members. Worth checking whether any at-risk members are represented in that slot.

The High band is valued at 149.96 pounds a month, alongside the air bike being out of service for
3 days. Worth asking whether any High-band members use that equipment.
```

Parkhead, from the screen, starting empty:

```
before:        SITE BRIEFING | Written on request from Parkhead's own figures. Nothing until
               somebody asks. | Write the briefing
while writing: ... | Writing the briefing
after 7s:      Written on 17 September from the figures above | Write it again |
               At Parkhead, as of 2026-09-17, 8 of 42 members scored are at risk: 3 High, 3 Medium
               and 2 Low ...
```

The row it wrote, and the header afterwards:

```
Parkhead 2026-09-17 gpt-5.6-luna in 1032 out 706 cost 0.1054 by hand 0.1054 match True
header: 0.11 US cents, 1 call
```

Every refusal answers the same way as it does locally:

```
no token [401] forbidden   not an object [400] bad request   no site_id [400] bad request
a site_id that is text [400] bad request   an unknown site [404] unknown site
the cap spent [429] daily limit
```

And the panel sits where it belongs, at both phone widths:

```
on the unfiltered queue, a briefing panel: false
on a site's queue, a briefing panel:       true
320px: page 305 vs viewport 320   nothing overflows its box
390px: page 375 vs viewport 390   nothing overflows its box
```

The briefings were deleted afterwards, so the deployment opens with nothing generated.

## Outcome

Both features exist. A briefing is written on request for one site from figures computed before the call:
the bands and how they moved, the twelve-week direction, the attendance slots that have thinned, the
equipment out of service and for how long, and what the High band is worth per month. It names the
situation, orders who to contact first with a reason for each position, and states any link between the
facts as something to check.

`slots.py` holds the new arithmetic, `briefing_facts.py` assembles a site's facts from stored rows,
`briefing_prompt.py` holds the instructions and the shape of the answer, `briefings.py` owns the table
and `briefing_endpoint.py` decides what the endpoint answers. `SiteBriefing` renders it on a
site-filtered queue.

Five decisions the slice left open, settled here.

**The two slot windows do not overlap**, which is where this departs from the decay ratio. For a member
the question is how now compares with their own long-run normal, and the scorer answers it conservatively
by leaving the recent weeks inside the baseline. For a slot the question is whether it changed, and a
window that contains the change it is measuring answers that one badly. A test asserts the difference
with numbers that can be checked by hand.

**The projection is the High band, and its horizon is an assumption.** Six weeks is not measured and
cannot be measured here: there are no cancellations to fit it against, and fitting it to the generator's
own leavers would measure the generator rather than the rule, which is what 0005 rules out. The prompt
says so and the briefings repeat it. Both revenue figures go into the prompt, the High band's and every
banded member's, so a reader can trace either and neither quietly replaces the other on the estate
screen.

**Regenerating replaces the prose and adds the tokens.** One row per site per day is what the key 003
chose allows. Keeping only the newest call's cost would drop a call that was billed out of a total this
project calls measured. The row's counts are therefore everything spent on that site's briefing today,
and the arithmetic still divides out by hand because price times tokens is linear.

**The body is stored as prose and rendered as stored.** The model answers in three parts and the endpoint
assembles them under headings. The column is `text` and now holds text, and what is on the screen is
character-for-character what is in the row, which is the property that makes a briefing checkable at all.

**A briefing belongs to a site, so the button is on a site's queue.** There is no estate-wide briefing:
that is a different document for a different reader, and the person who would act on this one runs one
site.

Three things came out different from the plan.

**The prompt needed two fixes that only reading the output would have found.** Every entry in the ordered
list arrived numbered under a heading that numbers them, and the instruction that nothing is sent was
being quoted back into the briefing as a sentence. The first is now asked for in the prompt and stripped
in assembly, because the model sometimes numbers anyway; the second is written as a constraint rather
than as a fact available for quoting. A third, smaller one padded the hypothesis list by pairing a figure
with itself, and each entry now has to join a fact about members to a fact about slots or equipment.

**The model call became generic.** A briefing and a draft share the pinned model, the pricing, the
failure classification and the truncation rule, and differ only in what they ask for back. `generate`
now takes the response shape, `Generated` carries whatever came back, and `Message` moved to sit beside
the prompt that asks for it.

**One test was not testing its own name.** The overlap test passed against a mutation that overlapped the
windows, because it used a slot with no recent visits, so the count was the same either way. Rewritten
with visits in both windows it fails against the overlap, and the rates it asserts are checkable by hand.
That is the second time in this project a test has only earned its keep once it was watched to fail.

Two things this slice does not do. Nothing here says whether a briefing is any good: there is no holdout
group and no outcome to score it against, and 016 compares models on the constraint rather than on
correctness. And the causation rule is held by a prompt and checked by a person reading eleven links,
which is the honest description of the guarantee.
