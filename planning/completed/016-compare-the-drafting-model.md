---
slice: 016
title: Compare the drafting model
status: complete
depends_on: [010, 013]
decisions: [0001, 0005, 0007]
---

# 016 - Compare the drafting model

## Goal

Run `gpt-5-nano`, `gpt-5.6-luna` and `gpt-5-mini` over the same members and the same sites, with the
prompts the application actually uses, and record which one to pin as an ADR. 0007 chose the incumbent
on a judgement about how models generally behave and said in terms that this slice exists to test it.

## Why now

It is last because it measures the thing 013 built. The briefing's rule against claiming a cause is the
hardest instruction either feature gives, 0007 says it is what this slice should stress hardest, and it
could not be stressed before it existed.

It is also the only claim in the project that rests on assumption rather than measurement, and the
project's whole argument is that those are different things.

## In scope

- A price table and a model argument on the one call this project makes, so a run can name the model it
  used and cost it correctly. Production behaviour does not change: the default is the pinned model.
- A comparison runner that calls each candidate with the production prompts, over the same six members
  and the same six sites, and writes every output to a file so the judging can be checked.
- The measure for drafting: how many drafts break a rule the drafting prompt states. An invented name, a
  stated reason for stopping, a score or a percentage, the wrong offer, a banned stock phrase, American
  spelling, an emoji, a dash standing in for punctuation. Each of those is what would make a reviewer
  edit rather than approve, and each is checkable rather than a matter of taste.
- The measure for the briefing: whether any output asserts a cause. Causal language across the whole
  briefing, plus every link read and quoted, as 013 did for the incumbent.
- Those checks in a module with tests, each test watched to fail against text that breaks the rule it
  guards. The checks are the instrument, and an instrument nobody calibrated measures nothing.
- ADR 0009 recording the result and either confirming the pin or moving it. 0007 is superseded only if
  the model changes.

## Not in scope

- Writing anything to `drafts` or `briefings`, or going through the endpoints. This is a measurement,
  not a feature. It does not consume the daily cap, it does not move any attempt counter, and it leaves
  the demonstration data as it found it.
- Changing either prompt. A prompt tuned against one model mid-comparison measures the tuning.
- Any claim that one model writes a better message. There is no reader panel and no outcome to score
  against. The claim is narrower: how often an output breaks a stated rule.
- Running the comparison in CI. It costs money and needs a key, and 0005 keeps the gate free of both.

## Done when

- Every candidate has drafted the same six members and briefed the same six sites, with the same
  controls, and every output is recorded.
- Every drafting rule violation is counted per model, and each count can be traced to the output that
  produced it.
- Every link in all eighteen briefings is read and quoted, and any causal claim is quoted in full.
- Measured cost per model for the full run, divided out by hand against the published prices.
- Each check in the new module has been watched to fail against text that breaks its rule.
- ADR 0009 is written, states what was measured and what it does not establish, and either confirms
  `gpt-5.6-luna` or names a replacement.
- The specification's open question about the model is closed.
- `make check` passes, and the demonstration data is as it was before the run.

## Evidence

Three models, the same six High-band members, the same six sites, the same three dropdown settings per
member. Nothing was tuned between runs, so the model is the only thing that differed.

**All three exist on the account**, checked before anything was built around them:

```
gpt-5-nano     available
gpt-5.6-luna   available
gpt-5-mini     available
```

**The result at the ceiling the application uses, 2000 tokens.**

```
model            drafts  briefings  broken  cost cents
gpt-5-nano     0/6     0/6             -       not recorded
gpt-5.6-luna   6/6     6/6             0      1.1215
gpt-5-mini     6/6     2/6             5      2.7381   {'dash as punctuation': 5}
```

`gpt-5-nano` produced nothing. Every one of its twelve calls stopped mid-sentence. A direct probe on one
briefing shows why:

```
gpt-5-nano     status=incomplete  reason='max_output_tokens'  out=1984  reasoning=1984  ceiling=2000
gpt-5.6-luna   status=completed   reason=None                 out=1045  reasoning= 710  ceiling=2000
gpt-5-mini     status=completed   reason=None                 out=1955  reasoning=1536  ceiling=2000
```

It spent the entire budget reasoning and returned no visible text at all. `gpt-5-mini` finished that one
with 45 tokens to spare and truncated four of the six.

**The result with the ceiling raised to 8000**, which asks whether a model can hold the rules when it is
not cut off:

```
model            drafts  briefings  broken  cost cents  rules
gpt-5-nano     6/6     5/6            11      2.4423  {'dash as punctuation': 10, 'asserts a cause': 1}
gpt-5.6-luna   6/6     6/6             0      1.0421  {}
gpt-5-mini     6/6     6/6            13      4.7517  {'dash as punctuation': 13}
```

**The cheapest model on paper is the dearest to run.** One draft, the same member and the same terms:

```
model          what          in    out    stored   by hand  match
gpt-5-nano     draft        540   5603    0.2268    0.2268  True
gpt-5.6-luna   draft        540    401    0.0589    0.0589  True
gpt-5-mini     draft        540   1464    0.3063    0.3063  True
gpt-5-nano     briefing    1052   6476    0.2643    0.2643  True
gpt-5.6-luna   briefing    1007    879    0.1256    0.1256  True
gpt-5-mini     briefing    1007   2126    0.4504    0.4504  True
```

401 output tokens against 5603 for the same message. Every figure divides out by hand against the
published price for the model that was asked for.

**Every link, read.** The incumbent wrote eleven across six briefings and every one is a hypothesis.
`gpt-5-mini` wrote twelve and every one is a hypothesis. `gpt-5-nano` wrote ten, and one of them is not:

```
worth checking whether Arc trainer outage for 5 days is contributing to the Wednesday
morning attendance drop from 6.9 to 5.7 visits per week
```

"Is contributing to" says the outage produced the drop. The opening does not undo it. No counter caught
this, a person reading did, and the phrasing is now in the check with a test behind it.

For contrast, the incumbent on the same site:

```
Worth checking whether M00153's visits falling from 1 to 0 a week sits alongside the Wednesday
morning slot thinning from 6.9 visits a week to 5.7 over the last three weeks.
```

**Every draft, read.** The incumbent's six read like a person at the desk. The candidates' do not always.
`gpt-5-mini` quotes the member's own figures back at them in three of six:

```
You've been with us two years on a premium membership at £49.99 a month ... You usually come
about 4.5 times a week

You've been with us for 17 months on the off-peak membership paying £24.99 a month
```

`gpt-5-nano` does the same in one:

```
Your pattern shows you last came 37 days ago, with a gap of 5.5 days.
```

None of that trips a counted rule. It is the report voice the prompt asks them to avoid, and it is what a
reviewer would edit. It is recorded as judgement rather than counted.

**The instrument, calibrated.** Fifteen rules, each broken in turn, each caught by the test that names it:

```
DRAFT_STOCK emptied          FAIL a_stock_phrase_is_caught
AMERICAN emptied             FAIL american_spelling_is_caught
EMOJI neutered               FAIL an_emoji_is_caught
DASH neutered                FAIL a_dash_standing_in_for_punctuation_is_caught
ANALYTICS emptied            FAIL the_language_of_measurement_is_caught
PLACEHOLDERS emptied         FAIL a_placeholder_is_caught
GREETING neutered            FAIL an_invented_name_is_caught
CAUSAL emptied               FAIL a_briefing_that_asserts_a_cause_is_caught, every_causal_construction
SENDING emptied              FAIL mentioning_sending_is_caught
ANY_OFFER emptied            FAIL an_offer_nobody_chose_is_caught, a_different_offer_from_the_one_chosen
percentage check removed     FAIL a_percentage_is_caught
self-numbering removed       FAIL an_entry_that_numbered_itself_is_caught
chosen-offer check removed   FAIL the_chosen_offer_has_to_be_there
causal check widened to the whole briefing   FAIL a_reason_for_a_position_is_not_a_cause
both corrections reverted    FAIL a_softened_cause_is_still_a_cause, an_offer_phrased_warmly
```

The first attempt at this mutation run reported six rules as unnoticed. It was breaking one phrase in a
list where the test text tripped a different phrase in the same list, so the check still fired. The
harness was weak, not the tests, and replacing a phrase with emptying the list showed it.

**Five defects in the instrument, four of them found by running it rather than reading it.**

```
a subject line and the first word of a body read as a greeting   "Hi\nFeel"  -> invented name
a message can miss its offer and make a different one            only the first was reported
the passive plural of sending was missing                        "were sent" not in the list
a reason for a position in the order of work read as a cause     "first because this is the
                                                                  highest-priced membership"
"a free class on us" read as two offers                          "on us" counted on its own
```

The fourth is the one that mattered. The briefing prompt asks for the reason each member is in their
position, so counting "first because" as a breach was counting the instruction being followed. It marked
five of the incumbent's six briefings as claiming a cause. The causation check now applies to the
situation and the links, and the order of work is read.

**A defect in the application, found by running a model that thinks too much.** The first run died on a
stack trace rather than a failure state:

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Briefing
  Invalid JSON: EOF while parsing a string at line 1 column 867
```

`generate` checks `response.status == "incomplete"` to discard a truncated message, and that check can
never fire for a structured answer, because the SDK parses before the status can be read. Its own
documentation says so: "Invalid JSON or schema-invalid text in an eligible message still raises a
validation error." So the truncation rule 010 wrote, which the specification calls out in terms, was
unreachable for both features. A reviewer would have got a stack trace where a row should have said the
message was discarded. Fixed, with a test watched to fail against the real error:

```
--- guard removed ---
FAILED tests/test_model.py::test_an_answer_cut_off_mid_json_is_discarded_rather_than_raised
tests/test_model.py:136: ValidationError
--- restored ---
12 passed
```

**Nothing was written.** The runner reads the database and calls the API and stores no row, so the
demonstration data is as it was:

```
drafts 0   briefings 0   risk_scores 3010   members 300   sites 6   entries 12195   equipment 100
```

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      184 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

The pin holds, and it now rests on a measurement. ADR 0009 records it: at the token ceiling this project
sets, `gpt-5-nano` produced nothing at all and `gpt-5-mini` truncated four of six briefings, while the
incumbent completed all twelve calls and broke no stated rule. Given room to finish, both candidates used
an em dash against an instruction that names it, ten times and thirteen times, and `gpt-5-nano` wrote the
only causal claim in the comparison. The cheapest model on paper cost more than twice the incumbent to
run, because it spends fourteen times as many output tokens reasoning.

`demogym.comparison` holds what counts as a rule broken, `scripts/compare_models.py` runs the two prompts
over every candidate and writes every output to a file, and the one call the project makes now takes the
model and the ceiling as arguments and prices the answer against the model that was asked for.

Three decisions the slice left open, settled here.

**The measurement does not touch the product.** The runner reads the database and calls the API and
stores nothing: no draft row, no briefing row, no entry in the daily cap. A comparison that consumed the
cap would make the demonstration unusable for the rest of the day, and one that wrote rows would put
invented-for-measurement text in the same table the interface reads.

**The hard rules are counted and the soft ones are read.** An em dash, a placeholder, a percentage or the
wrong offer can be found by looking at the text. Whether a message reads like a person or like a report
cannot, and pretending otherwise would have produced a number with a judgement hidden inside it. Both are
in the evidence, marked as what they are, and the reading is what caught the one causal claim.

**The ceiling is part of the result, not a nuisance.** Running only at 2000 would have said the candidates
cannot produce output, which is a fact about this project's settings rather than about the models.
Running only at 8000 would have hidden that raising it trades away the truncation guard. Both runs are
reported, and the decision rests on both.

Four things came out different from the plan.

**The first run died on a stack trace, and that was an application bug rather than a runner bug.** A
structured answer cut off at the ceiling is parsed before its status can be read, so the truncation rule
010 wrote could never fire for either feature. The SDK documents this. A reviewer would have seen a stack
trace where the interface should have said the message was discarded. Fixed, with a test watched to fail
against the real error. This slice was supposed to measure the application and it found a defect in it.

**The instrument needed five corrections, four of them found by running it.** The worst marked five of the
incumbent's six briefings as claiming a cause, because the briefing prompt asks for the reason each member
is in their position and "first because this is the highest-priced membership" is that instruction being
followed. Had that gone unexamined, this slice would have concluded the opposite of the truth about the
model it was measuring.

**The mutation run was wrong before the tests were.** It reported six rules as unnoticed. It had been
breaking one phrase in a list where the test text tripped a different phrase in the same list, so the
check still fired. Emptying the whole list showed every test doing its job. That is now three slices
running in which a check has been wrong before the thing it checked was.

**The causation constraint did not separate the models.** 0007 expected it to be the hardest thing and the
thing that would decide this. All three held it almost perfectly: twenty-three of twenty-four links across
the three models were hypotheses. What separated them was finishing inside the budget, and an em dash.
The prediction about which instruction would be hard was wrong, and the ADR says so.

What this does not establish. Six members and six sites is a small sample. The drafting measure is a count
of rules broken and not a reader preference, there is no holdout group, and no outcome exists to score any
of it against. It says that at this project's settings the incumbent completes every call and breaks no
stated rule, and that neither candidate does. That is all it says.
