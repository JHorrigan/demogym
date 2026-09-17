.PHONY: check lint test typecheck lint-web format migrate

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

# Applies pending migrations to the database named in the local environment file.
migrate:
	uv run --env-file .env demogym migrate
