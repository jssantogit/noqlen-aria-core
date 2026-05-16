# Post-core Handoff

Bloco 24 prepares the repository for the Final Post-core/Core Audit. It is release preparation only. No post-core tag was created, no package was published, no Android app was implemented, no player was implemented, and no audio driver was implemented.

## Current State

- Aria Core MVP Blocos 0-7 are complete and local tag `v0.1.0` exists.
- Blocos 8-17 are implemented and audited.
- Blocos 18-21 are implemented and await final post-core/core audit coverage for deferred audit items.
- Blocos 22-23 are planning/handoff docs only and await final post-core/core audit coverage for deferred audit items.
- Bloco 24 release-prep docs are complete.

## What Aria Core Provides

Aria Core provides contracts, states, policies, services, capabilities, fakes, mappers, adapters, snapshots, safe serialization, and sanitized output. It models readiness and safe decisions for app/player-facing behavior.

Aria Core does not provide real Android SDK integration, real UI, real playback, real provider integration, real streaming, real transcoding, or real audio-driver behavior.

## Handoff To Final Post-core/Core Audit

The final audit should consume:

- `docs/post-core-release-checklist.md`
- `docs/post-core-release-notes.md`
- `docs/post-core-api-surface.md`
- `docs/post-core-safety-summary.md`
- `docs/post-core-known-limitations.md`
- `docs/future-android-player-handoff.md`
- Existing Bloco specs and reviews.
- Existing audit checklists under `aria/review/`.
- `aria/context/current.md` and `aria/context/delta.md`.

The audit should decide whether a post-core release tag is ready. Bloco 24 does not make that decision.

## Handoff To Future Android Player

Future Android Player work is outside Aria Core and requires dedicated specs. It should proceed only after explicit approval.

- Future Android Player Phase A — Audio Output Research: survey Android audio output APIs, USB DAC feasibility, exclusive mode feasibility, and sample-rate/bit-depth negotiation. No implementation in Aria Core.
- Future Android Player Phase B — Playback Engine Adapter: design/prototype an adapter mapping Aria playback intents to a real playback layer. Adapter lives in the Android Player.
- Future Android Player Phase C — Exclusive USB Output Prototype: prototype exclusive USB output for targeted devices outside Aria Core.
- Future Android Player Phase D — Bit-perfect Validation: validate bit-perfect or bit-transparent behavior under test conditions outside Aria Core.
- Future Android Player Phase E — Production Audio Driver/Bridge Decision: decide whether to build, adopt, or avoid a production custom audio bridge. Aria Core remains driver-free.

## Handoff To Future App/UI Implementation

Future app/UI work should consume Aria Core as a thin adapter:

- Render Aria Core state/results/snapshots.
- Express user actions as Aria intents.
- Delegate platform callbacks and platform APIs to adapters.
- Keep heavy safety, policy, provider, storage/cache, queue, now-playing, playback availability, and capability logic in Aria Core or approved core-facing services.
- Do not move heavy safety/policy logic into UI.

## Must Not Bypass

Future Android app/player/UI work must not bypass Aria Core to call providers, Anchor provider internals, playback engines, storage APIs, cache mutation, MediaSession, Android Auto, notification controls, or audio APIs from UI screens.

## Release Decision Boundary

- No tag is created by Bloco 24.
- No publish action is attempted by Bloco 24.
- Final audit is the next gate.
- A post-core tag is ready only if final audit passes, validation is clean, docs are truthful, repository hygiene is clean, and the maintainer explicitly approves tag creation.
