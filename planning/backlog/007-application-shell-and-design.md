---
slice: 007
title: Build the application shell and the visual design
status: backlog
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

## Outcome
