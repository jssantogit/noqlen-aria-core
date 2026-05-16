# Requirements

## Status

Approved for Bloco 10 implementation in this task. Context package: Standard.

## Problem

Bloco 9 exposes source-derived app-facing library browse/search results, but app and future UI layers still lack core-owned contracts for filtering, sorting, recent activity, favorites state, and library readiness/health badges. Without those contracts, future UI would be tempted to call providers directly or invent provider-specific state.

## Goal

Add small, deterministic Aria Core models and services for library filters, sorting, recently added, recently played, favorites read state, favorites mutation blocking/future intent, and library readiness/health badges over existing app-facing source-derived library items.

## Non-goals

- No real provider integration.
- No direct Navidrome/Jellyfin/Emby integration.
- No Anchor provider internals.
- No filesystem traversal.
- No real favorites mutation.
- No smart playlist implementation.
- No queue, now-playing, or playback.
- No offline/cache.
- No Android/UI.
- No streaming implementation.
- No package publishing or git tag creation.

## Actors

- Future UI/app consuming Aria Core models.
- Aria Core library services.
- `MediaSourceClient` implementations and deterministic fakes.
- Tests verifying source boundary behavior.

## Functional requirements

- FR-01: Define `LibraryFilter` and `LibraryFilterSet` contracts for filtering app-facing library summaries.
- FR-02: Define `LibrarySortOption` and `LibrarySortDirection` contracts for deterministic ordering.
- FR-03: Define `LibraryActivityType`, `LibraryActivityRequest`, and `LibraryActivityResult` for source-derived recent activity.
- FR-04: Define `RecentlyAddedViewState` and `RecentlyPlayedViewState` view-state helpers.
- FR-05: Define `FavoriteItemSummary` and `FavoritesViewState` for favorites read state.
- FR-06: Define `LibraryHealthBadge` and `LibraryReadinessBadge` for source/library availability and warnings.
- FR-07: Implement `LibraryFilterService` over existing `LibraryBrowseResult` items without changing source data.
- FR-08: Implement `LibraryActivityService` that delegates through `MediaSourceClient` and returns safe unavailable state for unsupported capabilities.
- FR-09: Implement `LibraryFavoritesService` that reads favorites through `MediaSourceClient` and blocks real mutations as unsupported/future intent only.
- FR-10: Extend `FakeMediaSourceClient` only with deterministic activity/favorites/readiness scenarios needed for tests.
- FR-11: Surface degraded/unavailable source states without crashes.
- FR-12: Keep UI consumption on Aria Core models only.

## Non-functional requirements

- Use Python standard library only.
- Keep models dataclass/enum based and safe to serialize with existing helpers.
- Preserve source/provider boundaries and avoid provider-specific imports or names in public model behavior.
- Keep fake behavior deterministic, local, offline, and side-effect free.
- Keep behavior limited to Bloco 10; do not add Bloco 11 or Audit 8-10 behavior.

## Canonical Examples

- Given a library result has artists/albums/tracks, When a filter is applied, Then Aria returns a filtered app-facing result without changing the source.
- Given a library result has sortable fields, When a sort option is applied, Then Aria returns a deterministic ordered result.
- Given a source supports recently added, When recently added is requested, Then Aria returns normalized library item summaries.
- Given a source does not support recently played, When recently played is requested, Then Aria returns a safe unavailable result.
- Given a source supports favorites read state, When favorites are requested, Then Aria returns normalized favorite item summaries.
- Given favorites write/mutation is requested, When Bloco 10 handles it, Then it must be represented as unsupported or future intent, not real mutation.
- Given a source is degraded, When readiness badges are built, Then Aria returns warning/degraded badges without crashing.
- Given UI needs favorites later, When it consumes data, Then it uses Aria Core models only and does not call providers directly.

## Edge cases

- Empty library results stay empty after filtering and sorting.
- Unsupported filter fields return safe validation errors.
- Unsupported sort fields return safe validation errors.
- Sources without recently added/recently played/favorites capabilities return available=false app-facing results.
- Degraded sources preserve warnings and health/readiness badges.
- Unavailable sources return safe errors or unavailable view state.
- Empty activity/favorites lists are valid available results when capability exists.
- Favorites mutation requests never call a backend and never modify fake source state.

## Acceptance criteria

- Spec, implementation, tests, review, current, and delta are updated.
- Behavior Budget is present and respected.
- Test Risk Matrix is present and covered.
- Tests cover filtering, sorting, activity, favorites, unsupported capabilities, readiness/health badges, degraded/unavailable source behavior, and boundary checks.
- No real provider/filesystem/network/playback/UI/queue/cache behavior is added.
- Required validation passes.

## Open questions

- None for Bloco 10. Real provider mapping, favorites writes, smart playlists, queue, now playing, playback, Android/UI, and offline/cache require future specs.
