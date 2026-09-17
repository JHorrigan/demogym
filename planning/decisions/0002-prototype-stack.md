---
adr: 0002
status: accepted
date: 2026-09-17
supersedes:
superseded_by:
---

# 0002 - Build the prototype on Vercel and Neon rather than on cloud infrastructure

## Context

demogym has to produce something a person can open: a web application on a public URL, backed by a database, showing a synthetic dataset that was generated ahead of time, with a way to advance that dataset while the application is running.

It has no users, no uptime obligation, no real data, nobody on call, and one developer. The whole deployed surface is a web application, a database, and a small set of API endpoints.

A production deployment of the same system would carry obligations this one does not. Real member data under UK GDPR Article 9. Jobs that run whether or not anyone is watching. An operations team that depends on the tool being there in the morning. A security posture that survives review.

The risk in choosing between them is picking infrastructure sized for the second while building the first. That produces a repository where most of the work is deployment scaffolding and very little of it is the thing the project is actually about.

## Decision

The prototype runs on Vercel and Neon.

| Need | Choice |
|---|---|
| Application and hosting | Next.js App Router with TypeScript, deployed on Vercel |
| API surface | Python functions deployed alongside the application on Vercel |
| Database | Neon Postgres, one instance, numbered SQL migrations |
| Generation and seeding | A Python command-line tool in this repository, run locally against Neon |
| Model access, where a model is used | The Anthropic API directly, server side only |
| Continuous integration | One GitHub Actions workflow running `make check` |
| Secrets | Environment variables. `.env` locally, project variables on Vercel |

There is one database and it is the deployed one. The local tooling applies migrations and writes the seed data to the same Neon instance the application reads, so there is no export step and no second copy of the data to keep in step.

Whether a language model is used at all, and for what, is not settled by this decision. What is settled is the route taken when one is.

## Alternatives considered

A cloud deployment on AWS. Each component below solves a problem this project does not have yet, which is the reason for deferring it rather than an argument against it.

**API Gateway in front of Lambda.** The prototype has a handful of endpoints and any rate limiting is enforced in application code. API Gateway earns its place when there are enough routes that authorisation, throttling and per-route limits need to be policy rather than code.

**Fargate for the bulk work.** Generating and seeding a full dataset does not fit inside a function timeout, which is measured in tens of seconds. Here that is resolved by running it locally from a committed tool. On AWS it would be resolved by a scheduled task with no timeout ceiling. The constraint is identical and only the resolution differs by scale.

**Spot capacity for that task.** A batch generation run is interruptible and not latency sensitive, which is the workload Spot exists for. The prototype has no recurring compute to optimise.

**Aurora with serverless capacity.** Neon fills the same role here, which is Postgres that costs nothing when idle. The distinction that matters is not the engine but the boundary. Once the data is real member data, it belongs inside the account that governs it.

**DynamoDB for request-time state.** One piece of state in this system is read and written while a request is in flight, which is the counter behind the rate cap on the endpoint that advances the simulation. It needs a single-key lookup, an atomic increment and an expiry, which is what a key-value store is for. In the prototype that counter is a row in Postgres, which is adequate at one request at a time. The rest of the system stays relational, because the queries that matter aggregate and join across tables, and that is the wrong shape for a key-value store.

**A local development environment.** A containerised Postgres, or a database per developer, or a seeded test database torn down after each run. All three solve the problem of several people needing isolated databases that do not tread on each other, and of work continuing without a network. One developer working against one Neon instance has neither problem. Neon branching is the route if an isolated copy is ever wanted, and it costs less than a container because there is no second schema to keep in step.

**SST or another infrastructure-as-code tool.** The prototype's infrastructure is one Vercel project and one Neon database, both created by hand in minutes and neither likely to be recreated. Infrastructure as code earns its place when there are enough resources that reproducing them by hand is unreliable, or when more than one environment exists.

**Secrets Manager or Parameter Store.** The prototype holds one API key and one database URL. What the managed services add is rotation, audit and per-environment separation, none of which apply to a single set of credentials for synthetic data.

**CloudWatch logs and Sentry.** The prototype has no observability of any kind. This is a genuine gap rather than a deferred nicety. Nothing reports that a generation run failed except the person who started it.

**Alerting to email or Slack.** Nobody is on call. The bulk work is run by hand, so a failure is visible to the person who ran it at the moment it happens.

**Amazon Bedrock, or Claude Platform on AWS, for model access.** This is the one entry that is not about scale. On synthetic data, calling the Anthropic API directly carries no data protection weight. On real member data it would. Attendance records combined with the inferences drawn from them are special category data, so sending them to a third-party API is a processor relationship requiring a data processing agreement and a defensible transfer position. Inference reached from inside the account the data already occupies is a materially different posture. Bedrock is partner-operated with its own pricing and a lag on new features; Claude Platform on AWS is Anthropic-operated with same-day parity. Which of the three is right would be decided by where the data sits, not by preference.

Continuous integration is the one component that is the same in both worlds. A GitHub Actions workflow, running the same `make check`.

## Consequences

What survives a move to cloud infrastructure is most of the project. The schema, the generator, the rules, and the split between work done ahead of time and work done in a request. Those are the parts with reasoning in them.

What does not survive is the deployment configuration. The Vercel project, the Neon connection, the packaging of the Python functions. That is a day of work and it is the part with no judgement in it.

Two runtimes ship in one deployment, so there is a second dependency set and a second cold-start profile to think about. The Python version the project pins is now constrained by what the Vercel runtime offers rather than by what the project would otherwise choose, and `standards/python.md` has to agree with it.

One database means anything the local tool does lands directly on what the deployed application serves. There is no staging copy to get it wrong on first. For synthetic data with one developer that is a fair trade, and it is the first thing that would change on real data.

The prototype has no observability, no alerting, no secrets management beyond environment variables, and no authentication. Each is defensible for synthetic data with one operator, and each would be required before real data reached it.
