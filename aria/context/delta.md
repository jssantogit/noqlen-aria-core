# Delta Summary

## What changed

- Bloco 1 completed source-agnostic core contracts, safe result/state primitives, `ControlClient`, and `FakeControlClient`.
- Bloco 2 completed fake-first control services, result mapping, readiness, diagnostics, lifecycle preview, and deterministic failure/value overrides.
- Bloco 3 completed the dry-run/offline `AnchorControlClient` adapter and mapping layer while blocking apply-mode behavior.
- Workflow vNext added compact context files, context packages, Behavior Budget, Test Risk Matrix, fake-hostility checklist, minimal role prompts, spec-template updates, and ADR templates.
- Bloco 4 spec created: Android/player boundary contracts defining eight bridge protocols, supporting types, and composite snapshot — vocabulary only, no implementation.

## Evidence

- Blocos 1-3 are recorded as complete in `docs/aria-core-handoff.md` and `docs/handoff.md`.
- Workflow vNext validation passed locally: `git diff --check`, `python3 -m py_compile src/noqlen_aria/*.py`, CLI help, CLI doctor, and `python3 -m pytest`.
- Bloco 4 spec validation: all existing commands pass; no source/test/Android files created; contamination check clean.

## Decisions

- Aria Core remains UI-independent.
- `ControlClient` is source-agnostic.
- Anchor is one `ControlClient` adapter, not the center of Aria.
- Context files carry standing rules; prompts should carry only task deltas.

## Regressions found

- None recorded in this delta.

## Next step

- Bloco 4 spec is complete. Do not implement Bloco 4 yet.
- Run the formal Blocos 1-3 audit.

## Open decisions

- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
- Whether Bloco 4 implementation starts immediately after the Blocos 1-3 audit passes or after audit follow-ups are resolved.
- Whether Android boundary contracts should be Bloco 4 in the implementation sequence or remain as a later Fase 6 block as in the handoff roadmap.
