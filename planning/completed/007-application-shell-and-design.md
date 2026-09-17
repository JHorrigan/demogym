---
slice: 007
title: Build the application shell and the visual design
status: complete
depends_on: [002]
decisions: [0006, 0008]
---

# 007 - Build the application shell and the visual design

## Goal

The shell, the chrome and the design language that every screen afterwards inherits, built against fixtures before any screen needs it.

## Why now

Without this, each screen invents its own look and the result reads as three different tools. The header also carries two things the honesty rules require on every page, and that is not something to bolt on per screen.

It comes after the data slices and before the screens so that 008 and 009 are layout work against decisions already made, rather than design work disguised as feature work.

## In scope

- Navigation and layout shell covering the estate, the queue and the real-data page.
- Header on every page: the synthetic-data banner, and the running inference cost.
- One visual identity. Type, colour and spacing as tokens rather than ad-hoc values.
- The primitives the screens need: table, badge for the bands, button, and the row states.
- Loading, empty and failed states as reusable pieces. 0008 requires an empty queue to read as deliberate rather than broken, so the empty state is part of the work and not an afterthought.
- Responsive down to phone width. Both recipients are likely to open this on a phone.
- Accessibility baseline: a visible focus ring on every interactive element, labelled controls, semantic landmarks, and animation guarded by `prefers-reduced-motion`.
- Restyle the refusal page from 002 into the same design language.

## Not in scope

- Any query or real data. The shell renders against fixtures.
- The screens themselves. 008 and 009 build those inside this shell.
- Any model call or cost figure that is real. The header shows a placeholder until 011 makes it live.

## Done when

- Every route renders inside the shell, and the banner and the cost readout are present on all of them.
- Empty, loading and failed states exist as components and can be seen rendered.
- The application is usable at phone width with no horizontal scrolling.
- Tabbing through any page shows a visible focus ring on every interactive element.
- Animation is suppressed when `prefers-reduced-motion` is set.
- Colours meet contrast requirements against both surfaces they sit on.
- `make check` still passes.

## Evidence

Everything below was measured in headless Chrome against the built application, driven over the
DevTools protocol, rather than read off the source.

**The aesthetic direction.** An operations desk, not a marketing page. A warm paper ground, hairline
rules, squared corners throughout, wide-tracked uppercase labels over each reading, and every number set
in a monospace with tabular figures so columns line up and a reader can compare them down a page. Archivo
for text, Azeret Mono for every figure and account number. The specification says it should look like an
internal operations tool, and the distinctiveness comes from density and precision rather than decoration.

**Every colour was chosen by measurement, not by eye.** Ratios against the two grounds they sit on:

| Token | Hex | On paper | On white |
|---|---|---|---|
| ink | `#1a1814` | 16.27 | 17.73 |
| ink-dim | `#63604f` | 5.81 | 6.33 |
| ink-faint | `#8a8674` | 3.36 | 3.66 |
| high | `#a62b16` | 6.47 | 7.05 |
| medium | `#7a5200` | 6.35 | 6.92 |
| low | `#2f5a72` | 6.82 | 7.43 |
| accent | `#1f4d3f` | 8.79 | 9.58 |
| edge | `#7e7a68` | 3.96 | 4.31 |

Everything carrying text clears 4.5:1. `ink-faint` is 3.36:1 and is used for large text and
non-essential marks only. `edge` is the border of anything clickable and clears the 3:1 a control needs
to be identifiable. `rule` at 1.76:1 is a table hairline, which is structure rather than a control.

The first banner design was a pale amber tint, which measured 1.03:1 against the paper and read as
nothing at all. It is now a solid dark strip with an amber marker down its left edge: paper on strip is
13.48:1 and the marker on strip is 6.83:1. That also makes it survive being cropped into a screenshot,
which the honesty rules need it to.

The three band colours sit within half a stop of each other, because each has to clear 4.5:1 against the
same paper. Telling them apart therefore cannot rest on colour, so every badge carries the word as well.

**Every route renders inside the shell, with the banner and the cost readout on all of them.**

```
/                status=200  Inference cost  Synthetic data
/queue           status=200  Inference cost  Synthetic data
/real-data       status=200  Inference cost  Synthetic data
/interface       status=200  Inference cost  Synthetic data

refusal page     status=401  Synthetic data  not valid
```

The strip and the readout live in `app/[token]/layout.tsx` rather than on each page, so no screen can
ship without them. The refusal page carries the strip too.

**Empty, loading and failed exist as components and can be seen rendered.** `/[token]/interface` renders
every primitive and every state with invented values, linked from the footer. It holds the four bands,
the three button tones, all four row states including the three failure kinds, three real reason strings,
and the empty, loading and failed blocks.

**No page overflows at phone width.** Document `scrollWidth` against the viewport, on each route:

```
at 320px:                                     at 390px:
  estate     320 vs 320  no overflow            estate     390 vs 390  no overflow
  queue      320 vs 320  no overflow            queue      390 vs 390  no overflow
  real data  320 vs 320  no overflow            real data  390 vs 390  no overflow
  interface  320 vs 320  no overflow            interface  390 vs 390  no overflow
```

A dense table does not fit a phone and is not made to. It scrolls inside its own container, measured at
356px of container against 625px of content, so the page itself never scrolls sideways.

**Tabbing shows a ring on every interactive element.** Tab was dispatched repeatedly and the computed
outline read off `document.activeElement` at each stop:

```
 1  a "Estate"                 solid 2px rgb(31, 77, 63)   yes
 2  a "At-risk queue"          solid 2px rgb(31, 77, 63)   yes
 3  a "Running this on "       solid 2px rgb(31, 77, 63)   yes
 4  button "Draft all"         solid 2px rgb(31, 77, 63)   yes
 5  button "Draft"             solid 2px rgb(31, 77, 63)   yes
 6  button "Draft all"         solid 2px rgb(31, 77, 63)   yes
 7  button "Try again"         solid 2px rgb(31, 77, 63)   yes
 8  a "Interface states"       solid 2px rgb(31, 77, 63)   yes

elements reached with no ring: none
```

Nine elements match the interactive selector and eight are reached, because the disabled Redraft button
is correctly not in the tab order. One `:focus-visible` rule in `globals.css` covers all of them, so no
component has to remember.

**Animation is suppressed under `prefers-reduced-motion`.** The same page under both emulated settings:

```
no preference:  media query reports reduce: False
                animation-duration 2s, iterations infinite

reduce:         media query reports reduce: True
                animation-duration 1e-05s, iterations 1
```

Ten animated elements on the page, all covered by the blanket guard.

**Three things the screenshots caught that the markup did not.**

The synthetic-data strip took three lines at the top of every page on a phone. It now keeps the claim
that the figures were generated by code on small screens and adds the rest of the statement from `sm`
up, which is two lines rather than three without weakening what it says.

A table column cut off mid-word read as broken rather than as scrollable. The scroll container is now a
keyboard-reachable region, which is what a scrollable area needs anyway and which gives it a focus ring,
and a short fade sits over its right edge below `sm`.

The skeleton bars and the drafting mark were rounded where everything else in the language is squared.

`.label` uppercases, and the refusal page used it for the product name, which rendered a deliberately
lower-case name as DEMOGYM.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      87 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

The shell, the chrome and the design language exist, and 008 and 009 are now layout against decisions
already made.

`app/[token]/layout.tsx` is the shell. `components/` holds the pieces every screen shares: the strip, the
cost readout, the navigation rail, the band badge, the table primitives, the button, the three page
states and the four row states. Routes exist for the estate, the queue and the real-data page, each with
a short statement of what it will hold, plus the interface reference page.

Four decisions the slice left open, settled here.

**Light rather than dark.** The specification says a row gets cropped into a screenshot and travels
without its header, and a warm paper ground screenshots and prints cleanly. A site manager also reads
this in a bright room. There is no dark mode and no theme switch: the slice asks for one visual identity
and a second one is a second thing to keep right.

**The cost readout shows zero, and zero is the true figure** rather than a placeholder, because no model
call has been made. 011 wires it to the stored token counts. A made-up number in that position would be
exactly the kind of thing the honesty rules exist to stop.

**The daily limit is not styled as a failure.** It is one of the four row states and the only one of the
three failure kinds that is the cap working as designed. Dressing it in the same red as a broken call
would report a deliberate constraint as a malfunction, which the specification says in terms it should
not.

**A dense table scrolls inside itself at phone width** rather than restacking into cards. Cards for the
queue would be a second layout to design and keep in step, and the queue's whole point is comparing rows.
If that turns out to read badly on a real phone in 009, the row becomes the thing to redesign.

Two things this slice does not do. The shell renders against fixtures and touches no data, so nothing
here proves a query works. And no test covers any of it: 0005 puts the frontend behind `tsc` and `eslint`
and records that a typecheck is not a render. The measurements above are the substitute, and they were
taken by hand rather than by anything that will run again on the next change.
