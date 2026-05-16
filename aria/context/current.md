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
- `aria/specs/features/android-player-boundary-contracts/` — spec and implementation complete.
- `aria/specs/features/minimal-ui-shell-planning/` — spec/planning artifacts complete.
- `aria/specs/features/aria-mvp-hardening/` — spec and implementation complete.
- `aria/specs/features/aria-release-preparation/` — spec and implementation complete.
- Bloco 20 State Snapshots and End-to-End Fake Flows is complete; no active product implementation after commit.

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
- Future Android Player audio output phase (phases A–E) documented outside Aria Core in `docs/aria-core-handoff.md` and `docs/post-core-backlog.md`.
- Audit 14-17 is complete. Do not start Audit 18-20 or Bloco 21 without explicit approval and a dedicated spec/task.
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
