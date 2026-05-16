# Requirements

## Status

Approved for Bloco 15 implementation. Context package: Standard.

## Problem

Aria needs app/player-facing internet radio vocabulary before a future UI or player can present stations, manual station entries, live metadata, favorites/read state, and safe availability. Without core models, future UI or player work could call streams, directories, providers, or platform APIs directly.

## Goal

Add deterministic internet radio foundation models, fake scenarios, and `InternetRadioService` behavior for local validation and state construction only. Aria may model stations, directories, manual inputs, metadata, stream handles, favorites/read state, and playback availability. Aria must not stream radio or resolve radio streams into playable sessions.

## Non-goals

- No real radio streaming.
- No HLS, DASH, Shoutcast, or Icecast client implementation.
- No ICY network parsing or ICY socket reading.
- No real playback.
- No Android, UI, navigation, player screen, Media3, ExoPlayer, Kotlin, Java, or Gradle work.
- No provider direct integration.
- No direct Navidrome, Jellyfin, Emby, Anchor provider internals, or Anchor CLI calls.
- No provider mutation, including favorites mutation.
- No filesystem traversal.
- No network behavior.

## Actors

- Future UI/app consuming app-facing radio models.
- Future player/platform layer consuming abstract stream handles later.
- Aria Core service building deterministic radio state without external calls.
- Tests and fake scenarios proving safe local behavior.

## Functional Requirements

- FR-01: Define `RadioStationId` as a normalized station identity type.
- FR-02: Define `RadioStationRef` for source/category-independent station references.
- FR-03: Define `RadioStationSummary` with identity, display name, optional directory/source/import references, stream handle, metadata, artwork, favorite state, and availability.
- FR-04: Define `RadioSourceCapability` for read-only radio capability declarations.
- FR-05: Define `RadioDirectoryRef` for directory identity without direct integration.
- FR-06: Define `RadioImportSource` for manual, directory, provider-export, and unknown import origins without provider calls.
- FR-07: Define `ManualRadioStationInput` for caller-supplied station data.
- FR-08: Define `RadioStreamHandle` as an abstract handle that stores declared URI text and kind as data only and never opens streams.
- FR-09: Define `RadioStreamKind` with supported and unsupported stream categories.
- FR-10: Define `RadioPlaybackAvailability` and `RadioUnavailableReason` for safe available, degraded, unavailable, and unknown states.
- FR-11: Define `RadioMetadataState`, `IcyMetadataState`, and `RadioArtworkState` as app-facing metadata only.
- FR-12: Define `RadioFavoriteState` as read-only/future-intent state that never mutates providers.
- FR-13: Define `RadioValidationIssue` for local manual station validation failures.
- FR-14: Implement `InternetRadioService.validate_manual_station_input` using local-only validation.
- FR-15: Implement summary construction without opening network connections.
- FR-16: Implement stream handle construction without stream resolution.
- FR-17: Implement playback availability evaluation from declared kind, source capability, and availability inputs.
- FR-18: Implement metadata, ICY metadata, artwork, and favorite read-state builders.
- FR-19: Return safe `AriaResult` failures for invalid inputs.
- FR-20: Add deterministic fake radio scenarios for valid manual station, invalid URL, ICY metadata, artwork metadata, unsupported stream kind, unavailable station, degraded station, favorite read state, and favorite mutation unsupported/future-intent-only.

## Canonical Examples

- Given a manual radio station URL is valid, When it is validated, Then Aria returns a safe station summary without opening the network.
- Given a manual radio station URL is invalid, When it is validated, Then Aria returns a validation issue and does not attempt streaming.
- Given a station exposes ICY metadata, When metadata state is built, Then Aria stores metadata as app-facing state only.
- Given a station has artwork metadata, When radio station summary is built, Then artwork is represented as optional metadata only.
- Given a stream kind is unsupported, When playback availability is evaluated, Then Aria returns unavailable with a safe reason.
- Given a station is favorited by a source, When favorite state is read, Then Aria returns read-only/future-intent state without mutating provider data.
- Given UI needs radio later, When it consumes data, Then it uses Aria Core models and does not call streams/providers directly.

## Non-functional Requirements

- NFR-01: Standard library only; no new dependencies.
- NFR-02: Deterministic and local behavior only.
- NFR-03: No network, filesystem, playback, provider, Android, or UI imports or calls.
- NFR-04: Public API exports only intentional radio foundation names.
- NFR-05: Models must serialize through existing safe serialization.
- NFR-06: Invalid inputs must produce safe `AriaResult` or issue state, not raw exceptions.
- NFR-07: Tests must prove no real stream, provider, playback, filesystem, or Android behavior is required.

## Edge Cases

- Empty station name.
- Missing stream URL.
- Unsupported URL scheme.
- Whitespace around manual input fields.
- Unsupported stream kind.
- Unavailable source capability.
- Degraded station with warnings.
- Favorite read state present but mutation unavailable.
- Metadata absent, ICY metadata absent, artwork absent.
- Unknown availability or import source.

## Acceptance Criteria

- Spec files exist under `aria/specs/features/internet-radio-foundation/`.
- Radio contracts and `InternetRadioService` are implemented in allowed source files only.
- Fake radio scenarios are deterministic and local.
- Required tests cover station identity/reference behavior, manual validation, stream kind support, metadata, ICY data-only state, artwork, favorites/read state, unavailable/degraded behavior, and boundaries.
- No real streaming, HLS/DASH/Shoutcast client, ICY network parsing, network behavior, playback, provider integration/mutation, Android/UI code, or filesystem traversal is added.
- Behavior Budget, Test Risk Matrix, canonical examples, and delta checklist are present.

## Open Questions

- Which real radio directories or provider exports will feed these models later? Deferred.
- Which stream kinds future player layers will support first? Deferred.
- Whether favorite mutation will ever be supported through a provider adapter. Deferred and out of scope for Bloco 15.
