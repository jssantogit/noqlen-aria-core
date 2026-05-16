# Requirements

## Status

Approved for Bloco 12 implementation in this task. Context package: Standard.

## Problem

Aria Core has queue contracts, library summaries, and media-source boundaries, but no app/player-facing now-playing state. Future UI and playback-intent work need a deterministic state contract that can describe what is current, whether playback would be available later, whether a previous item is resumable, and when media is unavailable, without playing audio or resolving streams.

## Goal

Add a now-playing foundation that models current app/player-facing state only. The foundation must reference existing queue and media summary models, expose safe playback availability and resumable/unavailable state vocabulary, and provide a deterministic local `NowPlayingService` for building state snapshots.

## Non-goals

- No real playback.
- No playback intent execution.
- No stream resolution.
- No provider integration.
- No direct Navidrome, Jellyfin, or Emby integration.
- No Anchor provider internals.
- No Android, UI, screens, navigation, Kotlin, Java, Gradle, Media3, ExoPlayer, Activity, Fragment, or Compose.
- No queue mutation beyond consuming existing `QueueState` and `QueueItem` values.
- No offline/cache behavior.
- No smart playlist logic.
- No filesystem traversal.
- No network behavior.

## Actors

- Future app/player UI consuming app-facing Aria Core state.
- Future Bloco 13 playback-intent layer consuming playback availability vocabulary.
- Tests and fake scenarios verifying deterministic state behavior.

## Functional requirements

- FR-01: Define `NowPlayingState` as the app/player-facing now-playing snapshot.
- FR-02: Define `NowPlayingItem` as the current item summary that may reference a `QueueItem`, library summary, media ID, and media source ID.
- FR-03: Define `NowPlayingStatus` vocabulary for idle and non-playing app-facing states without starting playback.
- FR-04: Define `PlaybackAvailabilityState` and `PlaybackAvailabilityReason` vocabulary.
- FR-05: Define `PlaybackPositionSnapshot` with deterministic validation rules.
- FR-06: Define `ResumablePlaybackState` for previous or current resumable state.
- FR-07: Define `UnavailableMediaState` for explicit safe unavailable media state.
- FR-08: Define `NowPlayingService` that builds idle state, builds state from a queue current item, builds unavailable state, builds resumable state, validates position snapshots, and maps playback availability.
- FR-09: Reference `QueueState` and current `QueueItem` without mutating the queue.
- FR-10: Preserve library/media summaries when present and avoid provider calls.
- FR-11: Provide fake now-playing scenarios for deterministic tests.
- FR-12: Return safe `AriaResult` failures for invalid inputs.
- FR-13: Expose only intentional now-playing foundation public names.

## Non-functional requirements

- NFR-01: Standard library only; no dependencies.
- NFR-02: Deterministic local behavior only.
- NFR-03: App-facing serialized state must remain safe with `safe_serialize`.
- NFR-04: No provider, playback, network, filesystem, Android, UI, offline/cache, or smart playlist imports.
- NFR-05: Tests must cover positive and negative behavior paths from the Test Risk Matrix.
- NFR-06: Public names must be explicit through module `__all__` and top-level exports.

## Canonical Examples

- Given no active queue item, When now-playing state is requested, Then Aria returns idle/empty app-facing state.
- Given a queue has a current item, When now-playing state is built, Then it references that item without playing audio.
- Given current media is unavailable, When now-playing state is built, Then unavailable media state is explicit and safe.
- Given a previous item is resumable, When state is serialized, Then resumable state and position snapshot are explicit.
- Given playback availability is blocked, When UI consumes now-playing state later, Then it sees a safe unavailable reason and no playback starts.
- Given Bloco 13 will add playback intents, When Bloco 12 is implemented, Then no intent execution exists yet.
- Given UI needs now-playing later, When it consumes state, Then it uses Aria Core models and does not call media sources/providers directly.

## Edge cases

- Empty queue.
- Queue with `current_position=None`.
- Queue current position outside item bounds.
- Queue current item unavailable.
- Negative playback position.
- Playback position greater than known duration.
- Unknown duration.
- Blocked playback availability with missing reason.
- Resumable state without an item.

## Acceptance criteria

- Spec files exist under `aria/specs/features/now-playing-foundation/`.
- Behavior Budget, Test Risk Matrix, canonical examples, and delta update checklist are present.
- Now-playing contracts and deterministic `NowPlayingService` are implemented.
- Tests cover idle, queue current item, no current item, unavailable media, resumable state, invalid/negative position, position exceeding duration, availability reasons, serialization/defaults, and boundaries.
- No Bloco 13 playback intent execution exists.
- No real playback, stream resolution, provider integration, filesystem/network behavior, Android/UI, offline/cache, or smart playlist behavior exists.

## Open questions

- Future specs must decide how Bloco 13 maps playback intents to renderer/playback boundaries.
- Future specs must decide whether now-playing state snapshots need persistence/version migration.
