---
adr: 0001
status: accepted
date: 2026-09-16
supersedes:
superseded_by:
---

# 0001 - Keep the harness minimal and add mechanisms only when they earn their place

## Context

demogym is built by one person, in one repository, as a sequence of dependent slices, in a public repository.

A modern agentic development setup offers a great deal more machinery than that requires: agents that commit their own work, git worktrees for parallel agents, subagent fan-out, issue-tracker integrations, multi-repository layouts, containerised environments and multi-stage delivery pipelines. Every one of them solves a real problem on a team of several people working concurrently on a large codebase.

None of those conditions hold here. The risk is not that the project is under-tooled; it is that machinery gets added because it is available, leaving tooling in the repository that nothing depends on.

## Decision

Use the smallest harness that does the job, and record what was left out.

In use:

- `uv` for Python, `ruff` for format and lint, `pytest` for tests, behind a single `make check` gate.
- A project permission file that blocks the agent from committing, pushing, or reading secrets.
- `AGENTS.md` as the instruction file, per-language coding standards in `standards/`, and `planning/` for specification, decisions and slices.
- One CI workflow that runs `make check` on push.

Anything else is added only when a specific, repeated pain justifies it, and the ADR that adds it names that pain.

## Alternatives considered

**Agents committing their own work.** Every commit should be one a person read before it landed, and authorship should mean what it says. The agent proposes a message; a human commits.

**Git worktrees and parallel agents.** Worktrees isolate concurrent work. The build is a chain of dependencies, each slice resting on the one before it, so there is nothing to run in parallel. The isolation would cost more in ceremony than the sequencing discipline it replaces.

**Subagent fan-out and multi-agent orchestration.** Useful for sweeping a large codebase. Here it would spend tokens to review a few hundred lines, and it would blur who decided what, when the decision record is itself a deliverable.

**A multi-repository split.** A production estate would put the components in separate repositories. The deliverable here is the end-to-end story, and the seams between the components are the most important thing to be able to show in one place. Directory boundaries carry the same separation at a fraction of the cost.

**An issue tracker and a Jira MCP integration.** The backlog is a handful of files in `planning/backlog/`, readable by anyone who opens the repository. Moving it to a board would move the planning out of the repository and add an integration that serves a team that does not exist.

**A full delivery pipeline.** Matrix builds, staging environments, deploy gates and branch protection serve a team merging concurrently. One developer on one branch does not need them. A single workflow running `make check` is kept, because a check that passes on a clean machine is evidence and a check that passes only on the author's machine is a claim.

**Hooks that act on every edit.** Format-on-write is cheap, but `make check` already catches formatting, and a hook that silently rewrites files makes a diff harder to account for.

**Containers and infrastructure as code.** Both earn their place when an environment has to be reproduced, or when more than one of them exists. A single developer machine and a prototype on synthetic data is neither.

## Consequences

Every mechanism in the repository is in use. There is no unused tooling.

The costs are real. Commits are gated on a human being present, so work cannot run unattended. Without worktrees there is no way to explore two approaches at once. None of the machinery listed above is exercised by this project.

The test for adding anything later is a named, repeated pain, not a capability that happens to be available.
