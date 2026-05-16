# Design

## Summary

Bloco 13 adds three groups of intent models (playback, renderer, automation) and three deterministic local services that preview/validate intents against existing `QueueState` and `NowPlayingState` without executing playback, resolving streams, or calling providers/Android APIs.

## Context files read

- `AGENTS.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/scope-boundaries.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/architecture.md`
- `docs/safety.md`
- `aria/specs/_template/**`
- `aria/specs/features/now-playing-foundation/review.md`
- `aria/specs/features/queue-foundation/review.md`
- `src/noqlen_aria/now_playing.py`
- `src/noqlen_aria/queue.py`
- `src/noqlen_aria/contracts.py`

## Context package

Standard. See `aria/context/context-packages.md`.

## Existing project context

- Blocos 8-12 are implemented: `MediaSourceClient`, `LibraryService` (browse/search/filters/activity/favorites), `QueueService`, `NowPlayingService`.
- `QueueState` carries items, current position, repeat mode, shuffle state, and availability.
- `NowPlayingState` carries status (IDLE/READY/PAUSED/UNAVAILABLE/RESUMABLE), item, playback availability, position snapshot, and unavailable media state.
- `AriaResult[T]` is the standard result wrapper.
- `safe_serialize` and `sanitize_text` are available for safe output.

## Files to create

- `src/noqlen_aria/playback_intents.py` — playback, renderer, and automation intent models plus three services.
- `tests/test_playback_renderer_automation_intents.py` — comprehensive tests.
- `aria/specs/features/playback-renderer-automation-intents/requirements.md`
- `aria/specs/features/playback-renderer-automation-intents/design.md`
- `aria/specs/features/playback-renderer-automation-intents/tasks.md`
- `aria/specs/features/playback-renderer-automation-intents/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py` — add intentional exports.
- `tests/test_mvp_hardening.py` — update expected exports.
- `aria/context/current.md` — update Bloco 13 status.
- `aria/context/delta.md` — record changes.

## Files that must not be touched

- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/queue.py`
- `src/noqlen_aria/now_playing.py`
- `src/noqlen_aria/media_source.py`
- `src/noqlen_aria/library.py`
- `src/noqlen_aria/anchor_adapter.py`
- `src/noqlen_aria/android_boundaries.py`
- `src/noqlen_aria/cli.py`
- All existing test files except `test_mvp_hardening.py`
- All existing spec files
- All docs files except possibly `docs/handoff.md`

## Data flow

```
App/Player UI → PlaybackIntent → PlaybackIntentService.preview()
  → reads NowPlayingState + QueueState
  → returns PlaybackIntentResult (allowed/blocked/unavailable)

Automation client → AutomationIntent → AutomationIntentService.validate()
  → checks source safety level
  → maps to playback intent internally
  → returns AutomationIntentResult

Renderer selector → RendererSelectionIntent → RendererIntentService.validate_selection()
  → checks renderer availability
  → returns RendererSelectionResult
```

All services are local, deterministic, and side-effect-free. No stream resolution. No provider calls. No Android APIs.

## Error handling

- Invalid intent type: return `AriaResult(ok=False, error=AriaError(...))`.
- Intent blocked by state: return `AriaResult(ok=True, data=PlaybackIntentResult(allowed=False, ...))`.
- Unavailable renderer: return `AriaResult(ok=True, data=RendererSelectionResult(available=False, ...))`.
- Unknown automation source: return `AriaResult(ok=True, data=AutomationIntentResult(safety=UNSAFE, ...))`.

## Security considerations

- All intent models are frozen, immutable, and serializable.
- No secrets, credentials, or provider internals in models.
- Automation intents are validated for source safety level.
- All output is safe-serializable via `safe_serialize`.
- No network or filesystem access in any service.

## Provider boundary considerations

- This block does not call `MediaSourceClient` for stream resolution.
- This block does not call providers directly.
- This block does not access Anchor provider internals.
- This block does not call Navidrome, Jellyfin, Emby, or any provider.

## Renderer boundary considerations

- Renderer models are abstract identity and capability contracts only.
- No real renderer implementation.
- No audio driver, USB DAC, Bluetooth, or remote renderer access.
- `RendererType` is a vocabulary enum, not a real device enumeration.

## Automation boundary considerations

- Automation intents are public/core intent models, not UI automation scripts.
- `AutomationIntentSource` identifies the caller without requiring authentication.
- `AutomationSafetyLevel` classifies intents as safe, boundary, or unsafe.
- No platform-specific automation (no Android Auto, no MediaSession).

## Intent validation rules

### Playback intent validation

| State | Play | Pause | Resume | Stop | Skip Next | Skip Previous | Seek |
|-------|------|-------|--------|------|-----------|---------------|------|
| Idle, no item | blocked | unavailable | unavailable | unavailable | blocked | blocked | blocked |
| Idle, has item | allowed | unavailable | unavailable | unavailable | depends on queue bounds | depends on queue bounds | blocked (no position ref) |
| Ready | allowed | allowed | allowed | allowed | depends on queue bounds | depends on queue bounds | allowed |
| Paused | allowed | unavailable | allowed | allowed | depends on queue bounds | depends on queue bounds | allowed |
| Unavailable | blocked | unavailable | unavailable | unavailable | depends on queue bounds | depends on queue bounds | blocked |
| Resumable | allowed | blocked | allowed | allowed | depends on queue bounds | depends on queue bounds | allowed |

Skip Next is blocked when at last item with repeat OFF. Skip Previous is blocked when at first item.
Seek is blocked when position < 0 or (duration known and position > duration).

### Renderer selection validation

- Renderer available: allowed.
- Renderer unavailable: blocked/unavailable.
- Renderer capability mismatch: blocked with reason.

### Automation intent validation

- Public automation source with safe type: allowed.
- Unknown automation source: unsafe.
- Automation intents are mapped to internal playback intents for validation.

## Dependencies

- `noqlen_aria.contracts`: `AriaResult`, `AriaError`, `safe_serialize`.
- `noqlen_aria.queue`: `QueueState`, `QueueItem`, `QueueAvailabilityState`, `QueueRepeatMode`.
- `noqlen_aria.now_playing`: `NowPlayingState`, `NowPlayingStatus`, `PlaybackPositionSnapshot`, `PlaybackAvailabilityState`, `PlaybackAvailabilityReason`.
- Python stdlib: `dataclasses`, `enum`.

No external dependencies. No `requests`, `httpx`, `aiohttp`, `android`, `Media3`.

## Behavior Budget

See `aria/context/behavior-budget.md`.

- **New behaviors**:
  - add playback intent models;
  - add renderer selection models;
  - add automation intent models;
  - add deterministic intent preview/validation service;
  - add blocked/unavailable handling.
- **Public API changes**:
  - expose only intentional playback/renderer/automation intent names.
- **Files allowed**:
  - `src/noqlen_aria/**`
  - `tests/**`
  - `aria/specs/features/playback-renderer-automation-intents/**`
  - `aria/context/current.md`
  - `aria/context/delta.md`
  - `docs/handoff.md`, only if a tiny status note is needed.
- **Tests required**:
  - play/pause/resume/stop/skip/seek intent validation;
  - blocked playback behavior;
  - unavailable media behavior;
  - invalid seek behavior;
  - renderer unavailable behavior;
  - renderer unsupported capability behavior;
  - automation intent validation;
  - no provider/playback/network/filesystem/Android behavior.
- **Dependencies**: none external.
- **Stop if**:
  - real playback becomes necessary;
  - stream resolution becomes necessary;
  - Android/Media3/ExoPlayer/MediaSession becomes necessary;
  - provider integration becomes necessary;
  - offline/cache work becomes necessary.

## Risk classification

High. This block implements safety-critical intent validation and boundary enforcement. Reference `aria/context/test-risk-matrix.md`.

## Rollback strategy

- `git checkout -- src/noqlen_aria/__init__.py tests/test_mvp_hardening.py` and remove `src/noqlen_aria/playback_intents.py` plus `tests/test_playback_renderer_automation_intents.py`.
- Revert `aria/context/current.md` and `aria/context/delta.md`.

## Risks

- Intent validation rules may need refinement when real playback or stream execution is added (future).
- Renderer capability model may need expansion when real renderers exist (Bloco 16 or later).
- Automation safety classification is a starting point; future authentication/authorization is not in scope.

## Validation plan

- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- `git diff --check`
- Repository contamination check
- Provider/network/filesystem/Android search checks
- Offline/cache/smart-playlist search checks
- Confirm no real playback, no stream resolution, no provider integration
