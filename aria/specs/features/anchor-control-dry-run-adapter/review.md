# Review

## Status

Complete — Bloco 3 implementation is finished. 229 tests pass (2 Bloco 0 + 48 Bloco 1 + 76 Bloco 2 + 103 Bloco 3).

## Summary

Bloco 3 implementation delivers the `AnchorControlClient` adapter (`src/noqlen_aria/anchor_adapter.py`) plus `AnchorResultMapper` — a concrete `ControlClient` adapter that delegates to Anchor public API helpers in offline/dry-run mode only. The adapter implements all seven `ControlClient` protocol methods and supports optional `noqlen_anchor` dependency via lazy import and constructor injection. When `noqlen_anchor` is not installed, all methods return safe `ANCHOR_NOT_AVAILABLE` error results. `send_lifecycle_intent` is blocked from apply-mode execution — returns `APPLY_MODE_BLOCKED` error or uses dry-run helpers only. 103 comprehensive tests cover mapper correctness, not-available behavior, protocol conformance, error handling, integration with existing Aria services, sanitization, determinism, and safety boundaries. No real Anchor, Navidrome, Android, playback, queue, or cache code was introduced.

## Requirements coverage

All functional requirements (FR01–FR12) and non-functional requirements (NFR01–NFR08) are addressed.

| FR | Requirement | Status |
|----|-------------|--------|
| FR01 | `AnchorControlClient` satisfies `ControlClient` protocol structurally | Implemented — `isinstance(adapter, ControlClient)` passes |
| FR02 | Delegates to Anchor public API helpers, maps to Aria types | Implemented — all methods call `_call_anchor_helper` and map via `AnchorResultMapper` |
| FR03 | Only calls Anchor public API facade helpers | Implemented — no provider internals called |
| FR04 | Operates in offline/dry-run only; `send_lifecycle_intent` preview-only | Implemented — uses `*_dry_run` helpers or returns `APPLY_MODE_BLOCKED` |
| FR05 | Output mapping through `ResultMappingService` | Implemented — `_call_anchor_helper` uses `ResultMappingService.ok/err` |
| FR06 | Handles missing `noqlen_anchor` gracefully | Implemented — `_guard_not_available()` check in all methods |
| FR07 | Tests mock Anchor public API helpers | Implemented — all 103 tests use `unittest.mock.MagicMock` |
| FR08 | Dedicated module under `src/noqlen_aria/` | Implemented — `src/noqlen_aria/anchor_adapter.py` |
| FR09 | Supports status, diagnostics, readiness, capability summary, lifecycle preview | Implemented — all flows mapped |
| FR10 | Sanitizes outputs | Implemented — no secrets, raw logs, or paths in outputs |
| FR11 | Preserves source-agnostic architecture | Implemented — no Anchor types leak into contract layer |
| FR12 | Dry-run/apply safety boundary enforced | Implemented — `APPLY_MODE_BLOCKED` for lifecycle apply |

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | No runtime dependency on `noqlen_anchor` | Implemented — lazy import with try/except ImportError |
| NFR02 | All tests run without `noqlen_anchor` installed | Verified — no `noqlen_anchor` package present |
| NFR03 | No additions to `pyproject.toml` | Verified |
| NFR04 | No network/filesystem/subprocess calls | Verified — Mock objects only |
| NFR05 | Public names documented in English | Verified — docstrings on all classes and methods |
| NFR06 | Bloco 1 contract types for all I/O | Verified |
| NFR07 | Deterministic tests | Verified — repeated runs produce identical results |
| NFR08 | Python 3.11+, stdlib only | Verified — only `dataclasses`, `typing`, `unittest.mock` |

## Files changed

Implementation:

Created:

- `src/noqlen_aria/anchor_adapter.py` — `AnchorControlClient` + `AnchorResultMapper` (475 lines)
- `tests/test_anchor_adapter.py` — comprehensive adapter tests (103 test cases)

Modified:

- `aria/specs/features/anchor-control-dry-run-adapter/tasks.md` — all tasks marked complete
- `aria/specs/features/anchor-control-dry-run-adapter/review.md` — updated with implementation review
- `docs/handoff.md` — Bloco 3 status note

No source files, test files, or configuration files modified outside spec scope.

## Validation performed

Implementation validation:

- `pwd` — confirmed working directory
- `git status --short --branch` — only expected changes
- `git diff --check` — no whitespace issues
- `find` — all source, test, and spec files present
- `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean (4 files)
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works
- `python3 -m pytest` — 229/229 passed (2 + 48 + 76 + 103)
- Repository contamination check — clean

## Validation notes

- `noqlen_anchor` is not installed in this environment. The adapter's `_get_anchor()` returns `None`. All 103 tests use mocked Anchor modules injected via constructor.
- Anchor public API callable names are based on the candidate names from the planning context. Confirmation against a real `noqlen_anchor` package is deferred to a future integration block.
- The `is_anchor_available()` test patches `_get_anchor` directly for reliable testing.

## Non-goals check

| Non-goal | Status |
|---|---|
| No Anchor provider internals | Pass — only `noqlen_anchor.public_api` targeted |
| No Anchor CLI integration | Pass — no subprocess or CLI calls |
| No real Navidrome execution | Pass — mocked only |
| No real Jellyfin/Emby/Navidrome direct media source integration | Pass |
| No real lifecycle apply operations | Pass — `APPLY_MODE_BLOCKED` enforced |
| No real music library access | Pass |
| No Android SDK, Kotlin, Java, or Gradle | Pass |
| No playback engine, queue, now playing, cache/offline | Pass |
| No UI/screen/navigation/player code | Pass |
| No unrelated refactors | Pass |
| No additions to pyproject.toml | Pass |

## Risks remaining

- R01: Anchor public API callable names are unconfirmed. The adapter uses candidate names from the planning context. When a real `noqlen_anchor` package becomes available, the exact helper names must be confirmed and the adapter updated if needed.
- R02: `AnchorResultMapper` mapping logic makes assumptions about Anchor output shapes (dict-based). If the real Anchor public API returns different shapes (e.g., dataclasses, named tuples), the mapper may need adjustment.
- R03: `_get_anchor()` targets `noqlen_anchor.public_api`. If the actual Anchor public API module has a different name, the import path must be updated.

## Known limitations

- `AnchorResultMapper` does not have a standalone `to_lifecycle_preview` method. Lifecycle preview is handled inline in `send_lifecycle_intent` via dry-run helper calls.
- The adapter's `get_readiness()` has a fallback composition path when `get_readiness_report` is not available, but does not call `run_diagnostics` separately. Readiness warnings are derived from server/library connectivity only in the fallback path.
- `DiagnosticsViewState` is populated only by `get_readiness` (fallback) and `AnchorResultMapper.to_readiness_view_state`. No standalone `collect_diagnostics()` method exists on the adapter.
- Anchor public API callable names are candidate names only; exact confirmation requires access to the `noqlen_anchor` package.

## Follow-up tasks

- Confirm Anchor public API callable names against the real `noqlen_anchor` package when available.
- Update helper name references in `anchor_adapter.py` if the actual Anchor API differs.
- Expand `AnchorResultMapper` mapping logic for any additional Anchor output shapes.
- Add standalone `collect_diagnostics()` or `get_diagnostics()` method if a dedicated Anchor diagnostics helper becomes available.
- Formal Blocos 1–3 audit (planned after this implementation).
- Bloco 4: Android boundary contracts.

## Aria context updates needed

- `docs/handoff.md`: Updated with Bloco 3 completion status.
- `aria/specs/features/anchor-control-dry-run-adapter/`: All spec files updated with implementation details.

## Spec approval

- [x] Spec reviewed and approved for implementation.
- [x] Implementation complete and validated.
