# Tasks

## Preparation Checklist

- [x] Read required Aria workflow/context files.
- [x] Read Android/player, Android real integration, UI shell, architecture, safety, handoff, and backlog docs.
- [x] Read spec templates and validation checklist.
- [x] Read Bloco 22 review.
- [x] Confirm context package: Standard.
- [x] Confirm scope is documentation/handoff only.
- [x] Confirm Bloco 24 is not in scope.

## TDD Classification

Not required for this block because it is handoff/docs only.

Validation is still required. Any future implementation must create its own spec and tests.

## Test Risk Matrix

Risk classification: Low.

Rationale: Bloco 23 changes documentation and workflow state only. It does not change runtime behavior, public APIs, dependencies, source code, or tests.

Validation expectations:

- Run docs/format hygiene with `git diff --check`.
- Run existing smoke validation to prove no source behavior was affected.
- Run full test suite because the requested validation requires it.
- Run boundary searches to confirm no Android/player/audio-driver/provider implementation was added.
- Run repository contamination check.

## Behavior Budget Check

- [x] New behaviors limited to documentation/handoff only.
- [x] Public API changes: none.
- [x] Files allowed: `aria/specs/features/android-shell-handoff/**`, `docs/**`, `aria/context/current.md`, `aria/context/delta.md`.
- [x] Tests required: no new tests.
- [x] Dependencies: none.
- [x] Stop conditions not triggered.

## Planning/Documentation Tasks

- [x] Create `requirements.md` with status, problem, goal, non-goals, actors, functional requirements, non-functional requirements, Canonical Examples, edge cases, acceptance criteria, and open questions.
- [x] Create `design.md` with ownership maps, handoff flows, risks, validation, and Behavior Budget.
- [x] Create `tasks.md` with preparation, Test Risk Matrix, Behavior Budget, planning tasks, validation, review, and delta update checklist.
- [x] Initialize `review.md` during spec creation.
- [x] Create `docs/android-shell-handoff.md`.
- [x] Align `docs/android-real-integration-plan.md` if needed.
- [x] Align `docs/ui-shell-boundary.md` if needed.
- [x] Align `docs/android-boundary.md` if needed.
- [x] Align `docs/post-core-backlog.md` if needed.
- [x] Align `docs/aria-core-handoff.md` if needed.
- [x] Add a tiny `docs/handoff.md` status note if needed.
- [x] Update `aria/context/current.md` concisely.
- [x] Update `aria/context/delta.md` concisely.

## Validation Checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find docs aria/specs/features/android-shell-handoff aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Android/MediaSession/Media3/ExoPlayer/UI keyword search in `src` and `tests`.
- [x] Audio driver/JNI/NDK/AAudio/Oboe/USB keyword search in `src` and `tests`.
- [x] Documentation claim search for implemented Android shell/integration.

## Review Checklist

- [x] Spec was created.
- [x] Handoff docs were created or updated.
- [x] No source code changed.
- [x] No tests changed.
- [x] No Android/Kotlin/Java/Gradle files were added.
- [x] No Android/player/audio driver/provider implementation was added.
- [x] Docs do not claim Android shell exists.
- [x] Docs do not claim Android integration is implemented.
- [x] Future Android Player audio output phase remains separate.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Validation passes.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta Update Checklist

- [x] Record Bloco 23 handoff completion in `aria/context/delta.md`.
- [x] Record validation evidence in `aria/context/delta.md`.
- [x] Update next step without starting Bloco 24.
