# Tasks

## Preparation checklist

- [x] Read `AGENTS.md`.
- [x] Read `aria/context/current.md`.
- [x] Read `aria/context/delta.md`.
- [x] Read `aria/context/context-packages.md`.
- [x] Read `aria/context/scope-boundaries.md`.
- [x] Read `aria/context/repository-hygiene.md`.
- [x] Read `aria/context/behavior-budget.md`.
- [x] Read `aria/context/test-risk-matrix.md`.
- [x] Read `docs/aria-core-handoff.md`.
- [x] Read `docs/architecture.md`.
- [x] Read `docs/safety.md`.
- [x] Read `docs/anchor-integration.md`.
- [x] Read `docs/android-boundary.md`.
- [x] Read `docs/ui-shell-boundary.md`.
- [x] Read `docs/handoff.md`.
- [x] Read `docs/workflow-vnext.md`.
- [x] Read `aria/specs/_template/**`.
- [x] Read `aria/review/validation-checklist.md`.
- [x] Read `aria/specs/features/aria-release-preparation/requirements.md`.
- [x] Read `aria/specs/features/aria-release-preparation/design.md`.
- [x] Read `README.md`.
- [x] Read `pyproject.toml`.
- [x] Read `src/noqlen_aria/**`.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`:

| Area | Risk | Result |
|------|------|--------|
| Safety summary verification | High | All safety boundaries verified; documented in `docs/safety-summary.md` |
| Release checklist validation | Medium | Checklist created at `docs/release-checklist.md` with pass/fail per item |
| Version consistency | Medium | `__version__` and `version` match at `0.0.0`; no conflicting strings |
| Repository hygiene | Medium | Contamination check clean; no forbidden files tracked |
| Public API surface summary | Medium | Documented at `docs/api-surface.md` with stable export inventory |
| Test/validation matrix | Medium | 368/368 tests pass; CLI smoke works; compilation clean |
| Package metadata review | Low | `pyproject.toml` fields reviewed; consistent with MVP scope |
| README review | Low | README updated for MVP scope; no future features promised as implemented |
| Documentation consistency review | Low | All docs reviewed; future/backlog features marked as such |
| Changelog/release notes | Low | Release notes at `docs/release-notes.md`; Blocos 0-6 summarized |
| Handoff/backlog summary | Low | Handoff updated; backlog at `docs/post-core-backlog.md` |

## Behavior Budget check

Implementation phase:

- New behaviors: documentation only. No runtime behavior created. [x]
- Public API changes: none; only documentation of existing exports. [x]
- Files allowed: `docs/**`, `README.md`, `aria/specs/features/aria-release-preparation/**`, `aria/context/current.md`, `aria/context/delta.md`, `aria/review/**` if needed. [x]
- Tests required: validation only; existing tests confirmed passing. [x]
- Dependencies: none. [x]
- Stop if: release tag creation, package publishing, source changes, test changes, product behavior implementation, or post-core feature implementation becomes necessary. Not triggered. [x]

## Implementation tasks

This task implements the approved Bloco 7 release preparation spec.

### Task 1: Create release readiness checklist

- [x] Create `docs/release-checklist.md`.
- [x] Define checklist items covering: version consistency, package metadata, README, docs, API surface, safety, tests, hygiene, changelog, handoff, backlog, stop conditions.
- [x] Include canonical CLI invocation commands for automated checks.
- [x] Define clear pass/fail criteria for each item.
- [x] Define the final gate: all items must pass before tag/publish.

### Task 2: Verify version consistency

- [x] Compare `__version__` in `src/noqlen_aria/__init__.py` with `version` in `pyproject.toml`. Both at `0.0.0`.
- [x] Decision: keep `0.0.0` as pre-release; version bump deferred to final audit/tag decision.
- [x] No hardcoded version strings found elsewhere.

### Task 3: Review package metadata

- [x] Reviewed `pyproject.toml` fields. All correct and consistent with MVP scope.
- [x] No references to unimplemented features in package metadata.
- [x] Build system and packaging configuration is valid.

### Task 4: Review README

- [x] Updated `README.md` for MVP scope accuracy.
- [x] No future/backlog features presented as implemented.
- [x] Install/usage instructions are correct.

### Task 5: Review documentation consistency

- [x] Reviewed all public docs for MVP/future scope consistency.
- [x] Updated `docs/aria-core-handoff.md` status and next step.
- [x] Docs consistently mark future features as future/backlog.
- [x] Docs consistently describe Anchor as one `ControlClient` adapter.
- [x] No doc implies real Navidrome, Android, playback, queue, now playing, or cache support exists.

### Task 6: Produce public API surface summary

- [x] Created `docs/api-surface.md`.
- [x] Documents all stable public exports from `noqlen_aria` and `noqlen_aria.android_boundaries`.
- [x] Documents internal names not part of stable API (`AnchorResultMapper`).
- [x] All public exports are source-agnostic.

### Task 7: Produce safety summary

- [x] Created `docs/safety-summary.md`.
- [x] Confirmed: no real music-library access, no Navidrome calls, no Anchor internals, no Android/UI/playback/queue/cache, no provider hard coupling, no secrets/credentials.
- [x] Confirmed: optional Anchor dependency safe, lifecycle apply blocked, serialized output sanitized.
- [x] Confirmed: tests are local, offline, fake-first, deterministic.

### Task 8: Produce test/validation matrix

- [x] `python3 -m pytest`: 368 passed.
- [x] CLI smoke: `--help` and `doctor` work.
- [x] `python3 -m py_compile src/noqlen_aria/*.py`: clean.
- [x] Contamination check: clean.
- [x] Results documented in release checklist and delta.

### Task 9: Run repository hygiene check

- [x] Contamination check: clean (no output).
- [x] No forbidden files tracked.
- [x] `git add .` was not used.

### Task 10: Draft changelog/release notes

- [x] Created `docs/release-notes.md`.
- [x] Summarizes completed Blocos 0-6 scope.
- [x] Separates implemented features from future/backlog.
- [x] Includes safety boundaries, known limitations, version info, and quality gates.

### Task 11: Update handoff document

- [x] Updated `docs/handoff.md` with Bloco 7 complete status.
- [x] References release artifacts and post-core backlog.
- [x] References next step: final release audit and tag decision.

### Task 12: Produce post-core backlog summary

- [x] Created `docs/post-core-backlog.md`.
- [x] Lists spec'd future blocks (Blocos 7-21) from the roadmap.
- [x] Distinguishes spec'd blocks from unspec'd features.
- [x] Notes that future features require dedicated specs.

### Task 13: Define tag/release steps

- [x] Tag/release steps documented in `docs/release-checklist.md`.
- [x] Git tag format documented (v<version>).
- [x] Build and publish steps documented for reference.
- [x] Final stop conditions defined.

### Task 14: Final validation and commit

- [x] Release checklist re-run and all items pass.
- [x] All release artifacts created.
- [x] Context files updated.
- [x] Commit with explicit allowlisted paths.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find README.md pyproject.toml docs aria/specs/features/aria-release-preparation aria/context aria/review -maxdepth 5 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
- [x] Android SDK search check
- [x] Forbidden implementations search check
- [x] Apply-mode search check
- [x] Provider/CLI search check

## Review checklist

- [x] Confirm implementation matches the Bloco 7 spec.
- [x] Confirm no product behavior was added.
- [x] Confirm no post-core features were implemented.
- [x] Confirm no tag was created.
- [x] Confirm no publish action was attempted.
- [x] Confirm docs are honest about implemented vs future scope.
- [x] Confirm release checklist exists.
- [x] Confirm release notes exist.
- [x] Confirm public API summary exists.
- [x] Confirm safety summary exists.
- [x] Confirm post-core backlog exists.
- [x] Confirm tests pass.
- [x] Confirm `current.md` and `delta.md` stayed concise.
- [x] Confirm no private/local/tooling files are tracked.

## Delta update

- [x] Update `aria/context/current.md` to mark Bloco 7 complete.
- [x] Update `aria/context/delta.md` to record release preparation and validation evidence.
- [x] Keep both files concise.
- [x] Update `docs/handoff.md` with Bloco 7 implementation status.
