---
adr: 0003
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0003 - Generate the dataset locally and advance the simulation in a request

## Context

demogym has two kinds of work, and they are different sizes.

Building the dataset is the large one. It applies the schema, creates the sites and the members, and writes months of activity across all of them. It runs a handful of times: once to stand the thing up, and again whenever the rules that produce the data change.

Advancing the simulation is the small one. It adds a day of activity to a dataset that already exists. It is bounded by the size of the estate rather than by the length of the history, and it is the thing a person presses a button to do while looking at the page.

Neither of these is how a real deployment would get its data. In a working gym the rows arrive from the systems that already produce them. The access control or turnstile system records who came in and when. Equipment and class booking systems record what was used. The membership and billing system says who is active and on what plan. Staff key in by hand whatever the systems miss. The application reads a database that those feeds keep current, and nobody generates anything.

demogym has none of those feeds, so the dataset has to be manufactured and then moved by hand. Building it stands in for the history those systems would already hold, and advancing it stands in for a day of them reporting in.

Two constraints apply to where each of them can run. A Vercel function has a maximum duration measured in tens of seconds, which a full build will exceed and a single day will not. And a public URL means anything reachable from the page is reachable by anyone who finds it, so whatever runs in a request needs a ceiling that does not depend on people being polite.

There is also a fidelity argument. A real system loads its history once and then receives small increments as they happen. A prototype that rebuilds everything on demand takes a shape nothing in production takes.

## Decision

Bulk work runs locally. Incremental work runs in a deployed function.

| | Local tool | Deployed API |
|---|---|---|
| Schema migrations | yes | no |
| Build the dataset | yes | no |
| Advance by one step | no | yes |
| Reads for the application | no | yes |

The local tool is a Python command-line program committed to this repository and run against Neon, so anyone reading the repository can see exactly how the data was produced.

The endpoint that advances the simulation does one bounded step per call and carries a rate cap enforced server side. Nothing reachable from a request does work whose size is not known before it starts.

## Alternatives considered

**Run everything in deployed functions.** Break the build into chunks small enough to fit the duration ceiling, drive it from a schedule or a queue, and keep state so a run can resume. Vercel provides the pieces, including Queues and Worker Services with a Python SDK, so this is available rather than hypothetical. Rejected as disproportionate. It adds chunk state, resumability and idempotency to a job that is run by one person a handful of times, and it puts the unbounded half of the work behind a public URL. ADR 0001 applies.

**Run everything locally and let nothing deployed do work.** The application becomes a pure reader over a database somebody else filled. Architecturally this is the cleanest option and it removes the rate cap entirely. Rejected because the dataset would then be frozen, and a static snapshot is a screenshot with extra steps. The ability to move the data and watch the application respond is most of what makes the thing worth opening.

**Advance the simulation on every page view instead of on a button.** No control to build, and the data is always current. Rejected because it turns idle browsing into database writes, and it removes the one property that makes a cap easy to reason about, which is that advancing is something a person chooses to do.

**Ship a SQL dump or fixture file instead of a generator.** A committed dump is reproducible, needs no tooling to load, and removes the local tool entirely. Rejected for two reasons. The rules that produce the data are part of what this project is demonstrating, and a dump hides them behind a wall of INSERT statements. More practically, advancing the simulation needs the same rules the seed used, so those rules have to exist as code regardless. A dump would mean maintaining both.

**A broker and a worker process.** The production answer for genuinely long jobs, and it would lift the duration ceiling properly. Rejected on the same grounds as the first option, with more moving parts and the same conclusion.

## Consequences

The generation rules have to exist as importable code rather than as a script, because two callers need them: the local build and the deployed advance. What language those callers are written in, and whether they share one implementation, is decided in 0004.

Anyone can read the generator in the repository. Running it needs a database URL, which they will not have, so it is legible rather than reproducible by a stranger. That is the correct trade for a prototype writing to a single shared database.

The rate cap is load-bearing. It is the only thing between a public control and unbounded writes, so it needs a test rather than a comment, and that test is part of the first slice that ships the endpoint.

Nothing advances on its own. There is no scheduler, so the dataset moves when someone presses the button and at no other time. A real deployment would run this nightly whether anyone was watching or not, and that difference belongs on the page that says what this is not.

The local tool and the advance endpoint sit where a real ingestion path would. Nothing here reads an access control system, a booking system or a billing export, and no staff-facing form writes a row. Replacing the generator with those feeds is the first work a real deployment would do. Until then, every row in the database was written by code in this repository rather than observed in a gym, which is the concrete meaning of the synthetic-data rule the project runs on.

Data on the deployed site is only as fresh as the last build or the last advance. For synthetic data that is not a cost. On real data it would be the first thing to change.

Whether a step is produced by rule or by a language model is not decided here. Either way it runs in the same place and under the same cap, and if a model is involved the cap becomes a spend ceiling as well as a write ceiling.

The build has no observability, which follows from 0002. Nothing reports that a run failed except the person who started it, and that person is standing there, because the run is something they typed.
