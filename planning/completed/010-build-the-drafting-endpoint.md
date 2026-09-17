---
slice: 010
title: Build the drafting endpoint
status: complete
depends_on: [002, 003, 006]
decisions: [0003, 0004, 0005, 0006, 0007, 0008]
---

# 010 - Build the drafting endpoint

## Goal

A deployed Python endpoint that drafts the message to one member at risk: it takes a member and the
three settings a reviewer chose, assembles the facts from stored numbers, calls the pinned model, writes
the row from the response, and returns the message. Provable with `curl`.

## Why now

It is the first slice with a model in it, and the first thing the deployment runs that is not a page. The
data, the arithmetic and both screens are finished, so nothing here is entangled with anything else:
if a draft comes back wrong, the only new part is the part that produced it.

It also gives 0004 something to be about. Until now the deployed Python surface has been an argument in
a decision record and no code, and 0008 replaced the feature that decision originally pointed at.

011 cannot start without it. The controls, Draft all and the four row states are a client wired to this
endpoint, and wiring them to an endpoint that does not exist would mean building both at once and
guessing at the boundary between them.

## In scope

- One endpoint, `POST /api/draft`, deployed alongside the application. One member per call.
- The token check, performed by the endpoint itself rather than inherited from the application gate.
  0006 asks for exactly this, and it means taking `/api` out of the proxy's matcher so the two gates do
  not stand in for each other.
- Validation at the boundary: the member exists, is in the High band at the most recent scoring date, and
  has a draft left; tone, length and offer are each one of the fixed options. Nothing else is accepted.
- The facts, derived by arithmetic from stored rows: the reason string, the band, tenure, plan, monthly
  price, site, baseline rate, the date they last came, their usual day of the week and their usual time
  of day. The last two are computed here for the first time.
- The prompt, assembled from those facts and the reviewer's three selections. No free text reaches the
  model.
- The call to `gpt-5.6-luna`, pinned, returning a subject, a body and a rationale as structured output.
- The row written from the response before the endpoint returns, carrying the model, both token counts
  and the measured cost in fractional cents.
- The attempt limit of two per member, derived from the stored rows so a failed call cannot spend one.
- The daily cap across every model call, enforced server side in Postgres and counting requests the
  endpoint accepts. This needs a counter table, which 0002 anticipated.
- The three failure states from the specification, told apart by reading the error body rather than the
  status code, and returned under the names the interface already uses.
- A truncated message discarded rather than stored.
- Tests covering validation, the cap decision, the attempt limit, the failure classification, the cost
  arithmetic and the fact derivation. No database, no network, per 0005.

## Not in scope

- Anything on a screen. 011 owns the dropdowns, Draft all, redraft and the four row states, and 012 owns
  Approve, Edit and Reject. The `decision`, `edited_body` and `decided_at` columns stay null here.
- The briefing endpoint. 013 owns it, and it is a different prompt over different facts.
- Concurrency. 0008 puts the four-in-flight limit in the browser, because that is where the twenty calls
  are made.
- The running cost readout. It reads stored rows and lands with 011.
- Choosing the model. 0007 pins one and 016 measures it.
- Retrying inside the endpoint. The installed client already retries, and the specification forbids two
  retry budgets multiplying each other. What the client does is confirmed and recorded rather than added
  to.

## Done when

- A `POST` to the deployed `/api/draft` with the token and a valid body returns a subject, a body, a
  rationale, the pinned model ID, both token counts and a cost, and a matching row is in `drafts`.
- The same call without the token is refused, and it is refused by the endpoint rather than by the
  application gate. Removing the gate from `/api` and repeating the call shows which one refused it.
- Each of these is refused with a named reason and makes no model call: an unknown member, a member not
  in the High band at the most recent scoring date, a tone, length or offer outside the fixed lists, and
  a third draft for a member who already has two.
- The stored cost equals the token counts times the published price for the pinned model, checked by
  hand against 0007's table.
- Lowering the cap and calling again returns the daily limit state rather than a fault, and the member's
  attempt count does not move.
- Each of the four failure cases in the specification's table maps to one of the three states, proved by
  a test that fails when the mapping is reversed.
- Every string in the prompt is either a number this project computed or an option from a list. A test
  builds a prompt and checks each fact in it against the stored row it came from.
- A response that stopped at the token ceiling is discarded, and no row is written for it.
- The member's usual day and usual time can be checked by hand against their entries.
- `make check` passes.

## Evidence

Measured against the handler in `api/draft.py`, running over HTTP against the live Neon database and
the real API.

**A member drafted, end to end.** M00020 at Northgate, High band, warm and standard with a free class:

```
[200] member 1820, scored_on 2026-09-17, attempt 1
subject: A free class at Northgate
gpt-5.6-luna   in 537   out 604   cost 0.0832 cents
```

The body, 117 words:

> Hello,
>
> You usually make it to Northgate around four or five times a week, often on Friday mornings, so it has
> been a little while since your last visit on 12 September. We wanted to check in and ask how things are
> going.
>
> If there is anything you would like to tell us about your routine or your visits, please reply to this
> message or speak to the team next time you are in. We would be pleased to welcome you back whenever
> suits you.
>
> As a welcome back, we would like to offer you a free class. If that sounds useful, let us know and we
> can arrange it for you.
>
> Best wishes,
> The Northgate team

Every fact in it traces to a stored number. Four or five times a week is the stored baseline of 4.50.
Friday mornings is the count below. 12 September is the last entry on or before the scoring date. The
free class is the dropdown, not the model's idea.

**The reviewer's settings change the message rather than the model.** The redraft, direct and short with
no offer, came back at 44 words and offered nothing:

```
attempt 2: direct / short / none   (507 output tokens, 0.0716 cents)
subject: Your usual visits to Northgate
Hello, you usually visit Northgate several times a week, often on Friday mornings, but we have not seen
you for five days. Is everything all right? Let us know if there is anything we should be aware of, and
when you plan to return.
```

Both versions are kept, as the primary key requires.

**The prompt is assembled from stored rows and three list values, and nothing else.**

```
Member and site
- Account: M00020
- Site: Northgate
- Membership: premium, 49.99 pounds a month
- Member for: 2 years

What the attendance figures say, as of 2026-09-17
- Last came 5 days ago, 5.0 times their usual gap of 1 day. Usually attends 4.5 times a week.
- Their own established rate: 4.5 visits a week
- Last visit: 2026-09-12
- Came most often on a Friday, most often in the morning

How the reviewer wants it written
- Tone: warm
- Length: about 120 words
- Offer: a free class
```

Against the stored row for that member and date:

```
('M00020', 'Northgate', 'premium', Decimal('49.99'), joined 2024-04-19, 'high',
 baseline Decimal('4.50'),
 'Last came 5 days ago, 5.0 times their usual gap of 1 day. Usually attends 4.5 times a week.')
```

**The two habits counted by hand**, from `entries` over the same twelve-week window the scorer uses:

```
visits in the window: 52
by day:  Friday 12, Saturday 12, Wednesday 11, Monday 10, Thursday 5, Tuesday 2
by part: morning 52
```

Friday and Saturday tie at twelve, and the rule takes the earlier weekday. Twelve of fifty-two is why the
prompt says "came most often on a Friday" rather than "usually". The claim is a count, and the wording
is the count's size.

**The cost matches the token counts by hand.** 537 input at $0.20 per million and 604 output at $1.20 per
million is 0.0832 cents:

```
stored cost 0.0832 cents, by hand 0.0832 cents, match True
```

**Every refusal, over HTTP.** None of these reaches the model:

```
no token             401 {"error": "forbidden",       "message": "This endpoint is reached with the link token."}
wrong token          401 {"error": "forbidden",       "message": "This endpoint is reached with the link token."}
not JSON             400 {"error": "bad request",     "message": "the request body must be a JSON object"}
empty body           400 {"error": "bad request",     "message": "the request body must be a JSON object"}
bad tone             400 {"error": "bad request",     "message": "tone must be one of: warm, direct, encouraging"}
unknown member       404 {"error": "unknown member",  "message": "No member 999999 was scored at the most recent scoring date."}
medium band member   409 {"error": "not at risk",     "message": "Member 1804 is medium band. Only the High band is drafted for."}
third draft          409 {"error": "no drafts left",  "message": "Member 1820 has had a draft and a redraft."}
```

**The daily cap.** Against Neon at a cap of three, the statement refuses the fourth call and does not keep
counting past the cap:

```
call 1: reserve returned 1   accepted
call 2: reserve returned 2   accepted
call 3: reserve returned 3   accepted
call 4: reserve returned None   REFUSED
call 5: reserve returned None   REFUSED
stored count after five calls at a cap of three: 3
```

Through the endpoint, with today's counter set to the cap of 200:

```
another member, cap spent  [429] daily limit | The cap on model calls for today is spent. It resets tomorrow.
attempts stored for 1837: 0 -> 0
```

429 rather than a 5xx, because the cap working is not a fault.

**A refused call, end to end.** The same handler with a key the API rejects:

```
[503] unreachable
  The model could not be reached. Worth trying again.
  took 2.6s, which is the client not retrying an authentication error
  calls counted: 1 -> 2
  attempts stored for 1837: 0 -> 0
```

The call counts against the day and the member's attempt count does not move, which is the specification's
"a failure costs nothing" and its daily cap counting accepted requests, both at once. The provider's own
words went to the log rather than into the response:

```
the model refused a call: Error code: 401 - {'error': {'message': 'Incorrect API key provi...
```

**What the installed client already does**, read out of `openai==3.14.1` rather than assumed, which is why
no retry is added on top:

```
_constants.py   DEFAULT_MAX_RETRIES = 2   INITIAL_RETRY_DELAY = 0.5
                MAX_RETRY_DELAY = 8.0     MAX_RETRY_AFTER_DELAY = 120
_base_client.py _should_retry: obeys `x-should-retry`, then retries 408, 409, 429 and >= 500,
                and refuses a `Retry-After` above the 120 second maximum
```

**Timing.** Three runs of the real prompt, so the claim in 0008 that a call takes a couple of seconds can
be replaced with a measurement:

```
run 1    6.7s   in 537   out 635   reasoning 423
run 2    7.1s   in 537   out 631   reasoning 424
run 3    7.0s   in 537   out 699   reasoning 516
```

About seven seconds, and two thirds of the output tokens are reasoning rather than message. At low
reasoning effort the same prompt ran in 3.4 to 4.3 seconds for 278 to 333 output tokens, roughly half the
cost, and the three messages read no worse. That is left as a measurement for 016 rather than a change
here, because three drafts read by one person is not the edit-rate measure this project says it trusts.
Vercel's default function duration is 300 seconds, so seven seconds needs no configuration.

**Each rule broken, and the test that noticed.** Reversing or removing the rule, one at a time:

```
billing 429 told apart from a rate limit    test_an_exhausted_balance_is_not_worth_trying_again       FAIL
                                            test_a_refused_call_raises_the_state_the_row_should_show  FAIL
a truncated message is discarded            test_a_message_that_stopped_at_the_ceiling_is_discarded   FAIL
output tokens priced at the output rate     test_cost_is_the_published_price_times_the_tokens...      FAIL
                                            test_a_real_sized_draft_costs_a_fraction_of_a_cent        FAIL
                                            test_a_finished_message_carries_its_own_token_counts...   FAIL
a setting must be one of the options        test_each_setting_must_be_one_of_the_options...           FAIL
                                            test_a_setting_cannot_be_free_text_dressed_as_an_option   FAIL
                                            test_a_refused_request_reaches_neither_the_database...    FAIL
the endpoint checks the token itself        test_the_wrong_token_is_refused_by_the_endpoint_itself    FAIL
                                            test_a_missing_token_is_refused                           FAIL
a tie on days takes the earlier weekday     test_a_tie_on_days_takes_the_earlier_one_in_the_week      FAIL
habits counted over the baseline window     test_the_habits_are_counted_over_the_baseline_window_only FAIL
tenure drops the unfinished month           test_tenure_counts_whole_months_to_the_scoring_date       FAIL
the prompt never names the band             test_the_prompt_never_names_the_band_or_the_score         FAIL
no offer means offer nothing                test_no_offer_says_to_offer_nothing_rather_than...        FAIL
```

The first run of this produced ten blank results, because a mutation and its restore both landed inside
one second and the replacement was the same length as the original. CPython invalidates a `.pyc` on the
source's size and its modification time in whole seconds, so the stale bytecode was reused and the tests
ran against code that was no longer on disk. The run above sets `PYTHONDONTWRITEBYTECODE=1`.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      130 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployed endpoint.** Commit `88777c1`, against `https://demogym-ten.vercel.app/api/draft`:

```
no token           [401] json  forbidden      | This endpoint is reached with the link token.   (0.4s)
bad tone           [400] json  bad request    | tone must be one of: warm, direct, encouraging  (0.4s)
unknown member     [404] json  unknown member | No member 999999 was scored at the most...      (0.5s)
a real draft       [200] json  drafted        | A quick note from Northgate                     (7.7s)
```

The first line is the condition this slice cared about. Without the token the response is the endpoint's
own JSON, not the application's refusal page, so `/api` is outside the proxy's matcher and the gate that
refused the call is the one in the Python. The site root still answers 401 from the proxy, so the page
gate is untouched.

The row the deployed function wrote, read back out of Neon:

```
member 1853  2026-09-17  attempt 1  encouraging/standard/guest pass
  subject: A quick note from Northgate
  gpt-5.6-luna  in 537  out 648
  stored 0.0885 cents, by hand 0.0885 cents, match True
  decision None, edited_body None, decided_at None
calls counted today: 2 -> 3
```

The draft claimed three things about the member. All three check out against the entries:

```
draft:  "about twice a week"          stored baseline 2.00
draft:  "often on Monday mornings"    Monday 8 of 25 visits in the window, all 25 in the morning
draft:  "your last visit was 10 days ago"   last entry 2026-09-07, ten days before the scoring date
```

Both evidence drafts were deleted afterwards, so `drafts` is empty and the queue opens with nothing in it,
as 0008 requires. `model_calls` keeps today at three, which is the true count of calls the endpoint
accepted today and is what the cap is for.

## Outcome

A deployed Python function that drafts one member at risk, reachable at `/api/draft`, taking a member and
three dropdown settings and returning a subject, a body, a rationale, the pinned model ID, both token
counts and a measured cost. It is the first thing in this deployment that is not a page, and the first
call to a model in the project.

`facts.py` derives what the prompt may see, `prompt.py` assembles it, `drafting.py` validates the request,
`model.py` makes the one call and prices it, `drafts.py` reads and writes the rows, `cap.py` holds the
daily cap, and `draft_endpoint.py` decides what comes back. `api/draft.py` is twenty lines of HTTP over the
top. Migration 009 adds `model_calls`, the cap's counter, which 0002 had already anticipated as the one
piece of state read and written inside a request.

Six decisions the slice left open, settled here.

**The token travels in a header, not the path.** The pages carry the token as their first path segment;
the endpoint is one fixed path, so it reads `x-demogym-token`. `/api` came out of the proxy's matcher at
the same time. Two gates in front of one door means neither is tested, and 0006 asks for the endpoint's
own check rather than an inherited one.

**The scoring date is taken from the database, never from the request.** A caller names a member and
nothing else. There is no way to ask for a draft against a week that is no longer current.

**The daily cap is one SQL statement.** An insert with an `on conflict do update ... where calls < limit`,
so two requests arriving together cannot both read the count below the cap and both spend it. It counts
requests the endpoint accepted rather than rows written, which is why a failed call moved the counter and
left the member's attempt count alone.

**The provider's error body does not reach the reader.** The first version returned the raw upstream
message, which put a masked key fragment and an OpenAI help URL into a public response. The error now goes
to the log and the response carries one plain sentence for the state. A reviewer can act on none of the
provider's detail, and whoever ran the call can read all of it.

**A truncated message reads as unreachable.** The specification gives the interface three failure states
and a separate rule that a half-written message is discarded. Rather than add a fourth state, truncation
returns `unreachable` with its own sentence in the message field. The heading a reviewer sees will say the
model could not be reached, when what happened is that the message came back unfinished. That seam is
011's to look at when it renders the states.

**400, 401 and 403 also read as unreachable.** The specification's failure table is about what to retry,
not about what a row says, and the client already refuses to retry all three. A bad key is a deployment
fault a reviewer cannot act on, so it lands in the same state as a dropped connection, with the real cause
in the log.

Three things came out different from what was written down.

**A call takes about seven seconds, not the couple of seconds 0008 estimates.** Two thirds of the output
tokens are reasoning rather than message. At low reasoning effort the same prompt runs in three and a half
to four seconds for roughly half the tokens, and the drafts read no worse. That is recorded as a
measurement rather than acted on: three messages read by one person is not the edit-rate measure this
project says it trusts, and 016 is where a model parameter gets chosen on evidence. Vercel's default
function duration is 300 seconds, so seven seconds needs no configuration and none was added.

**The habits are hedged in the prompt, because the counts are thinner than they look.** M00020's modal day
is twelve visits out of fifty-two, which is a preference rather than a habit. The prompt says "came most
often on a Friday" and never "usually", and the tie between Friday and Saturday is broken by taking the
earlier weekday so the fact is at least deterministic. A member who trains five days a week has no usual
day, and a sentence claiming they do would be the model repeating our overstatement rather than inventing
its own.

**The specification gained an eighth table.** `model_calls` is bookkeeping rather than data, and the data
section now says so and says why the cap cannot be counted from the rows that were written.

Two things this slice does not do. Nothing tests the deployed function itself, per 0005: the tests cover
the decisions underneath it, and the function was proved by calling it. And the cap's atomicity rests on
one statement in Postgres, which no test in `make check` touches, because nothing in the gate has a
database. It was proved by running it at a cap of three and watching the fourth call refuse.

The thing worth keeping from this slice is how little the model was given. Eight facts, three list values,
and no entry rows. Every sentence in a draft that sounds like the writer knows the member is a number this
project computed, and all three claims in the deployed draft were checked back to the entries by hand.
