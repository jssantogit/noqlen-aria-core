# Requirements

## Status

Bloco 13 — Playback, Renderer and Automation Intents. Spec created. Implementation pending.

## Problem

Blocos 8-12 established media source, library, queue, and now-playing foundations. Aria Core lacks a structured way to preview and validate playback commands, renderer selection, and automation intents without executing real playback, calling providers, or depending on Android/Media3. UI/App consumers and future automation clients need safe, side-effect-free intent models that validate against available state.

## Goal

Add playback-facing intent models, renderer selection intent models, and public automation intent models. Implement deterministic local preview/validation services that check intents against `QueueState` and `NowPlayingState` without executing playback, resolving streams, calling providers, or using Android APIs.

## Non-goals

- Real playback execution.
- Real playback engine.
- Stream resolution or stream handles.
- Provider integration or direct provider calls.
- Direct Navidrome, Jellyfin, Emby, or any provider internals.
- Anchor provider internals or Anchor CLI integration.
- Android SDK, Kotlin, Java, or Gradle code.
- Media3/ExoPlayer implementation.
- Real MediaSession implementation.
- Android Auto implementation.
- UI, screens, navigation, or player code.
- Offline/cache behavior.
- Smart playlist logic.
- Filesystem traversal.
- Network behavior.

## Actors

- **App/Player consumer**: Future UI or player layer that reads intent previews and selects allowed operations.
- **Automation client**: External or internal client that sends structured automation intents.
- **Aria Core developer**: Writes services that validate and preview intents.

## Functional requirements

### FR1: Playback intent contracts

- Define `PlaybackIntent` with intent type, queue context, and target parameters.
- Define `PlaybackIntentType` enumerating play, pause, resume, stop, skip_next, skip_previous, seek.
- Define `PlaybackIntentResult` as a structured result with allowed/blocked/unavailable status.
- Define `PlaybackCommandPreview` as a lightweight preview of what would happen.
- Define `PlaybackIntentValidationIssue` for structured validation failures.
- Define `PlaybackBlockedReason` for blocked/unavailable reasons.
- Define `SeekTarget` for seek position with optional duration reference.
- Define `SkipDirection` enumerating next/previous.

### FR2: Renderer boundary contracts

- Define `RendererId` and `RendererRef` for renderer identity and reference.
- Define `RendererType` enumerating output types (phone, usb_dac, bluetooth, remote).
- Define `RendererAvailabilityState` for available/unavailable/disconnected states.
- Define `RendererCapabilitySummary` for capability metadata.
- Define `RendererSelectionIntent` for selecting a renderer.
- Define `RendererSelectionResult` for selection outcomes.

### FR3: Automation intent contracts

- Define `AutomationIntent` with type, source, and parameters.
- Define `AutomationIntentType` enumerating public automation operations.
- Define `AutomationIntentSource` to identify the caller.
- Define `AutomationIntentResult` with structured outcome.
- Define `AutomationSafetyLevel` for safe/unsafe/boundary classifications.

### FR4: Deterministic preview/validation services

- `PlaybackIntentService` must preview and validate playback intents against `QueueState` and `NowPlayingState`.
- `RendererIntentService` must validate renderer selection without accessing real renderers.
- `AutomationIntentService` must validate automation intents and return safe results.
- Services must be local, deterministic, and side-effect-free.

### FR5: Blocked/unavailable handling

- Pause/resume/stop/seek must return unavailable when `NowPlayingState` is idle.
- Seek must validate position bounds (non-negative, not exceeding known duration).
- Play must be blocked when current media is unavailable.
- Renderer selection must return unavailable when the renderer is unavailable.
- Unsupported capabilities must block without side effects.

### FR6: Intent validation against QueueState and NowPlayingState

- Play availability depends on queue having a current playable item.
- Skip next/previous respects queue bounds.
- Seek validates against known duration when available.

## Non-functional requirements

- NFR1: All models must be `frozen=True` dataclasses or enums.
- NFR2: All services must return `AriaResult`.
- NFR3: No imports of `requests`, `httpx`, `aiohttp`, `socket`, `urllib`.
- NFR4: No imports of `android`, `androidx`, Media3, ExoPlayer.
- NFR5: No imports of anchor internals or provider internals.
- NFR6: No filesystem traversal (`os.walk`, `glob.glob`, `scandir`).
- NFR7: No real playback, streaming, or audio execution.
- NFR8: Tests must be deterministic and offline.
- NFR9: Serialization must be safe via `safe_serialize`.

## Canonical Examples

### CE1: Idle state blocks pause

**Given** now-playing state is idle (no current item)
**When** pause intent is previewed
**Then** Aria returns a safe unavailable result and no playback occurs.

### CE2: Valid queue enables play preview

**Given** a queue has a current playable item at position 0
**When** play intent is previewed
**Then** Aria returns an allowed intent preview without starting playback.

### CE3: Unavailable media blocks play

**Given** current media is unavailable (queue item with UNAVAILABLE availability)
**When** play intent is requested
**Then** Aria returns blocked/unavailable reason safely.

### CE4: Invalid seek rejected

**Given** seek position is negative or beyond duration
**When** seek intent is validated
**Then** Aria returns validation failure.

### CE5: Unavailable renderer blocks selection

**Given** a renderer is unavailable
**When** renderer selection is requested
**Then** Aria returns a safe unavailable result.

### CE6: Unsupported capability blocks intent

**Given** renderer capability does not support a requested action
**When** the intent is previewed
**Then** Aria blocks it without side effects.

### CE7: Automation intent validation

**Given** an automation caller requests a public intent
**When** the intent is validated
**Then** Aria returns a structured result without executing provider/platform logic.

### CE8: Future UI consumes Aria Core models

**Given** UI needs playback controls later
**When** it consumes playback intents
**Then** it uses Aria Core models and does not call Android/player/provider directly.

## Edge cases

- Empty queue with no items: all playback intents return blocked/unavailable.
- Queue with items but no current position: play is allowed on first item; stop/pause/seek are unavailable.
- Skip next when at last item with repeat OFF: returns boundary exceeded.
- Skip previous when at first item: returns boundary exceeded.
- Seek to exact end boundary (position == duration): accepted for post-playback state.
- Concurrent intent previews: deterministic and idempotent.
- Renderer list is empty: selection returns unavailable.
- Automation intent from unknown source: returned as unsafe.
- Default model values: safe, no hidden side effects.
- Serialization round-trip: safe_serialize produces valid JSON.
- QueueState with PARTIALLY_UNAVAILABLE availability and current item is available: play is allowed.
- QueueState with UNAVAILABLE availability and no items: play is blocked.

## Acceptance criteria

1. `PlaybackIntent`, `PlaybackIntentType`, `PlaybackIntentResult`, `PlaybackCommandPreview`, `PlaybackIntentValidationIssue`, `PlaybackBlockedReason`, `SeekTarget`, `SkipDirection` are defined as frozen dataclasses/enums.
2. `RendererId`, `RendererRef`, `RendererType`, `RendererAvailabilityState`, `RendererCapabilitySummary`, `RendererSelectionIntent`, `RendererSelectionResult` are defined as frozen dataclasses/enums.
3. `AutomationIntent`, `AutomationIntentType`, `AutomationIntentSource`, `AutomationIntentResult`, `AutomationSafetyLevel` are defined as frozen dataclasses/enums.
4. `PlaybackIntentService` exists with preview and validate methods.
5. `RendererIntentService` exists with selection validation.
6. `AutomationIntentService` exists with intent validation.
7. All 8 canonical examples have corresponding tests.
8. All edge cases have test coverage.
9. No real playback, streaming, provider integration, Android, UI, offline/cache, smart playlist, filesystem, or network code exists.
10. All exports are intentional and present in `__init__.py` and `__all__`.
11. `current.md` and `delta.md` are updated.
12. Tests pass with `python3 -m pytest`.
13. Repository contamination check is clean.

## Open questions

- None. All boundary decisions are defined in this spec and in `scope-boundaries.md`.
