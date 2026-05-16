# Current Context

## Active milestone

- Aria Workflow vNext applies from the next task onward.
- Bloco 0 bootstrap/audit is complete.
- Bloco 1 contracts are complete.
- Bloco 2 fake control state mapping is complete.
- Bloco 3 `AnchorControlClient` dry-run/offline adapter is complete.
- Bloco 4 (Android/player boundary contracts) is implemented.

## Active slice

- Bloco 4 is complete: 9 bridge protocols, supporting types, composite snapshot, and 9 fake implementations.
- 129 boundary contract tests added; 358 total tests pass.
- Bloco 5 Minimal UI Shell Planning artifacts are complete (docs only, no implementation).
- Bloco 6 Aria MVP Hardening is implemented.
- Blocos 4-6 formal audit is complete.
- Bloco 7 Aria Core Release Preparation spec is the active planning task.
- Next: Bloco 7 release preparation implementation. Do not create a release tag or publish in this spec task.

## Active spec

- `aria/specs/features/android-player-boundary-contracts/` — spec and implementation complete.
- `aria/specs/features/minimal-ui-shell-planning/` — spec/planning artifacts complete. No UI implementation.
- `aria/specs/features/aria-mvp-hardening/` — spec and implementation complete.
- `aria/specs/features/aria-release-preparation/` — spec/planning active. No release implementation.
- No active product implementation.

## Current goal

- Create an implementation-ready spec for preparing the Aria Core MVP release.
- No tag, no publish, no source changes, no product behavior in this task.

## Allowed scope

- Spec creation in `aria/specs/features/aria-release-preparation/**` only.
- Context updates in `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` if needed.
- Validation and contamination checks.

## Forbidden scope

- Release tag creation or package publishing.
- Source code changes to `src/noqlen_aria/**`.
- Test changes.
- `pyproject.toml` or version changes.
- Product behavior without an approved spec.
- Android, UI, navigation, player, queue, now playing, playback engine, cache/offline, or storage UX implementation.
- Real Anchor, Navidrome, Jellyfin, Emby, provider, or media-source integration.

## Key risks

- Accidentally treating Anchor as the center of Aria instead of one `ControlClient` adapter.
- Expanding behavior during documentation, audit, or planning work.
- Reading the whole repository by default instead of using task-sized context.
- Letting fake clients become happy-path-only simulators.

## Expected files

- For workflow tasks: `AGENTS.md`, `docs/aria-core-handoff.md`, `docs/workflow-vnext.md`, `aria/context/**`, `aria/review/**`, `aria/prompts/**`, `aria/specs/_template/**`, `aria/agents/**`, `aria/decisions/**`.
- For product tasks: files named by the active spec and task only.

## Validation

- Run validation proportional to the task and record evidence.
- For workflow-only changes, confirm no source, tests, Android/UI, product behavior, mutation testing, or Pact Broker files changed.

## Stop condition

- Stop when the active task is implemented, validated, recorded in `aria/context/delta.md`, and reviewed against scope.
