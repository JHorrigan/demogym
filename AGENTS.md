# AGENTS.md

Instructions for any agent or person working in this repository. These govern the work; they are not suggestions.

## What this is

demogym is member-retention tooling for a fictional multi-site gym operator, built end to end on synthetic data.

It is a build specification and a working prototype, not a product. The point is to show a way of working: take a stated business problem, pick the narrowest version that produces real value, build it end to end, and be explicit about what running it on live data would take.

## Honesty rules

Non-negotiable. These are why the prototype can be shown to anyone.

- **All data is synthetic, and anything built on it says so.** Plausible invented figures without that label are indistinguishable from fabricated evidence.
- **No real operator's name, branding or identity appears anywhere.** Not in code, copy, commits, or the deployment.
- **Limitations are part of the deliverable.** What this does not do is written down, not left to conversation.
- **Report outcomes faithfully.** If a check fails, say so with the output. If a step was skipped, say that. Do not claim a slice works until it has been run and verified.

## Writing

Applies to every word in the repository and every word on screen: documentation, commit messages, code comments, and user-facing copy.

- **Nothing reads as machine-written.** No em dash or en dash as prose punctuation, and no `--` standing in for one. Use a full stop, a comma, or two sentences. A hyphen inside a range or a compound word is correct typography and stays.
- **No stock phrasing.** "Seamless", "effortless", "unleash", "delve", "at your fingertips", "a testament to", "in today's fast-paced", and their relatives. Name the specific thing instead.
- **No hedging filler.** "It is worth noting", "importantly", "essentially", "simply". If it is worth noting, note it.
- **No tricolon padding.** Three adjectives where one carries the meaning is a tell.
- **No apologising in copy.** Say what happened and what to do next.
- **British spelling.**
- **No emojis anywhere.** Code, output, logs, commit messages, pull requests.
- Vary sentence length. A uniform rhythm is its own tell.

## Coding standards

Before writing code in a language, read the standard for that language. They are rules, not suggestions.

- `standards/python.md`
- `standards/nextjs.md`, which covers TypeScript, TSX and Tailwind

A language gets its standard in the same commit as the decision that brings the language into the project.

## Conventions

- Python is managed with `uv`. `uv run`, `uv add`. Never `pip`, never bare `python`.
- Verify third-party library calls against current documentation through the `context7` MCP before writing or changing them. These APIs drift and training memory goes stale.
- One-line commit messages: an imperative summary, nothing else. No area prefix, no trailers, no co-author lines.
- Comments are sparse. Clear names and short docstrings instead.
- Short modules, short functions.
- Do not over-engineer. No speculative abstraction, no defensive layers around problems that do not exist yet. No exception handling without a failure it actually handles.

## Planning

Specification, decisions, slices and history live in `planning/`. Read `planning/README.md` first: it is the map, and it says when to read anything else.

## How to work

- Work incrementally. Small steps, each validated before the next one starts.
- Identify the root cause before fixing anything. Reproduce it, prove it, then fix it. No workarounds, no guessing.
- One test at a time. Be methodical.
- Do not run `git commit`. Propose the commit message and leave the commit to a human.
- No git worktrees. The repository is small enough to work in directly.
