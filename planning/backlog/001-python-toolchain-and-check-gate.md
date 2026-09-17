---
slice: 001
title: Set up the Python toolchain and the check gate
status: in progress
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

**Vercel Python version.** Vercel's Python runtime defaults to 3.12 and supports 3.12, 3.13 and 3.14,
set through `.python-version`, `pyproject.toml` or `Pipfile.lock`
(`vercel.com/docs/functions/runtimes/python`, read through context7 on 2026-09-17).
3.13 is offered, so `standards/python.md` needed no correction. `.python-version` holds `3.13` and
`pyproject.toml` sets `requires-python = ">=3.13"`.

**`uv sync` on a clean clone.** The tracked and untracked files were copied to an empty directory with
no `.venv`, and `uv sync --locked` resolved and installed from the lock file with no other setup.
`make check` then passed in that copy.

**`make check` order and exit code.** Output is `ruff format --check`, then `ruff check`, then `pytest`.
Exit code 0.

```
uv run ruff format --check .
2 files already formatted
uv run ruff check .
All checks passed!
uv run pytest
...
tests/test_package.py .                                                  [100%]
============================== 1 passed in 0.00s ===============================
EXIT=0
```

**A deliberate lint error fails the gate and names the file.** Adding an unused `import os` to
`src/demogym/__init__.py`:

```
uv run ruff check .
F401 `os` imported but unused
 --> src/demogym/__init__.py:3:8
Found 1 error.
make: *** [Makefile:7: lint] Error 1
EXIT=2
```

pytest did not run, so the gate stops at the first failure. Removing the import returned it to exit 0.

**Ruff 0.16 reaches Markdown.** `ruff format --check .` reported 27 files against 2 Python files in the
repository. Reproduced on a scratch `t.md`: ruff 0.16 formats Python code blocks inside Markdown by
default, and the 27 was 25 Markdown files plus the 2 Python ones. The planning documents are prose and
not code under test, so `extend-exclude = ["*.md"]` keeps the formatter off them. Recorded because it
changes what the gate covers.

**`setup-uv` has no moving major tag.** The first workflow run failed with
`Unable to resolve action astral-sh/setup-uv@v10, unable to find version v10`. The repository publishes
bare major tags only up to `v7`; the v10 line exists as `v10.0.0`, `v10.0.1` and `v10.1.0` and there is
no `v10` ref. The step is pinned to `astral-sh/setup-uv@v10.1.0`. `actions/checkout@v7` does have the
moving tag and is left as it is.

**CI.** Not yet verified. `.github/workflows/check.yml` runs `uv sync --locked` then `make check` on
push, with no secrets. The condition stays open until a run on a pushed commit is green.

## Outcome
