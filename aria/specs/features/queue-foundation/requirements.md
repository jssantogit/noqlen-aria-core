# Requirements

## Status

Approved for Bloco 11 implementation.

Context package used: Standard.

## Problem

Aria Core has media source and library state, but no app/player-facing queue contracts. Future UI, now-playing, and playback-intent work need deterministic queue state that can reference app-facing library/media items without playing audio, resolving streams, or calling providers.

## Goal

Add queue foundation models and a deterministic local `QueueService` for safe queue state transitions. Queues are app/player-facing state only and must support multiple queue references as a contract direction.

## Non-goals

- No real playback.
- No stream resolution.
- No provider integration.
- No direct Navidrome/Jellyfin/Emby integration.
- No Anchor provider internals.
- No Android/UI.
- No now playing.
- No offline/cache.
- No smart playlist logic.
- No filesystem traversal.
- No network behavior.
- No provider mutation.
- No `PlaybackIntentService` implementation.

## Actors

- Future UI/app/player adapter consuming queue state.
- Aria Core service code applying deterministic queue operations.
- Tests/fakes verifying local queue behavior.

## Functional Requirements

- FR-01: Define `QueueId` and `QueueItemId` reference types.
- FR-02: Define `QueueItem` that references app-facing `LibraryItemSummary` or an abstract `MediaId` without provider internals.
- FR-03: Define `QueueState` with queue id, mode/type, items, current position, repeat mode, shuffle state, and availability state.
- FR-04: Define `QueueCollectionState` for multiple queues and selected queue id.
- FR-05: Define `QueueRepeatMode`, `QueueShuffleState`, `QueueAvailabilityState`, and `QueueMode` or equivalent queue type model.
- FR-06: Define `QueueOperation`, `QueueIntent`, and `QueueOperationResult` models for app-facing queue mutations.
- FR-07: Implement `QueueService` for local deterministic state transitions: create, add, remove, clear, move/reorder, set current position, set repeat mode, set shuffle state, and select queue by id.
- FR-08: Preserve unavailable item state safely and never resolve streams.
- FR-09: Return safe `AriaResult`/operation result failures for invalid operations.
- FR-10: Support multiple queues as contracts/state, not UI tabs/screens.
- FR-11: Provide fake queue scenarios for tests.
- FR-12: Export only intentional queue foundation names from the public package.

## Non-functional Requirements

- NFR-01: Python standard library only; no new dependencies.
- NFR-02: No Android SDK, UI framework, playback engine, network, provider, or filesystem dependency.
- NFR-03: Queue behavior must be deterministic and serialization-safe.
- NFR-04: Queue models must be app-facing and provider-agnostic.
- NFR-05: Invalid operations must be safe, explicit, and non-mutating.
- NFR-06: Tests must cover positive and negative queue transitions.

## Canonical Examples

- Given an empty queue, When a track summary is added, Then `QueueState` contains one app-facing `QueueItem`.
- Given a queue has three items, When an item is moved, Then order is deterministic and current position remains valid.
- Given repeat-one is enabled, When queue state is serialized, Then repeat state is explicit and no playback occurs.
- Given shuffle is enabled, When queue order is requested, Then behavior is deterministic in tests.
- Given an item is unavailable, When it is added to queue, Then queue preserves safe unavailable state and does not resolve streams.
- Given multiple queues exist, When a queue is selected by id, Then only that queue state is changed.
- Given UI needs queue later, When it consumes queue data, Then it uses Aria Core models and does not call media sources/providers directly.

## Edge Cases

- Removing an unknown queue item id fails safely.
- Moving an unknown queue item id fails safely.
- Moving to a negative or out-of-range index fails safely.
- Setting current position outside bounds fails safely.
- Setting current position on an empty queue fails safely unless clearing uses `None`.
- Removing the current item keeps current position valid or resets it when the queue becomes empty.
- Clearing a queue removes items and current position but preserves queue identity and settings.
- Selecting an unknown queue id fails safely.
- Adding an unavailable item preserves `QueueAvailabilityState.UNAVAILABLE` without resolution.

## Acceptance Criteria

- Spec files exist under `aria/specs/features/queue-foundation/`.
- Queue contracts are implemented in `src/noqlen_aria/**`.
- `QueueService` implements deterministic local state transitions.
- Tests cover required queue state and operation behavior.
- Public API exports only intentional queue names.
- No Bloco 12 now-playing behavior is implemented.
- No real playback, stream resolution, provider integration, filesystem, network, Android/UI, offline/cache, or smart playlist behavior is added.
- `current.md` and `delta.md` are updated concisely.

## Open Questions

- Future specs will decide whether queue intents flow into a `PlaybackIntentService` or another playback orchestration boundary.
- Future specs will decide how persisted queue snapshots are versioned.
