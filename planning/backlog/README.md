# Backlog

Slices in intended build order. One at a time, finished before the next one opens.

A slice is written out in full shortly before it is built. Detailing all of them now would mean inventing checkable conditions for screens that have not been designed, and those conditions would be wrong by the time anyone read them.

| | Slice | Written | Produces |
|---|---|---|---|
| 012 | Record decisions on a draft | | Approve, Edit and Reject, the edit diff, "Approved, not sent" |
| 013 | Build the site briefing | | A briefing per site, generated on request |
| 014 | Write the running-on-real-data page | | What this does not do, and the regulatory position |
| 015 | Rewrite the README and write the running instructions | | A front door, and a way for someone else to run it |
| 016 | Compare the drafting model | | A measured choice between the three candidates, recorded as an ADR |

001 to 011 are done and sit in `completed/`. The data and the arithmetic are finished: the estate, the equipment and twelve weeks of scores are in Neon, with nineteen members in the High band at the most recent date. 004 was reopened by 006 as expected, and its file carries the amendment. The shell and the design language are in place, so the screens are layout rather than design. 010 put the model behind a deployed endpoint and 011 wired it to the queue, so the drafting feature is whole apart from the decision a person makes on what comes back.

## Where the order comes from

012 first of what remains. It is the last part of the drafting feature and the one the whole human-in-the-loop argument rests on: a message exists on the screen and nothing has happened to it yet.

012 and 013 are what is left of the two features. Drafting was split across three slices because the endpoint is provable by a command, the controls are provable on a screen, and the decisions are a separate surface with their own state.

014 to 016 close it out: what the project does not do, how someone else runs it, and the one claim it makes that should rest on measurement rather than assumption.

## Known to be missing

Nothing here covers observability, and 0002 records that as a genuine gap rather than a deferred nicety. A failed run is visible only to whoever started it.
