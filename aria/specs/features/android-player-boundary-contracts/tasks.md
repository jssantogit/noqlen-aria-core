# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/android-player-boundary-contracts/requirements.md`.
- [x] Read `aria/specs/features/android-player-boundary-contracts/design.md`.
- [x] Confirm Bloco 0-3 validation passes (CLI help, doctor, py_compile, pytest).
- [x] Confirm no source/test files exist at `src/noqlen_aria/android_boundaries.py` or `tests/test_android_boundaries.py`.
- [x] Confirm `pyproject.toml` has no external dependencies to add.

## TDD classification

Implementation is complete. TDD was used for high-risk boundaries:

### Required for TDD

- `PlaybackEngineBridge` command/state mapping: correct state transitions and error handling are critical for all downstream playback behavior.
- `AndroidStorageBridge` requirement checking: must correctly handle all `StorageStatus` values and `PermissionState` combinations.
- `ForegroundServiceBridge` lifecycle state transitions: incorrect service states cause Android ANR or crash.

### Recommended for TDD

- `MediaSessionBridge` action dispatch: must correctly map `MediaSessionAction` to internal commands.
- `AndroidAutoBridge` browse tree navigation: browse structure must be deterministic and safe.
- `AppLifecycleBridge` event-to-state mapping: must handle out-of-order events gracefully.
- `HeadsetControlBridge` event translation: must correctly map headset events to playback commands.
- All fake implementations: must be deterministic and never call real APIs.

### TDD approach used

1. Defined contracts and protocols from spec.
2. Implemented fake implementations with failure-injection hooks.
3. Wrote tests covering type correctness, structural typing, positive paths, error injection, and edge cases.
4. Refactored while keeping tests green.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`, this implementation addresses:

| Boundary | Risk | Tests | Coverage |
|---|---|---|---|
| PlaybackEngineBridge | Medium | 11 | States, commands, seek, error injection, determinism |
| MediaSessionBridge | Medium | 7 | State, metadata, action dispatch, error injection |
| AndroidStorageBridge | High | 10 | All statuses, requirements, permissions, error injection |
| AndroidAutoBridge | Medium | 9 | Root, browse, search, play, invalid nodes, empty query |
| ForegroundServiceBridge | High | 7 | Start, stop, idempotent start, notification, error injection |
| AppLifecycleBridge | High | 8 | Event sequence, foreground detection, atypical events, error injection |
| NotificationControlBridge | Medium | 5 | Action, content update, dismiss, error injection |
| LockScreenBridge | Medium | 4 | State update, action handling |
| HeadsetControlBridge | Medium | 8 | Connected state, button events, disconnected behavior, error injection |
| Composite Snapshot | Medium | 3 | Defaults, custom composition |
| Structural Typing | Medium | 9 | All fakes satisfy their protocols |
| Canonical Examples | — | 12 | CE-01 through CE-12 |
| Edge Cases | — | 7 | EC-01, EC-03, EC-05, EC-06, EC-08, EC-12 |

All high-risk items have negative tests proving failure paths are safe and deterministic.

## Behavior Budget check

Implementation stayed within budget:

- New behaviors: 9 bridge protocols, 12+ enum types, 15+ dataclasses, 9 fake implementations. All per spec. ✓
- Public API changes: `src/noqlen_aria/android_boundaries.py` with public exports. No changes to existing modules. ✓
- Files allowed: `src/noqlen_aria/android_boundaries.py`, `tests/test_android_boundaries.py`, spec/context files. ✓
- Tests required: 129 tests written. All pass. ✓
- Dependencies: none added beyond existing `noqlen_aria.contracts`. Python stdlib only. ✓
- Stop condition not triggered. ✓

No budget overrun.

## Implementation tasks

All tasks are complete.

### Task 1: Create source file skeleton

- [x] Create `src/noqlen_aria/android_boundaries.py` with module docstring and imports.
- [x] Import `AriaResult`, `AriaError`, `PermissionState` from `noqlen_aria.contracts`.
- [x] Create `tests/test_android_boundaries.py` with test imports and pytest markers.
- [x] Validate: `python3 -m py_compile src/noqlen_aria/android_boundaries.py` passes.

### Task 2: Implement PlaybackEngine boundary

- [x] Define `PlaybackState`, `PlaybackCommand`, `PlaybackPosition`, `TrackMetadata`, `PlaybackEngineSnapshot`.
- [x] Define `PlaybackEngineBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakePlaybackEngineBridge` with deterministic behavior.
- [x] Write TDD tests for all states, commands, metadata, snapshots, and fake determinism.
- [x] Validate: pytest passes for playback engine tests.

### Task 3: Implement MediaSession boundary

- [x] Define `MediaSessionAction`, `MediaSessionRepeatMode`, `MediaSessionShuffleMode`, `MediaSessionPlaybackState`, `MediaSessionMetadata`.
- [x] Define `MediaSessionBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeMediaSessionBridge` with deterministic behavior.
- [x] Write tests for action dispatch, state composition, metadata mapping.
- [x] Validate: pytest passes for media session tests.

### Task 4: Implement AndroidStorage boundary

- [x] Define `StorageType`, `StorageStatus`, `StorageRequirement`, `StorageStatusSnapshot`.
- [x] Define `AndroidStorageBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeAndroidStorageBridge` with configurable permission/status states.
- [x] Write TDD tests for all storage statuses, requirement checking, permission states.
- [x] Validate: pytest passes for storage bridge tests.

### Task 5: Implement Android Auto boundary

- [x] Define `AutoBrowseNodeType`, `AutoBrowseNode`, `AutoBrowseResult`, `AutoSearchResult`.
- [x] Define `AndroidAutoBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeAndroidAutoBridge` with deterministic browse tree.
- [x] Write tests for root, browse, search, play_from_node operations.
- [x] Validate: pytest passes for Android Auto tests.

### Task 6: Implement Foreground Service boundary

- [x] Define `ForegroundServiceState`, `ForegroundServiceRequirement`.
- [x] Define `ForegroundServiceBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeForegroundServiceBridge` with deterministic lifecycle.
- [x] Write TDD tests for state transitions, notification updates.
- [x] Validate: pytest passes for foreground service tests.

### Task 7: Implement App Lifecycle boundary

- [x] Define `AppLifecycleEvent`, `AppLifecycleState`.
- [x] Define `AppLifecycleBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeAppLifecycleBridge` with deterministic state machine.
- [x] Write TDD tests for event-to-state mapping, out-of-order events, foreground detection.
- [x] Validate: pytest passes for app lifecycle tests.

### Task 8: Implement Notification/LockScreen/Headset boundaries

- [x] Define `NotificationAction`, `LockScreenControlState`, `HeadsetEventType`.
- [x] Define `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge` as `@runtime_checkable Protocol`.
- [x] Implement `FakeNotificationControlBridge`, `FakeLockScreenBridge`, `FakeHeadsetControlBridge`.
- [x] Write tests for notification actions, lock-screen state, headset events.
- [x] Validate: pytest passes for all notification/peripheral tests.

### Task 9: Implement Composite Snapshot

- [x] Define `AndroidBoundarySnapshot` compositing all boundary states.
- [x] Write tests for composition, defaults, custom composition.
- [x] Validate: pytest passes for snapshot tests.

### Task 10: Final validation

- [x] Run full validation suite: `py_compile`, import check, pytest, contamination check.
- [x] Confirm no regression in Bloco 0-3 tests.
- [x] Confirm no forbidden files tracked.
- [x] Commit implementation artifacts.

## Validation checklist

Implementation phase:

- [x] `pwd` — confirmed working directory.
- [x] `git status --short --branch` — only expected changes.
- [x] `git diff --check` — no whitespace issues.
- [x] `find src/noqlen_aria tests aria/specs/features/android-player-boundary-contracts aria/context -maxdepth 5 -type f | sort` — all files present.
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [x] `python3 -m pytest` — 358/358 passed (229 existing + 129 new).
- [x] `grep -R "android\.\|androidx\.\|Media3\|ExoPlayer\|MediaSession\|AndroidAuto" src tests` — zero Android SDK references.
- [x] `grep -R "QueueService\|NowPlaying\|OfflineCache\|MediaSourceClient" src tests` — zero forbidden implementations.
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.

## Review checklist

- [x] Confirm non-goals: no Android SDK, no Kotlin/Java/Gradle, no real playback, no Media3/ExoPlayer, no real MediaSession, no real Android Auto, no queue/now playing, no offline/cache.
- [x] Confirm no source code changed outside spec scope.
- [x] Confirm no pyproject.toml changed.
- [x] Confirm no local/private/tooling artifacts staged.
- [x] Confirm spec completeness: requirements, design, tasks, review all present.
- [x] Confirm Canonical Examples translated to tests (12 CE tests).
- [x] Confirm Behavior Budget respected.
- [x] Confirm Test Risk Matrix applied.
- [x] Confirm context package (Standard) used.
- [x] Confirm nine boundary protocols + composite snapshot implemented.

## Delta update

- [ ] Update `aria/context/current.md` to reflect Bloco 4 implementation completion.
- [ ] Update `aria/context/delta.md` to record Bloco 4 implementation.
- [ ] Update `docs/handoff.md` with Bloco 4 implementation status note.
