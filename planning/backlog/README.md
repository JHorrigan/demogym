# Backlog

Slices in intended build order. One at a time, finished before the next one opens.

A slice is written out in full shortly before it is built. Detailing all of them now would mean inventing checkable conditions for screens that have not been designed, and those conditions would be wrong by the time anyone read them.

| | Slice | Written | Produces |
|---|---|---|---|
| 001 | Set up the Python toolchain and the check gate | yes | `make check` passes on a clean clone and runs in CI |
| 002 | Deploy the application behind a link token | yes | A protected URL that deploys on push, and `standards/nextjs.md` |
| 003 | Create the schema and the migration runner | yes | Seven tables in Neon |
| 004 | Generate and seed the estate | yes | Sites, members and six months of entries |
| 005 | Generate and seed the equipment | yes | Around a hundred units across the six sites |
| 006 | Score the estate | yes | `risk_scores` at twelve weekly dates, around twenty in the High band |
| 007 | Build the application shell and the visual design | yes | The chrome, the design language and the states every screen inherits |
| 008 | Build the estate screen | | Six sites ranked by at-risk rate, with the trend |
| 009 | Build the at-risk queue | | Every banded member, High first, with reasons |
| 010 | Build the drafting endpoint | | A deployed Python endpoint that drafts one member |
| 011 | Draft from the queue | | Tone, length and offer controls, Draft all, redraft, the four row states |
| 012 | Record decisions on a draft | | Approve, Edit and Reject, the edit diff, "Approved, not sent" |
| 013 | Build the site briefing | | A briefing per site, generated on request |
| 014 | Write the running-on-real-data page | | What this does not do, and the regulatory position |
| 015 | Rewrite the README and write the running instructions | | A front door, and a way for someone else to run it |
| 016 | Compare the drafting model | | A measured choice between the three candidates, recorded as an ADR |

## Where the order comes from

001 first because 0001 and 0005 both commit to `make check` being the gate, and nothing after it can claim to be done until it exists. It also settles which Python version the Vercel runtime offers, which `standards/python.md` currently assumes.

002 second because deployment is the thing most likely to go wrong late, and discovering that with three screens built is worse than discovering it with none.

003 to 006 build the data and the arithmetic, in the only order they can go in. 006 is where the generator's spread gets tuned against the scoring thresholds, so 004 and 006 will be revisited together.

007 sits between the data and the screens deliberately. Built after it, 008 and 009 are layout against decisions already made. Built without it, each screen invents its own look and the result reads as three different tools.

008 and 009 put computed data on a screen before any model is involved, so that when 010 lands the only new thing is the model.

010 to 013 are the two features. Drafting is split across three slices because the endpoint is provable by a command, the controls are provable on a screen, and the decisions are a separate surface with their own state.

014 to 016 close it out: what the project does not do, how someone else runs it, and the one claim it makes that should rest on measurement rather than assumption.

## Known to be missing

Nothing here covers observability, and 0002 records that as a genuine gap rather than a deferred nicety. A failed run is visible only to whoever started it.
