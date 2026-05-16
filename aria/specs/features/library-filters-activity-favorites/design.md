# Design

## Summary

Bloco 10 extends the library layer with filter/sort helpers, source-derived recently added/recently played/favorites state, and readiness/health badge models. The implementation remains fake-first and provider-agnostic by reusing existing `LibraryBrowseResult`, `LibraryItemSummary`, source capability summaries, and `MediaSourceClient` boundary methods.

## Context package

Standard. See `aria/context/context-packages.md`.

## Context files read

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
- `aria/specs/features/media-source-foundation/review.md`
- `aria/specs/features/library-browse-search/review.md`
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Bloco 8 introduced `MediaSourceClient`, source capabilities, source availability, and `FakeMediaSourceClient`. Bloco 9 introduced browse/search summaries and `LibraryBrowseService`/`LibrarySearchService`. Bloco 10 builds on those app-facing models and must not bypass them.

## Files to create

- `aria/specs/features/library-filters-activity-favorites/requirements.md`
- `aria/specs/features/library-filters-activity-favorites/design.md`
- `aria/specs/features/library-filters-activity-favorites/tasks.md`
- `aria/specs/features/library-filters-activity-favorites/review.md`
- `tests/test_library_filters_activity_favorites.py`

## Files to modify

- `src/noqlen_aria/library.py`
- `src/noqlen_aria/media_source.py`
- `src/noqlen_aria/__init__.py`
- Existing tests only where public exports or capability counts require updates.
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Android/Kotlin/Java/Gradle/UI/player/navigation files.
- Provider-specific implementation files.
- Anchor provider internals or Anchor CLI integration.
- Queue, now-playing, playback, offline/cache, smart playlist implementation files.
- Private/local tooling files, credentials, secrets, logs, caches, `.opencode/`, `.skills/`, and local config.

## Data flow

1. Browse/search still comes from `MediaSourceClient` through Bloco 9 services.
2. `LibraryFilterService.apply_filters` accepts a `LibraryBrowseResult`, `LibraryFilterSet`, and optional `LibrarySortOption`.
3. Filtering and sorting operate only on app-facing summary objects already returned by Aria Core.
4. `LibraryActivityService` requests activity from the source via `get_library_activity` and maps results into recent view states.
5. `LibraryFavoritesService` requests favorites through `get_favorites` and maps to `FavoritesViewState`.
6. Favorites mutation requests return unsupported/future-intent failure without calling source mutation methods.
7. Readiness/health badges use source info, capability summary, warnings, and availability states.

## Proposed model names

- Filters/sorting: `LibraryFilter`, `LibraryFilterSet`, `LibrarySortOption`, `LibrarySortDirection`.
- Activity/favorites: `LibraryActivityType`, `LibraryActivityRequest`, `LibraryActivityResult`, `RecentlyAddedViewState`, `RecentlyPlayedViewState`, `FavoriteItemSummary`, `FavoritesViewState`.
- Badges/services: `LibraryHealthBadge`, `LibraryReadinessBadge`, `LibraryFilterService`, `LibraryActivityService`, `LibraryFavoritesService`.

## Service responsibilities

- `LibraryFilterService`: validate supported filter/sort fields, return filtered/sorted `LibraryBrowseResult`, preserve source warnings/errors, and never call providers.
- `LibraryActivityService`: delegate read-only activity requests to source boundary, return safe unavailable view states for unsupported capabilities.
- `LibraryFavoritesService`: delegate read-only favorites requests, build favorites view state, and block real mutation.

## Existing browse/search model reuse

Filter/sort inputs and activity/favorites outputs use `LibraryBrowseItem` and `LibraryItemSummary` conversions. No provider or filesystem objects are introduced.

## Unsupported source capabilities

`SourceCapability.RECENTLY_ADDED`, `RECENTLY_PLAYED`, and `FAVORITES_READ` gate source activity/favorites reads. Unsupported capabilities return `available=False` with `CAPABILITY_NOT_SUPPORTED`, not exceptions.

## Degraded/unavailable source states

Degraded sources may return data with warnings and degraded badges. Unavailable sources return safe errors or unavailable states without crashing.

## Favorites boundary

Favorites are read/state-oriented only. A mutation request is represented as unsupported/future intent and does not call a provider or modify fake state.

## Deterministic tests

Fake source scenarios use fixed IDs, names, dates encoded as sortable strings, no randomness, no time reads, no network, no filesystem traversal, and no external process calls.

## Error handling

Validation failures return `AriaResult(ok=False, error=AriaError(...))` for local service misuse. Unsupported source capabilities return app-facing unavailable data with an embedded `AriaError` when the source method itself succeeds safely.

## Security considerations

All app-facing text flows through existing `AriaError`, `AriaWarning`, and `safe_serialize` behavior. No credentials, local paths, URLs, tokens, raw provider errors, filesystem paths, or provider internals are exposed.

## Provider boundary considerations

All provider behavior remains behind `MediaSourceClient`. No direct Navidrome/Jellyfin/Emby integration, Anchor provider internals, Anchor CLI calls, network calls, or filesystem scans are allowed.

## Dependencies

None.

## Risks

- Capability enum expansion can require updating existing tests.
- Filter/sort fields could grow into smart playlist logic; Bloco 10 limits them to simple app-facing predicates and deterministic ordering.
- Favorites mutation naming could imply writes; implementation returns unsupported instead.

## Rollback strategy

Revert the Bloco 10 spec directory, new tests, and the small additions to `library.py`, `media_source.py`, `__init__.py`, `current.md`, and `delta.md`.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/library-filters-activity-favorites aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Repository contamination and boundary search checks listed in the task prompt.

## Behavior Budget

- New behaviors: add library filter/sort models; add recently added/recently played/favorites models; add library readiness/health badge models; add service behavior for filter/sort/activity/favorites over existing app-facing library items; extend `FakeMediaSourceClient` scenarios only as needed.
- Public API changes: expose only intentional library filter/activity/favorites names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/library-filters-activity-favorites/**`, `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` only if a tiny status note is needed.
- Tests required: filtering, sorting, recently added, recently played, favorites available/unavailable, readiness/health badges, unsupported capability behavior, degraded/unavailable source behavior, no provider/filesystem/network behavior.
- Dependencies: none.
- Stop if: real provider mutation, direct filesystem access, queue/playback/now playing/cache, or smart playlist logic becomes necessary.
