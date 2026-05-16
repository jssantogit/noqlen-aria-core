# Aria Workflow Contract

This repository follows Aria Workflow. The local repository handoff/source of truth is `docs/aria-core-handoff.md`; compact current task state lives in `aria/context/current.md` and `aria/context/delta.md`.

Reading order before non-trivial work:

1. `aria/context/project.md`
2. `aria/context/scope-boundaries.md`
3. `aria/context/repository-hygiene.md`
4. `aria/context/current.md`
5. `aria/context/delta.md`
6. `aria/context/context-packages.md`
7. `docs/aria-core-handoff.md` when the selected context package requires it
8. Relevant files under `aria/context/`
9. Relevant checklists under `aria/review/`
10. Relevant reusable prompts under `aria/prompts/`

Create and review a spec before non-trivial product implementation, then implement one task at a time.

After changes, run appropriate validation and record the evidence. Keep commits small and focused.

Permanent scope rules live in `aria/context/scope-boundaries.md`.
Repository hygiene rules live in `aria/context/repository-hygiene.md`.
Audit and validation checklists live in `aria/review/`.
