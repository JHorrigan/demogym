.PHONY: check lint test typecheck lint-web format

check: lint test typecheck lint-web

lint:
	uv run ruff format --check .
	uv run ruff check .

test:
	uv run pytest

typecheck:
	npx tsc --noEmit

lint-web:
	npx eslint

format:
	uv run ruff format .
	uv run ruff check --fix .
