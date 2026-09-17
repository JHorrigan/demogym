# Planning

How work on demogym is specified, sliced, built and recorded.

## What is here

| Path | What it holds | When to read it |
|---|---|---|
| `specification.md` | The problem, what is being built, and the constraints on it | Before slicing, and when a slice needs the rule it implements |
| `decisions/` | Architecture decision records, numbered, immutable once accepted | When a decision is being made or questioned |
| `backlog/` | Slices not yet built, numbered in intended order | To find what is next |
| `completed/` | Slices that shipped, each with its outcome appended | Only when asked about past work |
| `history.md` | One line per retired slice | For the narrative of what happened when |
| `templates/` | The slice and ADR templates | When writing a new one |

## The flow

1. The specification says what the project is. It changes rarely.
2. Work is cut into slices in `backlog/`. Each slice is shippable on its own.
3. A slice is built, and it is done when its own `Done when` conditions are met and the evidence is recorded in the file.
4. The slice file moves to `completed/` with an `Outcome` section filled in: what was actually built, what the evidence was, and where it diverged from the plan.
5. One line goes into `history.md`.

## Rules

- One slice at a time. Finish it before opening the next.
- A slice fits on about a page. If it does not, it is two slices.
- Decisions are recorded as ADRs, not in commit messages or conversation. An accepted ADR is never edited; a decision that changes gets a new ADR that supersedes the old one.
- `completed/` is not read unless someone asks about past work. It exists to be auditable, not to be carried around.
- The specification holds the what and the why. Implementation detail belongs in slices, so the specification does not churn.

## Naming

- Slices: `NNN-short-kebab-title.md`, three digits, numbered in intended build order.
- ADRs: `NNNN-short-kebab-title.md`, four digits, numbered in the order decided.
