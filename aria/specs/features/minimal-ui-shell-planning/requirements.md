# Requirements

## Status

Draft for Bloco 5 — Minimal UI Shell Planning (spec/planning only).

## Problem

Aria Core currently has all control-plane contracts, fake-first services, a dry-run Anchor adapter, and nine Android/player boundary bridge protocols. Blocos 0–4 are implemented and audited. However, there is no documented plan for how a future minimal UI/app shell should consume Aria Core as a thin adapter.

Without a formal UI shell planning spec, future UI implementation risks:
- coupling directly to Anchor, Navidrome, or provider internals instead of going through Aria Core;
- duplicating control-plane, playback, diagnostics, or permission logic in UI code;
- violating the thin-adapter architecture where Aria Core is the app/player-facing core and UI is a display layer only;
- mixing screen/view state with core domain state;
- bypassing boundary contracts from Bloco 4 for playback, storage, MediaSession, etc.

## Goal

Define an implementation-ready planning spec for a future minimal UI/app shell that consumes Aria Core as a thin adapter. This spec defines:
- how future UI/app shell consumes Aria Core;
- what must stay inside Aria Core and must not leak into UI;
- what belongs to the future UI adapter;
- what the future UI must not call directly;
- expected app shell boundaries;
- expected screen/view model inputs, without implementing screens;
- how diagnostics/readiness/status data should be presented as app-facing state;
- how Android/player boundary contracts from Bloco 4 are consumed later;
- how future UI avoids direct Anchor/Navidrome/provider coupling.

No React, Compose, UI framework, Android SDK, Kotlin, Java, Gradle, screens, navigation, player UI, playback engine, Media3/ExoPlayer, MediaSession, Android Auto, queue, now playing, offline/cache, or real Android integration code exists in this spec.

## Non-goals

- No React/Compose/UI implementation.
- No Android SDK, Kotlin, Java, or Gradle files.
- No screens, navigation, or player UI.
- No real playback engine (Media3/ExoPlayer).
- No real MediaSession or Android Auto implementation.
- No queue or now playing engine implementation.
- No offline/cache/download implementation.
- No source code changes to `src/noqlen_aria/**`.
- No test file changes.
- No `pyproject.toml` modifications.
- No real Anchor, Navidrome, Jellyfin, Emby, or provider integration.
- No mutation testing policy or Pact Broker setup.
- No Android Auto implementation.
- No real storage/permission UX.

## Actors

- Future UI/adapter implementer (developer).
- Future thin Android player adapter (Kotlin/Java app).
- Future thin iOS adapter (Swift/UIKit app).
- Future thin desktop adapter (React/Electron or similar).
- Aria Core maintainer.
- Future implementation agents.

## Functional requirements

### FR-10: UI Shell Architecture Definition

- FR-10a: Define the thin-adapter architecture boundary: UI shell is a display layer with no business logic.
- FR-10b: Define that UI shell views map directly to Aria Core snapshots and state types.
- FR-10c: Define that UI shell actions delegate to Aria Core services and boundary contracts.
- FR-10d: Define the maximum thickness of the UI shell: view rendering, user input capture, and delegation only.

### FR-20: App-Facing State Contract

- FR-20a: Define `AppShellState` as a composite snapshot of all app-facing state that a UI shell may consume.
- FR-20b: `AppShellState` must be composed from existing Aria Core types: `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState`, `PermissionState`, `StorageAccessState`.
- FR-20c: `AppShellState` must include optional `AndroidBoundarySnapshot` from Bloco 4 for future Android adapter consumption.
- FR-20d: `AppShellState` must be serialization-safe (stdlib types only) for cross-layer transport.
- FR-20e: UI shell must consume `AppShellState` immutably; state mutations go through Aria Core services.

### FR-30: UI Shell Input/Delegate Contract

- FR-30a: Define `AppShellInput` as an enum or union type for all user-facing actions the UI shell may emit.
- FR-30b: `AppShellInput` must include lifecycle actions: `INITIALIZE`, `SHUTDOWN`, `RESET` (mapped from `LifecycleIntent`).
- FR-30c: `AppShellInput` must include diagnostic actions: `REFRESH_STATUS`, `COLLECT_DIAGNOSTICS`, `ASSESS_READINESS`.
- FR-30d: `AppShellInput` must include permission/storage actions: `CHECK_PERMISSION`, `CHECK_STORAGE`.
- FR-30e: `AppShellInput` must include playback actions (delegated through boundary contracts): `PLAYBACK_COMMAND` with a payload referencing Bloco 4 `PlaybackCommand`.
- FR-30f: `AppShellInput` action-to-service routing must stay in Aria Core, not in UI shell.

### FR-40: Anti-Coupling Rules

- FR-40a: UI shell must never call Anchor directly.
- FR-40b: UI shell must never call Navidrome directly.
- FR-40c: UI shell must never call provider internals.
- FR-40d: UI shell must never bypass `ControlClient` to reach server/library state.
- FR-40e: UI shell must never construct its own playback logic, queue logic, or now-playing logic.
- FR-40f: UI shell must never call Android boundary bridges directly; it delegates through Aria Core adapter layer.
- FR-40g: All app-to-core communication flows through a single `AppShellAdapter` entry point.

### FR-50: Screen/ViewModel Input Planning

- FR-50a: Define expected view models for each planned screen type without implementing screens.
- FR-50b: Status screen view model: maps from `ServerViewState` to display-ready fields (connected, server version, latency ms, last error text).
- FR-50c: Diagnostics screen view model: maps from `DiagnosticsViewState` to display-ready warning list with severity/action hints.
- FR-50d: Readiness screen view model: maps from `ReadinessViewState` to composite pass/fail indicators.
- FR-50e: Permission/storage screen view model: maps from `PermissionState` + `StorageAccessState` + Bloco 4 `AndroidStorageBridge` snapshot.
- FR-50f: All view models must be derived from app-facing state only; no raw provider data in view models.
- FR-50g: View model inputs must be defined as Python dataclasses for future cross-platform consumption.

### FR-60: Boundary Contract Consumption Plan

- FR-60a: Define how `AppShellAdapter` consumes Bloco 4 `PlaybackEngineBridge` for playback commands and state.
- FR-60b: Define how `AppShellAdapter` consumes Bloco 4 `MediaSessionBridge` for transport controls.
- FR-60c: Define how `AppShellAdapter` consumes Bloco 4 `AndroidStorageBridge` for storage permission state.
- FR-60d: Define how `AppShellAdapter` consumes Bloco 4 `AndroidAutoBridge`, `ForegroundServiceBridge`, `AppLifecycleBridge`, `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge`.
- FR-60e: All bridge consumption must happen inside Aria Core adapter; UI shell sees sanitized state only.

### FR-70: Diagnostics/Readiness Presentation Rules

- FR-70a: Diagnostics data presented to UI must be sanitized: no raw stack traces, no internal error codes, no secrets.
- FR-70b: `AriaWarning` messages are display-ready strings; UI shell may render them directly.
- FR-70c: `AriaError` codes are for logging and internal routing; UI shell should consume error messages, not error codes.
- FR-70d: Readiness composite `all_ready` is a single boolean for UI shell primary indicator.
- FR-70e: Individual readiness sub-states (`server.connected`, `library.available`, `control_configured`) are available for granular UI display.

### FR-80: Platform-Agnostic UI Shell Vocabulary

- FR-80a: All view model types use platform-agnostic Python dataclasses.
- FR-80b: No platform-specific UI concepts (Android Context, UIKit UIView, React component, etc.) in Aria Core types.
- FR-80c: UI shell adapters per platform translate view models into native UI components.
- FR-80d: Interaction between UI shell and Aria Core uses a single `AppShellAdapter` facade — no direct service calls from UI.

### FR-90: Spec Completeness Requirements

- FR-90a: Spec must define the `AppShellAdapter` protocol interface.
- FR-90b: Spec must define the `AppShellState` composite type.
- FR-90c: Spec must define the `AppShellInput` action type.
- FR-90d: Spec must define per-screen view model dataclasses for status, diagnostics, readiness, and permissions.
- FR-90e: Spec must include anti-coupling rules as a dedicated section.
- FR-90f: Spec must define how boundary contracts from Bloco 4 flow through the adapter.

## Canonical Examples

### CE-01: UI consumes server status through Aria Core only

Given a future thin UI shell
And an `AppShellAdapter` wired to Aria Core services
When the UI shell requests server status by calling `adapter.get_app_shell_state()`
Then the returned `AppShellState` contains a `ServerViewState` with `connected`, `server_url`, `server_version`, `latency_ms`
And the UI shell never calls Anchor directly
And the UI shell never calls Navidrome directly
And the UI shell never calls `ControlClient.get_server_state()` directly

### CE-02: UI renders diagnostics from sanitized app-facing data

Given a future thin UI shell
And `DiagnosticsService.collect()` has populated warnings
When the UI shell requests diagnostics via `adapter.collect_diagnostics()`
Then the returned `DiagnosticsViewState` contains display-ready `AriaWarning` messages
And no raw stack traces appear in the warning messages
And no internal error codes are exposed that require interpretation
And the UI shell does not access `ControlClient` internals

### CE-03: UI delegates playback commands through boundary contracts

Given a future thin UI shell with playback controls (play, pause, skip)
And an `AppShellAdapter` wired to Bloco 4 `PlaybackEngineBridge`
When the user taps the play button
Then the UI shell emits `AppShellInput.PLAYBACK_COMMAND(command=PlaybackCommand.PLAY)`
And `AppShellAdapter` routes this to `PlaybackEngineBridge.send_command(PlaybackCommand.PLAY)`
And the UI shell does not implement playback logic
And the UI shell does not call Media3/ExoPlayer directly

### CE-04: UI displays Android storage permission state

Given a future thin Android UI shell
And `AppShellAdapter` wires Bloco 4 `AndroidStorageBridge`
When the UI shell requests storage permission state via `adapter.get_app_shell_state()`
Then `AppShellState` includes `PermissionState` and `StorageAccessState` from Aria Core
And optionally includes `AndroidBoundarySnapshot.storage_status` from Bloco 4
And the UI shell never calls Android `Context.checkSelfPermission` directly
And the UI shell delegates platform permission requests to a future Android adapter

### CE-05: UI shell lifecycles through Aria Core intents

Given a future thin UI shell starting up
When the UI shell emits `AppShellInput.INITIALIZE` via `adapter.send_input(INITIALIZE)`
Then `AppShellAdapter` maps this to `LifecycleIntentService.validate("initialize")` and `ControlClient.send_lifecycle_intent(LifecycleIntent.INITIALIZE)`
And the UI shell does not construct its own initialization logic
And the UI shell does not call Anchor startup commands directly

### CE-06: Thin UI rule — UI has no business logic

Given a future UI shell screen rendering diagnostics
When the screen receives `DiagnosticsViewState` from the adapter
Then the screen renders warnings as text items directly
And the screen does not interpret warning codes
And the screen does not filter or transform warnings
And the screen does not trigger service calls based on warning content
And all interpretation and filtering stays in Aria Core services

### CE-07: Anti-coupling — UI never calls Anchor

Given a future thin UI shell
And an `AnchorControlClient` adapter exists in `src/noqlen_aria/anchor_adapter.py`
When the UI shell needs server connectivity status
Then the UI shell calls `adapter.get_app_shell_state()` (AppShellAdapter)
And `AppShellAdapter` internally calls `ControlClient.get_server_state()`
Which routes to `AnchorControlClient.get_server_state()` internally
And the UI shell has zero imports from `noqlen_aria.anchor_adapter`
And the UI shell has zero knowledge of Anchor module existence

### CE-08: UI consumes composite Android boundary snapshot

Given a future thin Android UI shell
And `AppShellAdapter` consumes all nine Bloco 4 bridge implementations
When the UI shell requests full state via `adapter.get_app_shell_state()`
Then `AppShellState` optionally contains `AndroidBoundarySnapshot` with `playback_engine`, `media_session`, `storage_status`, `foreground_service`, `app_lifecycle`, and `headset_connected`
And each sub-state is a serialization-safe dataclass
And the UI shell renders each sub-state in the appropriate screen/view model
And the UI shell never calls any bridge protocol directly

## Non-functional requirements

- NFR01: This spec is planning/documentation only. Zero source code, test code, or implementation artifacts created.
- NFR02: All proposed types use Python standard library only (`dataclasses`, `enum`, `typing`).
- NFR03: No runtime dependencies on Android SDK, Kotlin, Java, Gradle, React, Compose, or any UI framework.
- NFR04: All public names must be explicit, stable, and documented in English.
- NFR05: Proposed `AppShellState`, `AppShellInput`, and view model types must not leak Aria Core internals.
- NFR06: Proposed `AppShellAdapter` must be a single entry-point facade for all UI-to-Core communication.
- NFR07: All proposed view model types must be serialization-safe.
- NFR08: Anti-coupling rules must be explicit and verifiable by grep/inspection.
- NFR09: Bloco 4 boundary contracts must be consumed through the adapter layer, not directly by UI.
- NFR10: Spec must be platform-agnostic in design; per-platform UI adapters are future concerns.

## Edge cases

- EC01: UI shell requests state before Aria Core is initialized (adapter returns safe defaults, `ServerViewState.connected=False`).
- EC02: UI shell sends a playback command without a loaded track (adapter returns `AriaResult.ok=False` with safe error).
- EC03: UI shell requests `AndroidBoundarySnapshot` on a non-Android platform (adapter returns `None` or platform-specific unavailable marker).
- EC04: UI shell sends rapid repeated inputs (adapter queues or debounces; UI shell does not implement queue logic).
- EC05: UI shell renders a screen while underlying data changes (UI shell re-renders from new state; does not cache or diff state).
- EC06: `DiagnosticsViewState` contains zero warnings (UI shell renders an "All good" or empty state).
- EC07: `AppShellAdapter` wiring fails (adapter returns failed `AriaResult`; UI shell renders error state from adapter, not from raw error internals).
- EC08: UI shell on Android needs to request runtime permission (UI shell emits `AppShellInput.CHECK_PERMISSION`; adapter returns current state; actual permission dialog is delegated to future Android adapter).
- EC09: UI shell on iOS does not use `AndroidStorageBridge` (adapter returns `AndroidBoundarySnapshot` as `None`; iOS-specific boundaries are a future concern).
- EC10: `AppShellState` grows over time as more Aria Core services are added (dataclass fields are all optional; new fields are additive and backward-compatible).

## Acceptance criteria

- AC01: `aria/specs/features/minimal-ui-shell-planning/` contains `requirements.md`, `design.md`, `tasks.md`, and `review.md`.
- AC02: No source code, test code, `pyproject.toml`, Android files, Kotlin files, Java files, Gradle files, React/Compose files created or modified.
- AC03: Spec clearly states "this is planning only — do not implement UI."
- AC04: Spec defines `AppShellAdapter` protocol, `AppShellState` composite, `AppShellInput` action type, and per-screen view model types.
- AC05: Spec includes anti-coupling rules explicitly documented.
- AC06: Spec includes Canonical Examples using Given/When/Then format (at least 6).
- AC07: Spec includes Behavior Budget.
- AC08: Spec includes Test Risk Matrix.
- AC09: Context package (Standard) is documented.
- AC10: Delta update checklist is present.
- AC11: Existing validation commands pass without regression.
- AC12: Repository contamination check is clean.
- AC13: Spec is committed with `docs(spec): add minimal UI shell planning spec`.

## Open questions

- OQ01: Should `AppShellState` include `AndroidBoundarySnapshot` as a required or optional field? (Design: optional; non-Android platforms return `None`.)
- OQ02: Should `AppShellInput` use a flat enum or a discriminated union with per-action payloads? (Design: enum for action type + optional kwargs dict for payloads; keeps adapter routing simple.)
- OQ03: Should per-screen view model types be in a separate module from `AppShellAdapter`? (Design: proposed `src/noqlen_aria/app_shell.py` for adapter + state; view models may be co-located or in a future `src/noqlen_aria/view_models.py`.)
- OQ04: How does the UI shell consume `AppShellState` reactively (polling vs push)? (Design: adapter provides pull-based `get_app_shell_state()`; future blocks may add callback-based reactivity.)
- OQ05: Should anti-coupling rules be enforced at runtime or by convention? (Design: convention enforced by architecture review and grep/inspection checks; future blocks may add runtime guards.)
- OQ06: Should `AppShellAdapter` be a Protocol or a concrete class? (Design: Protocol for testability; concrete `FakeAppShellAdapter` for future tests.)
- OQ07: Is `AppShellInput` the same across all platforms (Android, iOS, desktop)? (Design: yes; platform-specific actions are handled by platform-specific adapter implementations behind the same protocol.)
