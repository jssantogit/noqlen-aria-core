# Requirements

## Status

Approved for Bloco 17 implementation in this task.

## Problem

Future player and UI layers need stable Aria Core vocabulary for playback capabilities, audio output readiness, bit-perfect feasibility, USB DAC/exclusive output readiness, format compatibility, and quality preferences. Without these contracts, future Android/player work would be forced to either call platform/audio APIs directly or invent duplicate state models.

## Goal

Add deterministic, state-only playback capability and audio output readiness models and services. Aria Core reports capability, readiness, preference, warning, and unavailable/degraded reasons from caller-provided declarations only. It never plays audio, opens streams, controls devices, applies gain, switches sample rates, or calls platform/provider APIs.

## Non-goals

- No real playback.
- No audio driver.
- No USB driver.
- No Android USB Host API.
- No JNI/NDK.
- No AAudio/Oboe.
- No Media3/ExoPlayer.
- No real MediaSession.
- No real bit-perfect output.
- No sample-rate switching.
- No DAC control.
- No DSP/EQ.
- No Android/UI.
- No provider integration.
- No stream execution.
- No transcoding implementation.
- No real gapless playback.
- No real crossfade implementation.
- No loudness/gain application.
- No filesystem, network, or device traversal.

## Actors

- Future UI/app layer consuming Aria Core state.
- Future Android Player adapter that may map platform/audio output state into Aria Core models.
- Aria Core deterministic tests and fake scenarios.
- Future audit reviewer verifying no real playback/audio output behavior exists.

## Functional requirements

- FR-01: Define gapless capability state with available/unavailable state and safe reasons.
- FR-02: Define loudness normalization capability state and ReplayGain awareness state without applying gain.
- FR-03: Define crossfade capability state with requested/available/unavailable behavior and safe reasons.
- FR-03a: Define fade-in and fade-out capability state with duration/timing preference, availability/readiness, and safe unavailable reasons.
- FR-04: Define bit-perfect capability/readiness state derived from declared source format, route/device support, and exclusive output availability.
- FR-05: Define audio output route state and route type for system audio, USB DAC, Bluetooth, remote, unknown, and unavailable routes.
- FR-06: Define audio output device state with declared sample-rate, bit-depth, and format support.
- FR-07: Define USB DAC and exclusive output capability states as declared capability/readiness only.
- FR-08: Define sample-rate, bit-depth, and audio format support models with deterministic compatibility checks.
- FR-09: Define audio output readiness state with available, degraded, unavailable, blocked reasons, and warnings.
- FR-10: Define playback quality preference mapping to bit-perfect, high quality, balanced, data saver, and automatic preferences.
- FR-11: Define playback capability summary and warnings for future UI consumption.
- FR-12: Implement `PlaybackCapabilityService` for gapless/crossfade/loudness/ReplayGain/quality preference/summary decisions from declared state only.
- FR-12a: Implement fade-in/fade-out capability evaluation from declared state only.
- FR-13: Implement `AudioOutputCapabilityService` for output readiness, format compatibility, USB DAC/exclusive output, and bit-perfect readiness from declared state only.
- FR-14: Provide deterministic fake/capability scenarios for normal system audio, USB DAC, exclusive available/unavailable, bit-perfect blocked, sample-rate mismatch, bit-depth mismatch, gapless/crossfade available/unavailable, ReplayGain metadata present/missing, and degraded/unavailable routes.
- FR-15: Return safe `AriaResult` errors for invalid declared sample-rate/bit-depth inputs.
- FR-16: Preserve public API intentionality by exposing only Bloco 17 names.

## Canonical Examples

- Given a source and output route support gapless, When capability summary is built, Then Aria reports gapless available without playing audio.
- Given loudness metadata is present, When ReplayGain awareness is evaluated, Then Aria reports metadata awareness without applying gain.
- Given crossfade is requested but the future output route does not support it, When capability is evaluated, Then Aria returns unavailable with a safe reason.
- Given fade-in is requested and source/route support fade processing, When fade capability is evaluated, Then Aria reports fade-in available without processing audio.
- Given fade-out timing is invalid, When fade capability is evaluated, Then Aria returns a safe structured error without processing audio.
- Given bit-perfect is desired but current route is Android system audio, When readiness is evaluated, Then Aria reports blocked by non-exclusive output.
- Given bit-perfect preference forbids signal-altering processing, When fade or crossfade is evaluated, Then Aria reports blocked by signal-processing policy as state only.
- Given a USB DAC route advertises 96 kHz / 24-bit support, When support is checked, Then Aria reports compatible format support as state only.
- Given exclusive output is unavailable, When bit-perfect readiness is requested, Then Aria returns degraded/unavailable state and no driver code runs.
- Given UI needs output capability later, When it consumes state, Then it uses Aria Core models and does not call Android/audio driver APIs.

## Non-functional requirements

- Deterministic local behavior only.
- Python standard library only; no new dependencies.
- State models must be frozen dataclasses or enums where practical.
- Services must not call network, filesystem, providers, platform APIs, playback engines, audio devices, subprocesses, or external drivers.
- Errors and warnings must use safe Aria Core result types.
- Public names must be intentional and covered by tests.

## Edge cases

- Missing route/device state returns unknown or unavailable state safely.
- Negative sample rate or bit depth returns a safe error.
- Empty support sets mean unknown support, not implicit real probing.
- Desired bit-perfect on system audio is blocked by non-exclusive output.
- Desired bit-perfect with unsupported sample rate or bit depth is unavailable/degraded by declared incompatibility.
- USB DAC route can be declared unavailable or degraded without driver behavior.
- Exclusive output can be declared unavailable and must block bit-perfect readiness.
- ReplayGain metadata missing means not aware; gain is never applied.
- Crossfade requested on unsupported route returns unavailable without playback behavior.
- Fade-in/fade-out requested on unsupported source or route returns unavailable without playback behavior.
- Fade timing must not be negative.
- Bit-perfect/exclusive output preference may block fade and crossfade because they are signal-altering features.

## Acceptance criteria

- Spec files exist under `aria/specs/features/playback-capability-models/`.
- Behavior Budget, Test Risk Matrix, canonical examples, and delta checklist are present.
- Source models and services are implemented under `src/noqlen_aria/`.
- Tests cover required capability/readiness/preference behavior and no-driver boundaries.
- No real playback/audio driver/Android/provider/network/filesystem/DSP/EQ behavior is added.
- `current.md` and `delta.md` are updated concisely.
- Required validation passes.

## Open questions

- Exact future Android Player bridge implementation remains deferred to a later Android Player phase.
- Future real bit-perfect validation criteria remain deferred and out of Aria Core scope.
