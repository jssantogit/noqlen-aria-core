# Tasks

## Preparation checklist

- [x] Read required context using Standard package.
- [x] Confirm Bloco 12 scope and forbidden Bloco 13 behavior.
- [x] Create requirements, design, tasks, and review spec files before implementation.
- [x] Verify canonical examples are testable.
- [x] Verify Behavior Budget is present.
- [x] Verify Test Risk Matrix is present.

## TDD classification

- Required for now-playing state transitions.
- Required for unavailable media handling.
- Required for resumable state/position validation.
- Required for playback availability states.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required validation |
|------|------|---------------------|
| Queue current item to now-playing state | High | Positive and negative tests for current item and missing/invalid current position |
| Unavailable media state | High | Explicit unavailable reason and no stream/provider call tests |
| Resumable state and position validation | High | Negative position and position beyond duration tests |
| Playback availability vocabulary | High | Each availability state and blocked reason tests |
| Model defaults and serialization | Medium | Deterministic defaults and `safe_serialize` tests |
| Public exports | Medium | `__all__` tests |
| Boundary preservation | High | Provider/network/filesystem/Android/playback-intent searches and introspection tests |

## Behavior Budget check

- [x] Scope limited to now-playing state/contracts, `NowPlayingService`, fake scenarios, tests, public exports, and workflow state.
- [x] No dependencies allowed.
- [x] No real playback, playback intent execution, stream resolution, provider integration, Android/UI, offline/cache, or smart playlist behavior allowed.

## Implementation tasks

- [x] Add `src/noqlen_aria/now_playing.py` models and service.
- [x] Add deterministic fake now-playing scenarios.
- [x] Add tests for idle/default now-playing state.
- [x] Add tests for now-playing from queue current item and queue without current item.
- [x] Add tests for unavailable media state.
- [x] Add tests for resumable state.
- [x] Add tests for invalid/negative position and position exceeding known duration.
- [x] Add tests for playback availability states and reasons.
- [x] Add serialization/defaults tests where relevant.
- [x] Add provider/network/filesystem/playback boundary tests.
- [x] Export intentional now-playing names from module and package.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/now-playing-foundation aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest` — 574/574 passed.
- [x] tracked forbidden-file contamination check
- [x] provider/network/filesystem/Android/playback-intent/offline/smart-playlist search checks

## Review checklist

- [x] Spec created.
- [x] Implementation matches Bloco 12 spec.
- [x] No Bloco 13 behavior implemented.
- [x] No playback intent execution implemented.
- [x] No real playback/streaming exists.
- [x] No provider integration added.
- [x] No direct provider internals used.
- [x] No filesystem/network behavior exists.
- [x] No Android/UI/offline/cache/smart playlist code added.
- [x] Behavior Budget and Test Risk Matrix present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` after implementation.
- [x] Update `aria/context/delta.md` after validation.
- [x] Update this `tasks.md` with completed tasks and evidence.
- [x] Update `review.md` with final review and validation evidence.
