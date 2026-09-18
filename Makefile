.PHONY: check lint test typecheck lint-web format migrate api smoke

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

# Runs the endpoints locally. `next dev` proxies /api here.
#
# Both env files, in the order Next.js reads them, so the endpoint and the page gate
# agree on the token. `.env` carries the database and the API key, `.env.local` the
# token the pages are served under in development, and the later file wins.
api:
	uv run --env-file .env --env-file .env.local python scripts/serve_api.py

# Applies pending migrations to the database named in the local environment file.
migrate:
	uv run --env-file .env demogym migrate

# Checks that the deployed application renders. Needs the network and the token, which
# is why it is not part of `make check`. See 0005.
smoke:
	uv run --env-file .env python scripts/smoke.py
