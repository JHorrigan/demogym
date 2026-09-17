---
adr: 0006
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0006 - Gate the deployed site behind a shared link token rather than authentication

## Context

The deployed site is going to two people. It is sent to a recruiter, who forwards it to a client. Neither of them should have to create an account, remember a password, or wait for an email before they can look at it. Friction between receiving the link and seeing the thing is the one cost this decision must not pay.

There is nothing on the site to protect. The data is synthetic, no real person appears in it, and nothing is sent to anybody. What needs protecting is the other direction. The site carries a control that writes rows to a database, and that control may call a language model, which costs money per press. A URL with no gate on it will be found. Crawlers find things nobody linked to, and a public endpoint that spends money is a bill waiting to happen.

So the requirement is narrow. Keep the site out of search results and away from anyone who did not receive the link, without putting a login in front of the two people who did.

## Decision

Access is a single token in the URL path, held in an environment variable. The link sent to the recruiter contains it, and anyone holding that link has full access.

Three things enforce it:

- **The application checks it once, in middleware**, so every page is covered rather than each one remembering to check.
- **The Python endpoints check it themselves**, independently of the application. A gate on the pages alone leaves the endpoint that writes rows reachable by anyone who guesses its path.
- **Every response carries `noindex`**, and the site publishes no sitemap. The token never appears in `robots.txt`, because a disallow rule naming the path would publish the thing it protects.

The site also sends `Referrer-Policy: no-referrer`, so a click from the page to anywhere else cannot carry the token in a `Referer` header.

Rotation is changing the environment variable, redeploying, and sending a new link. There is no revocation list and no per-recipient token.

This is not authentication and the project does not describe it as such. It is a shared secret in a URL. It goes on the list of what this does not do, next to the other things on that list.

## Alternatives considered

**No gate at all.** A public URL, zero friction, nothing to explain. This is the option the friction requirement points at, and it is wrong for one reason: the advance control writes rows and may spend money on model calls. Left public it is an open invitation, and the rate cap from 0003 would be the only thing standing in front of it. The cap should be the second line of defence rather than the first.

**Vercel's built-in deployment protection.** A password on the deployment, configured in the dashboard, no code at all. Rejected because it puts a login screen between the recipient and the page, which is the cost this decision exists to avoid. It is also a plan feature rather than something the repository controls, so nothing in the code would show that access was gated or how.

**HTTP basic auth in middleware.** Cheap to write and genuinely effective. Rejected for the same friction reason, made worse: a browser credential prompt in front of a portfolio piece reads as broken rather than as protected.

**Real authentication, with accounts and email links.** The correct answer for anything holding real data, and what a production deployment would have. Rejected as disproportionate. It is a sign-up flow, a mail provider and a session store, built so that two known people can look at a page of invented numbers.

**A token per recipient.** Two tokens, same access, so the logs show which link was opened and either can be retired on its own. Genuinely useful, and close to being worth it. Rejected under the rule 0001 sets: it adds a lookup and a lifecycle to solve a problem that has not happened, with two recipients who are both expected to open it. If the link spreads further than intended, this is the first change to make.

**An IP allowlist.** Considered and discarded quickly. Neither recipient's network is known in advance, and both are likely to open it on a phone.

## Consequences

The two people who matter click a link and see the site. Nothing is asked of them.

Anyone holding the link has everything. The link will sit in at least two mailboxes and may be forwarded again, and a URL is not a secret in any strong sense. It appears in browser history, in server access logs, and in anything that proxies the request. The gate keeps the site away from strangers and out of search indexes, and it should not be relied on for more than that.

The endpoints repeat the check that middleware already performs. That duplication is deliberate. The application and the Python functions are separate deployables reachable at separate paths, and a check that only one of them performs is not a check.

Losing control of the link costs a redeploy and a new message, and nothing else, because there is no real data behind it.

0002 records that the prototype has no authentication and that authentication would be required before real data reached it. That remains true. This decision adds a door, not an identity, and does not supersede it.
