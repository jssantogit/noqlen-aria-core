# Design

## Summary

Bloco 16 adds data-only stream quality, transcoding, network quality, and offline quality policy contracts with deterministic local services. Aria Core returns recommendations and unavailable/degraded reasons only; it does not transcode, stream, probe a network, download media, play audio, call providers, or use Android APIs.

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
- `aria/specs/_template/**`
- `aria/specs/features/offline-cache-storage-policy/review.md`
- `aria/specs/features/internet-radio-foundation/review.md`
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Bloco 14 provides offline/cache/storage policy without mutation. Bloco 15 provides internet radio foundation without streaming. Bloco 16 sits between radio/offline policy and future Bloco 17 playback capability models, and must not implement Bloco 17.

## Files to create

- `src/noqlen_aria/stream_quality.py`
- `tests/test_stream_quality_transcoding_network_policy.py`
- `aria/specs/features/stream-quality-transcoding-network-policy/requirements.md`
- `aria/specs/features/stream-quality-transcoding-network-policy/design.md`
- `aria/specs/features/stream-quality-transcoding-network-policy/tasks.md`
- `aria/specs/features/stream-quality-transcoding-network-policy/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Android/Kotlin/Java/Gradle files.
- Provider adapters or Anchor provider internals.
- Playback engine, UI, driver, or Bloco 17 files.
- Cache/download mutation implementation.
- Private/local tooling files.

## Data flow

Callers provide explicit preferences, declared profiles/capabilities, bandwidth budgets, network snapshots, source state, and renderer format hints. Services validate values, apply deterministic thresholds, and return data-only decisions inside `AriaResult`. No service performs IO.

## Error handling

Negative bitrate/bandwidth values return `AriaResult(ok=False)` with safe `AriaError` codes. Unsupported/degraded/unavailable states return successful policy decisions with explicit reasons when inputs are valid.

## Security considerations

No network, filesystem, provider, playback, Android, subprocess, or transcoder access is added. Decision messages are generic and safe for app display. Existing `safe_serialize` handles dataclasses/enums.

## Stream quality policy rules

- `StreamQualityPreference`: `LOW`, `MEDIUM`, `HIGH`, `AUTOMATIC`, `ORIGINAL`.
- `StreamQualityProfile`: named bitrate/format profile.
- `StreamQualityPolicy`: preference, optional bitrate limit, bandwidth budget, fallback policy, offline policy, and flags for offline/network behavior.
- `StreamQualityDecision`: selected profile/preference, reason, degraded flag, warning tuple, needs-transcoding flag, and no-execution summary.
- `StreamQualityReason`: preferred quality, bandwidth limited, bitrate limited, network degraded, source unavailable, format unsupported, transcoding needed/unavailable, offline preferred, fallback selected, invalid policy.

## Transcoding policy rules

- `TranscodingCapability`: declared support, input formats, output formats, and max output bitrate.
- `TranscodingPolicy`: requirement, preference, target format, target bitrate, and allowed flag.
- `TranscodingDecision`: available/unavailable, requirement, unavailable reason, target format, target bitrate, and summary.
- `TranscodingUnavailableReason`: none, unsupported source, policy disabled, source unavailable, input unsupported, output unsupported, bitrate unsupported, invalid policy.

## Network quality policy rules

- `NetworkQualityLevel`: `OFFLINE`, `POOR`, `DEGRADED`, `GOOD`, `EXCELLENT`, `UNKNOWN`.
- `NetworkQualityState`: level plus metered/roaming/unavailable flags.
- `NetworkConditionSnapshot`: caller-provided bandwidth/latency/loss/meters only.
- `NetworkPolicyDecision`: state, reason, recommended max bitrate, warnings.
- Decisions are from explicit snapshots/fakes only; no probing.

## Offline quality policy rules

If offline mode is preferred and an offline profile exists, `QualityPolicyService` returns that profile with `OFFLINE_PREFERRED`. It never downloads, mutates cache, or inspects the filesystem.

## Provider boundary considerations

Providers may later declare formats, source availability, and capability snapshots. Bloco 16 never calls providers directly, imports provider internals, resolves streams, or opens media handles.

## Dependencies

None. Standard library only plus existing `noqlen_aria.contracts`.

## Risks

- Thresholds are conservative placeholders and may need later tuning.
- Future renderer/provider layers must not treat decisions as execution commands.
- Transcoding vocabulary may expand when a real player/provider layer is specified.

## Rollback strategy

Remove `stream_quality.py`, its tests, public exports, and this spec/context update. No persisted data or external integration exists.

## Validation plan

- Required command list from the task.
- Boundary searches for network, transcoding, provider, filesystem, Android, driver, and smart playlist terms.
- Full `python3 -m pytest`.

## Behavior Budget

- New behaviors: add stream quality policy models; add transcoding capability/policy models; add network quality policy models; add offline quality policy models; add deterministic local quality decision services.
- Public API changes: expose only intentional stream quality/transcoding/network policy names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/stream-quality-transcoding-network-policy/**`, `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` only if needed.
- Tests required: quality preference mapping; bitrate/bandwidth policy; transcoding available/unavailable behavior; network quality level decisions; offline quality fallback; unsupported format/capability behavior; degraded/unavailable source behavior; no real network/streaming/transcoding/provider/Android behavior.
- Dependencies: none.
- Stop if: real transcoder, real stream probing, network calls, provider integration, playback engine integration, or Android integration becomes necessary.
