# Tasks

## Preparation checklist

- [x] Read `AGENTS.md`.
- [x] Read `aria/context/current.md`.
- [x] Read `aria/context/delta.md`.
- [x] Read `aria/context/context-packages.md`.
- [x] Read `aria/context/scope-boundaries.md`.
- [x] Read `aria/context/behavior-budget.md`.
- [x] Read `aria/context/test-risk-matrix.md`.
- [x] Read `docs/aria-core-handoff.md`.
- [x] Read `docs/architecture.md`.
- [x] Read `docs/safety.md`.
- [x] Read `docs/anchor-integration.md`.
- [x] Read `docs/android-boundary.md`.
- [x] Read `docs/ui-shell-boundary.md`.
- [x] Read `docs/handoff.md`.
- [x] Read `aria/specs/_template/**`.
- [x] Read `aria/review/validation-checklist.md`.

## TDD classification

Not applicable for this task. This is a spec/planning task with zero implementation.

Future Bloco 6 implementation must use tests for high-risk hardening behavior before or alongside source changes:
- public export tests;
- safe serialization tests;
- sanitized error/warning negative tests;
- optional dependency absence tests;
- Anchor dry-run/apply safety tests;
- forbidden integration/import checks where practical.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`:

| Area | Risk | Current spec task | Future implementation |
|------|------|-------------------|----------------------|
| Safe serialization | High | Proposed only | Negative tests for raw detail leakage |
| Sanitized errors/warnings | High | Proposed only | Negative tests for stack traces, paths, credentials, provider details |
| Dry-run/apply boundary | High | Proposed only | Tests proving lifecycle apply is blocked/unavailable |
| Optional dependency absence | High | Proposed only | Tests proving degraded-safe behavior without Anchor |
| Public exports | Medium | Proposed only | Deterministic intentional export tests |
| View/default degraded states | Medium | Proposed only | Unit tests for safe defaults |
| Documentation consistency | Low | Spec/review only | Docs review and grep checks |
| Repository hygiene | Low | Validation only | Contamination command and commit review |

No tests are required or created in this task. Validation only.

## Behavior Budget check

Spec/planning phase:

- New behaviors: proposed only, no implementation in this task. [x]
- Public API changes: proposed only, no source code. [x]
- Files allowed: spec directory only, plus `current.md`/`delta.md` if needed. [x]
- Tests required: none in this task, validation only. [x]
- Dependencies: none. [x]
- Stop if implementation code becomes necessary. Not triggered. [x]

## Implementation tasks

This task implements the spec only. It does not implement hardening.

### Task 1: Create spec directory

- [x] Create `aria/specs/features/aria-mvp-hardening/`.

### Task 2: Write `requirements.md`

- [x] Define problem and goal for Aria MVP hardening.
- [x] Define non-goals and forbidden scope.
- [x] Define functional requirements for public API surface review.
- [x] Define functional requirements for intentional exports.
- [x] Define functional requirements for safe serialization.
- [x] Define functional requirements for sanitized errors/warnings.
- [x] Define functional requirements for optional dependency behavior.
- [x] Define functional requirements for Anchor dry-run/apply safety.
- [x] Define no-provider-internals, no-CLI-as-integration, no-real-Navidrome, no-real-library checks.
- [x] Define no Android/UI/playback/queue/cache checks.
- [x] Define documentation consistency and test coverage review requirements.
- [x] Include Canonical Examples using Given / When / Then.
- [x] Include acceptance criteria.

### Task 3: Write `design.md`

- [x] Document context files read.
- [x] Document context package used: Standard.
- [x] Document files created and modified.
- [x] Document files forbidden for this spec task.
- [x] Document hardening architecture.
- [x] Document public API surface design.
- [x] Document safe serialization design.
- [x] Document error handling and optional dependency behavior.
- [x] Document Anchor dry-run/apply safety design.
- [x] Document documentation consistency design.
- [x] Include Behavior Budget.
- [x] Include Test Risk Matrix risk classification.
- [x] Include validation plan.

### Task 4: Write `tasks.md`

- [x] Document preparation checklist.
- [x] Document TDD classification.
- [x] Document Test Risk Matrix.
- [x] Document Behavior Budget check.
- [x] Document spec creation tasks.
- [x] Document future implementation tasks.
- [x] Document validation checklist.
- [x] Document review checklist.
- [x] Document delta update checklist.

### Task 5: Write `review.md`

- [x] Document expected requirements coverage.
- [x] Document context package used.
- [x] Document files created/modified.
- [x] Document validation performed placeholders for this task.
- [x] Document non-goals check.
- [x] Document Behavior Budget result.
- [x] Document risk/test coverage result.
- [x] Document risks remaining and follow-up implementation tasks.

## Future implementation tasks

These are for the next Bloco 6 implementation task only. Do not perform them in this spec task.

### Future Task A: Public API and export hardening

- [ ] Inventory public names across MVP modules.
- [ ] Decide intentional stable exports.
- [ ] Add or adjust `__all__` only if needed.
- [ ] Add tests for stable public exports.

### Future Task B: Serialization and sanitization hardening

- [ ] Inventory serialization paths.
- [ ] Add tests for safe serialization of results, states, errors, warnings, and boundary snapshots.
- [ ] Add negative tests for stack traces, credentials, local paths, provider exception text, raw logs, and music-library details.
- [ ] Make minimal code changes only if tests reveal unsafe output.

### Future Task C: Optional dependency hardening

- [ ] Simulate Anchor unavailable.
- [ ] Verify core imports, CLI help, and CLI doctor work.
- [ ] Verify readiness/status/diagnostics expose safe degraded behavior.
- [ ] Add focused tests.

### Future Task D: Anchor dry-run/apply safety hardening

- [ ] Verify dry-run lifecycle behavior remains contract-level.
- [ ] Verify lifecycle apply remains blocked or unavailable.
- [ ] Verify no provider internals, no Anchor CLI integration, no direct Navidrome execution, and no real library access.
- [ ] Add focused negative tests.

### Future Task E: Documentation and audit readiness

- [ ] Review docs for MVP/future scope consistency.
- [ ] Make tiny documentation clarifications if needed.
- [ ] Update delta with validation evidence.
- [ ] Prepare Bloco 4-6 formal audit evidence.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find aria/specs/features/aria-mvp-hardening aria/context -maxdepth 5 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`

## Review checklist

- [x] Confirm this is spec-only.
- [x] Confirm no source code changed.
- [x] Confirm no tests changed.
- [x] Confirm no hardening implementation was created.
- [x] Confirm no Android/UI/playback/queue/cache code was added.
- [x] Confirm no provider internals, CLI-as-integration, real Navidrome execution, or real music-library access was added.
- [x] Confirm Behavior Budget is present in the spec.
- [x] Confirm Test Risk Matrix is present in the spec.
- [x] Confirm Canonical Examples are present in the spec.
- [x] Confirm context package used is documented as Standard.
- [x] Confirm `current.md` and `delta.md` stayed concise.
- [x] Confirm no private/local/tooling files are tracked.
- [x] Confirm validation passed or failures are recorded.
- [ ] Confirm commit used explicit allowlisted paths, not `git add .`.

## Delta update

- [x] Update `aria/context/current.md` to mark Bloco 6 spec complete and next step as Bloco 6 implementation only after approval.
- [x] Update `aria/context/delta.md` to record Bloco 6 spec creation and validation evidence.
- [x] Keep both files concise.
- [x] Update `docs/handoff.md` only if a tiny status note is needed. Not needed.
