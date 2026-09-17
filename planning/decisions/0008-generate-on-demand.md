---
adr: 0008
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0008 - Generate drafts and briefings on demand, with the reviewer setting the terms

## Context

0003 decided that bulk work runs locally and bounded incremental work runs in a deployed function. It named the in-request work as advancing the simulation by one day. That feature has been dropped for time, so the example is gone while the principle it decided is untouched.

Meanwhile the specification had every draft written at seed time, so the queue would open with all twenty messages already sitting there. That is the wrong shape for what this project is trying to show. A reader who opens a page of finished text has no way to tell whether a model wrote it this morning or whether someone typed it into a fixture. The interesting part, which is a model doing the work while a person watches and then responding to being told to try again, would happen entirely off screen.

It also leaves nothing in the deployment calling a model, which would make 0004 an argument for a Python endpoint with nothing to do.

A reviewer's actual workflow is not reading what a machine produced. It is asking for something, reading it, and asking for a different one.

## Decision

Nothing is generated at seed time. `drafts` and `briefings` start empty and fill when someone asks.

One endpoint drafts one member. One endpoint writes one site's briefing. Both are bounded, both finish in a couple of seconds, and both are well inside a function timeout.

**Draft all** is the browser calling the per-member endpoint once per member, a few in flight at a time, rendering each draft as it returns. It is not one request that loops.

**The reviewer sets the terms before each call.** Three controls, dropdowns only:

| Control | Options |
|---|---|
| Tone | Warm, Direct, Encouraging |
| Length | Short, around 40 words, or Standard, around 120 |
| Offer | None, a free class, a guest pass, a personal training session |

**One redraft per member.** The row carries an attempt count and the endpoint refuses a third. A redraft may use the same settings or different ones.

**A daily cap across every model call**, enforced server side, independent of the per-member limit.

The scoring thresholds are tuned so the High band holds around twenty members, which is a queue one person can work through and a bound on everything downstream.

## Alternatives considered

**Generate everything at seed time, as the specification first had it.** Cheapest to run, no endpoint, no cap, no failure states. Rejected because it moves the only interesting moment off screen and leaves nothing deployed that calls a model. It would also mean writing 0004 to justify an endpoint that does nothing.

**One request that drafts all twenty in a loop.** The simplest thing for the browser to call. Rejected on arithmetic: twenty calls at two to three seconds each is forty to sixty seconds, and a function is capped in tens of seconds.

**One request that drafts all twenty concurrently, server side.** This does fit inside the timeout, and it was the closest alternative. Rejected because the whole call then succeeds or fails together, partial failure has nowhere sensible to go, and the page shows a spinner where it could be showing drafts arriving one by one. The per-member endpoint is less code and a better thing to watch.

**A free-text instruction box alongside the dropdowns.** More expressive, and what a real product would eventually offer. Rejected on two grounds. It puts unbounded user input into a prompt on a page whose only protection is a shared link, and it makes the set of prompts the system can produce infinite. With dropdowns the set is finite and every prompt that can reach the model is one somebody chose in advance.

**Unlimited redrafts.** More natural, and closer to how someone would really use it. Rejected because cost per member becomes unbounded and the daily cap becomes the only thing holding it. One redraft is enough to demonstrate the model responding to a changed instruction, which is the whole point of the control.

**Letting the model choose the offer.** It has the facts, so it could. Rejected because an offer has a price, which makes it an economic decision rather than a language one. Keeping it on a dropdown means no model ever decides what the business gives away, and that is a line worth being able to draw.

## Consequences

The deployed Python path is now substantial rather than token. It assembles a prompt from computed facts and a reviewer's selections, calls the model, writes the row, and enforces both limits. 0003 and 0004 describe something that exists.

The row in 0003's table naming the simulation advance as the in-request work is replaced by drafting. The principle that decision recorded is unchanged.

The queue opens empty. That has to read as deliberate rather than broken, so the empty state is part of the work rather than an afterthought.

Cost is bounded three ways that do not depend on each other: two calls per member, a daily cap across everything, and a High band of around twenty people. A full sweep of drafts, redrafts and briefings is about forty-six calls and roughly two and a half pence.

Failure becomes visible per row instead of hidden. One member's draft can fail while the rest succeed, and that row has to say so rather than sit blank.

Nothing reaching the model is free text. Every input is either a number this project computed or an option somebody picked from a list.
