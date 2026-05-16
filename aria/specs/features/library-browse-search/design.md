# Design

## Summary

Create a small `src/noqlen_aria/library.py` module with app-facing browse/search models and two services. Extend `MediaSourceClient` and `FakeMediaSourceClient` only enough to provide deterministic browse/search data through the media source boundary. No provider integration, filesystem traversal, streaming, playback, UI, filters, sorting, favorites, activity, queue, now-playing, offline, or cache behavior is added.

## Context package

Standard.

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
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/media-source-foundation/design.md`
- `aria/specs/features/media-source-foundation/tasks.md`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/media_source.py`
- `src/noqlen_aria/__init__.py`
- `tests/test_media_source.py`
- `tests/test_mvp_hardening.py`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core MVP v0.1.0 is complete. Bloco 8 created `MediaSourceClient`, `FakeMediaSourceClient`, media IDs, source capabilities, source availability states, and stream handles. Bloco 9 builds the library layer on top of that source boundary.

## Files to create

- `src/noqlen_aria/library.py`
- `tests/test_library_browse_search.py`
- `aria/specs/features/library-browse-search/requirements.md`
- `aria/specs/features/library-browse-search/design.md`
- `aria/specs/features/library-browse-search/tasks.md`
- `aria/specs/features/library-browse-search/review.md`

## Files to modify

- `src/noqlen_aria/media_source.py`
- `src/noqlen_aria/__init__.py`
- `tests/test_media_source.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/specs/features/library-browse-search/tasks.md`
- `aria/specs/features/library-browse-search/review.md`

## Files that must not be touched

- Provider integration files beyond the existing media source fake.
- Android, Kotlin, Java, Gradle, UI, navigation, player, queue, now-playing, offline, cache, and playback files.
- `pyproject.toml`.
- Private/local/tooling files.

## Proposed model names

- `LibraryBrowseCategory`
- `LibraryBrowseRequest`
- `LibraryBrowseResult`
- `LibrarySearchQuery`
- `LibrarySearchResult`
- `ArtistSummary`
- `AlbumSummary`
- `TrackSummary`
- `PlaylistSummary`
- `GenreSummary`
- `FolderSummary`
- `LibraryItemSummary`
- `LibraryBrowseService`
- `LibrarySearchService`

## Service responsibilities

`LibraryBrowseService` accepts a `MediaSourceClient`, forwards browse requests through the source boundary, and returns app-facing `AriaResult[LibraryBrowseResult]` values. It does not filter, sort, favorite, or enrich activity.

`LibrarySearchService` validates queries before calling the source. Empty or invalid input returns safe validation output. Valid queries are forwarded through the source boundary and normalized as `LibrarySearchResult`.

## How MediaSourceClient is consumed

`MediaSourceClient` is extended with:

- `browse_library(request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]`
- `search_library(query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]`

The library services call only those methods. They do not inspect provider internals, call network APIs, or read local directories.

## Data flow

```
Future UI/App/Player
    -> LibraryBrowseService / LibrarySearchService
    -> MediaSourceClient
    -> FakeMediaSourceClient or future adapter
    -> Aria Core library/search models
```

## Error handling

- Unsupported categories return `AriaResult(ok=True)` with `available=False` and a `CAPABILITY_NOT_SUPPORTED` error on the result model.
- Unavailable sources return `AriaResult(ok=False)` with `SOURCE_UNAVAILABLE`.
- Degraded sources return safe output with warnings preserved.
- Empty/invalid search queries return `AriaResult(ok=True)` with `valid_query=False` and `INVALID_SEARCH_QUERY` on the result model.
- Fake failures use deterministic `AriaError` injection hooks and do not throw raw exceptions.

## Security considerations

- Folder entries are `FolderSummary` source metadata only.
- No `os.walk`, `glob.glob`, `Path.iterdir`, or `scandir` behavior is implemented.
- No network libraries are used.
- No provider-specific imports, direct provider calls, Anchor internals, or Anchor CLI calls are added.
- No real stream URLs, credentials, tokens, or local library paths are exposed.

## Provider boundary considerations

Provider names may remain in docs/tests only as forbidden boundary checks. Type names, field names, service names, and module names remain source-agnostic. Current Anchor remains one optional control-plane adapter, not the library source implementation.

## Dependencies

None. Python standard library only.

## Risks

- Unsupported capability handling could accidentally become an exception path. Mitigation: required TDD coverage.
- Folder browse could be mistaken for filesystem traversal. Mitigation: model folders as source metadata and add boundary tests/search checks.
- Search could grow into filters/sorting. Mitigation: search only matches fake source summaries by query text; no filter/sort API.
- Public API could expand too broadly. Mitigation: intentional exports only.

## Rollback strategy

Revert the new `library.py`, tests, spec directory, and minimal `media_source.py`/`__init__.py` changes. No data migration or external cleanup is required because no real provider, filesystem, network, playback, or cache behavior is added.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/library-browse-search aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Repository contamination check with `git ls-files`.
- Required provider/network/filesystem/Android/queue boundary greps.

## Behavior Budget

- New behaviors: create library browse/search models; create browse/search services; extend fake media source scenarios only as needed.
- Public API changes: expose only intentional library browse/search names and extended media source browse/search methods.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/library-browse-search/**`, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: browse artists/albums/tracks/playlists/genres/folders; search query/result behavior; unsupported capability behavior; unavailable/degraded source behavior; no direct provider/filesystem/network behavior.
- Dependencies: none.
- Stop if: real provider integration becomes necessary; filesystem traversal becomes necessary; filters/favorites/recent activity need implementation; queue/playback/cache needs implementation.
