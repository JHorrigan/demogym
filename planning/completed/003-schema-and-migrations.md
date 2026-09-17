---
slice: 003
title: Create the schema and the migration runner
status: complete
depends_on: [001]
decisions: [0002, 0003]
---

# 003 - Create the schema and the migration runner

## Goal

The seven tables exist in Neon, created by numbered SQL applied in order by a committed tool.

## Why now

Everything after this writes rows. 0003 puts migrations in the local tool rather than in the deploy, so the tool has to exist before any data does.

## In scope

- Numbered SQL migration files for `sites`, `members`, `entries`, `equipment`, `risk_scores`, `drafts`, `briefings`, as specified.
- A Python command that applies pending migrations in order and records which have been applied.
- Connection by environment variable, `.env` locally, already covered by `.gitignore`.
- Indexes the queries in the specification will need, chosen from the specification rather than guessed.

## Not in scope

- Any data. 004 and 005 seed it.
- Rollback or down-migrations. 0001 applies: they solve a problem this project does not have.
- The application reading any of it.

## Done when

- Running the command against an empty database creates all seven tables.
- Running it a second time applies nothing and says so.
- Every column in the specification's SQL sketch exists with a sensible type, and the uniqueness constraints on `risk_scores` and `drafts` are in place.
- A test proves the runner applies files in numeric order rather than lexical or filesystem order.

## Evidence

**Checked against a throwaway Postgres first.** The SQL was applied to a disposable `postgres:17`
container by hand before it went near Neon, because there is one database and a syntax error found
half-way through it would leave a partly built schema. 0005 keeps Docker out of `make check` and it
stays out: this was one manual run, not a harness dependency.

**Against Neon, an empty database gets all seven tables.**

```
$ make migrate
uv run --env-file .env demogym migrate
Applied 001 create_sites
Applied 002 create_members
Applied 003 create_entries
Applied 004 create_equipment
Applied 005 create_risk_scores
Applied 006 create_drafts
Applied 007 create_briefings
```

**The second run applies nothing and says so.**

```
$ make migrate
No pending migrations.
```

`information_schema` in Neon lists `briefings`, `drafts`, `entries`, `equipment`, `members`,
`risk_scores`, `sites` and `schema_migrations`. The ledger holds numbers 1 to 7 against their names.

**Every column in the specification's sketch exists**, checked column by column against
`information_schema.columns`. Dates are `date`, `entered_at` and `decided_at` are `timestamptz`,
prices and readings are `numeric`.

`decay`, `typical_gap` and `gap_multiple` are nullable, because the arithmetic has no answer for them in
cases the specification describes: decay needs a baseline above zero, a typical gap needs two visits, and
a gap multiple needs a last visit. `baseline` and `recent_rate` are not null, because zero is an answer.

`cost_usd_cents` is `numeric(10, 4)` rather than an integer. A draft costs well under one cent, so an
integer column would round the measurement to zero and leave an estimate, which is the thing the
specification says storing cents was meant to avoid. A stored draft cost came back as `0.0612`.

**The uniqueness constraints are in place**, as primary keys:

```
risk_scores        PRIMARY KEY (member_id, scored_on)
drafts             PRIMARY KEY (member_id, scored_on, attempt)
drafts             FOREIGN KEY (member_id, scored_on) REFERENCES risk_scores(member_id, scored_on)
```

**The constraints reject bad rows rather than merely existing.** Each of these was attempted against the
scratch database:

| Attempt | Result |
|---|---|
| Equipment out of service with no `down_since` | rejected, `equipment_down_since_matches_status` |
| Equipment working with a `down_since` | rejected, same constraint |
| Both consistent forms | accepted |
| Band `critical` | rejected, `risk_scores_band_check` |
| A draft against a scoring date with no score | rejected, composite foreign key |
| A decision with no timestamp | rejected, `drafts_decision_has_a_timestamp` |
| A third attempt | rejected, `drafts_attempt_check` |

**Indexes, chosen from what the specification says the screens read**, not guessed:

```
entries_member_id_entered_at_idx    scoring reads one member's trailing window
entries_site_id_entered_at_idx      the briefing reads a site's attendance by day and time
members_site_id_idx                 the estate screen counts active members per site
equipment_site_id_status_idx        the estate screen shows what is out of service per site
risk_scores_scored_on_band_idx      band counts per scoring date, and the queue's latest date
```

`drafts` and `briefings` are read by their primary keys, so they carry no extra index.

**A test proves numeric order rather than lexical order.**
`test_load_orders_by_number_rather_than_by_filename` writes `10_tenth.sql`, `2_second.sql` and
`1_first.sql`, which are names where the two orders disagree, and asserts `[1, 2, 10]`. Eight tests cover
the runner in total, including that two migrations sharing a number are refused, that non-migration files
are ignored, and that the committed files are numbered from one without gaps. None of them touches a
database.

```
$ make check
uv run ruff format --check .
uv run ruff check .
uv run pytest      9 passed
npx tsc --noEmit
npx eslint
EXIT=0
```

## Outcome

The seven tables exist in Neon, created by numbered SQL applied in order by `demogym migrate`, with a
ledger recording what has been applied. Everything after this slice has somewhere to write rows.

Built as planned, with the ordering logic kept separate from the applying so the order test needs no
database, which is what 0005 asks of the Python surface.

Four decisions the slice left open, settled here.

One migration file per table, seven files, in dependency order. The alternative was one file for the
whole schema. A file per table makes the numeric ordering load-bearing rather than decorative, and it is
what the numeric-order test exercises.

`schema_migrations` is created by the runner rather than by a migration, because a migration that creates
the ledger cannot be recorded in it.

Each migration and its ledger row are written in one transaction, so a failure leaves nothing half
applied. Migrations are not wrapped in a single transaction across all of them, because each one is
independently recorded and independently resumable.

Bands are stored lower case, `high`, `medium`, `low`, and capitalised for display. The specification
writes them capitalised. Formatting for display is allowed by `standards/nextjs.md`, which draws the line
at deriving new values rather than presenting stored ones.

One thing is outstanding and it is not code. `.env.example` needs its `DATABASE_URL` line, and
`.claude/settings.json` denies `Read(./.env.*)`, which catches the one file in that family that is
committed on purpose and holds no secrets. Either the rule narrows to `.env` and `.env.local`, or the
line is added by hand.

Nothing here verifies that a migration applies until a person applies it, which is the gap 0005 names and
accepts. It was applied, by hand, twice, and the output is above.
