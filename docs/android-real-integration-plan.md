# Android Real Integration Plan

Bloco 22 is planning documentation only. It does not implement Android SDK calls, Kotlin, Java, Gradle, MediaSession, Media3, ExoPlayer, Android Auto, notifications, lock-screen controls, Bluetooth/headset handling, widgets, foreground services, playback engines, audio drivers, USB output, UI screens, provider integration, network behavior, or filesystem/device behavior.

Future Android real integration belongs to the Android app/platform layer. Aria Core remains platform-independent Python/core logic and continues to own app-facing state, intents, policy, readiness, validation, safety, snapshots, provider/source abstractions, and sanitized output.

Bloco 23 adds the Android shell handoff in `docs/android-shell-handoff.md`. That handoff explains how the future Android app/shell consumes Aria Core across startup, diagnostics, library/search, queue/now-playing, playback controls, provider readiness, permission/storage UX, media controls, Android Auto, and future audio boundaries.

## Integration Model

Future Android integration should follow this shape:

```text
Android UI and platform surfaces
  -> Android app/platform adapter
  -> Aria Core states and intents
  -> approved Aria contracts/adapters
  -> future platform/player/provider implementations
```

The Android app should be a consumer and adapter over Aria Core. It should not move heavy state, policy, validation, readiness, safety, provider logic, queue behavior, now-playing behavior, playback policy, or storage/cache policy into UI or platform code.

## Ownership

Aria Core owns:

- Playback intents and validation.
- Queue and now-playing state contracts.
- Renderer/output capability and readiness models.
- Provider/source readiness and capability models.
- Offline/cache/storage policy and confirmation state.
- Permission/storage boundary state.
- Profiles, preferences, snapshots, and sanitized results.
- Safety rules and platform-neutral orchestration.

Future Android app/platform layer owns:

- Android OS callbacks and lifecycle registration.
- Platform permission prompts and storage access calls.
- MediaSession, notification, lock-screen, Bluetooth/headset, Android Auto, foreground service, and widget wiring.
- Translation from platform events into Aria-safe intents.
- Translation from Aria state into platform display/session models.
- Playback engine adapter wiring in a future Android Player phase.

UI/platform code must not duplicate Aria queue state machines, now-playing policy, playback availability validation, provider readiness, storage/cache/offline policy, permission/storage interpretation, confirmation policy, sanitization, or audio capability policy.

## Media Controls

Future Android media controls should render Aria now-playing state and emit Aria playback intents. Play, pause, stop, skip, seek, and renderer/output actions must be validated through Aria Core before any future platform playback adapter acts on them.

Android controls must not own playback state machines, queue mutation, now-playing transitions, provider calls, stream resolution, or playback safety rules.

## MediaSession Planning

Future MediaSession integration is platform work. It should project Aria now-playing metadata, playback availability, supported actions, and safe errors into Android session state. Incoming session commands should become Aria-safe playback intents.

MediaSession must not become a second source of truth. Aria Core remains the source for intent validation, now-playing state, queue policy, provider/source readiness, and blocked/unavailable outcomes.

## Notification And Lock-screen Controls

Future notification and lock-screen controls should be platform projections of the same Aria state and intent model.

Notification and lock-screen actions should map to Aria intents. Metadata, artwork references, disabled actions, and error text should come from sanitized Aria state. Platform code may own notification channels, compact action layout, pending intents, lock-screen visibility, and OS-specific lifecycle behavior.

These surfaces must not bypass Aria Core or call providers, playback engines, storage APIs, or queue/now-playing logic directly.

## Bluetooth And Headset Controls

Bluetooth/headset events are platform input events. A future Android adapter should normalize button presses and transport events into Aria-safe intents. Duplicate, stale, unsupported, or ambiguous events should be handled through Aria validation and safe blocked/unavailable results.

The adapter should not directly control playback or mutate queue/now-playing state.

## Android Auto

Android Auto is a future platform surface over Aria models. Browse trees, search, playable items, now-playing metadata, playback actions, and unavailable/degraded states should be backed by Aria library/source/provider/queue/now-playing models through an app/platform adapter.

Android Auto code must not query providers directly, implement its own library policy, own queue behavior, or own playback decisions.

## Foreground Service

Foreground service lifecycle is Android platform work. A future service may host long-running playback/session wiring and required OS-visible notification behavior. Service start, stop, restart, recovery, notification channel behavior, and OS compliance remain Android responsibilities.

The service must not move Aria policy into platform code. Recovery should rehydrate from Aria-approved state or snapshots and continue sending platform events through Aria intents.

## Widgets

Widgets are optional future platform surfaces. They should display a small projection of Aria state and submit Aria intents through the Android app/platform adapter. Widgets must not call providers, playback engines, storage APIs, or boundary bridges directly.

Widget refresh and stale-state handling should remain a platform concern, while truth comes from Aria state.

## Permission And Storage UX

Future Android permission/storage UX should display Aria boundary state and delegate platform calls to Android code.

Aria Core owns platform-neutral permission/storage state, offline/cache/storage policy, confirmation policy, and safe explanation text. Android owns permission dialogs, storage access framework calls, OS result callbacks, and native error mapping. UI screens display state and route user intent; they do not call platform APIs directly.

## Playback Engine Adapter Expectations

A future playback engine adapter should translate Aria playback intents, stream handles, renderer selection, and output readiness into calls to the selected Android playback engine. It should report normalized success, unavailable, blocked, and warning states back through Aria-facing models.

The adapter must be designed under a future dedicated spec. Bloco 22 does not choose or implement Media3, ExoPlayer, a custom engine, or any playback engine.

## Audio Output And Driver Research Boundary

Bit-perfect output, custom USB output, exclusive output, sample-rate switching, bit-depth negotiation, DAC control, JNI/NDK, AAudio, Oboe, and audio-driver work remain in the future Android Player audio output phases documented in `docs/aria-core-handoff.md` and `docs/post-core-backlog.md`.

Aria Core may model requirements, preferences, readiness, and conflicts for a future audio output layer. Aria Core must not implement a real audio driver, USB output, or platform audio bridge.

## Adapter Responsibilities

Future Android adapters should:

- Convert Android platform callbacks into Aria-safe intents.
- Convert Aria state into platform display/session models.
- Preserve Aria as the source of truth for heavy state and policy.
- Surface blocked/unavailable/degraded states safely.
- Keep raw platform exceptions, stack traces, credentials, paths, and provider details out of UI-visible output.
- Keep platform APIs isolated from Aria Core.

Future Android adapters should not:

- Call providers directly.
- Own queue, now-playing, playback policy, storage/cache policy, or provider readiness.
- Treat MediaSession, Android Auto, notification, lock-screen, Bluetooth/headset, widget, or foreground service state as core truth.
- Implement custom audio output or driver work inside Aria Core.

## Future Specs Required

Each real implementation area needs its own future spec and tests before code is added:

- MediaSession and platform media controls.
- Notification and lock-screen controls.
- Bluetooth/headset event handling.
- Android Auto browse/playback integration.
- Foreground service lifecycle and recovery.
- Widgets.
- Permission/storage UX and Android platform calls.
- Playback engine adapter.
- Android Player audio output research and any custom/exclusive USB output prototype.
