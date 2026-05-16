# Android Shell Handoff

Bloco 23 is documentation/handoff only. It does not implement an Android shell, Android SDK calls, Kotlin, Java, Gradle, Compose, Activity, Fragment, UI screens, MediaSession, Media3, ExoPlayer, Android Auto, notifications, lock-screen controls, Bluetooth/headset handling, widgets, foreground services, playback engines, audio drivers, USB output, provider integration, network behavior, or filesystem/device behavior.

This handoff explains how a future Android shell/app should consume Aria Core without moving heavy logic into UI/platform code.

## Conceptual Model

```text
Android UI/shell
  -> Android app/platform adapters
  -> Aria Core state/results/intents
  -> approved Aria contracts/adapters
  -> future providers/player/platform implementations
```

The Android shell is a consumer and adapter over Aria Core. Android UI stays thin. Aria Core remains the source of truth for state, policies, validation, readiness, safety, result mapping, app-facing contracts, and sanitized output.

## Role Split

Android shell owns:

- Future app composition and navigation in the Android codebase.
- Rendering app-facing Aria state and results.
- Capturing user actions and expressing them as Aria intents.
- Presentation-only UI state.
- Delegating platform callbacks and platform-specific calls to Android platform adapters.
- Delegating real playback/audio work to the future Android Player/audio layer.

Aria Core owns:

- `AriaResult`, errors, warnings, safe serialization, and sanitized output.
- Status, diagnostics, readiness, lifecycle previews, and result mapping.
- Media source, library, search, queue, now-playing, playback intent, renderer, automation, provider readiness, and capability models.
- Offline/cache/storage policy, internet radio models, stream quality/network/transcoding policy, playback capability/readiness, profiles, preferences, backup/restore safety, snapshots, and fake flows.
- Heavy policy, validation, readiness, safety, and platform-neutral orchestration.

Android platform adapters own:

- Android SDK calls and OS callbacks.
- Permission dialogs and storage access calls.
- MediaSession, notifications, lock-screen controls, Bluetooth/headset events, foreground service, Android Auto, widgets, lifecycle callbacks, and device integration.
- Mapping platform events into Aria-safe intents.
- Mapping Aria state into platform display/session metadata.
- Normalizing platform errors into safe app-facing states.

Future Android Player/audio layer owns:

- Real playback execution.
- Playback engine choice, such as Media3/ExoPlayer or an alternative engine.
- Audio output routing implementation.
- Playback engine adapter implementation.
- Future custom/exclusive audio output research and approved prototypes.
- Any future JNI/NDK/AAudio/Oboe/USB audio bridge work under a separate spec.

## Data And Intent Flow

Aria Core to Android UI:

```text
Aria Core state/results/snapshots
  -> Android app-facing adapter/facade
  -> Android UI render state
```

Android UI and platform events to Aria Core:

```text
User action or platform callback
  -> Android shell/platform adapter
  -> Aria-safe intent or approved app-facing request
  -> Aria validation/result
```

The Android shell must treat Aria data as the source of truth. UI state may cache display data, but it must not become a queue, now-playing, provider, storage, or playback policy source of truth.

## Startup And Readiness Flow

Expected future handoff:

```text
Android shell starts
  -> requests Aria status/readiness/app snapshot
  -> renders connected/degraded/unavailable state from Aria
  -> requests permission/storage prompts only through platform adapters when Aria state indicates need
```

The shell must not call Anchor, providers, provider internals, backend health endpoints, or Anchor CLI directly during startup.

## Diagnostics And Support Snapshot Flow

Expected future handoff:

```text
User opens diagnostics/support
  -> Android shell requests Aria diagnostics and safe snapshot data
  -> Aria returns sanitized diagnostics/snapshot output
  -> Android displays or exports approved safe data only
```

The shell must not read raw logs, display stack traces, expose credentials, expose raw paths, inspect provider exceptions, or serialize platform exception objects for support output.

## Library Browse And Search Flow

Expected future handoff:

```text
User browses or searches
  -> Android shell calls Aria app-facing library/search services or models
  -> Aria applies source/provider capability and readiness rules
  -> Android renders success, empty, degraded, unavailable, or warning states
```

The shell must not query providers directly, call Anchor provider internals, or implement provider capability rules.

## Queue And Now-playing Flow

Expected future handoff:

```text
Android needs queue or now-playing state
  -> requests Aria queue/now-playing state
  -> renders immutable app-facing state
  -> sends queue or playback actions as Aria intents
```

The shell must not maintain a separate queue truth, now-playing state machine, playback availability policy, or provider-backed current item model.

## Playback Controls And Intents Flow

Expected future handoff:

```text
UI button or platform media event
  -> Android shell/platform adapter maps action to an Aria playback intent
  -> Aria validates and returns success, warning, blocked, or unavailable state
  -> future Android Player adapter acts only when a future implementation spec allows it
```

UI screens must not call playback engines, audio APIs, MediaSession, Android Auto, notifications, lock-screen controls, Bluetooth/headset handlers, or widgets directly.

## Offline And Cache Flow

Expected future handoff:

```text
Android needs offline/cache state
  -> consumes Aria offline/cache/storage policy models
  -> renders eligibility, pending, blocked, warning, or confirmation state
  -> routes user requests back through Aria-approved intents or future app-facing calls
```

The shell must not implement destructive cache/download behavior, storage traversal, storage cleanup, or offline mutation policy.

## Internet Radio Flow

Expected future handoff:

```text
Android displays radio station or live metadata state
  -> consumes Aria radio station, stream handle, availability, metadata, and favorite/read state
  -> renders unavailable/degraded/live metadata states
  -> delegates real radio playback to future Android Player work
```

The shell must not implement radio streaming, Shoutcast/HLS/DASH parsing, provider direct integration, or playback engine behavior.

## Stream Quality, Network, And Transcoding Flow

Expected future handoff:

```text
Android needs quality/network/transcoding decisions
  -> consumes Aria stream quality, network policy, and transcoding capability/policy models
  -> renders chosen quality, fallback, blocked, unavailable, or warning states
  -> leaves real network probing/transcoding/playback to future implementation specs
```

The shell must not implement transcoding, network probing, stream execution, or provider-specific quality rules.

## Playback Capability Flow

Expected future handoff:

```text
Android needs output/playback capability state
  -> consumes Aria playback capability and audio output readiness models
  -> renders gapless, crossfade, fade, loudness, bit-perfect, USB DAC, exclusive output, and format readiness states
  -> delegates real output behavior to future Android Player/audio specs
```

Capability/readiness can be modeled by Aria. Real audio output implementation belongs outside Aria Core.

## Provider Readiness Flow

Expected future handoff:

```text
Android needs provider/source availability
  -> consumes Aria provider/source readiness and capability models
  -> renders compatible, degraded, unavailable, requirement, and warning states
  -> routes account/provider actions through future approved adapter specs
```

The shell must not call providers directly, call Anchor provider internals, assume current Anchor is multi-provider, or treat provider sign-in as UI-owned core policy.

## Permission And Storage UX Flow

Expected future handoff:

```text
Android needs permission/storage UX
  -> consumes Aria platform-neutral permission/storage boundary state
  -> Android platform adapter performs OS permission/storage calls
  -> adapter reports native results back through approved Aria-facing state
```

Aria owns policy consequences and safe explanation text. Android owns OS prompts and native result callbacks.

## Media Controls And Android Auto Handoff

MediaSession, notifications, lock-screen controls, Bluetooth/headset controls, foreground service, Android Auto, and widgets are future platform surfaces. They should consume Aria state and emit Aria intents through Android platform adapters.

Android Auto browse/playback responses should use Aria library/source/provider/queue/now-playing models. Media controls should map to Aria playback intents. None of these platform surfaces should call providers, playback engines, storage APIs, or Aria bridge implementations directly from UI screens.

## Future Audio Output And Driver Boundary

Bit-perfect output, custom USB output, exclusive output, sample-rate switching, bit-depth negotiation, DAC control, JNI/NDK, AAudio, Oboe, and audio-driver work remain in the future Android Player/audio phase documented in `docs/aria-core-handoff.md` and `docs/post-core-backlog.md`.

The future Android Player may report capability/readiness/results back through Aria models. Aria Core must not contain real audio driver, USB output, platform audio bridge, or playback engine logic.

## Must Not Bypass Aria Core

The Android shell must not:

- Call providers directly.
- Call Anchor provider internals.
- Treat Anchor CLI as integration.
- Own safety policies.
- Own lifecycle/apply decisions.
- Own queue or playback business rules.
- Own provider capability rules.
- Own backup/restore safety rules.
- Expose secrets, credentials, raw paths, raw logs, stack traces, or provider exception objects.
- Move heavy orchestration out of Aria Core.
- Treat Android platform surfaces as the source of truth.
- Put playback engine, audio driver, USB output, or platform SDK logic in Aria Core.

## Future Specs Required

Future implementation should be split into dedicated specs before code is added:

- Android shell/app architecture and app-facing facade.
- Startup/readiness wiring.
- Diagnostics/support snapshot export.
- Library/search screen integration.
- Queue/now-playing UI integration.
- Playback controls and MediaSession integration.
- Notification/lock-screen/Bluetooth/headset controls.
- Foreground service lifecycle.
- Android Auto.
- Widgets.
- Permission/storage UX platform calls.
- Playback engine adapter.
- Android Player audio output research and any custom/exclusive USB output prototype.
