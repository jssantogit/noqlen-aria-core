# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/minimal-ui-shell-planning/requirements.md`.
- [x] Read `aria/specs/features/minimal-ui-shell-planning/design.md`.
- [x] Confirm Bloco 0-4 validation passes (CLI help, doctor, py_compile, pytest).
- [x] Confirm spec directory does not exist yet (clean creation).
- [x] Confirm no source/test files exist at `src/noqlen_aria/app_shell.py` or `tests/test_app_shell.py`.
- [x] Confirm `pyproject.toml` has no modifications to make.

## TDD classification

Not applicable for this task. This is a planning/spec task with zero implementation.

Future implementation tasks will follow TDD for:
- `AppShellAdapter` state composition correctness (all sub-states must be populated correctly).
- `AppShellInput` routing (every input must route to the correct service).
- Anti-coupling enforcement (grep verification that UI layer does not import forbidden modules).
- `FakeAppShellAdapter` must be deterministic and never call real services, filesystem, or network.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`, this spec-only task has:

| Area | Risk | Current | Future Implementation |
|------|------|---------|----------------------|
| Anti-coupling rules (FR-40) | High | Documentation only | Negative tests + grep checks |
| `AppShellAdapter` state composition | High | Proposed only | TDD with fixture coverage |
| `AppShellInput` routing | Medium | Proposed only | Unit tests per action type |
| View model defaults | Medium | Proposed only | Default-value tests |
| Canonical Examples | Low | Documented | 8 CE tests |
| Edge Cases | Low | Documented | 10 EC tests |
| Per-screen view models | Low | Proposed only | Rendering tests |
| Spec documentation | Low | This task | Review checklist |

No tests are required or created in this task. Validation only.

## Behavior Budget check

Implementation (spec/planning phase):

- New behaviors: documentation/spec only. Zero runtime changes. ✓
- Public API changes: proposed only via design.md. No source code. ✓
- Files allowed: `aria/specs/features/minimal-ui-shell-planning/**`, `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md`. ✓
- Tests required: none. Validation only (existing tests must pass). ✓
- Dependencies: none added. ✓
- Stop condition not triggered: no implementation code needed. ✓

## Implementation tasks

This is a planning task. All subtasks are documentation/spec creation.

### Task 1: Create spec directory

- [ ] Create `aria/specs/features/minimal-ui-shell-planning/` directory.

### Task 2: Write requirements.md

- [ ] Define problem: no documented plan for UI shell consuming Aria Core.
- [ ] Define goal: implementation-ready planning spec for thin UI shell.
- [ ] Define non-goals: no UI, no Android, no implementation.
- [ ] Define actors: future UI implementers, Aria Core maintainer.
- [ ] Define FR-10 through FR-90 (architecture, state, input, anti-coupling, view models, boundary consumption, diagnostics rules, platform-agnostic vocabulary, spec completeness).
- [ ] Define 8 Canonical Examples (CE-01 through CE-08).
- [ ] Define non-functional requirements (NFR01 through NFR10).
- [ ] Define 10 edge cases (EC01 through EC10).
- [ ] Define 13 acceptance criteria (AC01 through AC13).
- [ ] Define 7 open questions (OQ01 through OQ07).

### Task 3: Write design.md

- [ ] Document architecture: thin UI shell boundary diagram.
- [ ] Propose `AppShellAdapter` protocol and `AppShellState` composite.
- [ ] Propose `AppShellInput` enum and per-screen view model dataclasses.
- [ ] Document proposed module layout (`app_shell.py`).
- [ ] Document data flow (action routing and state composition diagrams).
- [ ] Document anti-coupling rules with verification methods.
- [ ] Document error handling, security, dependencies.
- [ ] Define Behavior Budget (spec/planning only).
- [ ] Define risks and risk classification.
- [ ] Define rollback strategy.
- [ ] Define validation plan.

### Task 4: Write tasks.md (this file)

- [ ] Document preparation checklist.
- [ ] Document TDD classification (future only).
- [ ] Document Test Risk Matrix.
- [ ] Document Behavior Budget check.
- [ ] Document implementation task list (all spec-creation tasks).
- [ ] Document validation checklist.
- [ ] Document review checklist.
- [ ] Document delta update steps.

### Task 5: Write review.md

- [ ] Document requirements coverage.
- [ ] Document context package used.
- [ ] Document files changed.
- [ ] Document validation performed and results.
- [ ] Document non-goals check.
- [ ] Document Behavior Budget result.
- [ ] Document risk/test coverage result.
- [ ] Document delta updates.
- [ ] Document risks remaining and known limitations.
- [ ] Document follow-up tasks.

### Task 6: Validation

- [ ] Run `pwd`.
- [ ] Run `git status --short --branch`.
- [ ] Run `find aria/specs/features/minimal-ui-shell-planning aria/context -maxdepth 5 -type f | sort`.
- [ ] Run `git diff --check`.
- [ ] Run `python3 -m py_compile src/noqlen_aria/*.py`.
- [ ] Run `PYTHONPATH=src python3 -m noqlen_aria.cli --help`.
- [ ] Run `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`.
- [ ] Run `python3 -m pytest`.
- [ ] Run repository contamination check.

### Task 7: Update context files and commit

- [ ] Update `aria/context/current.md` to reflect Bloco 5 spec completion.
- [ ] Update `aria/context/delta.md` to record Bloco 5 spec creation.
- [ ] Update `docs/handoff.md` with Bloco 5 spec status note.
- [ ] Commit with `docs(spec): add minimal UI shell planning spec`.

## Validation checklist

- [ ] `pwd` — confirm working directory.
- [ ] `git status --short --branch` — only expected changes.
- [ ] `git diff --check` — no whitespace issues.
- [ ] `find aria/specs/features/minimal-ui-shell-planning aria/context -maxdepth 5 -type f | sort` — all files present.
- [ ] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [ ] `python3 -m pytest` — all existing tests pass.
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.

## Review checklist

- [ ] Confirm this is spec-only: no source code changed.
- [ ] Confirm no tests changed.
- [ ] Confirm no UI/app shell implementation was added.
- [ ] Confirm no Android/player/queue/cache code was added.
- [ ] Confirm no React/Compose/Kotlin/Java/Gradle files.
- [ ] Confirm no `src/noqlen_aria/**` files modified.
- [ ] Confirm no `tests/**` files modified.
- [ ] Confirm no `pyproject.toml` modified.
- [ ] Confirm Behavior Budget present in spec.
- [ ] Confirm Test Risk Matrix present in spec.
- [ ] Confirm Canonical Examples present (8 examples).
- [ ] Confirm anti-coupling rules documented.
- [ ] Confirm `current.md` and `delta.md` updated.
- [ ] Confirm no private/local/tooling files tracked.
- [ ] Confirm `docs/handoff.md` updated with tiny status note.
- [ ] Confirm validation passed clean.
- [ ] Confirm repository contamination check clean.

## Delta update

- [ ] Update `aria/context/current.md` — mark Bloco 5 spec complete; next step is Blocos 1-3 audit or Bloco 5 implementation.
- [ ] Update `aria/context/delta.md` — record Bloco 5 spec creation with evidence.
- [ ] Update `docs/handoff.md` — add Bloco 5 spec status note.
