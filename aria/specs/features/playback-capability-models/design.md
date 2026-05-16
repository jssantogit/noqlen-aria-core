# Design

## Summary

Bloco 17 adds playback capability and audio output readiness contracts as state-only models and deterministic local services. The implementation models gapless, loudness/ReplayGain awareness, crossfade, fade-in/fade-out capability, bit-perfect readiness, USB DAC/exclusive output state, route/device readiness, sample-rate/bit-depth/format compatibility, and playback quality preferences without any real playback, audio output, signal processing, platform API, provider, DSP/EQ, or driver behavior.

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
- `aria/context/android-player-reference.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `docs/android-boundary.md`
- `aria/specs/_template/**`
- Bloco 14-16 review files
- Relevant source/tests under `src/noqlen_aria/` and `tests/`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core already has safe result primitives, deterministic services, public export hardening, playback/renderer intents, now-playing state, offline/cache policy, internet radio foundations, and stream quality/transcoding/network policy. Bloco 17 extends the Output / Renderer / Audio Capability and Playback Policy layers with capability/readiness/preference models only.

## Files to create

- `src/noqlen_aria/playback_capabilities.py`
- `tests/test_playback_capability_models.py`
- `aria/specs/features/playback-capability-models/requirements.md`
- `aria/specs/features/playback-capability-models/design.md`
- `aria/specs/features/playback-capability-models/tasks.md`
- `aria/specs/features/playback-capability-models/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Android/Kotlin/Java/Gradle files.
- Provider integration files beyond allowed source exports.
- Audio driver, USB driver, JNI/NDK, AAudio, Oboe, Media3, ExoPlayer, MediaSession, UI, and filesystem/device files.
- Audit 14-17 artifacts.
- Bloco 18 specs or implementation.
- Private/local tooling files.

## Data flow

Callers provide declared source/output state to `PlaybackCapabilityService` or `AudioOutputCapabilityService`. Services validate numeric support declarations, compare requested capabilities against declared support, and return `AriaResult` with state models, warnings, and summaries. No service performs discovery, playback, device access, platform calls, provider calls, stream resolution, or filesystem/network access.

## Proposed playback capability model names

- `GaplessCapabilityState`
- `LoudnessNormalizationCapabilityState`
- `ReplayGainAwarenessState`
- `CrossfadeCapabilityState`
- `FadeCapabilityState`
- `FadeMode`
- `FadeTimingPreference`
- `FadeAvailabilityState`
- `FadeUnavailableReason`
- `BitPerfectCapabilityState`
- `PlaybackCapabilitySummary`
- `PlaybackCapabilityWarning`
- `PlaybackQualityPreference`
- `PlaybackCapabilityUnavailableReason`

## Proposed audio output model names

- `AudioOutputRouteState`
- `AudioOutputRouteType`
- `AudioOutputDeviceState`
- `UsbDacCapabilityState`
- `ExclusiveOutputCapabilityState`
- `SampleRateSupport`
- `BitDepthSupport`
- `AudioFormatSupport`
- `AudioOutputReadinessState`
- `AudioOutputBlockedReason`

## Proposed service responsibilities

- `PlaybackCapabilityService` evaluates gapless, loudness/ReplayGain, crossfade, fade-in/fade-out, quality preference mapping, and summary construction from declared state only.
- `AudioOutputCapabilityService` evaluates sample-rate/bit-depth/format support, route/device readiness, USB DAC/exclusive output declarations, and bit-perfect readiness from declared state only.

## Bit-perfect readiness rules

Bit-perfect readiness is available only when requested, the source format declaration is valid, the route is available, exclusive output is available, bit-perfect capability is declared supported, and declared route/device support matches sample rate, bit depth, and format if provided. System audio or any non-exclusive route blocks bit-perfect readiness. Unsupported sample rate, bit depth, or format returns unavailable/degraded state with safe warnings. No sample-rate switching or DAC control occurs.

## USB DAC capability rules

USB DAC capability is declared by `UsbDacCapabilityState` and route type `USB_DAC`. Aria Core may report available, unavailable, or degraded USB DAC state from declarations only. It must never use Android USB Host APIs, device enumeration, drivers, JNI/NDK, AAudio, Oboe, or device paths.

## Gapless/crossfade/loudness capability rules

Gapless and crossfade are available only when source support and route support are both declared true. Crossfade can be requested and then rejected with `ROUTE_UNSUPPORTED`, `SOURCE_UNSUPPORTED`, or `SIGNAL_PROCESSING_DISABLED`. Loudness normalization and ReplayGain awareness report metadata awareness only; they never apply gain, normalize audio, or perform DSP/EQ.

## Fade capability rules

Fade-in and fade-out are modeled with `FadeCapabilityState`, `FadeMode`, `FadeTimingPreference`, `FadeAvailabilityState`, and `FadeUnavailableReason`. Fade is available only when requested, timing values are valid, source support is declared, route support is declared, and signal-altering processing is allowed by policy. Fade returns safe unavailable state for unsupported source/route and safe errors for invalid timing. Fade never changes volume, automates output gain, processes samples, schedules playback, or performs DSP/EQ.

## Bit-perfect and signal-processing conflict rules

Fade-in, fade-out, and crossfade are signal-altering features. When bit-perfect or exclusive-output policy forbids signal-altering processing, Aria Core reports fade/crossfade unavailable with `SIGNAL_PROCESSING_DISABLED`. Aria Core does not resolve the conflict by processing audio or controlling output devices.

## Audio output boundary considerations

Output route and device states are app-facing state snapshots for future UI and player adapters. They are not handles to devices and cannot execute audio operations. Unknown or missing support is conservative and state-only.

## Future driver bridge vocabulary

The model vocabulary may mention future custom/exclusive output bridge requirements as state fields and safe reasons. That vocabulary is documentation/model vocabulary only and is not a bridge implementation.

## Error handling

Invalid declared values return `AriaResult(ok=False)` with safe `AriaError` codes such as `INVALID_SAMPLE_RATE`, `INVALID_BIT_DEPTH`, or `INVALID_FORMAT`. Unsupported/degraded capabilities normally return `ok=True` state objects with safe reasons and warnings.

## Security considerations

No secrets, paths, provider internals, raw device identifiers, or driver details are accepted or emitted. Tests assert absence of forbidden imports/terms that would indicate real integration behavior.

## Dependencies

None beyond Python standard library and existing `noqlen_aria.contracts`.

## Risks

- Future app layers may confuse capability state with execution commands. Mitigation: summaries and tests state that no audio is played.
- Conservative support matching may need richer format models later. Mitigation: current models are simple and explicit.
- Bit-perfect terminology can imply real output. Mitigation: readiness is derived state only, with non-goals and boundary tests.

## Rollback strategy

Remove `src/noqlen_aria/playback_capabilities.py`, the new tests/spec directory, and the export/context updates. No migrations or external state exist.

## Validation plan

- Run requested compile, CLI, pytest, diff, contamination, and boundary search commands.
- Confirm no audit 14-17 or Bloco 18 work was started.
- Confirm no real playback/audio driver/Android/provider/network/filesystem/DSP/EQ code exists.

## Behavior Budget

- New behaviors:
  - add playback capability state models;
  - add fade-in/fade-out capability and timing preference models;
  - add audio output route/device readiness models;
  - add bit-perfect/USB DAC/exclusive output capability models;
  - add sample-rate/bit-depth/format support models;
  - add playback quality preference models;
  - add deterministic capability/readiness services.
- Public API changes:
  - expose only intentional playback capability names.
- Files allowed:
  - `src/noqlen_aria/**`
  - `tests/**`
  - `aria/specs/features/playback-capability-models/**`
  - `aria/context/current.md`
  - `aria/context/delta.md`
  - `docs/handoff.md`, only if a tiny status note is needed.
- Tests required:
  - gapless available/unavailable behavior;
  - loudness/ReplayGain awareness behavior;
  - crossfade available/unavailable behavior;
  - fade-in/fade-out available/unavailable behavior;
  - fade timing validation;
  - bit-perfect conflict with fade/crossfade signal-altering processing;
  - bit-perfect blocked/available/degraded behavior;
  - USB DAC capability state;
  - exclusive output capability state;
  - sample-rate/bit-depth support matching;
  - output/device readiness;
  - playback quality preference mapping;
  - no real playback/audio driver/Android/provider behavior.
- Dependencies:
  - none.
- Stop if:
  - real audio output becomes necessary;
  - real bit-perfect implementation becomes necessary;
  - Android audio APIs become necessary;
  - Media3/ExoPlayer becomes necessary;
  - USB driver/JNI/NDK/AAudio/Oboe becomes necessary;
  - DSP/EQ implementation becomes necessary.
