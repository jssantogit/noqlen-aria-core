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

Bloco 6 implementation requires tests for high-risk hardening behavior before or alongside source changes.

Implemented hardening tests cover:
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
| Safe serialization | High | Implemented | Negative tests for raw detail leakage |
| Sanitized errors/warnings | High | Implemented | Negative tests for stack traces, paths, credentials, provider details |
| Dry-run/apply boundary | High | Implemented | Tests proving lifecycle apply is blocked/unavailable |
| Optional dependency absence | High | Implemented | Tests proving safe behavior without Anchor |
| Public exports | Medium | Implemented | Deterministic intentional export tests |
| View/default degraded states | Medium | Covered by existing tests | Unit tests for safe defaults |
| Documentation consistency | Low | Implemented | Docs review and grep checks |
| Repository hygiene | Low | Pending final validation | Contamination command and commit review |

Tests are required for this implementation task and were added in `tests/test_mvp_hardening.py`.

## Behavior Budget check

Implementation phase:

- New behaviors: limited to MVP hardening. [x]
- Public API changes: explicit intentional exports and safe output helpers. [x]
- Files allowed: source, tests, docs, spec tracking, and concise context updates. [x]
- Tests required: high-risk hardening tests. [x]
- Dependencies: none. [x]
- Stop if Android/UI/playback/queue/cache/provider implementation becomes necessary. Not triggered. [x]

## Implementation tasks

This task implements the approved Bloco 6 hardening spec only.

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

Completed for this Bloco 6 implementation task.

### Future Task A: Public API and export hardening

- [x] Inventory public names across MVP modules.
- [x] Decide intentional stable exports.
- [x] Add or adjust `__all__` only if needed.
- [x] Add tests for stable public exports.

### Future Task B: Serialization and sanitization hardening

- [x] Inventory serialization paths.
- [x] Add tests for safe serialization of results, states, errors, warnings, and boundary snapshots.
- [x] Add negative tests for stack traces, credentials, local paths, provider exception text, raw logs, and music-library details.
- [x] Make minimal code changes only if tests reveal unsafe output.

### Future Task C: Optional dependency hardening

- [x] Simulate Anchor unavailable.
- [x] Verify core imports, CLI help, and CLI doctor work.
- [x] Verify readiness/status/diagnostics expose safe degraded behavior.
- [x] Add focused tests.

### Future Task D: Anchor dry-run/apply safety hardening

- [x] Verify dry-run lifecycle behavior remains contract-level.
- [x] Verify lifecycle apply remains blocked or unavailable.
- [x] Verify no provider internals, no Anchor CLI integration, no direct Navidrome execution, and no real library access.
- [x] Add focused negative tests.

### Future Task E: Documentation and audit readiness

- [x] Review docs for MVP/future scope consistency.
- [x] Make tiny documentation clarifications if needed.
- [x] Update delta with validation evidence.
- [x] Prepare Bloco 4-6 formal audit evidence.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests docs aria/specs/features/aria-mvp-hardening aria/context -maxdepth 5 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
- [x] Apply-helper search check. Matches are negative-test assertions and generated cache notices only.
- [x] Provider/CLI search check.
- [x] Android SDK/UI search check.
- [x] Queue/now-playing/offline/media-source search check.

## Review checklist

- [x] Confirm implementation matches the Bloco 6 spec.
- [x] Confirm no Bloco 7 release prep was started.
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

- [x] Update `aria/context/current.md` to mark Bloco 6 implementation complete and next step as Blocos 4-6 formal audit.
- [x] Update `aria/context/delta.md` to record Bloco 6 hardening and validation evidence.
- [x] Keep both files concise.
- [x] Update `docs/handoff.md` with Bloco 6 status note.
