# Requirements

## Status

Bloco 22 Android Real Integration Planning is approved for documentation and planning only.

Context package used: Standard.

## Problem

Aria Core already defines platform-neutral playback, now-playing, renderer, permission/storage, Android/player boundary vocabulary, and provider-readiness concepts. Future Android app work needs real media controls, lock-screen controls, notification controls, Bluetooth/headset handling, Android Auto, foreground-service behavior, widgets, permission/storage UX, MediaSession wiring, and playback engine adapters, but those platform responsibilities must not move heavy logic into Aria Core or into UI screens.

Without a planning artifact, future Android work could duplicate queue, now-playing, playback policy, provider readiness, storage safety, or audio-output decisions in Android code and accidentally couple this Python core to Android SDK concepts.

## Goal

Create a detailed planning spec and documentation for future real Android integration while keeping Aria Core platform-independent. The plan defines ownership, boundaries, risks, dependencies, adapter responsibilities, and expected state/intent flows for future Android app/platform work.

## Non-goals

- No Android SDK implementation.
- No Kotlin, Java, or Gradle files.
- No MediaSession implementation.
- No Media3 or ExoPlayer implementation.
- No Android Auto implementation.
- No notification, lock-screen, Bluetooth, or headset implementation.
- No widget implementation.
- No playback engine implementation.
- No audio driver implementation.
- No USB output implementation.
- No UI, screen, navigation, or app-shell implementation.
- No provider integration.
- No network behavior.
- No filesystem/device behavior.
- No source code behavior changes.
- No test changes unless existing docs validation requires them.
- No Bloco 23 work.

## Actors

- Future Android app/platform layer.
- Future Android media/session adapter.
- Future Android foreground service.
- Future Android Auto adapter.
- Future Android widget surface.
- Future playback engine adapter in the Android Player phase.
- Aria Core.
- End user controlling playback from app UI, media controls, lock screen, notification, Bluetooth/headset, Android Auto, or widgets.

## Functional Requirements

- Document that Bloco 22 is planning only and does not implement Android code.
- Document how future real Android media controls consume Aria playback intents and now-playing state.
- Document how lock-screen and notification controls map to Aria intents without bypassing Aria Core.
- Document how Bluetooth/headset events become Aria-safe playback intents.
- Document how Android Auto consumes Aria browse/playback data through an app/platform adapter.
- Document foreground service ownership and lifecycle expectations as platform-level responsibilities.
- Document widget boundaries as optional future platform surfaces over Aria state and intents.
- Document Android permission/storage UX handoff and platform-call ownership.
- Document MediaSession integration planning without implementing MediaSession.
- Document future playback engine adapter expectations without implementing a playback engine.
- Document the future audio output/driver research boundary and keep it in the Android Player phase, outside Aria Core.
- Document how Android app/platform code consumes Aria Core without moving heavy state, policy, validation, readiness, or safety logic into UI/platform code.
- Update workflow state concisely in `aria/context/current.md` and `aria/context/delta.md`.

## Non-functional Requirements

- Preserve Aria Core as platform-independent Python/core logic.
- Keep planning language explicit that Android implementation is future app/platform work.
- Keep app/UI screen responsibilities thin: render Aria state and emit Aria intents.
- Keep platform adapter responsibilities explicit: translate platform callbacks into Aria-safe intents and translate Aria state into platform display/session models.
- Do not introduce dependencies.
- Do not alter public APIs.
- Do not modify `src/noqlen_aria/**`, `tests/**`, `pyproject.toml`, or any Android/Kotlin/Java/Gradle files.
- Keep docs free of claims that real Android integration is implemented.

## Canonical Examples

Given Android media controls are needed later, When planning integration, Then Android consumes Aria playback intents and now-playing state instead of owning core logic.

Given lock-screen/notification controls are needed later, When planning controls, Then they map to Aria intents and do not bypass Aria Core.

Given Bluetooth/headset buttons are pressed later, When platform receives events, Then platform adapter converts them into Aria-safe intents.

Given Android Auto is added later, When it requests browse/playback data, Then it consumes Aria models through an app/platform adapter.

Given foreground service is needed later, When planning lifecycle, Then service lifecycle remains platform-level and does not move core policy out of Aria.

Given bit-perfect/custom USB output is researched later, When planning Android audio output, Then it remains in future Android Player phase, not Aria Core.

Given UI needs Android permission/storage UX later, When displaying it, Then it consumes Aria boundary state and delegates platform calls to Android code.

## Edge Cases

- Android media control event arrives while Aria reports playback unavailable: future adapter must convert the event to an Aria intent and respect the blocked/unavailable result.
- Notification or lock-screen action is stale after queue/now-playing changes: future adapter must refresh from Aria state and avoid local state machines.
- Bluetooth headset sends duplicate or unsupported commands: future adapter must normalize and validate through Aria intent handling.
- Android Auto requests data while provider/source readiness is degraded: future adapter must expose safe degraded Aria models, not query providers directly.
- Foreground service is killed or restarted by the platform: future platform layer owns service recovery while rehydrating state from Aria-approved snapshots/models.
- Widget displays old state: future widget refresh must consume Aria state and avoid direct provider, playback engine, or storage calls.
- Permission/storage request is denied: Android layer owns platform prompt/result handling, while Aria Core owns platform-neutral state and policy consequences.
- Future custom audio output research discovers platform constraints: decision remains in the future Android Player phase and does not introduce driver code into Aria Core.

## Acceptance Criteria

- Spec files exist under `aria/specs/features/android-real-integration-planning/`.
- `requirements.md`, `design.md`, `tasks.md`, and `review.md` include the required sections.
- Behavior Budget is present.
- Test Risk Matrix is present.
- Canonical Examples are present using Given / When / Then.
- Android real integration planning documentation exists under `docs/`.
- Planning covers real media controls, lock-screen controls, notification controls, Bluetooth/headset controls, Android Auto, foreground service expectations, widgets, permission/storage UX handoff, MediaSession integration planning, playback engine adapter expectations, future audio output/driver research boundary, and the Aria Core consumption model.
- Current and delta context files are updated concisely.
- No source code changed.
- No tests changed.
- No Android implementation was added.
- Required validation passes.
- Spec and docs are committed together with `docs(android): add real integration planning`.

## Open Questions

- Which Android app architecture will host future platform adapters?
- Which playback engine option will be selected in a future Android Player phase?
- Which Android versions and form factors will be supported for MediaSession, Android Auto, widgets, and foreground service policy?
- Whether custom/exclusive USB output is feasible remains future Android Player research, not Aria Core work.
