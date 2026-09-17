# Backlog

Slices in intended build order. One at a time, finished before the next one opens.

A slice is written out in full shortly before it is built. Detailing all of them now would mean inventing checkable conditions for screens that have not been designed, and those conditions would be wrong by the time anyone read them.

| | Slice | Written | Produces |
|---|---|---|---|
| 013 | Build the site briefing | | A briefing per site, generated on request |
| 014 | Write the running-on-real-data page | | What this does not do, and the regulatory position |
| 015 | Rewrite the README and write the running instructions | | A front door, and a way for someone else to run it |
| 016 | Compare the drafting model | | A measured choice between the three candidates, recorded as an ADR |

001 to 012 are done and sit in `completed/`. The data and the arithmetic are finished: the estate, the equipment and twelve weeks of scores are in Neon, with nineteen members in the High band at the most recent date. 004 was reopened by 006 as expected, and its file carries the amendment. The shell and the design language are in place, so the screens are layout rather than design. The drafting feature is whole: 010 put the model behind a deployed endpoint, 011 wired it to the queue, and 012 recorded what a person decided about what came back. 006 was amended after 011 found a scoring rule that misfired on members inside twelve weeks.

## Where the order comes from

013 first of what remains, and the last feature. It is the second domain the equipment data exists for, and it is the harder prompt: a briefing has to state a link between facts as a hypothesis to check rather than as a finding, which is the constraint 0007 says to stress hardest.

014 to 016 close it out: what the project does not do, how someone else runs it, and the one claim it makes that should rest on measurement rather than assumption.

## Known to be missing

Nothing here covers observability, and 0002 records that as a genuine gap rather than a deferred nicety. A failed run is visible only to whoever started it.
