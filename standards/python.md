# Python standard

Rules for Python in this repository. Read before writing or changing Python. Where a rule has a reason that is not obvious, the reason is given.

## Tooling

- Python 3.13.
- `uv` manages the environment and the dependencies. `uv run`, `uv add`, `uv sync`. Never `pip`, never bare `python` or `python3`.
- `ruff` formats and lints. Line length 100, rules `E`, `F`, `I`, `UP`, `B`.
- `pytest` runs the tests, rooted at `tests/`.
- `make check` runs lint then tests. It is the gate: a change is not finished until it passes on a clean checkout.
- Add dependencies with `uv add`, never by hand-editing `pyproject.toml`, so the lock file stays in step.

## Layout

- src layout. Importable code under `src/demogym/`, tests under `tests/`.
- One module does one thing and its name says which. A module that needs "and" to describe it is two modules.
- A module past roughly 200 lines is usually holding two ideas.
- No `utils.py`, no `helpers.py`, no `common.py`. A name that means nothing attracts everything.
- `__init__.py` holds imports and nothing else. No logic runs on import.

## Functions

- A function does one thing and returns one kind of thing.
- Past roughly 30 lines, or past three levels of indentation, it is doing too much.
- Arguments are explicit. No `**kwargs` pass-through except when wrapping a library that demands it.
- Prefer pure functions. Push side effects to the edges: database writes, API calls, file writes, and clock reads at the boundary, arithmetic in the middle. The middle is then testable without a fixture.
- Return values rather than mutating arguments.

## Names

- A name says what the thing is, in the language of the problem rather than the language of the code. `weekly_visit_rate`, not `calc_val`.
- No single-letter names outside a comprehension or an index.
- Booleans read as an assertion: `is_active`, `has_left`.
- A name that needs a comment to explain it is the wrong name.

## Types and docstrings

- Type hints on every function signature. Built-in generics (`list[str]`, `dict[str, int]`) and `X | None` rather than `Optional[X]`.
- `dataclass` for a record of fields. Pydantic only where data crosses a boundary and genuinely needs validating.
- A short docstring on every public module, class and function: one line saying what it does, plus what it returns when the name does not already say. No parameter tables restating the signature.
- Private helpers get a docstring only where the intent is not plain.
- Comments are sparse. A comment says why. The code says what.

## Errors

- Do not program defensively. Validate at the boundary where untrusted data enters, then trust it inside.
- No `try`/`except` without a specific failure it handles and a specific thing it does about it. Never a bare `except:`, never `except Exception: pass`.
- Let unexpected exceptions propagate. A traceback is more useful than a swallowed error and a wrong number.
- Raise the specific built-in exception. A wrong argument is a `ValueError`. Define a custom exception only when a caller needs to catch it distinctly.
- No backwards-compatibility shims, no deprecation paths. This repository has one caller and a git history.

## Tests

- `pytest`, plain functions, plain `assert`.
- A test name states the case: `test_baseline_uses_median_not_mean`, not `test_baseline_2`.
- Test behaviour, not implementation. A test that breaks on a rename with no behaviour change is a test to rewrite.
- Arithmetic gets tests at the boundaries of the rule, not one happy case in the middle.
- Do not mock code from this repository. Mock only at a genuine external edge, and prefer a fixture built from real shapes.
- A bug fix lands with the test that fails before it and passes after.

## Output

- No `print` in importable code. Scripts and entry points may print.
- No emojis in output, logs, or exception messages.
- Log the values needed to reproduce the situation. A message with no data in it is noise.
