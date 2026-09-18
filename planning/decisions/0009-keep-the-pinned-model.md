---
adr: 0009
status: accepted
date: 2026-09-18
supersedes:
superseded_by:
---

# 0009 - Keep gpt-5.6-luna pinned, on measurement rather than assumption

## Context

0007 pinned `gpt-5.6-luna` for both features and was explicit that it was doing so on a judgement about
how models generally behave rather than on a result: the smallest model of the current generation is
where instruction-following per penny is best. It named `gpt-5-nano` below and `gpt-5-mini` above as
candidates and left the comparison to a later slice. That slice is 016, and this records what it found.

All three ran the same two prompts over the same six High-band members and the same six sites, with the
same three dropdown settings per member. Nothing was tuned between runs, so the model is the only thing
that differed.

The measure for drafting and for briefings is how many outputs break a rule the prompt states. A
reviewer who has to fix one of those is editing rather than approving, which is the quality measure the
specification already commits to. The rules that can be found by looking at the text are counted by
`demogym.comparison`, whose checks were each watched to fail against text that breaks them. The rules
that need judgement were read.

## Decision

`gpt-5.6-luna` stays pinned for drafting and for briefings. 0007 is confirmed rather than superseded.

**At the token ceiling the application uses**, which is 2000 and which exists so that a truncated
message is a signal rather than a routine event:

| Model | Drafts | Briefings | Rules broken | Cost, US cents |
|---|---|---|---|---|
| gpt-5-nano | 0 of 6 | 0 of 6 | nothing to count | not recorded |
| gpt-5.6-luna | 6 of 6 | 6 of 6 | 0 | 1.1215 |
| gpt-5-mini | 6 of 6 | 2 of 6 | 5 | 2.7381 |

Cost covers the calls that produced something. A call that truncates raises before its token counts are
read, so nano's twelve and mini's four are billed and are not in that column. This is the same thing the
application does, where a failed call writes no row, and it means the figure understates what a model
that fails a lot actually costs.

`gpt-5-nano` produced nothing at all. Every one of its twelve calls spent the whole budget on reasoning
and stopped mid-sentence: on one briefing it used 1984 of 1984 output tokens, all of them reasoning, and
returned no visible text. `gpt-5-mini` wrote every draft but truncated four of six briefings.

**With the ceiling raised to 8000**, which asks the different question of whether a model can hold the
rules when it is not cut off:

| Model | Drafts | Briefings | Rules broken | Cost, US cents |
|---|---|---|---|---|
| gpt-5-nano | 6 of 6 | 5 of 6 | 11 | 2.4423 |
| gpt-5.6-luna | 6 of 6 | 6 of 6 | 0 | 1.0421 |
| gpt-5-mini | 6 of 6 | 6 of 6 | 13 | 4.7517 |

Three things decide it.

**The incumbent is the only one that finishes inside the budget.** Raising the ceiling to let a model
think is not free: it raises what a runaway call can cost and it weakens the truncation guard, which is
there because a half-written message is worse than none.

**The incumbent is the only one that broke no rule.** Both candidates used an em dash as punctuation
across their briefings, ten times for nano and thirteen for mini, against an instruction that names it.
`gpt-5-nano` also wrote one causal claim, quoted below.

**The cheapest model on paper is the dearest in practice.** `gpt-5-nano` is a quarter of the incumbent's
input price and a third of its output price, and it cost more than twice as much to run, because it
spends far more tokens reasoning. One draft: 401 output tokens for the incumbent, 5603 for nano.

On the hardest instruction, the rule against claiming a cause, all three were close. Every link the
incumbent wrote across six briefings was a hypothesis. So was every link `gpt-5-mini` wrote. `gpt-5-nano`
wrote one that was not, and a counter did not catch it:

```
worth checking whether Arc trainer outage for 5 days is contributing to the Wednesday
morning attendance drop from 6.9 to 5.7 visits per week
```

The opening does not undo the claim. "Is contributing to" says the outage produced the drop, which is
the one thing the prompt forbids. That phrasing is now in the check and it was found by reading.

## Alternatives considered

**Promote `gpt-5-mini`.** It held the causation rule in every briefing it wrote, which is the hardest
thing either feature asks for. Rejected because it truncated four of six briefings at the production
ceiling, broke the house style thirteen times when given room, and costs four and a half times the
incumbent for a full run. Nothing it does better is something this project needs.

**Demote to `gpt-5-nano`.** Rejected on all three measures at once: it cannot finish at the production
ceiling, it wrote the only causal claim in the comparison, and it costs more to run than the incumbent
despite a lower published price. The saving 0007 declined to chase turns out not to exist.

**Raise the ceiling and take the cheaper model.** This is the only version of the cheap option that
works, and it trades a real safety property for a saving that is negative. Rejected.

**Two models, a cheap one for drafting and a larger one for briefings.** 0007 rejected this on
complexity. The measurement removes the remaining reason to revisit it: the incumbent is both the
cheapest to run and the only one that breaks no rule, so there is no split that helps.

**Tune the prompts per model and compare again.** A prompt tuned against one model measures the tuning.
Rejected, and it is the reason nothing was changed between runs.

## Consequences

The pin in 0007 now rests on a measurement rather than on a judgement, and the specification's open
question about the model is closed.

The comparison is narrow and the ADR should not be read as more. Six members and six sites is a small
sample, the drafting judgement is a count of rules broken rather than a reader preference, and there is
no holdout group and no outcome to score any of it against. What it establishes is that at this
project's settings the incumbent completes every call and breaks no stated rule, and that neither
candidate does.

The comparison is reproducible. `scripts/compare_models.py` runs it, writes every output to a file, and
touches nothing: no draft row, no briefing row, no entry in the daily cap.

Running it again costs a few pence and needs a key, so it stays out of CI. 0005 keeps the gate free of
secrets and this does not change that.

Two things in the application changed to make the measurement possible, and both are improvements in
their own right. The one call the project makes now takes the model and the ceiling as arguments and
prices the answer against the model that was asked for, so a cost figure still means something if the
pin ever moves. And a structured answer cut off at the ceiling now reaches the truncation state it was
always meant to reach, which it did not before: the SDK parses before the caller can read the status, so
truncation arrived as a stack trace rather than as a row saying the message was discarded. 016 found
that by running a model that spends its whole budget thinking.
