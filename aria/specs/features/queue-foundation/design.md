# Design

## Summary

Bloco 11 adds queue foundation contracts and `QueueService` as deterministic app/player-facing state only. Queue items reference app-facing `LibraryItemSummary` values or abstract `MediaId` values. The service never plays audio, resolves streams, calls providers, mutates providers, imports Android SDK code, or implements now playing.

## Context Package

Standard. See `aria/context/context-packages.md`.

## Context Files Read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `aria/specs/_template/**`
- Bloco 8, 9, and 10 reviews
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing Project Context

Aria Core already has source-agnostic core contracts, media source models, and library summaries. Queue state should build on `LibraryItemSummary`, `MediaId`, and `MediaSourceId` while preserving provider boundaries. Bloco 12 now playing is not started.

## Files To Create

- `aria/specs/features/queue-foundation/requirements.md`
- `aria/specs/features/queue-foundation/design.md`
- `aria/specs/features/queue-foundation/tasks.md`
- `aria/specs/features/queue-foundation/review.md`
- `src/noqlen_aria/queue.py`
- `tests/test_queue_foundation.py`

## Files To Modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/specs/features/queue-foundation/tasks.md`
- `aria/specs/features/queue-foundation/review.md`

## Files That Must Not Be Touched

- Android/Kotlin/Java/Gradle files.
- UI, screen, navigation, player, now-playing, playback, offline/cache, smart playlist, or provider integration files.
- Private/local tooling files such as `.opencode/`, `.skills/`, `opencode.json`, `.env`, credentials, and secrets.
- `docs/handoff.md` unless a tiny status note is necessary.

## Proposed Models

- `QueueId = NewType("QueueId", str)`.
- `QueueItemId = NewType("QueueItemId", str)`.
- `QueueMode`: `STANDARD`, `RADIO`, `AUTOMATION` as contract vocabulary only.
- `QueueRepeatMode`: `OFF`, `ONE`, `ALL`.
- `QueueShuffleState`: `disabled: bool`, `seed: int`, with deterministic ordering by seed and item id.
- `QueueAvailabilityState`: `AVAILABLE`, `UNAVAILABLE`, `UNKNOWN`.
- `QueueItem`: queue item id, optional `LibraryItemSummary`, optional `MediaId`, optional `MediaSourceId`, availability, display name, and reason.
- `QueueState`: queue id, label, mode, items, current position, repeat mode, shuffle state, availability.
- `QueueCollectionState`: queues by id and selected queue id.
- `QueueOperation`: operation type, queue id, optional item, item id, target index, repeat mode, shuffle state, and label.
- `QueueIntent`: app-facing intent wrapper for a `QueueOperation`; not a playback intent.
- `QueueOperationResult`: changed flag plus resulting queue/collection state and optional message.
- `QueueService`: stateless service returning new immutable states.

## Service Responsibilities

`QueueService` creates and transforms local queue state. It supports creating queues, adding items, removing items, clearing queues, moving/reordering items, setting current position, setting repeat mode, setting shuffle state, selecting a queue by id, and returning deterministic display order for tests. It returns `AriaResult[QueueOperationResult]` and never mutates providers or external systems.

## Data Flow

Future UI/app code passes `QueueOperation` or calls specific `QueueService` methods with `QueueState`/`QueueCollectionState`. `QueueService` validates the request, creates a replacement state, and returns it through `AriaResult`. Queue items retain app-facing media references only.

## Queue Item References

When a library item is available, `QueueItem.from_library_item()` stores the `LibraryItemSummary` and copies its `item_id`, `source_id`, and display name into app-facing fields. Abstract media ids may be queued without a library summary through `QueueItem.from_media_id()`.

## Unavailable Media Representation

Unavailable media is represented by `QueueItem.availability = QueueAvailabilityState.UNAVAILABLE` and an optional safe `availability_reason`. The queue preserves this state and does not request streams, call `MediaSourceClient`, or call providers.

## Repeat and Shuffle Representation

Repeat state is a `QueueRepeatMode` enum. Shuffle state is a `QueueShuffleState` dataclass. Disabled shuffle returns insertion order. Enabled shuffle returns a deterministic order sorted by a stable key derived from `(seed, queue_item_id)`; tests can assert exact order.

## Multiple Queues

`QueueCollectionState` stores `queues: dict[QueueId, QueueState]` and `selected_queue_id`. `QueueService` methods that operate on a collection change only the targeted or selected queue.

## Queue State Transition Rules

- Creating a queue with no id uses a deterministic default id.
- Adding an item appends it and sets current position to `0` only if the queue was empty.
- Removing an item by id preserves valid current position or resets to `None` when empty.
- Moving an item requires an existing item id and a target index inside the queue.
- Setting current position requires an index inside the item range.
- Clearing a queue removes items and current position but preserves queue id, label, mode, repeat, shuffle, and availability.
- Selecting a queue requires an existing queue id and does not modify any queue content.
- Invalid operations return safe errors and do not mutate state.

## Error Handling

Invalid operations return `AriaResult(ok=False, error=AriaError(...))` with sanitized messages. Operation failures include unknown queue, unknown item, invalid position, invalid target index, and invalid operation payload.

## Security Considerations

Queue models contain app-facing identifiers and display strings only. They do not include credentials, raw provider responses, filesystem paths, stream URLs, or stack traces. Safe serialization uses existing `safe_serialize` behavior.

## Provider Boundary Considerations

Queue code must not import provider adapters, `MediaSourceClient`, Anchor internals, network clients, or filesystem traversal utilities. It may use `LibraryItemSummary`, `MediaId`, and `MediaSourceId` value models only.

## Dependencies

None. Use Python standard library plus existing Aria contracts and library/media value models.

## Risks

- Queue model names may overlap with future now-playing names. Mitigation: keep Bloco 11 names queue-specific.
- Shuffle behavior can become non-deterministic if random APIs are used. Mitigation: derive deterministic ordering from seed and item id.
- Service may accidentally drift into playback intent behavior. Mitigation: no play/pause/seek/stream APIs and tests enforce boundaries.

## Rollback Strategy

Revert `src/noqlen_aria/queue.py`, queue tests, queue exports, and queue-foundation spec/context changes. No migrations or external state exist.

## Validation Plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/queue-foundation aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Repository contamination check
- Provider/network/filesystem/Android/now-playing/offline/smart-playlist search checks

## Behavior Budget

- New behaviors: add queue state/contracts; add repeat/shuffle state; add queue operation/intent models; add `QueueService` for deterministic local state transitions; add multiple-queue contract support.
- Public API changes: expose only intentional queue foundation names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/queue-foundation/**`, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: create queue; add/remove/reorder items; move current position; repeat/shuffle state; unavailable item handling; multiple queue references; invalid operations; no provider/playback/network/filesystem behavior.
- Dependencies: none.
- Stop if: real playback, stream resolution, provider mutation, Android integration, or now-playing implementation becomes necessary.
