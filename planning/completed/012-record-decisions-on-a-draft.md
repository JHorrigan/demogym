---
slice: 012
title: Record decisions on a draft
status: complete
depends_on: [010, 011]
decisions: [0004, 0005, 0006, 0008]
---

# 012 - Record decisions on a draft

## Goal

A person decides. Approve, Edit or Reject on a drafted message, recorded with the action, the edit if
there was one, and the timestamp. A decided row says "Approved, not sent" on the row itself, an edit is
shown against what the model wrote, and the header carries how many approvals needed an edit.

## Why now

It is the last part of the drafting feature, and it is the part the whole argument rests on. Everything
before it produces a message; nothing until now records a human judgement about one. A prototype that
drafts and never decides demonstrates a model writing text, which is not what this project claims to be
about.

It is also the only honest quality measure the project can produce. 0005 rules out accuracy against the
generator's own labels, and the share of approvals that needed an edit is what is left. It cannot be
measured until somebody can edit.

## In scope

- One endpoint, `POST /api/decide`, applying the rules a decision has: the draft exists, no decision has
  been recorded for that member yet, the action is one of three, and an edit carries a body that differs
  from what the model wrote while the other two carry none.
- The decision written to the `decision`, `edited_body` and `decided_at` columns 003 created. The
  timestamp is the server's, not the caller's, and the attempt decided is the latest one, not one the
  caller names.
- Approve, Edit and Reject on the panel of a drafted member, on the latest draft.
- The edit surface: a field holding what the model wrote, which the reviewer changes and saves.
- The edit shown against the model's text once recorded, so what changed is visible rather than
  described.
- A decided panel reading "Approved, not sent", "Approved with an edit, not sent" or "Rejected", with
  the time it was decided.
- The share in the header: how many approvals needed an edit, out of how many approvals.
- Drafting refused for a member who has been decided, at the endpoint rather than only in the interface.

## Not in scope

- The briefing. 013 owns it.
- Undoing or changing a decision. The schema records one decision per draft and no history, and a
  reviewer who wants a different answer has the reject state for it.
- Sending anything. There is no outbound anything in this project, which is why the row says so.
- A percentage on the edit share. Five approvals do not support one, and the counts say the same thing
  without implying precision that is not there.
- Any change to the scoring or the drafting prompt.

## Done when

- A `POST` to the deployed `/api/decide` with the token records the decision, the edit and a timestamp
  on the latest draft for that member, and the stored row can be read back.
- Each of these is refused with a named reason and writes nothing: an unknown member, a member with no
  draft, a second decision on a member already decided, an action outside the three, an edit whose body
  matches the model's, and an approval or rejection carrying an edited body.
- Approving, editing and rejecting all work from the screen, and the panel says which one happened and
  when.
- An edited panel shows what the model wrote and what the reviewer changed, and the part that changed is
  marked rather than left for the reader to spot.
- A decided member has no Draft, Redraft or decision controls left, and the drafting endpoint refuses one
  if it is asked anyway.
- The header's edit share equals the counts in the database, and reads as nothing yet before the first
  approval.
- Nothing on any screen says a message was sent.
- No horizontal page scroll at 320px and 390px.
- `make check` passes.

## Evidence

Driven in headless Chrome against the live database and the real API, with the endpoints running from
the same files Vercel runs.

**Approve.** M00020, drafted and then approved from the screen:

```
pressed Approve on M00020
panel: Approved, not sent | 17 September at 20:00 | ATTEMPT 1 / WARM / STANDARD / NO OFFER
buttons left: []
header: 0 of 1  edited before approval    0.08 US cents, 1 call
```

The stored row, with the timestamp the database stamped rather than one the browser sent:

```
(1820, 1, 'approved', None, 2026-09-17 19:00:35 GMT)
```

19:00 GMT is 20:00 in the estate's own clock, which is what the row shows. No buttons are left: a
decided member has no redraft and no second decision.

**Edit.** The field opens on what the model wrote, and will not save until it differs:

```
the field opens on what the model wrote: Hello,  It has been a little while since your last visit ...
save disabled before a change: true
and the note says so:           true      ("Nothing has changed yet. Approve it as it stands instead.")
```

After one word was changed and the edit approved:

```
panel: Approved with an edit, not sent | 17 September at 20:02
marked as removed: ["your"]
marked as added:   ["you personallyr"]
header: 2 of 3  edited before approval
```

One word marked in each direction, which is the common case. A second edit that changed two places a
paragraph apart marked the whole span between them:

```
marked as removed: ["Hello,\n\nIt has been a little while since your last visit to Northgate on 13 July, so we"]
marked as added:   ["Hi there,\n\nIt has been a little while since your last visit to Northgate on 13 July, so we honestly"]
```

That is the reading erring towards saying more changed rather than less. Nothing marked as unchanged
differs between the two versions, because the unchanged ends are matched word for word from both
directions.

**Reject.**

```
pressed Reject on M00296
panel: Rejected | 17 September at 20:02
buttons left: []
header: 2 of 3  edited before approval
```

The approval counts did not move, because a rejection is not an approval.

**Every refusal, over HTTP.** None of these wrote anything:

```
no token                      [401] forbidden        | This endpoint is reached with the link token.
an action outside the three   [400] bad request      | decision must be one of: approved, edited, rejected
an approval carrying an edit  [400] bad request      | edited_body belongs to an edit, not to approved
an edit with no body          [400] bad request      | an edit needs an edited_body
a member with no draft        [404] nothing drafted  | Member 1837 has no draft at the most recent scoring date.
an unknown member             [404] nothing drafted  | Member 999999 has no draft at the most recent scoring date.
a second decision             [409] already decided  | Member 1820 has already been decided. A decision is final.
drafting a decided member     [409] already decided  | Member 1820 has been decided, so there is nothing to redraft.
```

The unchanged-edit rule needed an undecided member to show itself, because the already-decided check runs
first:

```
an edit that changes nothing  [409] edit unchanged   | The edit matches what the model wrote, so it is
                                                       an approval rather than an edit.
an edit of one word           [200] recorded edited
stored for that member: ('edited', True)
```

**The three states on the screen, and the edit form.** The panel of a drafted, undecided member carries
Approve, Edit and Reject with "Approving records a decision. It does not send anything." beside them. A
decided panel carries the decision and the time in place of the drafting state, and no controls at all.
The edit form opens prefilled, with Cancel beside a save button that stays disabled until something
changes.

**Phone widths, with a decided panel and an edit on the page.**

```
320px: page 305 vs viewport 320   nothing overflows its box
390px: page 375 vs viewport 390   nothing overflows its box
```

The only element wider than its box is the table's `sr-only` caption, hidden by design.

**A design defect the screenshot caught.** The first version put the marked-up edit underneath the
model's message, so a panel printed the same hundred and twenty words twice and the change was harder to
find rather than easier. The edit now replaces the original in place, and both versions are still on the
screen because the struck words are the model's own.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      147 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployed screen and endpoint.** Commit `465b850`, against `https://demogym-ten.vercel.app`. All
three decisions, from the browser:

```
Approve  M00020  Approved, not sent              | 17 September at 20:16   buttons left: []
Edit     M00054  Approved with an edit, not sent | 17 September at 20:17   buttons left: []
Reject   M00198  Rejected                        | 17 September at 20:17   buttons left: []

header after the edit: 1 of 2 edited before approval    0.13 US cents, 2 calls
```

The deployed edit was a pure insertion, and the marking says exactly that:

```
marked as removed: []
marked as added:   ["personally "]
```

The stored rows, with the timestamps the database stamped:

```
(1820, 1, 'approved', edited_body None,  2026-09-17 19:16:37 GMT)
(1854, 1, 'edited',   edited_body set,   2026-09-17 19:17:04 GMT)
approvals, edited: (2, 1)
every decision has a timestamp: True
decisions: [('approved', 1), ('edited', 1), ('rejected', 1)]
```

19:16 GMT is 20:16 in the estate's clock, which is what the row shows. The rejection is not counted as
an approval, which is why the share stayed at 1 of 2.

Every refusal answers the same way on the deployment as it does locally:

```
no token                      [401] forbidden       an approval carrying an edit  [400] bad request
an action outside the three   [400] bad request     an edit with no body          [400] bad request
a member with no draft        [404] nothing drafted an unknown member             [404] nothing drafted
a second decision             [409] already decided drafting a decided member     [409] already decided
```

Phone widths with a decided panel and an edit on the page:

```
320px: page 305 vs viewport 320   nothing overflows its box
390px: page 375 vs viewport 390   nothing overflows its box
```

The three evidence drafts were deleted afterwards, so the deployed queue opens with nothing in it and
reads 45 members, 18 High, 16 Medium, 11 Low.

## Outcome

A person decides, and the decision is recorded. Approve, Edit and Reject sit on the panel of a drafted
member, a decided panel says which one happened and when in place of the drafting state, an edit is
shown with the change marked inside the message, and the header carries how many approvals needed an
edit.

`decisions.py` holds the three actions and the boundary checks, `decide_endpoint.py` decides what the
endpoint answers, and the write lands in the `decision`, `edited_body` and `decided_at` columns 003
created without a migration. `api/decide.py` is six lines, because the HTTP glue moved to
`json_endpoint.py` where both endpoints share it. On the screen, `Decision`, `DecisionControls`,
`EditAgainstDraft` and `ApprovalReadout` are the new pieces.

Six decisions the slice left open, settled here.

**A decision belongs to the member, not to an attempt.** Approve, Edit or Reject on any draft closes
that member: no second decision, and no redraft afterwards. The column would allow one decision per
attempt, which would let a member carry two approvals and would make the edit share a count of drafts
rather than of members. The drafting endpoint enforces the second half of that, so it holds against a
stale page rather than only against the interface.

**The endpoint chooses the attempt and stamps the time.** A caller names a member and an action, exactly
as the drafting endpoint takes a member and three settings. A page that has been open while a redraft
happened elsewhere cannot record a decision against the draft it remembers.

**An edit that changes nothing is refused rather than stored.** It is an approval, and recording it as an
edit would inflate the one quality figure this project claims. The save button is disabled for the same
reason, and says why.

**The edit replaces the original in place rather than sitting beneath it.** The first version printed the
message twice, once plain and once marked, and a screenshot made it obvious that this hides the change
rather than showing it. Both versions are still on the screen: the struck words are the model's.

**The marking matches unchanged words in from both ends.** Anything shown as unchanged is
character-for-character the same in both versions. A scattered edit widens the marked span to cover
everything between the changes, which over-reports rather than under-reports. The alternative was a real
alignment algorithm in TypeScript, which 0005 leaves untested, and a diff that quietly misaligns on a
screen whose whole argument is honesty is worse than one that says "this span changed".

**The share is counts, not a percentage.** Two approvals do not support a percentage, and 50% on a
denominator of two implies precision that is not there. Before the first approval it reads "None yet"
rather than a zero that looks like a measurement.

Two things came out different from the plan.

**The HTTP glue was shared rather than copied.** `api/decide.py` would have been a second copy of
`api/draft.py`'s twenty lines of request reading and response writing, and 013 would have made a third.
`JsonEndpoint` holds it once and each endpoint supplies only `answer`. The development server routes both
paths through the same class, so there is still one HTTP implementation rather than a real one and a
local one.

**The edited body is the one free-text field in the project.** 0008 keeps free text out of prompts, and
this text never reaches a model: it is stored beside the draft, rendered by React which escapes it, and
bounded at four thousand characters at the boundary. Worth stating plainly, because "nothing reaching the
model is free text" and "nothing in this project accepts free text" are different claims and only the
first one is true.

Two things this slice does not do. Nothing tests the screen, per 0005. And a decision cannot be undone:
the schema records one decision per draft with no history, and a reviewer who wants a different answer
has Reject for it.
