# Next.js and TypeScript standard

Rules for the web application in this repository. Read before writing or changing TypeScript, TSX or
CSS. Where a rule has a reason that is not obvious, the reason is given.

## Tooling

- Next.js 16, App Router, TypeScript, React 19.
- Tailwind CSS 4, configured through `@theme` in `app/globals.css`. There is no `tailwind.config.js`,
  because version 4 puts the configuration in the stylesheet.
- `npm` manages the dependencies. `package-lock.json` is committed and `npm ci` is what CI runs.
- ESLint 9 with `eslint-config-next`, flat config in `eslint.config.mjs`.
- `tsc --noEmit` typechecks. `strict` is on and stays on.
- `make check` runs `ruff`, `pytest`, `tsc` and `eslint`, in that order, stopping at the first failure.
  A change is not finished until it passes on a clean checkout.
- No component library and no UI kit. The interface is small enough to write, and a kit would decide
  the design language that 007 exists to decide.

There is no formatter for TypeScript and TSX. `ruff` covers Python and nothing covers the web code, so
formatting is a matter of matching the file you are in. Prettier is the obvious fix and it is not here
yet, under the rule 0001 sets: added when the inconsistency actually costs something.

## Layout

- `app/` holds routes. Route segments are lower case and hyphenated.
- `app/[token]/` is everything behind the access gate. The token is a real route segment rather than a
  rewrite, so every link carries it and nothing has to remember to add it back.
- `proxy.ts` at the root is the access gate. Next.js 16 renamed `middleware.ts` to `proxy.ts` and the
  exported function from `middleware` to `proxy`. Older examples will say otherwise.
- A component used by one route lives beside that route. It moves to `components/` at the point a
  second route imports it, and not before.
- One component per file, named the same as the file.
- A file past roughly 150 lines is usually holding a component and a second thing that wants its own
  file.
- No `utils.ts`, no `helpers.ts`, no `lib/misc.ts`. A name that means nothing attracts everything.

## Components

- Server Components by default. `"use client"` goes on the smallest component that genuinely needs
  interaction or browser state, not on the page that contains it.
- Data is read in Server Components. A client component receives what it needs as props.
- A component renders one thing. Past roughly three levels of nesting in the returned markup, there is
  a child component waiting to be named.
- Props are explicit and typed inline unless the type is shared. No prop spreading through a component
  that does not own the props.
- Return markup rather than building strings of it.

## The frontend does no arithmetic

Every number on screen was computed before it got there. Bands, rates, revenue at risk, projections and
costs are calculated in Python and stored on the row. The application reads them and puts them on a
page.

This is the boundary the specification rests on. A figure recalculated in a component cannot be traced
back to the row that produced it, and two places computing the same number will eventually disagree.
Formatting a stored number for display is not arithmetic. Deriving a new one is.

## Names

- A name says what the thing is, in the language of the problem rather than the language of the code.
  `AtRiskQueue`, not `DataTable`.
- Components in `PascalCase`, everything else in `camelCase`.
- Booleans read as an assertion: `isDrafting`, `hasDecision`.
- A name that needs a comment to explain it is the wrong name.

## Types

- No `any`. No `as` to silence the compiler, and no `!` non-null assertion. If the type is wrong, fix
  the type.
- `type` for object shapes. `interface` only when something genuinely extends it.
- Narrow unions rather than optional booleans. A row is `"not drafted" | "drafting" | "drafted" |
  "failed"`, which is four states the compiler can check, not three flags that can contradict each other.
- Nothing typechecks across the Python and TypeScript boundary. 0005 records this as the sharpest edge
  in the project. An endpoint's response shape is agreed by hand, so write the type next to the fetch
  that reads it and keep it honest.

## Errors

- Do not program defensively. Validate at the boundary where untrusted data enters, then trust it
  inside.
- No `try`/`catch` without a specific failure it handles and a specific thing it does about it. Never a
  `catch` that swallows.
- Throw with the values needed to reproduce the situation. A message with no data in it is noise.
- `error.tsx` and `not-found.tsx` are added where a route has a failure worth showing, not as a matter
  of routine.
- A failure states what happened and what to do next. It does not apologise.

## Styling

- Tailwind utilities in the markup. No CSS modules, no styled components, no inline `style` except for
  a value that is genuinely computed.
- Colours, spacing and type scale come from the tokens in `app/globals.css`. A hex code in a component
  is a token that has not been named yet.
- Every response carries `noindex` and `Referrer-Policy: no-referrer`, set in `next.config.ts` so no
  page has to remember. The access token never appears in `robots.txt`.

## Copy

Everything on screen follows the writing rules in `AGENTS.md`. The synthetic-data label is not
decoration: a screen of plausible invented figures without it is indistinguishable from fabricated
evidence.

## Tests

There are none, and that is a decision rather than an omission. 0005 records why: these components
render values that are already computed, so the assertions would restate the markup and would need
rewriting every time the markup moved. `tsc` and `eslint` catch the three things that can actually go
wrong here, which are a name that does not exist, a shape that does not match, and a page that fails to
build.

Nothing verifies that the deployed page renders. A typecheck is not a render. One smoke test against the
deployed URL is the cheapest useful addition and the first one to make.
