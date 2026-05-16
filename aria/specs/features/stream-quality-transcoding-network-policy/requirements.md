# Requirements

## Status

Approved for Bloco 16 implementation. Context package: Standard.

## Problem

Aria Core needs app-facing vocabulary for stream quality, transcoding readiness, network quality, bandwidth budgets, bitrate limits, and offline quality preferences. Future provider/player/platform layers need deterministic policy decisions from Aria Core without Aria opening streams, probing networks, transcoding audio, downloading media, or calling providers directly.

## Goal

Add policy-only models and deterministic local services for stream quality, transcoding availability, network quality, and offline quality fallback behavior.

## Non-goals

- No real transcoding.
- No real stream execution.
- No network probing.
- No provider direct integration.
- No Android/UI.
- No Media3/ExoPlayer.
- No playback engine.
- No offline download/cache mutation.
- No Bloco 17 playback capability implementation.
- No HLS/DASH/Shoutcast/Icecast parsing or streaming client.
- No filesystem traversal.

## Actors

- Future app/UI consuming Aria Core policy decisions.
- Future provider/source adapter declaring capabilities and source state.
- Future player/platform layer consuming policy-only recommendations.
- Tests and fake scenarios validating deterministic behavior.

## Functional requirements

- FR-01: Define stream quality preference, profile, policy, decision, reason, bitrate limit, bandwidth budget, quality fallback policy, and offline quality policy models.
- FR-02: Define transcoding capability, policy, decision, unavailable reason, requirement, and preference models.
- FR-03: Define network quality state, level, condition snapshot, policy decision, and reason models.
- FR-04: `QualityPolicyService` must evaluate explicit stream quality preferences, bandwidth budgets, bitrate limits, network states, source availability, format support, and optional fallback/transcoding needs.
- FR-05: `TranscodingPolicyService` must evaluate transcoding availability from declared local capability/policy only.
- FR-06: `NetworkQualityPolicyService` must evaluate network quality from provided snapshots only.
- FR-07: Offline quality policy must prefer offline quality decisions without downloading or mutating cache state.
- FR-08: Invalid negative bitrate or bandwidth values must return safe `AriaResult` failures.
- FR-09: Unsupported format/capability and degraded/unavailable source states must be represented as decisions, reasons, warnings, or unavailable states rather than crashes.
- FR-10: Services must be deterministic, local, standard-library only, and fake-friendly.
- FR-11: Public API expansion must expose only intentional Bloco 16 names.

## Non-functional requirements

- Python standard library only.
- No external dependencies.
- No network, streaming, transcoding, filesystem, provider, playback, Android, or UI imports.
- All decisions are data-only and serializable by existing safe serialization.
- Same inputs produce same outputs.
- Invalid inputs return safe `AriaResult` errors, not raw exceptions.

## Canonical Examples

- Given a user prefers high quality and bandwidth is sufficient, When stream quality is evaluated, Then Aria returns a high-quality policy decision without opening a stream.
- Given bandwidth budget is low, When stream quality is evaluated, Then Aria selects a safer lower-quality decision with a clear reason.
- Given transcoding is unsupported by the source, When transcoding policy is evaluated, Then Aria returns unavailable without crashing.
- Given a format is unsupported by the future renderer, When quality policy is evaluated, Then Aria can recommend a fallback/transcoding need as a decision only.
- Given network quality is degraded, When stream policy is evaluated, Then Aria returns a warning/degraded policy decision.
- Given offline mode is preferred, When offline quality policy is evaluated, Then Aria uses offline quality preferences without downloading anything.
- Given UI needs stream quality state later, When it consumes data, Then it uses Aria Core models and does not call providers, streams or network directly.

## Edge cases

- Negative bitrate limit.
- Negative available bandwidth.
- Zero available bandwidth.
- Unknown bandwidth and automatic quality.
- Source unavailable.
- Source degraded.
- Format unsupported by future renderer.
- Transcoding required but unavailable.
- Offline mode preferred without offline quality profile.
- Empty supported transcoding format set.

## Acceptance criteria

- Spec files exist under `aria/specs/features/stream-quality-transcoding-network-policy/`.
- Stream quality, transcoding, network quality, bandwidth, bitrate, fallback, and offline quality contracts are implemented.
- Deterministic policy services are implemented.
- Tests cover required positive, negative, fallback, degraded, unavailable, and boundary behaviors.
- Behavior Budget, Test Risk Matrix, canonical examples, and delta update checklist are present.
- Validation passes.
- No forbidden real integration behavior is added.

## Open questions

- Future provider/player layers may tune thresholds after real-world use; Bloco 16 uses conservative deterministic defaults only.
