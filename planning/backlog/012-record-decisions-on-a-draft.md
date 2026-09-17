---
slice: 012
title: Record decisions on a draft
status: backlog
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

## Outcome

Filled in when the slice moves to `completed/`.
