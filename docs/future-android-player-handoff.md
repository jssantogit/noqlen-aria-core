# Future Android Player Handoff

This document is a future-project handoff. It does not start Future Android Player work and does not implement Android, playback, audio output, USB, JNI/NDK, AAudio, Oboe, Media3, ExoPlayer, MediaSession, Android Auto, or UI behavior.

## Boundary

Aria Core owns contracts, states, policies, services, capabilities, fakes, sanitized results, readiness, validation, snapshots, and safe app-facing models.

Future Android Player owns real platform and playback implementation. It may consume Aria Core playback intents, queue/now-playing state, stream handles, quality policy, output readiness, and capability models through approved adapter boundaries.

## Phase A — Audio Output Research

Research Android audio output APIs and constraints outside Aria Core:

- Android audio paths and OS version constraints.
- USB DAC accessibility.
- Exclusive mode feasibility.
- Sample-rate and bit-depth negotiation.
- Latency, stability, and device support risks.
- Existing engine/driver options.

No implementation should occur in Aria Core.

## Phase B — Playback Engine Adapter

Design and prototype a playback engine adapter in the Android Player project:

- Map Aria playback intents to real playback engine calls.
- Report blocked, unavailable, warning, and success states back through Aria-facing results.
- Preserve Aria Core policy and validation as source of truth.
- Avoid moving queue, now-playing, provider, cache, safety, or capability logic into UI.

## Phase C — Exclusive USB Output Prototype

Prototype exclusive USB output outside Aria Core only after a dedicated future spec:

- Target a limited device matrix.
- Validate sample-rate switching and bit-depth behavior.
- Capture stability and fallback behavior.
- Keep prototype status explicit.

## Phase D — Bit-perfect Validation

Validate whether the prototype is bit-perfect or bit-transparent under documented conditions:

- Define test fixtures and measurement approach.
- Record device-specific limitations.
- Record fallback paths and cases where bit-perfect behavior is unavailable.
- Do not claim universal support.

## Phase E — Production Audio Driver/Bridge Decision

Decide whether to build a production driver/bridge, adopt an existing solution, or avoid custom output. Aria Core remains driver-free regardless of the decision.

## App/UI Rule

The future Android app/UI must remain a thin adapter over Aria Core. Heavy safety, readiness, policy, provider, queue, now-playing, playback availability, storage/cache, quality, transcoding, and capability logic must not be moved into UI screens.
