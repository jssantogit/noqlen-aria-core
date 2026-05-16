# Current Context

## Active milestone

- Aria Workflow vNext applies from the next task onward.
- Bloco 0 bootstrap/audit is complete.
- Bloco 1 contracts are complete.
- Bloco 2 fake control state mapping is complete.
- Bloco 3 `AnchorControlClient` dry-run/offline adapter is complete.
- Bloco 4 (Android/player boundary contracts) is implemented.
- Bloco 5 minimal UI shell planning artifacts are complete.
- Bloco 6 Aria MVP hardening is complete.
- Bloco 7 Aria Core Release Preparation is complete.
- Local tag `v0.1.0` exists; Aria Core MVP is complete.
- Bloco 8 (Media Source Foundation) is implemented and audited.
- Bloco 9 (Library Browse/Search) is implemented and audited.
- Bloco 10 (Library Filters, Activity and Favorites) is implemented and audited.
- Bloco 11 (Queue Foundation) is implemented and audited.
- Bloco 12 (Now Playing Foundation) is implemented and audited.
- Bloco 13 (Playback, Renderer and Automation Intents) is implemented and audited.
- Audit 8-13 (Media/Library/Queue/Playback Audit) is complete.
- Bloco 14 (Offline, Cache and Storage Policy) is implemented.
- Bloco 15 (Internet Radio Foundation) is implemented.
- Bloco 16 (Stream Quality, Transcoding and Network Policy) is implemented.
- Bloco 17 (Playback Capability Models) is implemented.
- Audit 14-17 (Offline/Radio/Quality/Capabilities Audit) is complete.
- Bloco 18 (Profiles, Preferences, Backup and Restore) is implemented.
- Bloco 19 (Smart Playlists) is implemented.
- Bloco 20 (State Snapshots and End-to-End Fake Flows) is implemented.
- Bloco 21 (Provider Extension Readiness) is implemented.
- Bloco 22 (Android Real Integration Planning) is complete as planning/docs only.
- Bloco 23 (Android Shell Handoff) is complete as handoff/docs only.
- Bloco 24 (Post-core Release Prep) is complete as release-prep/docs only.

## Active spec

- `aria/specs/features/offline-cache-storage-policy/` — spec and implementation complete.
- `aria/specs/features/internet-radio-foundation/` — spec and implementation complete.
- `aria/specs/features/stream-quality-transcoding-network-policy/` — spec and implementation complete.
- `aria/specs/features/playback-capability-models/` — spec and implementation complete.
- `aria/specs/features/profiles-preferences-backup-restore/` — spec and implementation complete.
- `aria/specs/features/smart-playlists/` — spec and implementation complete.
- `aria/specs/features/state-snapshots-e2e-fake-flows/` — spec and implementation complete.
- `aria/specs/features/library-filters-activity-favorites/` — spec and implementation complete.
- `aria/specs/features/queue-foundation/` — spec and implementation complete.
- `aria/specs/features/playback-renderer-automation-intents/` — spec and implementation complete.
- `aria/specs/features/now-playing-foundation/` — spec and implementation complete.
- `aria/specs/features/library-browse-search/` — spec and implementation complete.
- `aria/specs/features/media-source-foundation/` — spec and implementation complete.
- `aria/specs/features/provider-extension-readiness/` — spec and implementation complete.
- `aria/specs/features/android-real-integration-planning/` — spec/planning artifacts complete.
- `aria/specs/features/android-shell-handoff/` — spec/handoff artifacts complete.
- `aria/specs/features/post-core-release-prep/` — spec/release-prep artifacts complete.
- `aria/specs/features/android-player-boundary-contracts/` — spec and implementation complete.
- `aria/specs/features/minimal-ui-shell-planning/` — spec/planning artifacts complete.
- `aria/specs/features/aria-mvp-hardening/` — spec and implementation complete.
- `aria/specs/features/aria-release-preparation/` — spec and implementation complete.
- Bloco 24 Post-core Release Prep is complete; no active product implementation after commit.

## Current goal

- Aria Core MVP is Blocos 0-7 and local tag `v0.1.0` exists.
- Bloco 8 Media Source Foundation is implemented and validated.
- Bloco 9 Library Browse/Search is implemented and validated.
- Bloco 10 Library Filters, Activity and Favorites is implemented and validated.
- Bloco 11 Queue Foundation is implemented and validated.
- Bloco 12 Now Playing Foundation is implemented and validated.
- Bloco 13 Playback, Renderer and Automation Intents is implemented and validated.
- Bloco 14 Offline, Cache and Storage Policy is implemented and validated.
- Bloco 15 Internet Radio Foundation is implemented and validated.
- Bloco 16 Stream Quality, Transcoding and Network Policy is implemented and validated.
- Roadmap clarification complete: Bloco 15 is now Internet Radio Foundation; Bloco 16 is Stream Quality, Transcoding and Network Policy; Bloco 17 is Playback Capability Models.
- Bloco 17 Playback Capability Models is implemented and validated as capability/readiness/preference models only, including fade-in/fade-out capability and bit-perfect conflict state.
- Bloco 18 Profiles, Preferences, Backup and Restore is implemented and validated as local-only profile/preference state, in-memory backup bundle, and preview-first restore models/services.
- Bloco 19 Smart Playlists is implemented as local-only smart playlist, saved filter, and deterministic smart mix models/services over provided app-facing candidates.
- Bloco 20 State Snapshots and End-to-End Fake Flows is implemented as sanitized in-memory state snapshots, structural snapshot diffs, and deterministic local-only fake flow traces.
- Bloco 21 Provider Extension Readiness is implemented as provider descriptor/readiness/capability/registry models and deterministic local-only readiness/discovery services. Current Anchor remains Navidrome-focused; no real provider integration, provider auth, network, mutation, streaming, playback, Android/UI, or Bloco 22 behavior was added.
- Bloco 22 Android Real Integration Planning is complete as documentation only in `docs/android-real-integration-plan.md` and `aria/specs/features/android-real-integration-planning/`. No Android SDK, Kotlin/Java/Gradle, MediaSession, Media3/ExoPlayer, Android Auto, notification/lock-screen/Bluetooth/headset/widget, foreground service, playback engine, audio driver, USB output, UI, source, or test implementation was added.
- Bloco 23 Android Shell Handoff is complete as documentation only in `docs/android-shell-handoff.md` and `aria/specs/features/android-shell-handoff/`. No Android SDK, Kotlin/Java/Gradle, Compose/Activity/Fragment/UI, MediaSession, Media3/ExoPlayer, Android Auto, notification/lock-screen/Bluetooth/headset/widget, playback engine, audio driver, USB output, provider, source, or test implementation was added.
- Bloco 24 Post-core Release Prep is complete as documentation/release-prep only in `docs/post-core-release-checklist.md`, `docs/post-core-release-notes.md`, `docs/post-core-api-surface.md`, `docs/post-core-safety-summary.md`, `docs/post-core-known-limitations.md`, `docs/post-core-handoff.md`, `docs/future-android-player-handoff.md`, and `aria/specs/features/post-core-release-prep/`. No source, tests, version, tag, publish, Android app, real player, audio driver, provider integration, network behavior, or filesystem/device behavior was added.
- Future Android Player audio output phase (phases A–E) documented outside Aria Core in `docs/aria-core-handoff.md` and `docs/post-core-backlog.md`.
- Audit 14-17 is complete. Audit 18-20 and Audit 21-23 were deferred to the final post-core/core audit. Bloco 24 prepared final audit inputs. Next gate is Final Post-core/Core Audit; do not create a post-core tag or publish packages before it passes and release actions are explicitly approved.
- No publish until approved.

## Allowed scope

- Context and handoff documentation updates.
- Audit 8-13 is complete.
- Publish only when explicitly approved.

## Forbidden scope

- Post-core feature implementation without a dedicated spec.
- Product behavior without an approved spec.
- Android, UI, navigation, player, further queue expansion, playback intents, playback engine, cache/offline mutation, or storage UX implementation.
- Real Anchor, Navidrome, Jellyfin, Emby, provider, or media-source integration.
- Real download, cache write/delete, destructive cleanup, filesystem traversal, device storage inspection, Android storage APIs, stream resolution, radio streaming, Shoutcast/HLS/DASH parsing, provider direct integration, real playback/audio output, audio/USB driver behavior, DSP/EQ, Audit 18-20, Bloco 21 behavior, or later post-core behavior without a dedicated spec.

## Key risks

- Accidentally treating Anchor as the center of Aria instead of one `ControlClient` adapter.
- Expanding behavior during documentation, audit, or planning work.
- Reading the whole repository by default instead of using task-sized context.
- Letting fake clients become happy-path-only simulators.
- Publishing without explicit approval.

## Expected files

- For workflow tasks: `AGENTS.md`, `.github/**`, `docs/aria-core-handoff.md`, `docs/workflow-vnext.md`, `aria/context/**`, `aria/review/**`, `aria/prompts/**`, `aria/specs/_template/**`, `aria/agents/**`, `aria/decisions/**`.
- For product tasks: files named by the active spec and task only.

## Validation

- Run validation proportional to the task and record evidence.
- For workflow-only changes, confirm no source, tests, Android/UI, product behavior, mutation testing, or Pact Broker files changed.

## Stop condition

- Stop when the active task is implemented, validated, recorded in `aria/context/delta.md`, and reviewed against scope.
