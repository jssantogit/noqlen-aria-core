# Tasks

## Preparation checklist

- [x] Read Standard context package and task-specific files.
- [x] Create Bloco 10 spec before implementation.
- [x] Verify scope boundaries and repository hygiene.
- [x] Confirm Bloco 10 does not start Audit 8-10 or Bloco 11.

## TDD classification

- Required for unsupported capability behavior.
- Required for favorites mutation blocking/unavailable behavior.
- Required for degraded/unavailable source behavior.
- Required for deterministic sorting.
- Recommended for filter behavior and badge defaults.

## Test Risk Matrix

- High risk: unsupported source capability behavior, favorites mutation blocking, degraded/unavailable source behavior, deterministic sorting. Requires negative tests and deterministic failure paths.
- Medium risk: filter behavior, fake scenarios, readiness/health badge defaults, public exports. Requires representative deterministic tests.
- Low risk: spec/review/context updates. Requires docs validation and diff checks.

## Behavior Budget check

- [x] Budget defined in `design.md`.
- [x] Implementation stays within allowed files.
- [x] No dependencies added.
- [x] No provider/filesystem/network/playback/UI/queue/cache/smart playlist behavior added.
- [x] Public API additions limited to intentional Bloco 10 names.

## Implementation tasks

- [x] Add filter/sort models and `LibraryFilterService`.
- [x] Add activity/favorites models and services.
- [x] Add readiness/health badge models and service helpers.
- [x] Extend `MediaSourceClient` and `FakeMediaSourceClient` with read-only activity/favorites scenarios.
- [x] Export intentional public names.
- [x] Add/update deterministic tests.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/library-filters-activity-favorites aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Provider/network/filesystem/Android/queue-now-playing-cache boundary searches.

## Review checklist

- [x] Spec created and implemented only as scoped.
- [x] Behavior Budget present and respected.
- [x] Test Risk Matrix present and covered.
- [x] Canonical Examples covered by tests.
- [x] No Audit 8-10 work started.
- [x] No Bloco 11 behavior implemented.
- [x] No smart playlist behavior implemented.
- [x] No real provider integration or provider internals.
- [x] No filesystem traversal.
- [x] No real favorites mutation.
- [x] No streaming/playback/Android/UI/queue/now-playing/cache.
- [x] Current and delta updated concisely.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 10 completion.
- [x] Update `aria/context/delta.md` with concise change and evidence.
- [x] Update this task list to completion.
- [x] Update `review.md` with final evidence.
