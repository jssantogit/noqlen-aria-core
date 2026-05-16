# Tasks

## Preparation checklist

- [x] Read Standard context package.
- [x] Read scope and hygiene boundaries.
- [x] Read Behavior Budget and Test Risk Matrix.
- [x] Read relevant prior reviews.
- [x] Create spec before implementation.

## TDD classification

- Required for rule validation.
- Required for unsupported operator/field behavior.
- Required for provider mutation blocking.
- Required for deterministic smart mix behavior.
- Required for missing metadata behavior.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|------|------|-------------------|
| Provider mutation blocking | High | Negative tests prove provider playlist creation is unsupported and side-effect free. |
| Unsupported field/operator validation | High | Negative tests prove safe validation issues and unavailable previews. |
| Missing metadata behavior | High | Tests prove partial/unavailable result without crash. |
| Deterministic smart mix behavior | High | Tests prove same seed gives same order and no global randomness. |
| Queue/playback boundary | High | Tests prove services expose no queue/playback mutation/start path. |
| Rule evaluation and filtering | Medium | Positive tests for favorite, recent, genre/artist/album fields. |
| Sorting/limits | Medium | Deterministic sort and limit tests. |
| Public exports/serialization | Medium | Hardening and safe serialization tests. |
| Spec/docs | Low | Review confirms required sections. |

## Behavior Budget check

- [x] Budget documented in `design.md`.
- [x] Implementation stays within allowed files.
- [x] No new dependencies.
- [x] No provider writes, queue mutation, playback, background jobs, filesystem scans, network, Android/UI, or Bloco 20 behavior.

## Implementation tasks

- [x] Add smart playlist, saved filter, and smart mix contracts in `src/noqlen_aria/smart_playlists.py`.
- [x] Add deterministic `SmartPlaylistService` and `SavedFilterService`.
- [x] Add deterministic fake/library scenarios.
- [x] Export intentional public names in module and package `__all__`.
- [x] Add tests for validation, previews, deterministic sorting/limits/mixes, empty library, missing metadata, and boundaries.
- [x] Update hardening public export test.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/smart-playlists aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check
- [x] Provider/network/filesystem/Android/queue/playback/Bloco 20 search checks

## Review checklist

- [x] Spec created.
- [x] Implementation matches Bloco 19 spec.
- [x] No Bloco 20 behavior implemented.
- [x] No provider playlist creation or provider mutation.
- [x] No queue mutation or playback.
- [x] No filesystem/network behavior.
- [x] No Android/UI code.
- [x] Behavior Budget present and respected.
- [x] Test Risk Matrix present and covered.
- [x] Tests pass.
- [x] `current.md` and `delta.md` concise.
- [x] No private/local/tooling files tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 19 status.
- [x] Update `aria/context/delta.md` with concise change and validation evidence.
- [x] Record review result in `review.md`.
