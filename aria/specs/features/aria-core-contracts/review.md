# Review

## Summary

Bloco 1 spec (Aria Core Contracts) defines the first product-level contracts for Aria Core. This review is a stub created alongside the spec. Full review will be performed after implementation.

## Requirements coverage

All functional requirements (FR01–FR14) and non-functional requirements (NFR01–NFR06) are addressed by the design. The design proposes a single `contracts.py` module containing all contract types, enums, the `AnchorClient` protocol, and `FakeAnchorClient`.

## Files changed

Spec-only commit. Files created:

- `aria/specs/features/aria-core-contracts/requirements.md`
- `aria/specs/features/aria-core-contracts/design.md`
- `aria/specs/features/aria-core-contracts/tasks.md`
- `aria/specs/features/aria-core-contracts/review.md`

No source files, test files, or configuration files modified.

## Validation performed

Spec-only validation at commit time:

- `git status --short --branch` — clean working tree after spec commit.
- `git diff --check` — no whitespace issues.
- `python3 -m py_compile src/noqlen_aria/*.py` — passes.
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- `python3 -m pytest` — passes (Bloco 0 tests only).
- Repository contamination check — clean.

## Validation notes

- Spec is self-contained within `aria/specs/features/aria-core-contracts/`.
- No implementation files were created.
- Existing Bloco 0 validation passes without regression.
- `FakeAnchorClient` return values in the design are optimistic defaults; tests during implementation may need to cover failure injection.

## Non-goals check

| Non-goal | Status |
|---|---|
| No real Anchor integration | Pass — this is a spec, no implementation |
| No Anchor provider internals | Pass |
| No Anchor CLI as integration layer | Pass |
| No direct Navidrome access | Pass |
| No Android SDK or UI | Pass |
| No playback implementation | Pass |
| No queue implementation | Pass |
| No cache/offline implementation | Pass |
| No real music library access | Pass |
| No UI/product behavior | Pass |

## Risks remaining

- Contract method set may be incomplete for future blocks. This is an accepted risk; `Protocol` allows non-breaking additions.
- `FakeAnchorClient` defaults may be too optimistic. Tests during implementation should include failure-mode scenarios.

## Known limitations

- Spec defines contracts only; no integration with real Anchor.
- `AnchorClient` method set is a design proposal and may expand in later blocks.
- No Android-specific types or names appear in the design.

## Follow-up tasks

- Implement Bloco 1 contracts per the spec (do not start until this spec is reviewed and approved).
- After implementation, update this review file with full audit results.
- Consider adding `DiagnosticsViewState.warnings` field decision during implementation.
- Consider whether `AriaResult` needs factory functions (`ok()`, `err()`) during implementation.

## Aria context updates needed

- None for this spec-only block. After implementation, consider recording any discovered workflow mistakes in `aria/context/mistakes.md`.
