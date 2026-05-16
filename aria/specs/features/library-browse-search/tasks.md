# Tasks

## Preparation checklist

- [x] Read required Standard context files.
- [x] Confirm Bloco 8 media source foundation exists.
- [x] Confirm no Bloco 10 behavior is needed for Bloco 9.
- [x] Confirm allowed/forbidden files.
- [x] Confirm no dependencies are needed.

## TDD classification

- Required for unsupported capability behavior.
- Required for search validation.
- Required for degraded/unavailable source behavior.
- Required for safe folder metadata behavior.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Expected coverage |
|------|------|-------------------|
| Unsupported capability behavior | High | Playlists/folders return safe unavailable results, no crash |
| Search validation | High | Empty/invalid query returns safe validation result |
| Degraded/unavailable source behavior | High | Warnings preserved for degraded, safe error for unavailable |
| Safe folder metadata | High | Folder summaries are source items only; no filesystem traversal |
| Browse models/services | Medium | Artists, albums, tracks, playlists, genres, folders |
| Fake scenarios | Medium | Healthy, no playlists, no folders, degraded, unavailable, empty, no-match |
| Public exports | Medium | Only intentional library names exposed |
| Docs/spec state | Low | Context/delta concise and accurate |

## Behavior Budget check

- [x] New behaviors fit budget: browse/search models, services, fake scenarios only.
- [x] Public API expansion limited to intentional names.
- [x] Files stay inside allowed paths.
- [x] Tests cover required behavior.
- [x] No dependencies added.
- [x] Stop conditions not triggered.

## Implementation tasks

- [x] Create `library.py` browse/search models.
- [x] Create `LibraryBrowseService` and `LibrarySearchService`.
- [x] Extend `MediaSourceClient` with browse/search methods.
- [x] Extend `FakeMediaSourceClient` with deterministic browse/search scenarios.
- [x] Expose intentional public API names.
- [x] Add browse/search tests.
- [x] Update `tasks.md` and `review.md` after implementation.
- [x] Update `aria/context/current.md` and `aria/context/delta.md` concisely.
- [x] Run validation.
- [ ] Commit spec and implementation together.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/library-browse-search aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Provider/network/filesystem/Android/queue boundary search checks.

## Review checklist

- [x] Spec created.
- [x] Implementation matches spec.
- [x] No Bloco 10 behavior implemented.
- [x] No real provider integration added.
- [x] No direct provider internals used.
- [x] No filesystem traversal exists for folders.
- [x] No streaming/playback exists.
- [x] No Android/UI/queue/now-playing/cache code added.
- [x] Behavior Budget present and satisfied.
- [x] Test Risk Matrix present and covered.
- [x] Tests pass.
- [x] No private/local/tooling files tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with Bloco 9 completion and next step.
- [x] Update `aria/context/delta.md` with concise Bloco 9 change/evidence.
- [x] Keep current/delta concise.
- [x] Do not start Bloco 10.
