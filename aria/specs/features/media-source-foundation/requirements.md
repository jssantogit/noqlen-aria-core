# Requirements

## Status

Draft for Bloco 8 — Media Source Foundation.

## Problem

Aria Core has `ControlClient` for the control-plane boundary but no media/library-layer boundary and no source capability model. Future library browse/search, playlists, metadata, stream handles, normalized media IDs, and source capabilities all need a contract layer between the control plane and provider-backed sources. Without this foundation, the library layer would couple to provider internals (Navidrome, Jellyfin, Emby) or assume Anchor already exposes a multi-provider media API — which it does not.

Current Anchor integration remains Navidrome-focused. Additional providers are a future provider-extension-readiness concern, not a current implementation. Aria must not call Anchor provider internals directly. Aria must not assume Anchor already supports multiple providers.

## Goal

Define the `MediaSourceClient` boundary contract, a `FakeMediaSourceClient` for fake-first development, a source capability summary model, media source identity/reference models, abstract media IDs, an abstract stream handle, a provider capability discovery model, provider/source availability states, and safe degraded behavior — without implementing real provider integration, real streaming, real playback, or UI code.

## Non-goals

- No real provider integration (Navidrome, Jellyfin, Emby, or any other).
- No real streaming implementation.
- No real playback engine.
- No UI, Android, screens, navigation, or player code.
- No direct call to Navidrome, Jellyfin, Emby, or any provider internals.
- No assumption that Anchor already supports multiple providers.
- No Anchor CLI integration.
- No real music library access.
- No queue, now playing, cache, offline, or download implementation.
- No source code for `MediaSourceClient` yet; spec only.
- No pyproject.toml changes.
- No test file creation in this task.

## Actors

- Aria Core services (future library, sync, playlist, and queue layers).
- Future UI/App/Player thin adapter.
- Implementation agents.
- Maintainer.

## Functional requirements

### FR-01: MediaSourceClient boundary

- FR-01a: Define `MediaSourceClient` as a `typing.Protocol` (or `@runtime_checkable`) that represents the media/library-layer boundary. It must expose capability discovery, media identity operations, and stream handle resolution.
- FR-01b: `MediaSourceClient` must use `AriaResult[T]` for all return types consistently.
- FR-01c: `MediaSourceClient` must be source-agnostic — it models a media source generically, not a Navidrome, Jellyfin, or Emby source.

### FR-02: FakeMediaSourceClient

- FR-02a: Define `FakeMediaSourceClient` as a deterministic, configurable implementation of `MediaSourceClient`.
- FR-02b: `FakeMediaSourceClient` must support deterministic failure injection on all public methods via `_*_error` hooks (following the `FakeControlClient` pattern from Bloco 1).
- FR-02c: `FakeMediaSourceClient` must expose configurable source identity, capabilities, and media catalog for testing.
- FR-02d: `FakeMediaSourceClient` must never call real network, filesystem, or provider code.

### FR-03: Source capability summary model

- FR-03a: Define a `SourceCapability` enum or set of capability flags representing what a media source can provide: artists, albums, tracks, playlists, genres, folders, search, stream, ratings, scrobbling, lyrics, and similar browse/playback-facing capabilities.
- FR-03b: Define a `SourceCapabilitySummary` dataclass that aggregates which capabilities a source supports and which are unavailable.
- FR-03c: Capability mapping must be normalized — different sources declare capabilities differently, but Aria models them with a single capability vocabulary.
- FR-03d: Missing or unsupported capabilities must be represented explicitly as unavailable, not silently absent.

### FR-04: Media source identity/reference models

- FR-04a: Define a `MediaSourceId` newtype or structured identifier that uniquely identifies a media source within Aria.
- FR-04b: Define a `MediaSourceInfo` dataclass with source identity, display name, provider type (abstract, not brand-bound), and availability state.
- FR-04c: Define a `MediaSourceType` enum for abstract source categories (e.g., REMOTE_SERVER, LOCAL_LIBRARY, CLOUD_STORAGE) — not Navidrome/Jellyfin/Emby brand names.

### FR-05: Abstract media IDs

- FR-05a: Define a `MediaId` newtype representing an abstract, normalized media identifier (artist, album, track, playlist, genre, folder) that is independent of any specific source's internal ID scheme.
- FR-05b: Define a `MediaIdKind` enum for the type of media entity the ID refers to (`ARTIST`, `ALBUM`, `TRACK`, `PLAYLIST`, `GENRE`, `FOLDER`, `STREAM`).
- FR-05c: Abstract media IDs must be serializable and safe for use in snapshots and across boundaries.

### FR-06: Abstract stream handle

- FR-06a: Define a `StreamHandle` dataclass representing a future stream resource without implementing real streaming. It carries a stream identifier, source reference, format/quality hints, and an availability state.
- FR-06b: `StreamHandle` availability must default to `UNAVAILABLE` or `STREAM_NOT_RESOLVED` — stream resolution is a future concern.
- FR-06c: The stream handle model must not assume any specific streaming protocol, codec, or transport.

### FR-07: Provider capability discovery model

- FR-07a: Define a `ProviderCapability` model that maps to `SourceCapability` from FR-03. Provider capability means what a specific provider type can offer when queried; source capability is what a specific source instance currently exposes.
- FR-07b: Capability discovery must report supported capabilities without requiring a live connection to any provider.
- FR-07c: Capability discovery must degrade gracefully when a source or provider is unavailable.

### FR-08: Provider/source availability states

- FR-08a: Define a `SourceAvailabilityState` enum: `AVAILABLE`, `DEGRADED`, `UNAVAILABLE`, `UNKNOWN`.
- FR-08b: Define a `ProviderAvailabilityState` enum: `CONNECTED`, `DISCONNECTED`, `AUTH_REQUIRED`, `ERROR`, `UNKNOWN`.
- FR-08c: `MediaSourceInfo` from FR-04b must carry a `SourceAvailabilityState`.
- FR-08d: The availability model must not assume a live connection exists.

### FR-09: Safe degraded behavior

- FR-09a: When a source capability is unavailable, `MediaSourceClient` must return safe `AriaResult` with an `AriaError` or a capability-missing state — never a raw exception.
- FR-09b: When a stream handle cannot be resolved, the result must be unavailable and safe (no crash, no raw traceback).
- FR-09c: All fake implementations must model degraded/unavailable states so that callers can test handling of missing sources and missing capabilities.

### FR-10: No provider internals

- FR-10a: `MediaSourceClient` must not expose provider-specific fields, IDs, tokens, or connection details.
- FR-10b: No class, enum, or dataclass in this boundary may reference Navidrome, Jellyfin, Emby, Subsonic, or any other provider brand directly.
- FR-10c: Anchor is not the center of Aria; `MediaSourceClient` must not depend on Anchor internals or assume Anchor already supports multiple providers.

### FR-11: Spec-only constraint

- FR-11a: This task creates spec files only. No source code is created.
- FR-11b: Proposed implementation files are documented in `design.md` but not written.
- FR-11c: No `pyproject.toml`, test files, or existing source files are modified.

## Canonical Examples

### CE-01: Source capability summary — artists/albums/tracks

Given a `FakeMediaSourceClient` configured with capabilities for artists, albums, and tracks
And playlists and genres are not supported
When `source.get_capability_summary()` is called
Then the result is `AriaResult[SourceCapabilitySummary]` with `ok=True`
And the `SourceCapabilitySummary.supported` set contains `ARTISTS`, `ALBUMS`, `TRACKS`
And the `SourceCapabilitySummary.unavailable` set contains `PLAYLISTS`, `GENRES`
And no crash or raw traceback occurs.

### CE-02: Missing capability — playlists unavailable

Given a `FakeMediaSourceClient` with a source that does not support playlists
When `source.get_capability_summary()` is called and mapped to `SourceCapabilitySummary`
Then the `PLAYLISTS` capability is marked as `unavailable`
And the result is still `ok=True` (capability query itself succeeded)
And no exception is raised.

### CE-03: Stream handle unavailable

Given a future scenario where `source.request_stream(media_id)` is called
And the source cannot resolve the stream (e.g., track missing, source offline)
When `source.request_stream(media_id)` returns
Then the result is `AriaResult[StreamHandle]` with `ok=True` and `data.availability=UNAVAILABLE`
Or `ok=False` with an `AriaError(code="STREAM_NOT_RESOLVED" | "SOURCE_UNAVAILABLE")`
And the caller handles this gracefully without crashing.

### CE-04: Provider boundary enforced

Given a future UI or library service that lists providers
When Aria talks to a media source
Then Aria must use `MediaSourceClient` methods only
And never call `source._navidrome_api`, `source._jellyfin_client`, or any provider-specific internals
And the boundary is enforced by typing, not by runtime guards on private fields.

### CE-05: Anchor not assumed multi-provider

Given the current Anchor adapter remains Navidrome-focused
When documenting media source concepts and provider extension readiness
Then the spec must not claim that current Anchor already supports multiple providers
And provider extension readiness (Bloco 20) is explicitly a future concern
And `MediaSourceClient` is designed to not depend on Anchor exposing a multi-provider API today.

### CE-06: UI consumes Aria models, not provider internals

Given a future UI needs library data
When it queries media source state
Then it must consume `MediaSourceClient` responses (capability summaries, media IDs, source info)
And must never consume Navidrome IDs, Jellyfin IDs, Emby IDs, or any provider-specific data model
And all identifiers are Aria-normalized `MediaId` instances.

### CE-07: Source identity and availability

Given a `FakeMediaSourceClient` with `MediaSourceInfo(source_id="src-1", source_type=REMOTE_SERVER, availability=DEGRADED)`
When `source.get_source_info()` is called
Then the result is `AriaResult[MediaSourceInfo]` with `ok=True`
And `data.availability` is `SourceAvailabilityState.DEGRADED`
And `data.source_type` is `MediaSourceType.REMOTE_SERVER` (not `NAVIDROME` or `JELLYFIN`).

### CE-08: Capability discovery with unavailable source

Given a `FakeMediaSourceClient` with `source.set_availability(SourceAvailabilityState.UNAVAILABLE)`
When `source.get_capability_summary()` is called
Then the result is `AriaResult[SourceCapabilitySummary]` with `ok=False` and an `AriaError(code="SOURCE_UNAVAILABLE")`
And callers do not crash when reading the error.

## Non-functional requirements

- NFR01: All contracts use Python 3.11+ standard library only (`dataclasses`, `enum`, `typing`).
- NFR02: No runtime dependencies on external libraries beyond existing `noqlen_aria.contracts`.
- NFR03: No Android SDK, Kotlin, Java, Gradle, or platform-specific code.
- NFR04: All public names must be explicit, stable, and documented in English.
- NFR05: All types must be serialization-safe (no callables, no non-serializable fields).
- NFR06: `MediaSourceClient` must be `@runtime_checkable` for structural typing consistency with `ControlClient`.
- NFR07: All `AriaResult[T]` returns must follow the established pattern (ok/data/error/warnings).
- NFR08: Capability enums must be exhaustive; unknown capabilities must produce safe errors.
- NFR09: `FakeMediaSourceClient` must follow the fake-hostility pattern: configurable failure states, deterministic behavior, no external calls.
- NFR10: No provider brand names in type names, enum values, or field names. Use abstract categories and domain-generic identifiers.

## Edge cases

- EC01: `MediaSourceClient.get_capability_summary()` called before any source is connected — returns `UNKNOWN` capabilities or an error.
- EC02: `MediaSourceClient.request_stream(media_id)` with a `MediaId.kind` that is not a streamable type (e.g., a folder) — returns error.
- EC03: `FakeMediaSourceClient` with all capabilities set to unsupported — capability summary shows empty `supported` and populated `unavailable`.
- EC04: `MediaSourceInfo` with `availability=UNKNOWN` — callers must handle all four states without assuming a connection.
- EC05: `SourceCapabilitySummary` comparison between two sources with different capability profiles — each is independently valid.
- EC06: Serialization round-trip of `MediaId`, `StreamHandle`, `SourceCapabilitySummary`, and `MediaSourceInfo` — all fields survive.
- EC07: `FakeMediaSourceClient` with injected `_get_capability_summary_error` returns the configured error — no real provider query happens.
- EC08: `SourceCapability` enum includes future capabilities not yet implemented by any source — the summary model handles them as `unavailable`.
- EC09: Multiple `MediaSourceClient` instances for different sources — each has independent identity, capabilities, and availability.
- EC10: `ProviderCapability` mapping to `SourceCapability` when a provider defines a capability that has no exact Aria equivalent — it is normalized to a best-fit capability or marked unavailable.
- EC11: All fake methods that return `AriaResult` must handle the case where the underlying data store is empty or partially populated.
- EC12: `MediaSourceId` equality and hashing — two identical IDs from different source instances must compare equal.

## Acceptance criteria

- AC01: `aria/specs/features/media-source-foundation/` contains `requirements.md`, `design.md`, `tasks.md`, and `review.md`.
- AC02: No source code, test code, `pyproject.toml`, Android files, or provider integration files are created by this spec.
- AC03: Spec clearly states that Bloco 8 defines the media source foundation — no real provider integration, no real streaming, no real playback, no UI.
- AC04: Spec defines the proposed implementation file(s) and test file(s) for later implementation.
- AC05: Existing validation commands pass without regression (368 tests, CLI help, CLI doctor, py_compile).
- AC06: Repository contamination check is clean.
- AC07: Spec includes Canonical Examples using Given/When/Then format (8 examples).
- AC08: Spec includes Behavior Budget.
- AC09: Spec includes Test Risk Matrix.
- AC10: Context package used is documented.
- AC11: Delta update checklist is present.
- AC12: Spec does not claim current Anchor is multi-provider.
- AC13: No Navidrome, Jellyfin, Emby, or other provider brand names appear in proposed type/field/enum names.
- AC14: Spec is committed with `docs(spec): add media source foundation spec`.

## Open questions

- OQ01: Should `MediaSourceClient` be split into sub-protocols (e.g. `BrowseableSource`, `StreamableSource`) or remain a single protocol? (Design: single protocol for v0; sub-protocols considered a future refinement.)
- OQ02: Should `StreamHandle` include a URI, or is a stream identifier opaque? (Design: opaque identifier + format hints + availability; actual URI is a future implementation detail.)
- OQ03: Should `MediaSourceId` use UUID, integer, or string? (Design: string newtype for flexibility; source implementation may use any internal scheme.)
- OQ04: How should `SourceCapabilitySummary` handle capabilities that are partially supported? (Design: supported/unavailable binary for v0; partial support and "degraded" capability is a future refinement.)
- OQ05: Should `MediaSourceClient` expose a `search` method, or is search purely a library-layer concern? (Design: `MediaSourceClient` exposes capability to declare search support; actual search API is library-layer (Bloco 9-10 concern).)
- OQ06: Should `ProviderCapability` be a separate model or just a provider-level label on `SourceCapability` entries? (Design: separate model; provider capability reflects what a provider type can offer; source capability reflects what a specific source instance currently exposes.)
- OQ07: Should `FakeMediaSourceClient` pre-populate a sample catalog, or start empty? (Design: start with configurable empty/default catalog; sample data added during implementation for testing.)
