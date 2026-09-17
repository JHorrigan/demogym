---
slice: 001
title: Set up the Python toolchain and the check gate
status: backlog
depends_on: []
decisions: [0001, 0005]
---

# 001 - Set up the Python toolchain and the check gate

## Goal

`make check` exists, runs on a clean clone, and runs in CI on every push. After this slice, every later slice has something to prove itself against.

## Why now

0001 states that the project uses uv, ruff and pytest behind a single `make check`, plus one workflow running it on push. 0005 defines what that gate runs. `standards/python.md` names the exact configuration. None of it exists in the repository, so three committed documents currently describe something that is not there, and no slice after this one can honestly say it is done.

It also settles an open question that blocks the schema and the endpoint: which Python versions the Vercel runtime actually offers. `standards/python.md` pins 3.13 without that being confirmed.

## In scope

- `pyproject.toml` with the `uv_build` backend, src layout, and `requires-python` set to a version the Vercel Python runtime supports.
- `.python-version`, `uv.lock`.
- ruff configured at line length 100 with rules `E`, `F`, `I`, `UP`, `B`.
- pytest rooted at `tests/`, with `src/demogym/` as the package.
- `Makefile` with `check`, `lint`, `format`, `test`, where `check` runs lint then test and stops at the first failure.
- One GitHub Actions workflow running `make check` on push, needing no secrets.
- Confirm the Vercel Python runtime's supported versions and correct `standards/python.md` if 3.13 is not among them.

## Not in scope

- `tsc` and `eslint`. There is no frontend yet, and 002 extends the gate to cover it.
- Any application code beyond whatever trivial module and test prove the gate runs.
- The database, the generator, any endpoint.

## Done when

- `uv sync` succeeds from a fresh clone with no other setup.
- `make check` exits zero, and its output shows ruff running before pytest.
- Introducing a deliberate lint error makes `make check` exit non-zero and naming the file; removing it makes it pass again.
- The workflow run on the pushed commit is green.
- `standards/python.md` and `pyproject.toml` name the same Python version, and that version is one Vercel offers.

## Evidence

## Outcome
