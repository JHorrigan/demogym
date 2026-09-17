---
adr: 0007
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0007 - Use OpenAI for model access, and gpt-5.6-luna for both features

## Context

0002 named the Anthropic API as the route for model access. This decision replaces that choice. The rest of 0002 stands.

Two features call a model, and both are short text generation from facts that were computed before the call was made. Neither does arithmetic, neither retrieves anything, and neither reasons over a long context.

Drafting writes roughly a hundred and twenty words to one member from about eight precomputed facts. It is an easy task for any current model.

The briefing writes roughly two hundred words for one site. It has to synthesise several facts, produce a short ordered list with a reason attached to each position, and state any apparent link between facts as a hypothesis without asserting that one caused the other. That last constraint is a negative instruction held across a whole output, and it is the hardest thing either feature asks for.

A full run is about thirty drafts and six briefings. Roughly thirty-three thousand input tokens and ten and a half thousand output tokens.

There is existing credit on an OpenAI account and none on an Anthropic one. That is the entire reason for the provider. No technical claim is being made about one provider over the other.

## Decision

Model access goes to the OpenAI API directly, server side only.

Both features use `gpt-5.6-luna`, pinned by exact model ID. The redraft control uses the same model as the draft it replaces, so the two are comparable and a reviewer choosing between them is choosing between outputs rather than between models.

Published prices per million tokens, and what a full run costs at each:

| Model | Input | Output | Full run |
|---|---|---|---|
| gpt-5-nano | $0.05 | $0.40 | about $0.006 |
| gpt-4.1-nano | $0.10 | $0.40 | about $0.007 |
| gpt-5.6-luna | $0.20 | $1.20 | about $0.019 |
| gpt-5-mini | $0.25 | $2.00 | about $0.029 |
| gpt-5.4-mini | $0.75 | $4.50 | about $0.072 |

The gap between the cheapest option and this one is roughly one penny per run. At that scale cost is not the binding constraint, so the choice is made on which model holds the briefing's constraint rather than on which is cheapest. `gpt-5.6-luna` is the smallest model of the current generation, which is where instruction-following per penny is best.

That last point is a judgement about how models generally behave, not a measured result for this prompt. The comparison slice exists to test it.

## Alternatives considered

**The Anthropic API, as 0002 chose.** Rejected because the credit is on an OpenAI account. This is a commercial reason and it is the only reason. Nothing in the design depends on the provider beyond one client and one model string.

**gpt-5-nano, the cheapest available.** It would do the drafting perfectly well. Rejected because it would also do the briefing, where a previous-generation nano is weakest at holding a negative constraint across a long output, and the saving is about a penny per run. Choosing it would be optimising the smaller number at the expense of the larger one.

**gpt-5-mini or gpt-5.4-mini.** More capable, and between ten and twenty times the output price. Rejected because nothing in either feature needs it. If measurement says otherwise the comparison slice promotes one, and that is a better route than assuming it now.

**Two models, a cheap one for drafting and a larger one for briefings.** Defensible at volume, where drafting would dominate the bill. Rejected here because it means two pinned IDs, two cost lines and two prompt shapes to maintain, in order to save a penny on a run of thirty-six calls. ADR 0001 applies.

**Azure OpenAI Service.** The same argument Bedrock gets in 0002. On real member data, running inference inside the tenancy that already governs the data is a materially different position from sending it to a public API, and it is what a real deployment would have to evaluate. On synthetic data it carries no weight and it adds a subscription to configure. Deferred rather than rejected.

**The Batch API, at half price.** It is asynchronous, so the seed would have to submit, poll and wait. Half of two pence does not pay for a job state machine.

## Consequences

The provider is chosen for a commercial reason, and the ADR says so rather than dressing it as a technical evaluation. If the credit runs out, this is the decision to revisit, and the change is one client and one model string.

The model ID is pinned, so a run is reproducible and a cost figure means something. It also dates the repository, which is the correct trade: a floating alias would make an old cost figure quietly wrong.

Both features share one model, so there is one pin, one cost calculation and one thing to change.

The causation constraint has to be carried explicitly in the briefing prompt rather than assumed from the model's good manners, and it is the thing the comparison slice should stress hardest. A briefing that asserts the treadmills caused the churn is worse than no briefing, because it is confident and wrong in a document a manager might act on.

The comparison slice stays in the plan. Candidates are `gpt-5-nano` below and `gpt-5-mini` above, run on the same members, judged on how often a person had to edit the output.
