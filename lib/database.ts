import { neon } from "@neondatabase/serverless";

/**
 * The read connection to Neon.
 *
 * Queries go over HTTPS rather than a pooled socket, so there is no pool to
 * exhaust and nothing to hold open between requests. The application only reads:
 * 0004 keeps anything that applies a rule in Python, so nothing here writes.
 */
export const sql = neon(requireUrl());

function requireUrl(): string {
  const url = process.env.DATABASE_URL;
  if (!url) {
    throw new Error("DATABASE_URL is not set, so no screen can read anything");
  }
  return url;
}
