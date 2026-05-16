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
- Bloco 7 implemented: release readiness checklist, release notes, public API surface summary, safety summary, post-core backlog summary, handoff update, and README refresh. Documentation only; no publish, source, version, or implementation changes.
- Roadmap alignment update: Aria Core MVP is Blocos 0-7; post-core feature expansion is being restored explicitly as Blocos 8-23. Advanced library/player features and Android real integration remain backlog.
- Bloco 20 wording update: provider extension readiness, not real multi-provider support through current Anchor.
- Local tag `v0.1.0` exists. No publish action is recorded in this delta.
- Release artifacts created: `docs/release-checklist.md`, `docs/release-notes.md`, `docs/api-surface.md`, `docs/safety-summary.md`, `docs/post-core-backlog.md`.
- Workflow improvements from Noqlen Playbook comparison added: broader repository hygiene categories, PR template, read-only local repository study prompt, clearer audit finding/status fields, and Workflow vNext references. Workflow/template changes only.
- Bloco 8 spec created: `aria/specs/features/media-source-foundation/` with `requirements.md`, `design.md`, `tasks.md`, `review.md`. Defines `MediaSourceClient`, `FakeMediaSourceClient`, source capability models, abstract media IDs, stream handle, provider capability discovery, and availability states. Spec only; no implementation, no provider integration, no streaming, no playback, no UI.
- Bloco 8 implemented: `src/noqlen_aria/media_source.py` with `MediaSourceClient` protocol, `FakeMediaSourceClient` (deterministic, failure-injection hooks, value overrides), and 11 supporting types. `tests/test_media_source.py` adds 100 tests covering contracts, capability mapping, error injection, determinism, safe degraded behavior, and provider boundary enforcement.
- Bloco 9 implemented: `src/noqlen_aria/library.py` with browse/search models and services, plus minimal `MediaSourceClient`/`FakeMediaSourceClient` browse/search extensions. `tests/test_library_browse_search.py` covers artists, albums, tracks, playlists, genres, safe folder metadata, search validation/results, unsupported capabilities, degraded/unavailable sources, empty/no-match scenarios, and boundary enforcement. No Bloco 10 behavior added.

## Evidence

- Blocos 1-3 are recorded as complete in `docs/aria-core-handoff.md` and `docs/handoff.md`.
- Workflow vNext validation passed locally.
- Bloco 4 implementation validation: `python3 -m pytest` 358/358 pass; zero Android SDK references; contamination clean.
- Bloco 5 planning artifact validation: all requested commands pass; no source/test files created; contamination clean.
- Bloco 6 implementation validation: `python3 -m pytest` 368/368 pass; contamination clean. All search checks clean.
- Bloco 7 release preparation validation: `python3 -m pytest` 368/368 pass; contamination clean; all search checks clean; version consistency confirmed; release artifacts created.
- Playbook comparison workflow update validation: `git diff --check` passed; tracked forbidden-file grep returned no matches; `git status --short --branch` reviewed. No source, tests, Android/UI, product behavior, release tag, or publish changes intended.
- Bloco 8 spec validation: `python3 -m pytest` 368/368 pass; contamination clean; no source code, tests, provider integration, streaming, playback, or UI created.
- Bloco 8 implementation validation: `python3 -m pytest` 468/468 pass (368 base + 100 new); `py_compile` clean; CLI help/doctor pass; all search checks clean (provider integration, network, Android, forbidden implementations); contamination clean.
- Bloco 9 implementation validation: `python3 -m pytest` 506/506 pass; `py_compile` clean; CLI help/doctor pass; provider/network/filesystem/queue checks clean; Android grep only reports an existing safety docstring in `android_boundaries.py`; contamination clean.

## Decisions

- Aria Core remains UI-independent.
- `ControlClient` is source-agnostic.
- Anchor is one `ControlClient` adapter, not the center of Aria.
- Context files carry standing rules; prompts should carry only task deltas.
- Local tag `v0.1.0` exists; publish still requires explicit approval.
- Cross-repository workflow study should be read-only and sanitized unless a separate task explicitly scopes retrofit work.

## Regressions found

- None recorded in this delta.
- None recorded for the workflow update.

## Next step

- Provider roadmap wording patch is complete.
- Bloco 8 (Media Source Foundation) is implemented and validated.
- Bloco 9 (Library Browse/Search) is implemented and validated (506/506 tests).
- Next step: Bloco 10 only after explicit approval and a dedicated spec.
- Post-core features (Blocos 8-23 in the roadmap) require dedicated specs before implementation.

## Open decisions

- Whether/when to publish package artifacts.
- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
