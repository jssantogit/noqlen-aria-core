# Tasks

## Preparation checklist

- [x] Read all required context files.
- [x] Read existing spec templates and review files.
- [x] Read existing source and test files for conventions.
- [x] Create spec directory: `aria/specs/features/offline-cache-storage-policy/`.
- [ ] Create `requirements.md`.
- [ ] Create `design.md`.
- [ ] Create `tasks.md`.
- [ ] Create `review.md`.
- [ ] Implement `src/noqlen_aria/offline_cache.py`.
- [ ] Implement `tests/test_offline_cache_storage_policy.py`.
- [ ] Update `src/noqlen_aria/__init__.py`.
- [ ] Update `aria/context/current.md`.
- [ ] Update `aria/context/delta.md`.
- [ ] Run validation.
- [ ] Commit.

## TDD classification

- **Required** (must have negative tests): cache eligibility, storage pressure policy, cleanup preview, confirmation-required behavior, invalid budget/size validation.
- **Recommended**: model defaults and serialization.

## Test Risk Matrix

Per `aria/context/test-risk-matrix.md`:

| Area | Classification | Tests needed | Negative tests required |
|------|---------------|-------------|------------------------|
| Cache eligibility (FR-02) | High risk | 8+ | Yes (ineligible cases) |
| Storage pressure policy (FR-05, FR-06) | High risk | 10+ | Yes (invalid, critical) |
| Cleanup preview (FR-07) | High risk | 8+ | Yes (empty, zero-candidate) |
| Confirmation-required (FR-08) | High risk | 8+ | Yes (blocked without confirm) |
| Invalid budget/size (FR-09) | High risk | 8+ | Yes (negative, overflow) |
| Offline availability (FR-01) | Medium risk | 5+ | Yes (unsupported sources) |
| Cache operation preview (FR-03) | Medium risk | 6+ | Yes (blocked operations) |
| Pending cache operations (FR-04) | Medium risk | 4+ | Yes (empty states) |
| Model defaults and serialization | Medium risk | 5+ | No (correctness only) |
| OfflineCachePolicyService (FR-12) | High risk | 8+ | Yes (all paths) |
| StoragePressureService (FR-06) | High risk | 8+ | Yes (all levels) |
| CacheCleanupPreviewService (FR-07) | High risk | 8+ | Yes (edge cases) |
| Determinism, no external calls | High risk | 4+ | Yes |

## Behavior Budget check

- [ ] New behaviors: offline/cache/storage policy models, cache operation intent/preview models, storage pressure models, cleanup preview models, deterministic local policy services. Within budget.
- [ ] Public API changes: `src/noqlen_aria/offline_cache.py` exports and `__init__.py` updates. Within budget.
- [ ] Files: only source, tests, spec, context, handoff files touched. Within budget.
- [ ] Tests: 80+ tests planned covering all high-risk areas. Within budget.
- [ ] Dependencies: none beyond `noqlen_aria.contracts`. Within budget.
- [ ] Stop conditions not triggered.

## Implementation tasks

### T-01: Create spec files
Create `requirements.md`, `design.md`, `tasks.md`, `review.md` in `aria/specs/features/offline-cache-storage-policy/`.

### T-02: Implement offline/cache/storage policy models
In `src/noqlen_aria/offline_cache.py`, define:
- `OfflineAvailabilityState`, `OfflineAvailabilityReason`
- `CachePolicyState`, `CachePolicyMode`, `CacheEligibilityState`
- `CacheOperationIntent`, `CacheOperationType`, `CacheOperationPreview`, `CacheOperationResult`
- `PendingCacheOperation`
- `StoragePressureState`, `StoragePressureLevel`, `StorageBudget`
- `CacheCleanupPolicy`, `CacheCleanupPreview`
- `CacheConfirmationState`, `CacheBlockedReason`

### T-03: Implement OfflineCachePolicyService
Add `OfflineCachePolicyService` with `evaluate_offline_availability`, `evaluate_cache_eligibility`, and `preview_cache_operation`.

### T-04: Implement StoragePressureService
Add `StoragePressureService` with `evaluate_pressure` and `can_accept_operation`.

### T-05: Implement CacheCleanupPreviewService
Add `CacheCleanupPreviewService` with `preview_cleanup` and `evaluate_cleanup_candidates`.

### T-06: Update __init__.py exports
Add all Bloco 14 public names to `src/noqlen_aria/__init__.py` and `__all__`.

### T-07: Write tests
Create `tests/test_offline_cache_storage_policy.py` covering all canonical examples, edge cases, high-risk areas, and model defaults.

### T-08: Validate boundaries
Run all search checks to confirm no forbidden behavior.

### T-09: Update workflow state
Update `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md`.

## Validation checklist

- [ ] `pwd`
- [ ] `git status --short --branch`
- [ ] `find` — expected files present
- [ ] `git diff --check`
- [ ] `python3 -m py_compile src/noqlen_aria/*.py`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [ ] `python3 -m pytest` — all tests pass
- [ ] Repository contamination check
- [ ] Provider boundary search
- [ ] Network boundary search
- [ ] Filesystem boundary search
- [ ] Android boundary search
- [ ] Forbidden future implementation search (Transcode, StreamQuality, SmartPlaylist)

## Review checklist

- [ ] All FR-01 through FR-12 implemented
- [ ] All NFR-01 through NFR-08 enforced
- [ ] 8 canonical examples tested
- [ ] 12 edge cases tested
- [ ] Behavior Budget respected
- [ ] Test Risk Matrix applied
- [ ] No real download/cache write/delete
- [ ] No filesystem traversal
- [ ] No Android storage APIs
- [ ] No provider integration
- [ ] No stream resolution/playback
- [ ] No Bloco 15 behavior
- [ ] Spec review initialized

## Delta update checklist

- [ ] Update `aria/context/current.md` — active milestone, active spec, current goal.
- [ ] Update `aria/context/delta.md` — what changed, evidence, decisions, next step.
- [ ] Optionally update `docs/handoff.md` with tiny status note.
