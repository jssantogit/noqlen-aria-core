# Workflow vNext

Aria Workflow vNext reduces repeated prompt/context bloat while preserving existing safety rules.

## Current and Delta

- `aria/context/current.md` is the first-stop compact state for the active block or task.
- `aria/context/delta.md` is the rolling handoff between sessions and should be updated after meaningful tasks.
- Neither file replaces `docs/aria-core-handoff.md`; they prevent copying the large handoff into every prompt.

## Context Packages

- Tiny: isolated one-file or one-test tasks.
- Standard: normal implementation, spec, or review work.
- Full: block planning, formal audit, complex regressions, or architecture disputes.

Canonical policy: `aria/context/context-packages.md`.

## Role Prompts

- Planner: `aria/prompts/planner-minimal.md`.
- Implementer: `aria/prompts/implementer-minimal.md`.
- Reviewer: `aria/prompts/reviewer-minimal.md`.

Prompts should describe what changed and what task is active. Standing rules live in context files.

## Behavior Budget

Every non-trivial spec or task should define a Behavior Budget for behavior changes, public API changes, files allowed, tests, dependencies, and stop conditions.

Canonical policy: `aria/context/behavior-budget.md`.

## Test Risk Matrix

Tasks classify risk as High, Medium, or Low. High-risk changes require negative tests and should use TDD where practical.

Canonical policy: `aria/context/test-risk-matrix.md`.

## Fake Hostility

Fake clients must model hostile and degraded conditions, not just happy paths.

Canonical checklist: `aria/review/fake-hostility-checklist.md`.

## ADRs

Use `aria/decisions/` only for significant architectural decisions. Keep ADRs short and supersede rather than rewrite accepted records.

## Not Adopted Now

- Mutation testing policy.
- Pact Broker.
- Heavy agent framework.
- Full A/B testing process.
- Contract harness implementation as part of this workflow-only task.
