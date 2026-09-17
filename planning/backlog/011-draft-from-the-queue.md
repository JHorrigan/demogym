---
slice: 011
title: Draft from the queue
status: backlog
depends_on: [007, 009, 010]
decisions: [0002, 0005, 0006, 0008]
---

# 011 - Draft from the queue

## Goal

The queue can be worked. A reviewer sets the terms, presses Draft on one member or Draft all on the
High band, and watches messages arrive one at a time. Every row says which of the four states it is in,
and the running cost moves as calls are made.

## Why now

010 built the endpoint and proved it from a command. Nothing else in the project needs it, so it is
either wired to a screen next or it is a feature nobody can see.

It is also the first thing in the project a reader watches happen. Everything so far renders a number
that was computed before they arrived. This is the slice where a model does the work while somebody
looks at it, which 0008 says is the point of generating on demand.

012 needs it. Approve, Edit and Reject act on a drafted message, and there is nothing to act on until
one exists on the screen.

## In scope

- The three controls from 0008, as one set governing the next call rather than one set per row: tone,
  length and offer, dropdowns only, no free text.
- Draft, per member, on High rows only.
- Draft all, the browser calling the per-member endpoint once per member with at most four calls in
  flight, rendering each message as it returns rather than waiting for the sweep.
- Redraft, once per member, disabled when the endpoint has nothing left to give.
- The four row states from 007, wired to what the endpoint actually answers: not drafted, drafting,
  drafted, failed. Failed says which of the three things happened, and only the transient one offers
  another go.
- The drafted subject, message and rationale on the row, with the three settings that produced it, so
  a redraft can be compared against what it replaced.
- Drafts already stored, read on page load, so a reload shows the work rather than losing it.
- The running cost readout in the header, summed from the stored token counts, replacing the zero 007
  put there.
- The High band restructured from table rows into panels. A hundred and twenty words does not belong
  in a table cell, and 007 said the row is the thing to redesign if it stops working.

## Not in scope

- Approve, Edit and Reject, the edit against the model's text, and "Approved, not sent". 012 owns all
  of it, and the `decision` columns stay null here.
- The briefing and anything about which member to contact first. 013 owns both.
- Medium and Low rows. They keep the table 009 built and they gain nothing: a drafted message for a
  Low-band member is work nobody will do today.
- Any change to the endpoint. If this slice wants something the endpoint does not return, that is a
  finding to record rather than a change to make here.
- Persisting the reviewer's dropdown settings between visits. The stored row carries what each draft
  was made with, which is the part that has to survive.

## Done when

- The queue opens with no messages in it, and the empty state reads as deliberate rather than broken.
- Pressing Draft on one member fills that member's panel and no other, and the row moves through
  drafting to drafted without the page jumping.
- Draft all fills every High row, never has more than four calls in flight, and renders each message as
  it arrives rather than all at the end. The four can be counted.
- Draft all does not stop when one member fails. The rest of the sweep finishes and the failed row says
  so on the row.
- A member with a draft and a redraft has no button left, and both versions are on the screen.
- Reloading the page shows every stored draft, with the tone, length and offer each was made with.
- Each of the three failure states renders on the row it belongs to. The transient one offers another
  go; the other two do not, and the daily limit does not read as a fault.
- The cost readout equals the sum of `cost_usd_cents` over the stored drafts, checked against the
  database, and the call count equals the number of rows.
- Nothing on the screen claims a message was sent.
- No horizontal page scroll at 320px and 390px.
- `make check` passes.

## Evidence

Measured in headless Chrome over CDP, driving the real page against the live Neon database and the real
API. Every draft below was written by `gpt-5.6-luna` while the browser watched.

**The queue opens empty.** Nineteen panels, each saying so, and one Draft all offering the number it
would write:

```
panels: 19
buttons: Draft all 19 | Draft | Draft | Draft
cost: 0.00 US cents, 0 calls
first panel: M00020 / High / Northgate / £49.99 a month / member for 2 years /
             Last came 5 days ago, 5.0 times their usual gap of 1 day. Usually attends 4.5 times
             a week. / No message yet / Draft
```

**One member, through the three states.** Pressing Draft on M00020:

```
before:   No message yet | Draft
pressed:  Drafting | Draft
after 9s: Drafted, not sent | Redraft | ATTEMPT 1 / WARM / STANDARD / NO OFFER
          A quick check-in from Northgate
cost:     0.09 US cents, 1 call
```

No other panel moved.

**Draft all, with the four in flight countable.** Sampled every 400ms for the whole sweep:

```
highest in flight at any sample: 4

messages on the page, as they arrived:
  0.5s:0  7.3s:1  8.5s:2  8.9s:3  10.1s:4  15.4s:5  16.2s:6  16.6s:7  19.4s:8  23.4s:9
  24.7s:10  26.3s:11  27.9s:12  33.5s:13  35.5s:14  36.4s:15  38.0s:16  42.4s:17  43.6s:18  45.6s:19

meter: 4 IN FLIGHT / 18 TO GO ... 4 IN FLIGHT / 13 TO GO ...
buttons afterwards: {"Redraft": 19}
```

Nineteen messages over forty-five seconds, in fours. Not one request at the start and nineteen messages
at the end.

**The cost readout is the stored sum.** After the sweep, from the database and from the header:

```
database:  19 rows, sum(cost_usd_cents) = 1.5616
header:    1.56 US cents, 19 calls
```

**A redraft, on different terms.** The dropdowns moved to direct, short and a guest pass, then Redraft
on M00020:

```
controls: direct / short / guest pass
the redraft landed after about 8s
attempts on the panel:
  ATTEMPT 1 / WARM / STANDARD / NO OFFER
  ATTEMPT 2 / DIRECT / SHORT / GUEST PASS
buttons on the panel: []
stored: [(1, warm, standard, none), (2, direct, short, guest pass)]
```

Both versions on the screen, each labelled with what it was written on, and no button left.

**The three failure states, each produced rather than mocked.**

The endpoint stopped, then Redraft pressed:

```
Could not reach the model | Transient. Worth trying again. | Try again
```

The endpoint pointed at a stub that answers 429 with `insufficient_quota`, which is what an empty account
returns:

```
No credit remaining | Trying again will not help. The account needs topping up first.
buttons offered: none
```

The log line from that call shows the classification had something to classify:

```
the model refused a call: Error code: 429 - {'error': {'message': 'You exceeded your current quota...
```

And with today's counter set to 197 against a cap of 200, so three calls remained, Draft all over all
nineteen:

```
what each panel says: {"drafted": 3, "daily limit": 16}
a capped row: Daily limit reached | The cap on model calls for today is spent. It resets tomorrow.
buttons offered on capped rows: []
cost: 0.27 US cents, 3 calls
```

Sixteen failures and the sweep still finished all nineteen. The capped rows are set in plain ink rather
than the red a fault gets, because the cap working is not a fault.

**A failure costs nothing, and the retry works.** The failed redraft above, followed by restarting the
endpoint and pressing Try again:

```
pressed Try again on M00020
  after 11s: Drafted, not sent | ATTEMPT 1 ...
stored:     [(1820, 1), (1820, 2)]
calls counted today: 2
```

Two calls counted for two stored drafts. The failed one is not among them, because the endpoint was not
running to accept it, and it did not spend the member's redraft either.

**Phone widths, with a message on the page.**

```
320px: page 305 vs viewport 320   nothing overflows its box
390px: page 375 vs viewport 390   nothing overflows its box
```

The only element wider than its box at either width is the table's `sr-only` caption, which is hidden by
design. The panel header wraps to two lines and the message reads at full width.

**A defect in the scorer, found by putting a reason next to a message.** M00141 at Riverside reads "No
visits at all in their first four weeks", and the drafted message said "It has been a little while since
your last visit to Riverside on 29 August". Both were true and the pair reads as a contradiction:

```
M00141  joined 2026-07-13, first four weeks 13 July to 10 August
        every visit: 2026-08-15, 2026-08-22, 2026-08-28, 2026-08-29
```

The reason was accurate about the window and silent about everything after it. It now says both, and the
test fails without the fix:

```
test_no_visits_in_the_window_still_says_when_they_last_came   FAIL
```

After rescoring, the three rows carrying that reason:

```
M00106  No visits at all in their first four weeks. Last came 4 days ago.
M00118  No visits at all in their first four weeks.
M00141  No visits at all in their first four weeks. Last came 19 days ago.
```

M00118 never came, and still reads that way. The bands did not move: 19 High, 15 Medium, 12 Low, the same
as before the rescore.

That fix exposed a scoring question rather than settling one. M00106 is banded High for an empty first
four weeks while having attended four days ago. The rule that produces it was written for a twelve-week
window. The specification now carries it as an open question.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      131 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

Filled in when the slice moves to `completed/`.
