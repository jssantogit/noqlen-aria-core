# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/android-player-boundary-contracts/requirements.md`.
- [x] Read `aria/specs/features/android-player-boundary-contracts/design.md`.
- [ ] Confirm Bloco 0-3 validation passes (CLI help, doctor, py_compile, pytest).
- [x] Confirm no source/test files exist at `src/noqlen_aria/android_boundaries.py` or `tests/test_android_boundaries.py`.
- [x] Confirm `pyproject.toml` has no external dependencies to add.

## TDD classification

This spec is documentation-only. No TDD is applicable in this phase.

During future implementation:

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

### TDD approach (future implementation)

1. Write a failing test for the bridge protocol compliance.
2. Implement the minimum fake to pass.
3. Refactor while keeping tests green.
4. Commit each bridge group atomically.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`, this task is **Low risk** (documentation/spec only).

Future implementation task risk classifications:

| Boundary | Risk | Rationale |
|---|---|---|
| PlaybackEngineBridge | Medium | View-state defaults, public exports |
| MediaSessionBridge | Medium | View-state defaults, public exports |
| AndroidStorageBridge | High | Permission/storage state, safety rules |
| AndroidAutoBridge | Medium | Fake scenarios, public exports |
| ForegroundServiceBridge | High | Lifecycle intents, integration adapter behavior |
| AppLifecycleBridge | High | Lifecycle intents, integration adapter behavior |
| NotificationControlBridge | Medium | Fake scenarios, public exports |
| LockScreenBridge | Medium | Fake scenarios, public exports |
| HeadsetControlBridge | Medium | Fake scenarios, public exports |
| Composite Snapshot | Medium | View-state defaults |
| Fake Implementations | High | Sanitization, result mapping, missing dependency behavior |

High-risk items require negative tests, TDD where practical, and must prove failure paths are safe and deterministic.

## Behavior Budget check

This task stays within the budget defined in `design.md`:

- New behaviors: spec documentation only. Zero runtime behavior changes. ✓
- Public API changes: proposed only via future module layout. No source code. ✓
- Files allowed: spec directory only, plus `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md`. ✓
- Tests required: none. ✓
- Dependencies: none added. ✓
- Stop if implementation code needed. ✓

No budget overrun.

## Implementation tasks

All tasks below are for future implementation. Not executed now.

### Task 1: Create source file skeleton

- [ ] Create `src/noqlen_aria/android_boundaries.py` with module docstring and imports.
- [ ] Import `AriaResult`, `AriaError`, `PermissionState`, `StorageAccessState` from `noqlen_aria.contracts`.
- [ ] Create `tests/test_android_boundaries.py` with test imports and pytest markers.
- [ ] Validate: `python3 -m py_compile src/noqlen_aria/android_boundaries.py` passes.

### Task 2: Implement PlaybackEngine boundary

- [ ] Define `PlaybackState`, `PlaybackCommand`, `PlaybackPosition`, `TrackMetadata`, `PlaybackEngineSnapshot`.
- [ ] Define `PlaybackEngineBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakePlaybackEngineBridge` with deterministic behavior.
- [ ] Write TDD tests for all states, commands, metadata, snapshots, and fake determinism.
- [ ] Validate: pytest passes for playback engine tests.

### Task 3: Implement MediaSession boundary

- [ ] Define `MediaSessionAction`, `MediaSessionRepeatMode`, `MediaSessionShuffleMode`, `MediaSessionPlaybackState`, `MediaSessionMetadata`.
- [ ] Define `MediaSessionBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeMediaSessionBridge` with deterministic behavior.
- [ ] Write tests for action dispatch, state composition, metadata mapping.
- [ ] Validate: pytest passes for media session tests.

### Task 4: Implement AndroidStorage boundary

- [ ] Define `StorageType`, `StorageStatus`, `StorageRequirement`, `StorageStatusSnapshot`.
- [ ] Define `AndroidStorageBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeAndroidStorageBridge` with configurable permission/status states.
- [ ] Write TDD tests for all storage statuses, requirement checking, permission states.
- [ ] Validate: pytest passes for storage bridge tests.

### Task 5: Implement Android Auto boundary

- [ ] Define `AutoBrowseNodeType`, `AutoBrowseNode`, `AutoBrowseResult`, `AutoSearchResult`.
- [ ] Define `AndroidAutoBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeAndroidAutoBridge` with deterministic browse tree.
- [ ] Write tests for root, browse, search, play_from_node operations.
- [ ] Validate: pytest passes for Android Auto tests.

### Task 6: Implement Foreground Service boundary

- [ ] Define `ForegroundServiceState`, `ForegroundServiceRequirement`.
- [ ] Define `ForegroundServiceBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeForegroundServiceBridge` with deterministic lifecycle.
- [ ] Write TDD tests for state transitions, notification updates.
- [ ] Validate: pytest passes for foreground service tests.

### Task 7: Implement App Lifecycle boundary

- [ ] Define `AppLifecycleEvent`, `AppLifecycleState`.
- [ ] Define `AppLifecycleBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeAppLifecycleBridge` with deterministic state machine.
- [ ] Write TDD tests for event-to-state mapping, out-of-order events, foreground detection.
- [ ] Validate: pytest passes for app lifecycle tests.

### Task 8: Implement Notification/LockScreen/Headset boundaries

- [ ] Define `NotificationAction`, `LockScreenControlState`, `HeadsetEventType`.
- [ ] Define `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge` as `@runtime_checkable Protocol`.
- [ ] Implement `FakeNotificationControlBridge`, `FakeLockScreenBridge`, `FakeHeadsetControlBridge`.
- [ ] Write tests for notification actions, lock-screen state, headset events.
- [ ] Validate: pytest passes for all notification/peripheral tests.

### Task 9: Implement Composite Snapshot

- [ ] Define `AndroidBoundarySnapshot` compositing all boundary states.
- [ ] Write tests for composition, defaults, serialization round-trip, partial availability.
- [ ] Validate: pytest passes for snapshot tests.

### Task 10: Final validation

- [ ] Run full validation suite: `py_compile`, import check, pytest, contamination check.
- [ ] Confirm no regression in Bloco 0-3 tests.
- [ ] Confirm no forbidden files tracked.
- [ ] Commit implementation artifacts.

## Subagent packages

None required for spec phase.

Future implementation may benefit from subagents per boundary group:
- Agent 1: PlaybackEngine + MediaSession boundaries (Tasks 2-3)
- Agent 2: Storage + Foreground Service + Lifecycle boundaries (Tasks 4, 6, 7)
- Agent 3: Android Auto + Notification/LockScreen/Headset boundaries (Tasks 5, 8)
- Agent 4: Composite snapshot + final validation (Tasks 9-10)

## Validation checklist

Spec-only phase:

- [ ] `pwd` — confirm working directory.
- [ ] `git status --short --branch` — clean or only expected changes.
- [ ] `git diff --check` — no whitespace issues.
- [ ] `find aria/specs/features/android-player-boundary-contracts aria/context -maxdepth 5 -type f | sort` — all spec files present.
- [ ] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [ ] `python3 -m pytest` — all existing tests pass.
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [ ] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [ ] Confirm non-goals: no Android SDK, no Kotlin/Java/Gradle, no real playback, no Media3/ExoPlayer, no real MediaSession, no real Android Auto, no queue/now playing, no offline/cache.
- [ ] Confirm no source code changed outside spec scope.
- [ ] Confirm no pyproject.toml changed.
- [ ] Confirm no local/private/tooling artifacts staged.
- [ ] Confirm spec completeness: requirements, design, tasks, review all present.
- [ ] Confirm Canonical Examples use Given/When/Then format.
- [ ] Confirm Behavior Budget is present and respected.
- [ ] Confirm Test Risk Matrix is present.
- [ ] Confirm context package (Standard) is documented.
- [ ] Confirm contract list matches requirements (eight bridge protocols + composite snapshot).

## Delta update

- [ ] Update `aria/context/current.md` to reflect Bloco 4 spec completion.
- [ ] Update `aria/context/delta.md` to record Bloco 4 spec creation.
- [ ] Update `docs/handoff.md` with Bloco 4 spec status note if needed.
