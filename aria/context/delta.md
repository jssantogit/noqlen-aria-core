# Delta Summary

## What changed

- Blocos 4-6 formal audit found stale context/handoff references and CLI/doc wording that still described earlier blocks; audit-scoped corrections were applied.
- Bloco 1 completed source-agnostic core contracts, safe result/state primitives, `ControlClient`, and `FakeControlClient`.
- Bloco 2 completed fake-first control services, result mapping, readiness, diagnostics, lifecycle preview, and deterministic failure/value overrides.
- Bloco 3 completed the dry-run/offline `AnchorControlClient` adapter and mapping layer while blocking apply-mode behavior.
- Workflow vNext added compact context files, context packages, Behavior Budget, Test Risk Matrix, fake-hostility checklist, minimal role prompts, spec-template updates, and ADR templates.
- Bloco 4 implemented: `src/noqlen_aria/android_boundaries.py` with 9 bridge protocols, supporting types, and 9 deterministic fake implementations.
- Bloco 5 Minimal UI Shell Planning artifacts created: `docs/ui-shell-boundary.md` and architecture/android boundary updates. Documentation only.
- Bloco 6 implemented: explicit package/module exports, safe serialization and sanitization helpers, safer Anchor adapter exception output, hardening tests. No Android/UI/playback/queue/cache/provider implementation.
- Bloco 7 implemented: release readiness checklist, release notes, public API surface summary, safety summary, post-core backlog summary, handoff update, and README refresh. Documentation only — no tag, publish, source, version, or implementation changes.
- Release artifacts created: `docs/release-checklist.md`, `docs/release-notes.md`, `docs/api-surface.md`, `docs/safety-summary.md`, `docs/post-core-backlog.md`.
- Workflow improvements from Noqlen Playbook comparison added: broader repository hygiene categories, PR template, read-only local repository study prompt, clearer audit finding/status fields, and Workflow vNext references. Workflow/template changes only.

## Evidence

- Blocos 1-3 are recorded as complete in `docs/aria-core-handoff.md` and `docs/handoff.md`.
- Workflow vNext validation passed locally.
- Bloco 4 implementation validation: `python3 -m pytest` 358/358 pass; zero Android SDK references; contamination clean.
- Bloco 5 planning artifact validation: all requested commands pass; no source/test files created; contamination clean.
- Bloco 6 implementation validation: `python3 -m pytest` 368/368 pass; contamination clean. All search checks clean.
- Bloco 7 release preparation validation: `python3 -m pytest` 368/368 pass; contamination clean; all search checks clean; version consistency confirmed; release artifacts created.
- Playbook comparison workflow update validation: `git diff --check` passed; tracked forbidden-file grep returned no matches; `git status --short --branch` reviewed. No source, tests, Android/UI, product behavior, release tag, or publish changes intended.

## Decisions

- Aria Core remains UI-independent.
- `ControlClient` is source-agnostic.
- Anchor is one `ControlClient` adapter, not the center of Aria.
- Context files carry standing rules; prompts should carry only task deltas.
- Version remains `0.0.0` until a version decision is made during final audit or tag approval.
- No release tag or publish action was taken in this task.
- Cross-repository workflow study should be read-only and sanitized unless a separate task explicitly scopes retrofit work.

## Regressions found

- None recorded in this delta.
- None recorded for the workflow update.

## Next step

- Final release audit and tag decision.
- Do not create a release tag or publish until the release checklist passes and the maintainer approves.
- Post-core features (Blocos 7-21 in the roadmap) require dedicated specs before implementation.

## Open decisions

- When to bump the version from `0.0.0`.
- When to create the first release tag.
- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
