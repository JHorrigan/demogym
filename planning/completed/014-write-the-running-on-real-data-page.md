---
slice: 014
title: Write the running-on-real-data page
status: complete
depends_on: [007, 013]
decisions: [0005, 0006, 0007, 0008]
---

# 014 - Write the running-on-real-data page

## Goal

The third screen, written out. What this prototype does not do, what a real deployment would connect
to, the regulatory position, and what the first week of a real engagement looks like. 007 put the route
in the shell with a placeholder on it; this fills it.

## Why now

It is the last thing the honesty rules require and the first thing anybody sceptical will ask for. It
could not be written earlier: the limitations worth stating are the ones the build actually ran into,
and two of them only exist because 011 and 013 found them. Writing it before the features were built
would have produced a list of guesses.

It also comes before 015, because the README points at this page rather than repeating it.

## In scope

- Replace the placeholder at `/[token]/real-data` with the page itself.
- What a real deployment would connect to: access control, membership and billing, the asset register,
  class booking and CRM, and which table each one replaces.
- What the system does not do, gathered in one place rather than left to conversation: nothing is sent,
  no contact suppression or frequency cap, no holdout group so effectiveness cannot be claimed, no
  seasonality model, no authentication beyond a shared link token, members under four weeks unscored,
  no accuracy figure and the reason why, and data only as fresh as the seed.
- The ten datasets deliberately left out, each with what it would add, from the specification.
- The two claims that are narrower than they sound: free text does enter the system even though none of
  it reaches a model, and the briefing's rule against claiming a cause is held by a prompt and a person
  reading the output.
- The regulatory position: special category data under UK GDPR Article 9, profiling, and the four things
  a real deployment needs before it runs.
- The first week of a real engagement, as an ordered list of what actually happens in it.
- The open question the scoring rule still carries, because a real deployment meets it in week one.

## Not in scope

- Any figure read from the database. This page is prose about the system rather than a reading of it,
  and a number hardcoded into it would be wrong the next time the estate is reseeded. Where a count
  matters, the page names the rule rather than the count.
- Any change to the specification. The page is the specification's limitations put on a screen for the
  reader who will never open `planning/`, and where the two disagree the specification is right.
- The README and the running instructions. 015 owns those, and this page is what they point at.
- Anything about model choice beyond what is already decided. 016 measures that.

## Done when

- `/[token]/real-data` carries all eight sections above, and every limitation listed in the
  specification's "Deliberately absent" appears on it.
- Nothing on the page is a figure read from the database or hardcoded from a seed.
- The page reads in the house voice: no dashes standing in for punctuation, no stock phrasing, British
  spelling, no apology.
- The page renders inside the shell with the synthetic-data strip and the cost readout, as every screen
  does.
- No horizontal page scroll at 320px and 390px, and the heading structure is one `h1` with `h2` beneath
  it in order.
- Tabbing through the page shows a focus ring on every link on it.
- `make check` passes.
- Deployed, and checked on the deployment rather than only locally.

## Evidence

Everything below was measured against the built page in headless Chrome, driven over the DevTools
protocol, rather than read off the source. The dev server was started with a known access token so
nothing had to be read out of the environment file.

**The page, its structure and its spine.** Eight numbered sections, and a contents rail whose order
comes from the same list the sections are numbered from, so the two cannot drift:

```
headings: H1 Running this on real data
          H2 What this is | H2 What it would connect to | H2 What this does not do |
          H2 Data deliberately left out | H2 Two claims that are narrower than they sound |
          H2 The regulatory position | H2 The first week of a real engagement |
          H2 What is still open

rail links: 8, anchors that resolve to nothing: 0
sections: what-this-is, what-it-would-connect-to, what-this-does-not-do, left-out,
          narrower-claims, regulatory-position, first-week, still-open
rail order matches section order: true

strip: true          cost readout: true          words on the page: 1878
```

**Every limitation the specification records appears on the page.** Thirty phrases checked against
the rendered text, covering the ten cut datasets, the nine things the system does not do, both
narrower claims, the four regulatory requirements and both open questions:

```
checked 30 required phrases, missing 0
```

**Nothing on the page is read from the database.** The route imports no query module, calls no
`fetch`, and is not a client component:

```
$ grep -rn 'from "@/lib\|fetch(\|use client' app/[token]/real-data/
(no matches)

imports across the route:  ./Contents  ./Note  ./Pairs  ./Section  ./Steps
                           ./absences  ./feeds  ./leftOut  ./sections  react
```

Every number in the copy is a rule rather than a reading: four weeks, twelve weeks, three weeks, one
visit a week, six months, Article 9. The one estate figure on it, six sites averaging fifty members,
is the same figure the shell's own header already carries and comes from the specification rather
than from a row. It is the only sentence on the page that would need editing if the estate were
regenerated at a different size.

**A focus ring at every stop.** Tab dispatched as a real key event and the computed outline read off
`document.activeElement` each time:

```
  1  shell a  "Estate"                            solid 2px rgb(99, 96, 79)    yes
  2  shell a  "At-risk queue"                     solid 2px rgb(99, 96, 79)    yes
  3  shell a  "Running this on real data"         solid 2px rgb(26, 24, 20)    yes
  4  main  a  "What this is"                      solid 2px rgb(31, 77, 63)    yes
  5  main  a  "What it would connect to"          solid 2px rgb(31, 77, 63)    yes
  6  main  a  "What this does not do"             solid 2px rgb(31, 77, 63)    yes
  7  main  a  "Data deliberately left out"        solid 2px rgb(31, 77, 63)    yes
  8  main  a  "Two claims that are narrower tha"  solid 2px rgb(31, 77, 63)    yes
  9  main  a  "The regulatory position"           solid 2px rgb(31, 77, 63)    yes
 10  main  a  "The first week of a real engagem"  solid 2px rgb(31, 77, 63)    yes
 11  main  a  "What is still open"                solid 2px rgb(31, 77, 63)    yes
 12  shell a  "Interface states"                  solid 2px rgb(31, 77, 63)    yes
```

The thirteenth stop is the Next.js development overlay, which is not part of the page.

Reading the computed outline after calling `element.focus()` reported no ring on any of the eight
links, because a scripted focus does not match `:focus-visible` here and the blanket rule in
`globals.css` is written against it. The ring is real and the measurement was wrong, which is why
this is dispatched as a key event.

**Phone widths.**

```
320px: page 320 vs viewport 320   nothing overflows its box
390px: page 390 vs viewport 390   nothing overflows its box
```

**Two things a screenshot caught that the markup did not.**

The first: at 1280px the section rules ran the full width of the shell while the prose stopped at a
reading measure, so two thirds of every rule crossed empty paper. The page is now held to a sheet
width and the rules stop with the text.

The second: the two qualified claims in section 05 were marked down their left edge, and the two open
questions in section 08 were not, although they are the same kind of statement. Both now use one
`Note` component, which also took the duplicated markup out of the page.

**The copy against the writing rules.**

```
dashes standing in for punctuation:  0
stock phrasing:                      0
American spellings:                  0
emoji:                               0
```

One match came back on the stock-phrasing sweep, "simply not coming", which is the specification's
own wording and means merely rather than hedging. It stays.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      161 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

**The deployment.** Commit `1286af4`, against `https://demogym-ten.vercel.app`. The same checks, run
against the deployment rather than a local build:

```
GET https://demogym-ten.vercel.app/<token>/real-data  status=200  65285 bytes
required phrases: 30 checked, 0 missing
sections present: 8 of 8
h2s in order: What this is | What it would connect to | What this does not do |
              Data deliberately left out | Two claims that are narrower than they sound |
              The regulatory position | The first week of a real engagement | What is still open
synthetic-data strip: True    cost readout: True    contents rail: True
```

Driven in a browser against the deployment:

```
rail links: 8, anchors that resolve to nothing: 0
rail order matches section order: true
words on the page: 1878

320px: page 320 vs viewport 320   nothing overflows its box
390px: page 390 vs viewport 390   nothing overflows its box
```

Twelve tab stops, every one of them ringing, and the thirteenth wraps back to the first, so there is
no development overlay on the deployment as there is locally:

```
  1  shell a  "Estate"                            solid 2px rgb(97, 95, 78)    yes
  2  shell a  "At-risk queue"                     solid 2px rgb(99, 96, 79)    yes
  3  shell a  "Running this on real data"         solid 2px rgb(26, 24, 20)    yes
  4  main  a  "What this is"                      solid 2px rgb(31, 77, 63)    yes
  5  main  a  "What it would connect to"          solid 2px rgb(31, 77, 63)    yes
  6  main  a  "What this does not do"             solid 2px rgb(31, 77, 63)    yes
  7  main  a  "Data deliberately left out"        solid 2px rgb(31, 77, 63)    yes
  8  main  a  "Two claims that are narrower tha"  solid 2px rgb(31, 77, 63)    yes
  9  main  a  "The regulatory position"           solid 2px rgb(31, 77, 63)    yes
 10  main  a  "The first week of a real engagem"  solid 2px rgb(31, 77, 63)    yes
 11  main  a  "What is still open"                solid 2px rgb(31, 77, 63)    yes
 12  shell a  "Interface states"                  solid 2px rgb(31, 77, 63)    yes
 13  shell a  "Estate"                            solid 2px rgb(99, 96, 79)    yes
```

The first attempt at this check read the token out of `.env.local` and the deployment answered 401.
The two files hold different tokens: `.env.local` is the one `next dev` uses and `.env` is the one
the deployment was given. The check reads `.env`.

## Outcome

The third screen is written. Eight numbered sections carry what the prototype does not do, the four
systems a real deployment would read instead of the generator, the ten datasets cut and what each
would add, the two claims that are narrower than they sound, the regulatory position, the first week
of a real engagement, and the two questions still open.

`page.tsx` holds the prose and the structure. `Section` numbers each one from `sections.ts`, which
`Contents` also numbers from, so the rail and the page cannot drift apart. `Pairs` renders a term
against what there is to say about it, `Steps` an ordered list where the order is load-bearing, and
`Note` a statement that needs qualifying. The three long lists live in `feeds.ts`, `absences.ts` and
`leftOut.ts`, which keeps the page to the shape of the document rather than the weight of its
content.

Three decisions the slice left open, settled here.

**The page reads nothing.** It imports no query module and calls no `fetch`, so there is no figure on
it that could go stale or contradict a row. Every number in the copy is a rule: four weeks, twelve
weeks, three weeks, one visit a week, Article 9. The single exception is six sites averaging fifty
members, which is the specification's own figure and the one the shell header already carries, and it
is named in the evidence rather than left to be noticed.

**Observability is on the page.** It was recorded in the backlog README as a genuine gap rather than
a deferred nicety, and nowhere a reader would see it. A limitation that only appears in `planning/`
is not part of the deliverable.

**The first week is written as five steps, and none of them is model work.** Four of them are getting
an export, joining it, rescoring against real history and reading the queue with the person who would
work it. The fifth opens the impact assessment. That is the honest answer to what a real engagement
starts with, and it is more convincing than a list of features.

Three things came out different from the plan.

**Two defects only the screenshot found.** At full width the section rules ran the whole width of the
shell while the prose stopped at a reading measure, so most of every rule crossed empty paper; the
page is now held to a sheet width. And the two qualified claims in section 05 were marked down their
left edge while the two open questions in section 08, which are the same kind of statement, were not.
Both now use one `Note`, which also took duplicated markup out of the page. That is the third time in
this project a screenshot has caught something the markup did not.

**The focus-ring measurement was wrong before the ring was.** Reading the computed outline after
calling `element.focus()` reported no ring on any of the eight links. A scripted focus does not match
`:focus-visible`, which is what the blanket rule in `globals.css` is written against. Dispatching Tab
as a real key event shows the ring at every stop. The page was never at fault and the check was.

**The deployment check needed the right environment file.** `.env.local` and `.env` hold different
tokens, the first for `next dev` and the second for the deployment, and reading the wrong one
answered 401. Worth knowing for 015 and 016, which both have to reach the deployment.

What this slice does not do: it says nothing that the specification does not already say. It is the
specification's limitations put in front of the reader who will never open `planning/`, and where the
two disagree the specification is right.
