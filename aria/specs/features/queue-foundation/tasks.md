# Tasks

## Preparation Checklist

- [x] Read required Standard context package files.
- [x] Read Behavior Budget and Test Risk Matrix context.
- [x] Read Bloco 8, 9, and 10 reviews.
- [x] Read relevant source and tests.
- [x] Create spec before implementation.
- [x] Verify Canonical Examples are explicit.

## TDD Classification

- Required for queue state transitions.
- Required for invalid operation behavior.
- Required for unavailable item handling.
- Required for multiple queue handling.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|---|---|---|
| Queue state transitions | High | Positive and negative tests for add, remove, clear, move, current position |
| Invalid operations | High | Safe `AriaResult` errors and non-mutating state |
| Unavailable item handling | High | Preserve unavailable state and prove no stream/provider behavior |
| Multiple queue handling | High | Select and mutate only targeted queue |
| Shuffle determinism | Medium | Stable order in repeated calls/tests |
| Repeat/default models | Medium | Defaults and safe serialization |
| Public exports | Medium | Intentional queue names only |
| Docs/spec updates | Low | Review checklist and validation evidence |

## Behavior Budget Check

- [x] New behavior limited to Bloco 11 queue foundation.
- [x] Public API limited to intentional queue foundation names.
- [x] No dependencies added.
- [x] Allowed files only.
- [x] Stop conditions checked before implementation.

## Implementation Tasks

- [x] Add queue models and operation/result contracts.
- [x] Add deterministic `QueueService`.
- [x] Add fake queue scenario helpers.
- [x] Export intentional queue names from `noqlen_aria`.
- [x] Add tests for queue defaults, add/remove/clear/reorder/current position/repeat/shuffle/unavailable/multiple queues/invalid operations.
- [x] Add tests proving no provider/network/filesystem/playback dependency.
- [x] Update public API hardening test.

## Validation Checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/queue-foundation aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check
- [x] Provider/network/filesystem/Android/now-playing/offline/smart-playlist search checks

## Review Checklist

- [x] Spec created.
- [x] Implementation matches Bloco 11 spec.
- [x] No Bloco 12 behavior implemented.
- [x] No now playing behavior implemented.
- [x] No real playback/streaming exists.
- [x] No provider integration added.
- [x] No provider internals used.
- [x] No filesystem/network behavior added.
- [x] No Android/UI/offline/cache/smart playlist code added.
- [x] Behavior Budget present and respected.
- [x] Test Risk Matrix present and covered.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files tracked.

## Delta Update Checklist

- [x] Update `aria/context/current.md` with Bloco 11 completion and next-step guardrails.
- [x] Update `aria/context/delta.md` with concise Bloco 11 summary and validation evidence.
- [x] Update this task list after implementation.
- [x] Update `review.md` after validation.
