# Design

## Summary

Bloco 14 adds offline availability, cache policy and storage pressure foundations to Aria Core as policy/state/intent-preview models with deterministic local services. Implementation lives in a single new module `src/noqlen_aria/offline_cache.py`. All models are `@dataclass(frozen=True)` or `Enum`. All services are plain classes returning `AriaResult[T]`. No real download, cache mutation, filesystem access, network access, Android APIs, or provider integration.

## Context package

Standard. Per `aria/context/context-packages.md`.

## Context files read

- `AGENTS.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/scope-boundaries.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `aria/context/repository-hygiene.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `aria/specs/_template/` (requirements, design, tasks, review)
- `aria/specs/features/media-source-foundation/review.md`
- `aria/specs/features/library-browse-search/review.md`
- `aria/specs/features/library-filters-activity-favorites/review.md`
- `aria/specs/features/playback-renderer-automation-intents/review.md`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/playback_intents.py`
- `src/noqlen_aria/library.py`
- `src/noqlen_aria/services.py`
- `tests/test_playback_renderer_automation_intents.py`
- `tests/test_library_filters_activity_favorites.py`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core is a modular Python core of a music player with:
- `contracts.py` — `AriaResult[T]`, `AriaError`, `AriaWarning`, safe serialization
- `media_source.py` — `MediaSourceClient`, `FakeMediaSourceClient`, `SourceCapability`
- `library.py` — browse, search, filter, activity, favorites
- `queue.py` — queue state, service
- `now_playing.py` — now playing state, service
- `playback_intents.py` — playback, renderer, automation intents
- Models are `@dataclass(frozen=True)` or `Enum` with `auto()`
- Services are plain classes with deterministic methods returning `AriaResult[T]`
- Tests use `_data(result)` / `_err(result)` pattern

## Files to create

- `aria/specs/features/offline-cache-storage-policy/requirements.md`
- `aria/specs/features/offline-cache-storage-policy/design.md`
- `aria/specs/features/offline-cache-storage-policy/tasks.md`
- `aria/specs/features/offline-cache-storage-policy/review.md`
- `src/noqlen_aria/offline_cache.py` — all models and services
- `tests/test_offline_cache_storage_policy.py` — all tests

## Files to modify

- `src/noqlen_aria/__init__.py` — add offline/cache/storage policy exports
- `aria/context/current.md` — update active milestone and spec
- `aria/context/delta.md` — record Bloco 14 implementation
- `docs/handoff.md` — tiny status note (if needed)

## Files that must not be touched

- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/anchor_adapter.py`
- `src/noqlen_aria/android_boundaries.py`
- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/media_source.py`
- `src/noqlen_aria/library.py`
- `src/noqlen_aria/queue.py`
- `src/noqlen_aria/now_playing.py`
- `src/noqlen_aria/playback_intents.py`
- `pyproject.toml`
- All existing test files (except when imports are benign)
- All Android, Kotlin, Java, Gradle files
- Any secret, credential, log, cache, or temporary file

## Data flow

```
UI/App -> OfflineCachePolicyService.evaluate_offline_availability(item, source_capabilities)
       -> OfflineAvailabilityState + OfflineAvailabilityReason
       -> consumes state; no filesystem/network calls

UI/App -> OfflineCachePolicyService.preview_cache_operation(intent, policy, budget)
       -> CacheOperationResult with preview, confirmation state, blocked reason
       -> UI shows preview; no real execution

Future Cache Engine -> approved CacheOperationIntent -> real download (future Bloco, out of scope)

UI/App -> StoragePressureService.evaluate_pressure(budget)
       -> StoragePressureState with level and details
       -> purely arithmetic from explicit input

UI/App -> CacheCleanupPreviewService.preview_cleanup(policy, budget, candidates)
       -> CacheCleanupPreview listing items never deleted
```

## Error handling

All service methods return `AriaResult[T]`:
- `ok=True, data=...` for successful evaluation
- `ok=False, error=AriaError(...)` for invalid input (negative budgets, etc.)

Services never raise exceptions. Invalid inputs produce safe error results.

Blocked operations return `ok=True, data=CacheOperationResult(allowed=False, ...)` — the result itself carries the blocked state. This distinguishes "the policy evaluation succeeded but the operation is blocked" from "the policy service itself failed".

## Security considerations

- No secrets, credentials, or tokens are handled.
- No file paths or URLs are constructed or returned.
- All outputs are display-safe Aria model values.
- No raw exceptions or stack traces are exposed.

## Storage safety considerations

- No filesystem access of any kind.
- No directory traversal, file listing, or file stat.
- No `os`, `os.path`, `pathlib`, `glob`, `shutil`, or `tempfile` imports.
- Storage budget values come only from explicit function parameters.

## Provider boundary considerations

- No provider imports or calls.
- No Anchor, Navidrome, Jellyfin, Emby references.
- `SourceCapability` enum from media_source.py is referenced only as a type hint for evaluating source cache capability.
- Services do not instantiate or call `MediaSourceClient`.

## Offline/cache policy rules

### Pressure classification (StoragePressureService)

| Condition | Level |
|-----------|-------|
| max_bytes <= 0 | returns error |
| free_bytes <= 0 | CRITICAL |
| free_bytes <= reserved_bytes | CRITICAL |
| used_bytes > max_bytes | CRITICAL |
| free_bytes <= 10% * max_bytes | HIGH |
| free_bytes <= 25% * max_bytes | MEDIUM |
| free_bytes <= 50% * max_bytes | LOW |
| otherwise | NONE |

### Cache policy per mode

| Mode | NONE/LOW pressure | MEDIUM pressure | HIGH pressure | CRITICAL pressure |
|------|------------------|----------------|---------------|-------------------|
| CONSERVATIVE | ALLOWED (no confirm) | BLOCKED | BLOCKED | BLOCKED |
| BALANCED | ALLOWED (no confirm) | ALLOWED (confirm) | BLOCKED | BLOCKED |
| AGGRESSIVE | ALLOWED (no confirm) | ALLOWED (no confirm) | ALLOWED (confirm) | BLOCKED |

When `REQUIRES_CONFIRMATION` is returned, `CacheConfirmationState.REQUIRED` is set on the preview.

## Cleanup preview rules

Cleanup preview is generated from explicit candidate lists and policy rules. The service:
- Filters candidates by policy (min_age_days, max_candidates)
- Sums estimated bytes
- Returns preview without modifying anything
- Respects reserved_bytes from budget (bytes below reserved are never cleaned)
- Returns empty preview for zero candidates or zero max_candidates

## Dependencies

Internal only:
- `noqlen_aria.contracts` — `AriaResult`, `AriaError`

No external dependencies. No `pyproject.toml` changes.

## Risks

- R01: Pressure classification thresholds are arbitrary and may need tuning for real devices. Mitigation: thresholds are simple percentages; easy to adjust.
- R02: Cleanup preview depends on explicit candidate lists; real candidate enumeration is deferred to future cache engine. Mitigation: preview accepts explicit lists from caller.
- R03: Conservative/Balanced/Aggressive mode semantics may not match all user expectations. Mitigation: modes are documented as policy rules; services are deterministic so behavior is predictable.

## Risk classification

Per `aria/context/test-risk-matrix.md`:
- **High risk**: cache eligibility, storage pressure policy, cleanup preview, confirmation-required behavior, invalid budget/size validation.
- **Medium risk**: model defaults, serialization, service determinism.

## Rollback strategy

Remove `src/noqlen_aria/offline_cache.py`, `tests/test_offline_cache_storage_policy.py`, revert `__init__.py`, and remove spec directory. No other files affected.

## Validation plan

1. `pwd`
2. `git status --short --branch`
3. `find src/noqlen_aria tests aria/specs/features/offline-cache-storage-policy aria/context -maxdepth 6 -type f | sort`
4. `git diff --check`
5. `python3 -m py_compile src/noqlen_aria/*.py`
6. `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
7. `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
8. `python3 -m pytest`
9. `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true`
10. Provider boundary: `grep -R "NavidromeProvider\|Jellyfin\|Emby\|noqlen_anchor.cli\|subprocess.*noqlen-anchor" -n src tests || true`
11. Network: `grep -R "requests\.|httpx\.|aiohttp\.|urllib\.|socket\." -n src tests || true`
12. Filesystem: `grep -R "os.walk\|glob\.glob\|pathlib.Path.*iterdir\|scandir\|unlink\|rmtree\|remove(" -n src tests || true`
13. Android: `grep -R "android\.\|androidx\.\|MediaStore\|SAF\|Media3\|ExoPlayer\|Activity\|Fragment\|Compose\|Kotlin\|Gradle" -n src tests || true`
14. Forbidden future: `grep -R "Transcode\|StreamQuality\|SmartPlaylist" -n src tests || true`

## Behavior Budget

- **New behaviors**: add offline/cache/storage policy models; add cache operation intent/preview models; add storage pressure models; add cleanup preview models; add deterministic local policy services.
- **Public API changes**: expose offline/cache/storage policy names via `__init__.py` and `offline_cache.py` `__all__`.
- **Files allowed**: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/offline-cache-storage-policy/**`, `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md`.
- **Tests required**: offline available/unavailable behavior; cache eligibility; cache policy modes; pending cache operations; storage pressure levels; cleanup preview behavior; confirmation-required behavior; invalid budget/size behavior; no real filesystem/provider/network/Android behavior.
- **Dependencies**: none beyond `noqlen_aria.contracts`.
- **Stop if**: real download/cache write/delete becomes necessary; device storage inspection becomes necessary; Android storage API becomes necessary; provider mutation becomes necessary; stream resolution/playback becomes necessary.
