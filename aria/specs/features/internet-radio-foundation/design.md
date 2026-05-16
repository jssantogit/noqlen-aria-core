# Design

## Summary

Bloco 15 adds an internet radio foundation module with immutable app-facing models, local-only validation, deterministic service methods, and fake scenarios. The design treats streams, ICY/live metadata, artwork, directories, imports, and favorites as data/state only. It deliberately avoids radio streaming, stream parsing, provider calls, playback, Android, and filesystem behavior.

## Context Package

Standard.

## Context Files Read

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
- `aria/specs/features/offline-cache-storage-policy/review.md`
- Relevant `src/noqlen_aria/**` and `tests/**`
- `aria/review/validation-checklist.md`

## Existing Project Context

Aria Core already exposes source-agnostic contracts, media source stream handles, library/favorites read states, queue, now playing, playback intent, and offline/cache policy foundations. Bloco 15 fits the Internet Radio / Live Stream layer as a model/service foundation only. It must not start Bloco 16 stream quality/transcoding/network policy or Bloco 17 playback capability models.

## Files To Create

- `src/noqlen_aria/internet_radio.py`
- `tests/test_internet_radio_foundation.py`
- `aria/specs/features/internet-radio-foundation/requirements.md`
- `aria/specs/features/internet-radio-foundation/design.md`
- `aria/specs/features/internet-radio-foundation/tasks.md`
- `aria/specs/features/internet-radio-foundation/review.md`

## Files To Modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files That Must Not Be Touched

- Android, Kotlin, Java, Gradle, UI, navigation, player, Media3, and ExoPlayer files.
- Provider internals, Anchor CLI integration, Navidrome/Jellyfin/Emby direct integration.
- Bloco 16 stream quality/transcoding/network policy files.
- Bloco 17 playback capability model files.
- Offline/cache implementation beyond unchanged existing models.
- Private/local tooling files.

## Proposed Radio Models

- `RadioStationId`: `NewType` over `str`.
- `RadioStationRef`: station id plus display name and optional directory/source labels.
- `RadioStationSummary`: complete app-facing station summary.
- `RadioSourceCapability`: read-only capability enum.
- `RadioDirectoryRef`: directory identity data only.
- `RadioImportSource`: import origin enum.
- `ManualRadioStationInput`: local manual input data.
- `RadioStreamHandle`: abstract handle with handle id, station id, stream kind, declared URI, format hint, and label.
- `RadioStreamKind`: `MP3`, `AAC`, `OGG`, `OPUS`, `HLS`, `DASH`, `SHOUTCAST`, `UNKNOWN`.
- `RadioPlaybackAvailability`: availability state, reason, warnings.
- `RadioMetadataState`: title/artist/album/program/live flags plus optional ICY metadata.
- `IcyMetadataState`: ICY title, name, genre, URL, bitrate, interval as data only.
- `RadioArtworkState`: optional artwork/thumbnail URI and attribution metadata as data only.
- `RadioFavoriteState`: read-only favorite state and future-intent availability.
- `RadioUnavailableReason`: safe reason enum.
- `RadioValidationIssue`: validation issue enum.

## Service Responsibilities

`InternetRadioService` will:

- Validate manual station input locally.
- Build station summaries from explicit caller-provided data.
- Build abstract stream handles from declared data without resolving streams.
- Evaluate playback availability from declared stream kind, source support, and explicit availability/degraded inputs.
- Build metadata, ICY metadata, artwork, and read-only favorite state.
- Return safe `AriaResult` for invalid inputs.
- Block favorite mutation with a safe unsupported/future-intent-only result.

## Data Flow

Caller-provided manual input or fake scenario data enters `InternetRadioService`. The service trims and validates local strings, constructs data models, evaluates availability from enum/capability inputs, and returns `AriaResult` wrapping app-facing models. No method opens a URI, parses a stream, calls a provider, starts playback, or reads the filesystem.

## Error Handling

Invalid manual station input returns `AriaResult(ok=False)` with a safe `AriaError` and issue details where appropriate. Unsupported stream kinds return successful availability state with `available=False` and `RadioUnavailableReason.UNSUPPORTED_STREAM_KIND` so future UI can render a safe unavailable state. Favorite mutation attempts return safe unavailable/future-intent-only state instead of mutating anything.

## Security Considerations

- URLs are treated as declared text only.
- No credentials, tokens, provider internals, filesystem paths, or raw exceptions are exposed.
- No network or filesystem APIs are imported.
- App-facing messages use existing safe result/error patterns.

## Radio Stream Boundary Considerations

`RadioStreamHandle` is not a playable session. It stores station id, declared URI text, and kind only. `HLS`, `DASH`, and `SHOUTCAST` are intentionally modeled as unsupported for this block to avoid adding parsers or clients. Actual playback belongs to a future player/platform layer.

## Provider Boundary Considerations

`RadioDirectoryRef` and `RadioImportSource` are references only. They do not imply provider integration. Favorites are read/state/future-intent only; no provider mutation or backend write exists.

## Metadata Handling Rules

ICY/live metadata is data-only and caller-provided. Aria does not read ICY from a socket, parse live stream bytes, refresh metadata, fetch artwork, or dereference artwork URLs. Artwork is optional metadata attached to summaries.

## Dependencies

No new dependencies. Use `dataclasses`, `enum`, `typing`, and existing `AriaResult`/`AriaError`/`AriaWarning`.

## Risks

- R01: Stream handle fields could be mistaken for playable stream resolution. Mitigation: tests assert no playback/session methods and docs state data-only.
- R02: HLS/DASH/Shoutcast names could encourage parser implementation. Mitigation: evaluate them as unsupported in this block.
- R03: Favorites could be mistaken for provider mutation. Mitigation: mutation method returns unsupported/future-intent-only.

## Rollback Strategy

Remove `internet_radio.py`, its tests, top-level exports, spec directory, and concise context updates. No persisted data or external state is introduced.

## Validation Plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/internet-radio-foundation aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Required contamination and boundary search checks from the task prompt.

## Behavior Budget

- New behaviors: add internet radio models; add radio station validation; add radio metadata/artwork state models; add radio stream handle abstraction; add radio availability state; add deterministic `InternetRadioService` behavior; add fake radio scenarios.
- Public API changes: expose only intentional radio foundation names from `noqlen_aria.internet_radio` and top-level package exports.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/internet-radio-foundation/**`, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: station identity/reference behavior; manual station validation; supported/unsupported stream kind behavior; radio metadata state; ICY metadata state as data only; artwork metadata state; favorite read/state behavior; unavailable/degraded radio behavior; no real network/streaming/playback/provider/Android behavior.
- Dependencies: none.
- Stop if: real radio streaming, HLS/DASH/Shoutcast client implementation, ICY network parsing, Android/player integration, or provider mutation becomes necessary.
