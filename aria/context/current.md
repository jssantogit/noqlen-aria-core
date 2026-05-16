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
- Bloco 6 Aria MVP Hardening spec is complete (planning only, no implementation).
- Do not redo Bloco 3.
- Next: Bloco 6 implementation only after approval; do not implement hardening without the active spec task.

## Active spec

- `aria/specs/features/android-player-boundary-contracts/` — spec and implementation complete.
- `aria/specs/features/minimal-ui-shell-planning/` — spec/planning artifacts complete. No UI implementation.
- `aria/specs/features/aria-mvp-hardening/` — spec complete. No hardening implementation.
- No active product implementation.

## Current goal

- Keep future tasks focused with compact context packages.
- Preserve existing safety rules while avoiding large repeated prompts.

## Allowed scope

- Workflow, context, review, prompt, spec-template, agent, and decision documentation.
- Audit preparation for existing Blocos 1-3 work.
- Bloco 4 planning only after the Blocos 1-3 audit passes.

## Forbidden scope

- Product behavior without an approved spec.
- Android, UI, navigation, player, queue, now playing, playback engine, cache/offline, or storage UX implementation.
- Real Anchor, Navidrome, Jellyfin, Emby, provider, or media-source integration.
- Mutation testing policy, Pact Broker setup, or new contract harness implementation unless a future spec adopts them.

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
