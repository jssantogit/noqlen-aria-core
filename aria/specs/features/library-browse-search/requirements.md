# Requirements

## Status

Approved for implementation in this combined Bloco 9 spec and implementation task.

Context package used: Standard.

## Problem

Bloco 8 created the media source boundary, but Aria Core still has no app-facing library browse/search contracts. Future UI must not call media sources, provider APIs, Anchor internals, a local filesystem, streaming, playback, queue, or cache code directly. Aria needs a small foundation that normalizes source data into safe, source-agnostic browse/search state.

## Goal

Add library browse/search models and services on top of `MediaSourceClient` for artists, albums, tracks/songs, playlists, genres, and safe source-provided folder entries.

## Non-goals

- No real provider integration.
- No direct Navidrome, Jellyfin, or Emby integration.
- No Anchor provider internals.
- No Anchor CLI integration.
- No filesystem traversal.
- No real streaming.
- No playback engine.
- No Android, UI, screen, navigation, Kotlin, Java, or Gradle work.
- No filters, sorting, favorites, recently-added, or recently-played behavior.
- No queue, now-playing, offline, cache, or download behavior.

## Actors

- Future UI/App/Player: consumes Aria Core browse/search models only.
- `LibraryBrowseService`: app-facing browse orchestration over `MediaSourceClient`.
- `LibrarySearchService`: app-facing search orchestration over `MediaSourceClient`.
- `MediaSourceClient`: media/library boundary consumed by services.
- `FakeMediaSourceClient`: deterministic source fake for tests.

## Functional requirements

- FR-01: Define `LibraryBrowseCategory` for artists, albums, tracks, playlists, genres, and folders.
- FR-02: Define browse request/result models with safe unavailable output for unsupported categories.
- FR-03: Define search query/result models with safe validation output for empty or invalid queries.
- FR-04: Define source-agnostic summaries: `ArtistSummary`, `AlbumSummary`, `TrackSummary`, `PlaylistSummary`, `GenreSummary`, `FolderSummary`, and `LibraryItemSummary`.
- FR-05: `LibraryBrowseService` must consume `MediaSourceClient`, never provider APIs or filesystem traversal.
- FR-06: `LibrarySearchService` must consume `MediaSourceClient`, never provider APIs or network calls.
- FR-07: Unsupported playlists or folders must return a safe unavailable result, not raise.
- FR-08: Degraded source warnings must be preserved in browse/search results.
- FR-09: Unavailable sources must return safe errors/results without crashing.
- FR-10: Folder browsing must treat folder entries as source metadata only.
- FR-11: `FakeMediaSourceClient` must include deterministic scenarios for healthy, no-playlists, no-folders, degraded, unavailable, empty library, empty/no-match search, and invalid query behavior.

## Non-functional requirements

- Deterministic tests only.
- Python standard library only.
- No new dependencies.
- App-facing errors and warnings remain sanitized by existing `AriaError` and `AriaWarning` behavior.
- Public API expansion is limited to intentional library browse/search names.

## Canonical Examples

- Given a fake media source supports artists, When artists are browsed, Then Aria returns normalized artist summaries.
- Given a fake media source supports albums and tracks, When an album or song list is browsed, Then Aria returns source-agnostic app-facing items.
- Given a source does not support playlists, When playlists are browsed, Then Aria returns a safe unavailable result without crashing.
- Given a search query is empty or invalid, When search runs, Then Aria returns a safe validation result.
- Given a source is degraded, When browse/search runs, Then warnings are preserved and output remains safe.
- Given folder entries are browsed, When a source returns folder metadata, Then Aria treats them as source items and does not touch the local filesystem.
- Given UI needs library search later, When it consumes results, Then it uses Aria Core models only.

## Edge cases

- Empty library returns successful empty lists.
- No-match search returns a valid empty result.
- Unsupported categories return unavailable browse results.
- Source unavailable returns safe error output.
- Degraded source preserves warnings with safe partial output.
- Empty or whitespace-only search query returns validation output.
- Folder IDs and display names are opaque source metadata, not local paths to traverse.

## Acceptance criteria

- Spec files exist under `aria/specs/features/library-browse-search/`.
- Browse/search contracts and services are implemented.
- Fake source scenarios needed for browse/search are implemented.
- Tests cover required browse/search behavior and boundaries.
- Behavior Budget and Test Risk Matrix are present and satisfied.
- `aria/context/current.md` and `aria/context/delta.md` are concise and updated.
- Required validation passes.
- Bloco 10 behavior is not implemented.

## Open questions

- None for Bloco 9. Filters, sorting, favorites, activity, queue, now-playing, playback, and cache remain future specs.
