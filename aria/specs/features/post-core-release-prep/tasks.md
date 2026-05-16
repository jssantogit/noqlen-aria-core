# Tasks

## Preparation checklist

- [x] Read Standard context package and required task docs.
- [x] Confirm Bloco 24 is documentation/release-prep only.
- [x] Confirm source, tests, package metadata, tag, publish, Android/player/audio/provider implementation are out of scope.
- [x] Review `src/noqlen_aria/__init__.py` for existing public exports to summarize.

## TDD classification

Not required because this block is release documentation/prep only. Validation is still required. Final audit will perform safety/API/repository checks.

## Test Risk Matrix

Low risk by `aria/context/test-risk-matrix.md` because changes are docs/spec/context only. Proportional validation still includes full existing tests and boundary searches because release readiness depends on no false claims and no forbidden implementation.

## Behavior Budget check

- [x] New behaviors limited to documentation/release-prep only.
- [x] Public API changes: none.
- [x] Files limited to allowed spec/docs/README/context paths.
- [x] Tests: no new tests required.
- [x] Dependencies: none.
- [x] Stop conditions reviewed.

## Release-prep tasks

- [x] Create `docs/post-core-release-checklist.md`.
- [x] Create `docs/post-core-release-notes.md`.
- [x] Create `docs/post-core-api-surface.md`.
- [x] Create `docs/post-core-safety-summary.md`.
- [x] Create `docs/post-core-handoff.md`.
- [x] Create `docs/post-core-known-limitations.md`.
- [x] Create `docs/future-android-player-handoff.md`.

## Documentation tasks

- [x] Update `docs/handoff.md` with Bloco 24 release-prep status.
- [x] Update `docs/post-core-backlog.md` with Bloco 24 and final audit next gate.
- [x] Update `docs/aria-core-handoff.md` status and next step.
- [x] Update `README.md` only for stale status/roadmap wording and post-core artifact links.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find README.md docs aria/specs/features/post-core-release-prep aria/context aria/review -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Tracked private/local/tooling contamination check.
- [x] False implementation claim search.
- [x] Android/player/audio/provider forbidden implementation searches.

## Review checklist

- [x] Spec created.
- [x] Release-prep docs created or updated.
- [x] No source code changed.
- [x] No tests changed.
- [x] No version/tag/publish action occurred.
- [x] No Android/player/audio-driver/provider implementation added.
- [x] Docs do not falsely claim future implementation exists.
- [x] Final audit is listed as next gate.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Validation passes.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` after release-prep docs are complete.
- [x] Update `aria/context/delta.md` with concise Bloco 24 summary and validation evidence.
