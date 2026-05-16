# UI Shell Boundary

Bloco 5 defines planning artifacts for a future minimal UI/app shell. This document is documentation only. It does not implement screens, navigation, an app shell, Android code, playback, media sessions, queues, now playing, cache, or provider integrations.

## Roles

### Future UI/App Shell

The future UI/app shell is a thin adapter over Aria Core.

It may:

- Render app-facing state produced by Aria Core.
- Capture user input and express it as Aria Core intents.
- Display safe errors and warnings that Aria Core already sanitized.
- Delegate platform-specific prompts and platform callbacks to a platform adapter.

It must not:

- Call Anchor directly.
- Call Navidrome, Jellyfin, Emby, or provider internals directly.
- Own orchestration logic.
- Own safety rules.
- Own lifecycle/apply decisions.
- Own playback engine logic.
- Own queue, now playing, offline/cache, or provider logic.
- Call Android/player boundary bridges directly.

### Aria Core

Aria Core owns contracts, states, results, intents, diagnostics, readiness, lifecycle previews, safety boundaries, adapters, and future orchestration.

Aria Core is responsible for:

- Mapping backend/control-plane data into app-facing state.
- Returning `AriaResult` values instead of raw exceptions.
- Sanitizing `AriaError` and `AriaWarning` data before UI display.
- Deciding whether lifecycle/apply operations are safe.
- Owning control-plane access through `ControlClient`.
- Keeping Anchor as one adapter, not a UI dependency.
- Keeping provider access behind future source/provider contracts.
- Keeping Android/player boundaries abstract.

### Platform Adapter

A platform adapter is the future platform-specific bridge between native platform events and Aria Core. It is not the UI screen layer.

It may:

- Translate platform callbacks into Aria Core intents.
- Translate Aria Core app-facing state into platform-specific display models.
- Request platform permissions only after Aria Core state indicates the need.
- Implement platform-specific wiring in a future dedicated block.

It must not:

- Bypass Aria Core to call providers.
- Treat Android/player boundary contracts as real Android implementations.
- Implement Media3, ExoPlayer, MediaSession, Android Auto, queue, or cache logic in this core phase.

## Data Flow

Future UI consumes state from Aria Core:

```text
Aria Core
  -> AriaResult[ServerViewState]
  -> AriaResult[ReadinessViewState]
  -> AriaResult[DiagnosticsViewState]
  -> AriaResult[PermissionState]
  -> AriaResult[StorageAccessState]
  -> optional AndroidBoundarySnapshot
  -> Future UI/App Shell
```

Future UI sends intents to Aria Core:

```text
Future UI/App Shell
  -> refresh status
  -> collect diagnostics
  -> preview lifecycle intent
  -> request lifecycle intent execution
  -> request permission/storage state
  -> request playback or media control intent
  -> Aria Core
```

The UI never calls providers, Anchor, Navidrome, Android APIs, playback engines, or boundary bridge implementations directly.

## App-Facing State Boundary

Future UI may consume these existing Aria Core states and results:

- `AriaResult[T]`: success/failure envelope for UI-facing operations.
- `AriaError`: sanitized error message and stable internal code.
- `AriaWarning`: sanitized warning message and stable internal code.
- `ServerViewState`: server connectivity, version, latency, and last safe error.
- `LibraryViewState`: library availability and aggregate counts.
- `DiagnosticsViewState`: safe warnings for display.
- `ReadinessViewState`: composite readiness, status, diagnostics, and `all_ready`.
- `LifecycleIntent`: lifecycle actions requested by UI and decided by Aria Core.
- `PermissionState`: platform-agnostic permission state.
- `StorageAccessState`: platform-agnostic storage state.
- `AndroidBoundarySnapshot`: optional future Android/player boundary snapshot from Bloco 4.

Future UI must treat these values as immutable display inputs. Mutations and decisions go back through Aria Core.

## Intent Boundary

Future UI may express user actions as intents, but it does not decide how they are executed.

Allowed conceptual intent categories:

- Refresh status.
- Collect diagnostics.
- Assess readiness.
- Preview lifecycle action.
- Confirm lifecycle action.
- Check permission state.
- Check storage state.
- Request playback command.
- Request media transport action.

Aria Core decides routing, validation, safety, dry-run/apply behavior, and boundary dispatch.

## Screen Data Boundaries

### Status and Readiness

Status and readiness views consume `ServerViewState` and `ReadinessViewState` only.

They may display:

- Connected or disconnected state.
- Server version.
- Latency in milliseconds.
- Library availability.
- Readiness pass/fail.
- Sanitized last error message.

They must not:

- Ping Anchor directly.
- Query Navidrome directly.
- Interpret provider-specific health checks.
- Decide lifecycle/apply behavior.

### Diagnostics

Diagnostics views consume `DiagnosticsViewState` only.

They may display:

- Warning messages.
- Warning count.
- Empty/all-clear state.
- Optional severity labels supplied by Aria Core in future view models.

They must not:

- Read raw logs.
- Display stack traces.
- Inspect provider exceptions.
- Re-run backend checks independently.

### Lifecycle Preview

Lifecycle confirmation views consume lifecycle preview data from Aria Core.

They may display:

- Intent name.
- Human-readable description.
- Whether an action is reversible.
- Whether an action requires apply/confirmation.

They must not:

- Execute lifecycle behavior directly.
- Bypass dry-run/apply safeguards.
- Call Anchor startup, shutdown, or reset APIs directly.

### Permission and Storage

Permission/storage views consume `PermissionState`, `StorageAccessState`, and future storage boundary snapshots.

They may display:

- Permission granted, denied, unknown, or not applicable.
- Storage available, unavailable, or unknown.
- Safe explanation text supplied by Aria Core.
- A prompt affordance delegated to the future platform adapter.

They must not:

- Call platform permission APIs directly.
- Access the filesystem directly.
- Mutate storage, cache, or downloads.
- Decide destructive cleanup behavior.

### Playback and Media Controls

Playback/media control views consume abstract playback state and expose intent affordances only.

They may display:

- Play, pause, stop, seek, skip, and transport affordances based on Aria Core state.
- Disabled states when Aria Core reports unavailable capability.
- Safe error messages returned by Aria Core.

They must not:

- Implement playback state machines.
- Call Media3, ExoPlayer, MediaSession, Android Auto, or audio APIs directly.
- Own queue or now playing behavior.
- Translate headset, lock-screen, or notification events without Aria Core routing.

## Android/Player Boundary Consumption

Bloco 4 Android/player boundary contracts remain abstract. They are vocabulary and fake-first contracts, not Android SDK integration.

Future UI must consume them only through an Aria Core-facing adapter layer. The UI does not import or call these bridge protocols directly:

- `PlaybackEngineBridge`
- `MediaSessionBridge`
- `AndroidStorageBridge`
- `AndroidAutoBridge`
- `ForegroundServiceBridge`
- `AppLifecycleBridge`
- `NotificationControlBridge`
- `LockScreenBridge`
- `HeadsetControlBridge`

The platform adapter may wire those bridges in a future dedicated block, but the screen layer still consumes app-facing state and emits intents only.

## Thin UI Examples

These examples are conceptual documentation. They are not runnable UI code.

### Server Status Rendering

Given the future UI needs server status,
When it renders status,
Then it consumes `ServerViewState` through Aria Core state,
And it displays `connected`, `server_version`, `latency_ms`, and safe error text,
And it does not call Anchor, Navidrome, or provider internals directly,
And it does not own retry or orchestration logic.

### Diagnostics Rendering

Given the future UI needs diagnostics,
When it shows diagnostics,
Then it consumes `DiagnosticsViewState.warnings`,
And each warning is already sanitized by Aria Core,
And the UI does not read logs, stack traces, provider exceptions, or raw backend output,
And the UI does not decide which diagnostics are safe to run.

### Lifecycle Preview Confirmation

Given the future UI offers an initialize, shutdown, or reset action,
When the user asks to preview the action,
Then the UI displays Aria Core lifecycle preview data,
And it waits for Aria Core to indicate whether apply/confirmation is required,
And it does not call Anchor lifecycle commands directly,
And it does not bypass dry-run/apply safeguards.

### Permission/Storage Prompt State

Given the future UI needs storage permission UX,
When it renders the prompt state,
Then it consumes `PermissionState` and `StorageAccessState`,
And it displays granted, denied, unknown, or unavailable state from Aria Core,
And platform permission requests are delegated to a future platform adapter,
And the UI does not call platform permission APIs or filesystem APIs directly.

### Playback Control Intent Display

Given the future UI wants playback controls,
When it shows play, pause, skip, or seek affordances,
Then it renders controls from Aria Core state and capabilities,
And user actions are emitted as playback/media intents,
And Aria Core routes them through future boundary contracts,
And the UI does not implement playback logic, queue logic, now playing logic, or media engine logic.

## Safe Output Expectations

All UI-facing output must be safe for display:

- No secrets.
- No credentials.
- No raw filesystem paths unless explicitly sanitized.
- No raw stack traces.
- No provider-internal exception objects.
- No personal music-library contents unless supplied by an approved future media-source contract.
- No destructive action details that bypass confirmation.

If data is not already sanitized by Aria Core, future UI must not display it.

## Review Checklist For Future UI Work

- Does the UI import only the allowed Aria app-shell adapter surface?
- Does the UI avoid direct Anchor, Navidrome, Jellyfin, Emby, and provider imports?
- Does the UI render state instead of computing business decisions?
- Does the UI emit intents instead of executing lifecycle or playback operations?
- Does the UI avoid Android SDK, playback engine, MediaSession, Android Auto, queue, now playing, and cache logic unless a future spec allows it?
- Does the UI display only sanitized errors and warnings?
- Does the platform adapter preserve Bloco 4 boundaries as abstract contracts?
