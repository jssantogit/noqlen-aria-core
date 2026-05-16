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
- Final roadmap alignment: Aria Core MVP is Blocos 0-7; post-core feature expansion is Blocos 8-20.
- Next: Final release audit and tag decision. Do not create a release tag or publish until the release checklist passes and the maintainer approves.

## Active spec

- `aria/specs/features/android-player-boundary-contracts/` — spec and implementation complete.
- `aria/specs/features/minimal-ui-shell-planning/` — spec/planning artifacts complete.
- `aria/specs/features/aria-mvp-hardening/` — spec and implementation complete.
- `aria/specs/features/aria-release-preparation/` — spec and implementation complete.
- No active product implementation.

## Current goal

- Aria Core MVP release preparation is complete. Release artifacts are documented.
- Advanced library/player features and Android real integration remain post-core backlog, not MVP blockers.
- Final release audit and tag decision are next.
- No tag, no publish until approved.

## Allowed scope

- Final release audit reviewing the release artifacts.
- Context and handoff documentation updates.
- Tag and publish only when explicitly approved.

## Forbidden scope

- Post-core feature implementation without a dedicated spec.
- Product behavior without an approved spec.
- Android, UI, navigation, player, queue, now playing, playback engine, cache/offline, or storage UX implementation.
- Real Anchor, Navidrome, Jellyfin, Emby, provider, or media-source integration.

## Key risks

- Accidentally treating Anchor as the center of Aria instead of one `ControlClient` adapter.
- Expanding behavior during documentation, audit, or planning work.
- Reading the whole repository by default instead of using task-sized context.
- Letting fake clients become happy-path-only simulators.
- Creating a release tag or publishing before all checklist items pass.

## Expected files

- For workflow tasks: `AGENTS.md`, `.github/**`, `docs/aria-core-handoff.md`, `docs/workflow-vnext.md`, `aria/context/**`, `aria/review/**`, `aria/prompts/**`, `aria/specs/_template/**`, `aria/agents/**`, `aria/decisions/**`.
- For product tasks: files named by the active spec and task only.

## Validation

- Run validation proportional to the task and record evidence.
- For workflow-only changes, confirm no source, tests, Android/UI, product behavior, mutation testing, or Pact Broker files changed.

## Stop condition

- Stop when the active task is implemented, validated, recorded in `aria/context/delta.md`, and reviewed against scope.
