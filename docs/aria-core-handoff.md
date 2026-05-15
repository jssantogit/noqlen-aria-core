# Noqlen Aria Core Handoff

## Status

- Aria Bloco 0 bootstrap is complete.
- Aria Workflow exists.
- Bloco 0 audit should be complete before Bloco 1 implementation.
- Aria Core contracts are next, but only through spec first.
- This document is the local repository source of truth for future Aria work.

## Source of truth

This file replaces dependency on any chat-only uploaded handoff file.

Future agents must use repository files:

- `AGENTS.md`
- `aria/context/`
- `aria/review/`
- `aria/prompts/`
- `docs/aria-core-handoff.md`

## Ecosystem position

`Flux -> Forge -> Anchor -> Aria`

- Flux prepares, downloads, and stages music artifacts.
- Forge organizes the final music library.
- Anchor serves and controls local server/core operations.
- Aria orchestrates app/player-facing state and flows on top of stable cores.

## Product definition

- Noqlen Aria Core is the app/player-facing orchestration core.
- Aria Core is not the Android app.
- Aria Core is not UI.
- Aria Workflow is the development method, not the product.
- Future UI must be a thin adapter over Aria Core.

Expected future flow:

`Future UI/App/Player -> Aria Core -> ControlClient -> AnchorControlClient adapter -> Navidrome`

## What Aria Core should provide

- App-facing state models.
- Lifecycle intent models.
- Diagnostics/readiness presentation data.
- Result/error/warning mapping.
- Permission/storage state abstractions.
- Source-agnostic control client boundary (`ControlClient`).
- Fake-first testing support (`FakeControlClient`).
- Safe orchestration flows independent of UI.

## What Aria may consume from Anchor later

Likely future consumption surfaces:

- Anchor public API facade.
- Service factories.
- Diagnostics helpers.
- Readiness/safety summaries.
- Android integration report/plan helpers.
- Server status/health/lifecycle helpers.
- Config dry-run/render helpers.
- Structured result objects.

Exact Anchor callable names must be confirmed from the current Anchor public API during the future Anchor adapter block.

## What Aria must not do

- Must not bypass Anchor to control Navidrome directly.
- Must not call Anchor provider internals.
- Must not use Anchor CLI as app integration API.
- Must not mutate a real music library directly.
- Must not expose secrets, raw logs, or personal paths.
- Must not put orchestration logic in UI.
- Must not implement Android SDK/UI/player in early core blocks.
- Must not implement playback, queue, cache/offline, Android Auto, or MediaSession without dedicated specs.

## Future product context

Future planning only:

- Anchor control/status/diagnostics.
- Library navigation and search.
- Queues.
- Now playing.
- Playback refinement.
- Future cache/offline behavior.
- Android media controls as future boundary.
- Android Auto as future boundary.
- Permissions/storage UX as future boundary.

These are planning context only. These are not Bloco 0 or Bloco 1 implementation scope. These are not permission to implement UI, playback, queue, now playing, cache/offline, MediaSession, Android Auto, or storage/permission UX now. Each feature family requires a dedicated spec.

## Android player inspiration

Product inspiration only:

- Poweramp: audio polish, customization, EQ/DSP.
- Musicolet: local/offline UX and queues.
- Symfonium: server-client model, cache/offline, and mature Android UX.
- Plexamp: now playing polish, gapless, loudness, and pre-cache.
- VLC: robustness and compatibility.
- AIMP / foobar2000 / Neutron: playlists, ReplayGain, hi-res, and DSP.

This is not authorization to implement UI. This is not authorization to implement playback. This is not authorization to implement cache/offline. This is not authorization to implement DSP/EQ.

## Future architecture vocabulary

Future boundary names only:

- `PlaybackEngine`
- `MediaSessionBridge`
- `AndroidStorageBridge`
- `QueueService`
- `LibraryPresentationService`
- `OfflineCachePolicyService`
- `AudioCapabilitiesService`

These names are documentation vocabulary only for now. They must not become source code in Bloco 0 or spec-only tasks.

## Recommended development order

1. Bloco 0 — repository bootstrap and Aria Workflow.
2. Bloco 0 Audit — bootstrap/workflow/safety audit.
3. Bloco 1 Spec — Aria Core contracts spec.
4. Bloco 1 Implementation — contracts and fake client only.
5. Bloco 2 — build services on top of source-agnostic ControlClient boundary.
6. Bloco 3 — AnchorControlClient adapter, offline/dry-run only.
7. Bloco 4 — Android boundary contracts, no Android SDK.
8. Later — minimal UI shell only after stable core.

## Bloco 1 target

Planned Bloco 1 scope:

- `AriaResult`
- `AriaError`
- `AriaWarning`
- `ServerViewState`
- `LibraryViewState`
- `DiagnosticsViewState`
- `ReadinessViewState`
- `LifecycleIntent`
- `PermissionState`
- `StorageAccessState`
- `ControlClient` protocol (source-agnostic; Anchor is one future adapter)
- `FakeControlClient`

Bloco 1 must not implement real Anchor integration, UI, Android SDK, playback, queue, now playing, cache/offline, MediaSession, Android Auto, or storage/permission UX.

## Safety rules

- Dry-run before apply.
- Explicit apply for real operations later.
- Fake-first development.
- No real music library in tests.
- No real Navidrome in tests.
- No secrets.
- No personal paths.
- Sanitized output.
- No direct provider internals.
- No broad git add.
- No local tooling artifacts committed.

## Open questions

- How will Aria call Anchor later?
- Direct Python embedding?
- Local HTTP API?
- Bridge process?
- Separate local service?
- Platform-specific adapter?
- Will Aria depend directly on `noqlen_anchor` or only an interface first?
- What is the minimum stable Aria public API?
- Which Anchor helper is the first real integration target?
- How should Anchor results be mapped into Aria results?
- How should Android storage permission state be represented?
- Who owns permission request flow: UI shell or Aria Core?
- What is the first dry-run end-to-end flow?
- How will apply-mode operations be protected later?
