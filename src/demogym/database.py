"""Opens a connection to the one Postgres database this project has."""

import os

import psycopg


def connect() -> psycopg.Connection:
    """Connects using DATABASE_URL, which is the deployed Neon instance."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return psycopg.connect(url)
