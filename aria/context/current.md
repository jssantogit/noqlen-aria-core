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

## Active spec

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
- No active product implementation.

## Current goal

- Aria Core MVP is Blocos 0-7 and local tag `v0.1.0` exists.
- Bloco 8 Media Source Foundation is implemented and validated.
- Bloco 9 Library Browse/Search is implemented and validated.
- Bloco 10 Library Filters, Activity and Favorites is implemented and validated.
- Bloco 11 Queue Foundation is implemented and validated.
- Bloco 12 Now Playing Foundation is implemented and validated.
- Bloco 13 Playback, Renderer and Automation Intents is implemented and validated.
- Do not start Bloco 14 without explicit approval and a dedicated spec.
- No publish until approved.

## Allowed scope

- Context and handoff documentation updates.
- Audit 8-13 is complete.
- Publish only when explicitly approved.

## Forbidden scope

- Post-core feature implementation without a dedicated spec.
- Product behavior without an approved spec.
- Android, UI, navigation, player, further queue expansion, playback intents, playback engine, cache/offline, or storage UX implementation.
- Real Anchor, Navidrome, Jellyfin, Emby, provider, or media-source integration.

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
