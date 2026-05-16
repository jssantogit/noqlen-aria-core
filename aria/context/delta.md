# Delta Summary

## What changed

- Bloco 1 completed source-agnostic core contracts, safe result/state primitives, `ControlClient`, and `FakeControlClient`.
- Bloco 2 completed fake-first control services, result mapping, readiness, diagnostics, lifecycle preview, and deterministic failure/value overrides.
- Bloco 3 completed the dry-run/offline `AnchorControlClient` adapter and mapping layer while blocking apply-mode behavior.
- Workflow vNext added compact context files, context packages, Behavior Budget, Test Risk Matrix, fake-hostility checklist, minimal role prompts, spec-template updates, and ADR templates.
- Bloco 4 spec created: Android/player boundary contracts defining eight bridge protocols, supporting types, and composite snapshot — vocabulary only, no implementation.
- Bloco 4 implemented: `src/noqlen_aria/android_boundaries.py` with 9 bridge protocols, 12+ enum types, 15+ dataclasses, composite `AndroidBoundarySnapshot`, and 9 deterministic fake implementations. 129 new tests added; 358 total tests pass.
- Bloco 5 Minimal UI Shell Planning spec created: defines `AppShellAdapter` protocol, `AppShellState` composite, `AppShellInput` action enum, per-screen view models, anti-coupling rules, and Bloco 4 boundary consumption plan. Spec/planning only — no implementation.
- Bloco 5 planning artifacts created: `docs/ui-shell-boundary.md`, architecture/android boundary updates, thin UI examples, and handoff note. Documentation only — no UI/source implementation.

## Evidence

- Blocos 1-3 are recorded as complete in `docs/aria-core-handoff.md` and `docs/handoff.md`.
- Workflow vNext validation passed locally: `git diff --check`, `python3 -m py_compile src/noqlen_aria/*.py`, CLI help, CLI doctor, and `python3 -m pytest`.
- Bloco 4 spec validation: all existing commands pass; no source/test/Android files created; contamination check clean.
- Bloco 4 implementation validation: `python3 -m pytest` 358/358 pass; zero Android SDK references; zero forbidden implementations; contamination check clean.
- Bloco 5 spec validation: all existing commands pass; no source/test files created or modified; contamination check clean.
- Bloco 5 planning artifact validation: all requested commands pass; search-check matches are documentation/planning references only; contamination check clean.

## Decisions

- Aria Core remains UI-independent.
- `ControlClient` is source-agnostic.
- Anchor is one `ControlClient` adapter, not the center of Aria.
- Context files carry standing rules; prompts should carry only task deltas.

## Regressions found

- None recorded in this delta.

## Next step

- Bloco 4 implementation is complete. 9 bridge boundaries, all fakes, 129 tests.
- Bloco 5 Minimal UI Shell Planning artifacts are complete. Documentation only, no implementation.
- Next step: Bloco 6 spec.

## Open decisions

- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
- Whether Bloco 4 implementation starts immediately after the Blocos 1-3 audit passes or after audit follow-ups are resolved.
- Whether Android boundary contracts should be Bloco 4 in the implementation sequence or remain as a later Fase 6 block as in the handoff roadmap.
