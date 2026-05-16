# Requirements

## Status

Draft. Bloco 14 — Offline, Cache and Storage Policy foundation.

## Problem

Aria Core has no vocabulary for modeling offline availability, cache policy decisions, or storage pressure awareness. Without these policy-layer models, future UI and platform layers would need to invent their own cache/offline logic, creating inconsistency and provider coupling. Aria must provide deterministic, preview-only policy contracts so that offline/cache/storage decisions are predictable, safe, and provider-agnostic — before any real download or cache mutation is introduced.

## Goal

Add offline availability, cache policy and storage pressure foundations as policy/state/intent-preview models with deterministic local services. These models define *what* can be cached and *under what conditions*, but never *execute* the cache operation.

## Non-goals

- No real downloads.
- No real cache writes or deletes.
- No destructive cleanup.
- No filesystem traversal or device storage inspection.
- No Android storage APIs (SAF, MediaStore).
- No provider mutation.
- No stream resolution.
- No playback engine.
- No UI.
- No Bloco 15 stream quality/transcoding behavior.
- No network behavior.
- No Anchor/Navidrome/Jellyfin/Emby integration.
- No smart playlist implementation.

## Actors

- **Policy services**: offline/cache/storage policy evaluators that consume item metadata and explicit budget values.
- **Future UI/app layer**: consumers of cache policy states, previews, and confirmation requirements.
- **Future cache engine**: consumers of cache operation intents approved by policy.
- **Future platform storage layer**: consumers of storage pressure states and cleanup previews.

## Functional requirements

### FR-01: Offline availability evaluation
Aria must provide an `OfflineAvailabilityState` enum (AVAILABLE, UNAVAILABLE, UNKNOWN) and `OfflineAvailabilityReason` enum (SUPPORTED, UNSUPPORTED_SOURCE, NO_CACHE_CAPABILITY, ITEM_NOT_CACHEABLE, UNKNOWN) so that consumers can check whether a media item is eligible for offline use without executing any download.

### FR-02: Cache policy state and mode
Aria must provide `CachePolicyState` (ALLOWED, BLOCKED, REQUIRES_CONFIRMATION, UNKNOWN), `CachePolicyMode` (CONSERVATIVE, BALANCED, AGGRESSIVE), and `CacheEligibilityState` (ELIGIBLE, INELIGIBLE_FORMAT, INELIGIBLE_SOURCE, INELIGIBLE_UNSUPPORTED, UNKNOWN) so that cache decisions are explicit and configurable.

### FR-03: Cache operation intent and preview
Aria must provide `CacheOperationType` (ADD_TO_CACHE, REMOVE_FROM_CACHE, CLEAR_CACHE), `CacheOperationIntent`, `CacheOperationPreview`, and `CacheOperationResult` so that operations are expressed as intents with deterministic previews before any real execution. Previews must include a confirmation requirement when the operation is risky.

### FR-04: Pending cache operation tracking
Aria must provide `PendingCacheOperation` so that queued cache intents can be tracked in policy state without performing real work.

### FR-05: Storage pressure modeling
Aria must provide `StoragePressureLevel` (NONE, LOW, MEDIUM, HIGH, CRITICAL), `StoragePressureState`, and `StorageBudget` so that storage conditions are modeled deterministically from explicit input values — not real device inspection.

### FR-06: Storage pressure evaluation from explicit inputs
Aria must provide a `StoragePressureService` that calculates pressure levels from only explicit `StorageBudget` input values. It must classify pressure as CRITICAL when free_bytes < reserved_bytes, HIGH when free_bytes < 10% of max_bytes, MEDIUM when free_bytes < 25%, LOW when free_bytes < 50%, and NONE otherwise.

### FR-07: Cache cleanup preview without deletion
Aria must provide `CacheCleanupPolicy`, `CacheCleanupPreview`, and a `CacheCleanupPreviewService` that generates a preview of candidate cleanup effects — listing candidate items, estimated bytes, and confirmation requirements — without deleting any real files.

### FR-08: Confirmation-required state
Aria must provide `CacheConfirmationState` (NOT_REQUIRED, REQUIRED) and `CacheBlockedReason` (SOURCE_UNAVAILABLE, ITEM_NOT_CACHEABLE, STORAGE_PRESSURE_CRITICAL, STORAGE_PRESSURE_HIGH, BUDGET_EXCEEDED, INVALID_BUDGET, OPERATION_UNSUPPORTED, NONE) so that risky operations require explicit confirmation.

### FR-09: Invalid budget/size validation
Aria must return safe error/blocked results when storage budget values are invalid (negative max_bytes, negative size estimates, overflow conditions, zero-budget operations).

### FR-10: Deterministic local policy services
All services must be deterministic: they must depend only on explicit input values and never call network, filesystem, provider internals, Android APIs, or playback engines.

### FR-11: Safe confirmation modeling
When a cache operation requires confirmation, the preview result must explicitly set `CacheConfirmationState.REQUIRED` and include a human-readable summary so that UI can prompt the user without risk of accidental execution.

### FR-12: OfflineCachePolicyService
Aria must provide `OfflineCachePolicyService` with methods:
- `evaluate_offline_availability` — returns `OfflineAvailabilityState` and reason from item metadata and source capabilities.
- `evaluate_cache_eligibility` — returns `CacheEligibilityState` for a given item.
- `preview_cache_operation` — returns a `CacheOperationResult` with preview, confirmation state, and blocked reason.

## Non-functional requirements

### NFR-01: Python stdlib only
No external dependencies beyond `noqlen_aria.contracts`. Uses `dataclasses`, `enum`, `typing` from stdlib.

### NFR-02: No provider integration
No imports from Anchor, Navidrome, Jellyfin, Emby, or any provider library.

### NFR-03: No Android platform code
No Android SDK, Kotlin, Java, Gradle, SAF, MediaStore, or platform-specific imports.

### NFR-04: No filesystem or network access
No `os`, `os.path`, `pathlib`, `glob`, `shutil`, `urllib`, `http`, `requests`, `aiohttp`, `socket`, or similar modules that touch filesystem or network.

### NFR-05: No real cache mutation
No file creation, deletion, modification, or filesystem traversal.

### NFR-06: Deterministic behavior
Same inputs produce same outputs. No randomness, time-dependence, or external state.

### NFR-07: AriaResult consistency
All service methods return `AriaResult[T]` where T is the appropriate model type.

### NFR-08: Public names intentional
All exported types are listed in `__all__`. Names use Aria domain vocabulary, not provider brands.

## Canonical Examples

### CE-01: Offline available state
Given a media item from a cache-capable source and the item is marked as downloadable,
When `evaluate_offline_availability` is called,
Then the service returns `OfflineAvailabilityState.AVAILABLE` with `OfflineAvailabilityReason.SUPPORTED` — without downloading anything.

### CE-02: Cache ineligible item
Given a media item from a source that does not support caching,
When `evaluate_cache_eligibility` is called,
Then the service returns `CacheEligibilityState.INELIGIBLE_SOURCE` safely.

### CE-03: Storage pressure blocks cache
Given storage pressure is HIGH (free_bytes < 10% of max_bytes),
When `evaluate_cache_eligibility` is called for a cachable item under conservative policy,
Then the service returns `CachePolicyState.BLOCKED` with `CacheBlockedReason.STORAGE_PRESSURE_HIGH`.

### CE-04: Cache operation requires confirmation
Given a cache operation intent under HIGH storage pressure and AGGRESSIVE policy,
When `preview_cache_operation` is called,
Then the preview returns `CacheConfirmationState.REQUIRED` and the confirmation message is explicit.

### CE-05: Cleanup preview without deletion
Given a cleanup request with a `CacheCleanupPolicy` targeting items older than 30 days,
When `preview_cleanup` is called,
Then the service returns a `CacheCleanupPreview` listing candidate items and estimated bytes freed — without deleting any real files.

### CE-06: Invalid budget validation
Given a `StorageBudget` with `max_bytes = -1`,
When `evaluate_pressure` is called,
Then the service returns an error result with a validation error message.

### CE-07: Invalid size blocks operation
Given a cache operation with estimated_size_bytes = -500,
When `preview_cache_operation` is called,
Then the preview returns `CacheBlockedReason.INVALID_BUDGET` and allows = False.

### CE-08: UI-safe state consumption
Given the UI needs offline status,
When it consumes `OfflineAvailabilityState` and `CacheEligibilityState` from Aria Core,
Then it uses Aria Core models exclusively and does not call Android/filesystem/provider APIs directly.

## Edge cases

- EC-01: Item with no cache capability returns UNAVAILABLE.
- EC-02: Zero max_bytes budget returns NONE pressure level.
- EC-03: Exactly at boundary (free_bytes = 10% of max) is classified as MEDIUM, not HIGH.
- EC-04: Add operation when cache is full returns BLOCKED.
- EC-05: Remove operation on non-cached item returns safe result without error.
- EC-06: Empty cleanup candidate list returns preview with zero items and zero bytes.
- EC-07: Conservative policy mode blocks all operations under MEDIUM pressure when requires confirmation.
- EC-08: Balanced policy mode allows operations under LOW pressure without confirmation.
- EC-09: Aggressive policy mode allows operations under MEDIUM pressure without confirmation.
- EC-10: Cleanup preview with max_candidates=0 returns empty list.
- EC-11: Budget with used_bytes > max_bytes returns CRITICAL pressure.
- EC-12: Budget with reserved_bytes > max_bytes returns invalid error.

## Acceptance criteria

1. All FR-01 through FR-12 implemented and testable.
2. All NFR-01 through NFR-08 enforced.
3. All 8 canonical examples pass as test cases.
4. All 12 edge cases covered in tests.
5. No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage API, provider mutation, stream resolution, or playback engine.
6. Behavior Budget respected.
7. Test Risk Matrix applied.
8. `python3 -m pytest` passes with all existing tests.
9. Repository hygiene and contamination checks pass.
10. Spec review initialized.

## Open questions

- None. Scope is clearly bounded by non-goals.
