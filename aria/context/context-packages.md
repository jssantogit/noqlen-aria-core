# Context Packages

Use the smallest context package that can safely complete the task.

## Tiny

Use for isolated one-file or one-test tasks.

Read:

- `AGENTS.md`
- `aria/context/current.md`
- The active `tasks.md` item only

## Standard

Use for normal implementation, spec, or review work.

Read Tiny plus:

- Active `design.md`
- Files targeted by the task
- Relevant tests

## Full

Use only for block planning, formal audit, complex regressions, or architecture disputes.

Read Standard plus:

- Relevant ADRs in `aria/decisions/`
- Relevant architecture and context docs
- Relevant review checklists

## Role defaults

- Planner: Tiny to Standard; Full only for planning, audit, or architecture conflicts.
- Implementer: Standard by default; Tiny for tiny tasks; Full discouraged.
- Reviewer: Standard by default; Full only for formal audits or structural regressions.

## Prompt policy

- Prompts should say what changed, what task is active, and what evidence exists.
- Context files carry standing rules.
- Agents should not read the whole repository by default.
- Escalate to a larger package only when the smaller package cannot answer a safety, design, or validation question.
