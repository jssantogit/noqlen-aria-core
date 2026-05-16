# Requirements

## Status

Bloco 23 Android Shell Handoff is approved for documentation and handoff only.

Context package used: Standard.

## Problem

Aria Core now has post-core models and planning for provider readiness, library/search, queue, now playing, playback intents, offline/cache, internet radio, quality policy, playback capability, snapshots, and future Android real integration. The future Android shell needs a clear handoff that explains how to consume these Aria Core capabilities without moving heavy state, policy, validation, readiness, safety, result mapping, provider logic, playback rules, or platform-independent orchestration into UI/platform code.

Without an explicit shell handoff, future Android work could duplicate Aria policies, call providers directly, call Anchor provider internals, treat Android platform surfaces as the source of truth, or blur Aria Core, Android platform adapter, and future Android Player/audio responsibilities.

## Goal

Create a clear handoff for the future Android shell/app so it can consume Aria Core as a thin consumer/adapter while platform-specific Android calls and future playback/audio implementation remain outside Aria Core.

## Non-goals

- No Android SDK implementation.
- No Kotlin, Java, or Gradle files.
- No Compose, Activity, Fragment, screen, navigation, or UI implementation.
- No MediaSession implementation.
- No Media3 or ExoPlayer implementation.
- No Android Auto implementation.
- No notification, lock-screen, Bluetooth, or headset implementation.
- No widget implementation.
- No playback engine implementation.
- No audio driver implementation.
- No USB output implementation.
- No provider integration.
- No network behavior.
- No filesystem/device behavior.
- No source code changes.
- No test changes unless existing validation requires them.
- No Bloco 24 work.

## Actors

- Future Android shell/app.
- Future Android UI screens.
- Future Android platform adapters.
- Future Android Player/audio layer.
- Aria Core.
- Future support/diagnostics workflows.
- End user using app UI, platform media controls, Android Auto, widgets, or permission/storage prompts.

## Functional Requirements

- Document that Bloco 23 is documentation/handoff only.
- Document future Android shell responsibilities.
- Document how Android consumes Aria Core state, results, and intents.
- Document how Android maps platform events into Aria-safe intents.
- Document what must stay inside Aria Core.
- Document what belongs to Android platform adapters.
- Document what belongs to the future Android Player/audio layer.
- Document what Android UI must not call directly.
- Document expected startup/readiness flow.
- Document expected diagnostics/support snapshot flow.
- Document expected library/search/queue/now-playing flow.
- Document expected playback intent/control flow.
- Document expected offline/cache/radio/quality/capability flow.
- Document expected provider readiness flow.
- Document expected permission/storage UX flow.
- Document expected media controls/Android Auto handoff.
- Document boundaries for future custom audio output/driver research.
- Update workflow state concisely in `aria/context/current.md` and `aria/context/delta.md`.

## Non-functional Requirements

- Preserve Aria Core as platform-independent Python/core logic.
- Keep Android shell and UI as thin consumers/adapters over Aria Core.
- Keep heavy state, policy, validation, readiness, safety, result mapping, and app-facing contracts in Aria Core.
- Keep Android SDK calls, permissions, MediaSession, notifications, foreground service, Android Auto, widgets, and device integration in future Android platform adapters.
- Keep real playback, audio output, Media3/ExoPlayer or alternative playback engine, and possible custom/exclusive audio output research in the future Android Player/audio layer.
- Do not introduce dependencies.
- Do not alter public APIs.
- Do not modify `src/noqlen_aria/**`, `tests/**`, `pyproject.toml`, or Android/Kotlin/Java/Gradle files.
- Keep docs free of claims that an Android shell exists or that Android integration is implemented.

## Canonical Examples

Given Android app startup needs status, When the shell initializes, Then it consumes Aria readiness/status models and does not call Anchor/provider internals.

Given Android UI needs diagnostics, When it displays diagnostics, Then it consumes sanitized Aria diagnostics/snapshot data.

Given Android UI needs library search, When it requests browse/search, Then it calls Aria app-facing services/models and not providers directly.

Given Android media controls trigger play/pause later, When Android receives a control event, Then the platform adapter maps it into Aria playback intents.

Given Android Auto requests browse/playback data later, When the app responds, Then it uses Aria models and platform adapters.

Given storage permission UX is needed, When Android displays permission state, Then it consumes Aria boundary state and performs platform calls outside Aria Core.

Given future bit-perfect/custom output is researched, When Android Player handles it, Then it reports capability/readiness back through Aria models and does not put driver logic in Aria Core.

## Edge Cases

- Startup status is unavailable or degraded: Android shell must render Aria readiness/status results and avoid direct Anchor/provider checks.
- Diagnostics include warnings: UI must display sanitized Aria diagnostics/snapshot data and avoid raw logs, stack traces, paths, or provider exceptions.
- Library browse/search source is degraded: Android shell must consume Aria unavailable/degraded models rather than querying providers directly.
- Queue/now-playing state is stale: Android shell must refresh from Aria state and avoid local state machines.
- Media control event arrives while playback is blocked: platform adapter must send an Aria playback intent and respect blocked/unavailable results.
- Offline/cache/radio/quality/capability data is incomplete: Android shell must render Aria policy/readiness state and not make platform or provider assumptions.
- Provider readiness says unavailable: Android shell must surface the Aria state and not attempt provider direct integration.
- Permission/storage prompt is denied: Android layer owns platform prompt/result handling while Aria owns platform-neutral state and policy consequences.
- Future custom audio output research changes feasibility: Android Player reports capability/readiness through Aria models and keeps driver logic outside Aria Core.

## Acceptance Criteria

- Spec files exist under `aria/specs/features/android-shell-handoff/`.
- `requirements.md`, `design.md`, `tasks.md`, and `review.md` include required sections.
- Behavior Budget is present.
- Test Risk Matrix is present.
- Canonical Examples are present using Given / When / Then.
- Android shell handoff documentation exists under `docs/`.
- Handoff covers startup/readiness, diagnostics/support snapshot, library/search, queue/now-playing, playback controls/intents, offline/cache, internet radio, stream quality/network/transcoding policy, playback capabilities, provider readiness, permissions/storage UX, media controls/Android Auto, and future audio output/driver boundaries.
- Strict must-not-bypass rules are documented.
- Current and delta context files are updated concisely.
- No source code changed.
- No tests changed.
- No Android implementation was added.
- Required validation passes.
- Spec and docs are committed together with `docs(android): add Android shell handoff`.

## Open Questions

- Which future Android architecture will host the shell and platform adapter boundary?
- Which Aria app-facing facade should a future Android shell use first?
- Which future specs will split MediaSession, Android Auto, foreground service, widgets, playback engine, and permission/storage platform work?
- Which support snapshot export format is appropriate for Android support workflows?
- Which Android Player/audio approach will be selected remains future work outside Aria Core.
