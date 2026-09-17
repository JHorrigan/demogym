# History

One line per retired slice, oldest first. Detail lives in the completed slice file; this is the narrative index.

Format: `YYYY-MM-DD - NNN title - what shipped - ADRs touched - divergence from plan`

2026-09-17 - 001 Set up the Python toolchain and the check gate - `make check` running ruff then pytest, green in CI on a clean clone - 0001, 0005, neither changed - ruff 0.16 formats Markdown so `*.md` is excluded, and `setup-uv` has no `v10` tag so it is pinned to `v10.1.0`
2026-09-17 - 002 Deploy the application behind a link token - a Next.js placeholder on Vercel gated by a path token, refusing with a page, plus `standards/nextjs.md` and `tsc` and `eslint` in the gate - 0002, 0005, 0006, none changed - the gate is `proxy.ts` because Next 16 renamed middleware, the token is a real route segment rather than a rewrite, and `vercel.json` was needed to stop Vercel building the repository as a Python project
2026-09-17 - 003 Create the schema and the migration runner - seven tables in Neon, applied in numeric order by `demogym migrate` with a ledger and indexes drawn from the specification - 0002, 0003, neither changed - one migration file per table so the ordering is load-bearing, the ledger is created by the runner rather than by a migration, and bands are stored lower case and capitalised for display
2026-09-17 - 004 Generate and seed the estate - 6 sites, 300 members and 12,110 entries in Neon from a committed generator, with 14 invariant tests each checked by breaking the rule it guards - 0003, 0005, neither changed - arrivals are generated in Europe/London and stored as timestamptz, seeding replaces rather than appends, and a leaving-date bug found by the invariants put 7 entries on members' leaving dates
