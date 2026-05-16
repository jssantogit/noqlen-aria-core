# Behavior Budget

Behavior Budget is the per-task limit on how much behavior may change.

It limits:

- Number of behavior changes.
- Public API expansion.
- Number of files touched.
- Number of services or models changed.
- Whether new dependencies are allowed.
- Whether new tests are required.

Every non-trivial spec or task should define a Behavior Budget before implementation starts.

If implementation exceeds the budget, stop and ask for a new task or spec. Do not silently expand scope.

Behavior Budget cannot override `aria/context/scope-boundaries.md`, `aria/context/repository-hygiene.md`, or any active spec non-goals.

## Behavior Budget

- New behaviors:
- Public API changes:
- Files allowed:
- Tests required:
- Dependencies:
- Stop if:
