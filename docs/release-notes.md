# Release Notes — Aria Core MVP

tag: v0.1.0 (local tag complete)
date: 2026-05-16

## Summary

Noqlen Aria Core MVP is tagged locally as `v0.1.0` for the modular app/player-facing core of a music player. These release notes cover control-plane contracts, source-agnostic services, a dry-run/offline Anchor adapter, Android/player boundary vocabulary, minimal UI shell planning artifacts, and MVP hardening with safe serialization and intentional public exports.

MVP scope is Blocos 0-7. Post-core feature expansion starts after `v0.1.0`, is tracked as Blocos 8-23, and remains backlog.

## What Is Included

### Bloco 0 — Bootstrap / Workflow
- Repository structure and Aria Workflow contract.
- Public docs for architecture, safety, Anchor integration, Android boundaries, and UI shell boundary.
- Aria context files, spec templates, review templates, and minimal role prompts.
- Minimal safe local CLI with `doctor` command.

### Bloco 1 — Core Contracts
- Source-agnostic `ControlClient` protocol for control-plane behavior.
- `FakeControlClient` for fake-first development and testing.
- Safe result primitives: `AriaResult[T]`, `AriaError`, `AriaWarning`.
- View states: `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState`.
- Platform-agnostic `PermissionState` and `StorageAccessState`.
- `LifecycleIntent` enumeration for control-plane actions.

### Bloco 2 — Control Services Fake-First
- `StatusService`, `DiagnosticsService`, `ReadinessService`, `LifecycleIntentService`, `ResultMappingService`.
- `LifecycleIntentPreview` for safe lifecycle preview without execution.
- Deterministic failure injection and value overrides in `FakeControlClient`.

### Bloco 3 — Anchor Adapter Dry-Run
- `AnchorControlClient` — a dry-run/offline adapter implementing `ControlClient`.
- `AnchorResultMapper` for mapping Anchor-style results into Aria contracts.
- Lazy optional `noqlen_anchor` import with safe degraded behavior when unavailable.
- Lifecycle dry-run previews supported; apply-mode operations remain blocked.

### Bloco 4 — Android/Player Boundary Contracts
- 9 bridge protocols: `PlaybackEngineBridge`, `MediaSessionBridge`, `AndroidStorageBridge`, `AndroidAutoBridge`, `ForegroundServiceBridge`, `AppLifecycleBridge`, `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge`.
- Supporting types: 12+ enum types, 15+ dataclasses, composite `AndroidBoundarySnapshot`.
- 9 deterministic fake implementations for testing.
- Abstract vocabulary only — no Android SDK integration.

### Bloco 5 — Minimal UI Shell Planning Artifacts
- `AppShellAdapter` protocol and `AppShellState` composite.
- Anti-coupling rules: UI renders Aria Core state, emits Aria Core intents, never calls providers directly.
- Documentation only — no UI implementation.

### Bloco 6 — Aria MVP Hardening
- Intentional public exports with `__all__` in `noqlen_aria`.
- `safe_serialize` helper for JSON-compatible, sanitized output.
- `sanitize_text` helper for user-facing safe messages.
- Safer Anchor adapter exception handling.
- Hardening tests covering public exports, safe serialization, sanitized errors, optional Anchor absence, and dry-run/apply safety.
- 368 tests passing.

### Bloco 7 — Release Preparation
- Release readiness checklist, release notes, public API surface summary, safety summary, post-core backlog, and handoff updates.
- Local tag `v0.1.0` exists; no package publishing action is documented here.

## Safety Boundaries

- No real music-library access.
- No direct Navidrome, Jellyfin, Emby, or provider calls.
- No Anchor provider internals or Anchor CLI integration.
- No Android SDK, Kotlin, Java, Gradle, Compose, or UI code.
- No Media3, ExoPlayer, MediaSession, Android Auto, playback engine, queue, now playing, offline/cache, or storage mutation.
- No secrets, credentials, local paths, raw logs, or personal data in release artifacts.
- Anchor remains an optional dry-run adapter. Missing Anchor packages return safe degraded results.
- Lifecycle apply operations remain blocked/unavailable.
- All serialized output is sanitized and safe for user-facing display.
- Tests are local, offline, fake-first, and deterministic (368 passing).

## Architecture Summary

```
Future UI/App/Player -> Aria Core -> contracts/adapters -> providers/backends
```

Aria Core owns contracts, states, services, policies, capabilities, fakes, mappers, adapters, snapshots, safe serialization, and tests.

Anchor is one optional `ControlClient` adapter, not the center of Aria. Aria depends on contracts, not Anchor internals.

## Known Limitations

- Local tag `v0.1.0` exists. Package publishing is not documented as complete.
- The `AnchorControlClient` is dry-run/offline only. Real lifecycle apply operations are blocked.
- Android/player boundary contracts are abstract vocabulary and fake implementations only. No real Android SDK, MediaSession, playback, or auto implementation exists.
- No real Navidrome, Jellyfin, Emby, or provider integration exists.
- `MediaSourceClient` and the full library/search layer are future work.
- Queue, now playing, offline/cache, stream quality, output/renderer, and playback policy layers are future work.
- The CLI is a minimal smoke/doctor tool. No management, configuration, or control-plane CLI commands exist.

## Post-Core Backlog

See `docs/post-core-backlog.md` for the full post-core roadmap.

Key future areas:
- Media source foundation and `MediaSourceClient` (Bloco 8)
- Library browse/search for artists, albums, songs, folders, playlists, and genres (Bloco 9)
- Library filters, recently added, recently played, and favorites (Bloco 10)
- Queue, repeat/shuffle, predictable queue behavior, multiple queues, and safe errors (Bloco 11)
- Now playing, playback availability, resumable state, and unavailable media state (Bloco 12)
- Playback, renderer selection, and public automation intents (Bloco 13)
- Offline/cache/storage policy, cache cleanup, pending sync/cache states, and storage pressure (Bloco 14)
- Stream quality, transcoding, network quality, and offline quality policy (Bloco 15)
- Gapless, loudness/ReplayGain awareness, crossfade, bit-perfect, and output/device capability state (Bloco 16)
- Profiles, preferences, backup, and restore for Aria config/state (Bloco 17)
- Smart playlists, smart mixes, saved filters, and rule-based playlist planning (Bloco 18)
- State snapshots, API snapshot behavior, and fake end-to-end flows (Bloco 19)
- Provider extension readiness through generic provider/source abstractions, without direct provider internals or assuming current Anchor multi-provider support (Bloco 20)
- Android real integration planning for media controls, Bluetooth/headset, Android Auto, foreground service, and widgets (Bloco 21)
- Android shell handoff for the separate future app/UI (Bloco 22)
- Post-core release prep and next steps for the real app (Bloco 23)

All future blocks require dedicated specs before implementation.

## Quality Gates

- Blocos 1-3 formal audit: passed.
- Blocos 4-6 formal audit: passed.
- 368 tests, all passing.
- Repository contamination check: clean.
- All search checks (Android SDK, forbidden implementations, apply-mode, provider/CLI integration): clean.
