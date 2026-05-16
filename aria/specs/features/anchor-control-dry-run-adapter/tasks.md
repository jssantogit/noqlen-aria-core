# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/anchor-control-dry-run-adapter/requirements.md`.
- [x] Read `aria/specs/features/anchor-control-dry-run-adapter/design.md`.
- [x] Confirm Bloco 0 + Bloco 1 + Bloco 2 validation passes (CLI help, doctor, py_compile, pytest — 126 tests).
- [x] Confirm `src/noqlen_aria/anchor_adapter.py` and `tests/test_anchor_adapter.py` do not exist yet.
- [x] Confirm `pyproject.toml` has no external dependencies to add.
- [x] Locate and confirm Anchor public API callable names from the current Anchor public API module (`noqlen_anchor.public_api` or equivalent). — No real `noqlen_anchor` package is available in this environment. Used the candidate names from the planning context as the adapter's target helper names. Exact names must be confirmed when `noqlen_anchor` becomes available.
- [x] Confirm which candidate Anchor public API surfaces have matching helpers and which are absent. — No real Anchor package; all candidate surfaces are implemented as target helpers, with `ANCHOR_HELPER_NOT_FOUND` error path for any absent helper.

## TDD classification

### Required for TDD

- `AnchorResultMapper` output mapping: translating Anchor output shapes into Aria contract types (`ServerViewState`, `LibraryViewState`, `ReadinessViewState`, `DiagnosticsViewState`, `PermissionState`, `StorageAccessState`). TDD is required because incorrect mapping silently produces wrong app-facing states that downstream consumers rely on. Every mapping function must be verified against known Anchor output shapes.
- `AnchorControlClient` behavior when `noqlen_anchor` is not installed: every method must return `AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", ...))`. TDD is required because missing dependency handling must never crash the application and must produce consistent error results.
- `AnchorControlClient.send_lifecycle_intent` apply-mode blocking: must never execute real lifecycle operations. Must return preview-only result or `APPLY_MODE_BLOCKED` error. TDD is required because accidental apply-mode execution could trigger destructive real-world operations.

### Recommended for TDD

- `AnchorControlClient` diagnostics/readiness adapter flows: methods like `get_readiness()` call multiple Anchor helpers and compose their outputs via fallback composition. TDD recommended to verify composition correctness, error propagation, and warning collection.
- `AnchorControlClient` config dry-run adapter flow: `send_lifecycle_intent` calling Anchor dry-run/plan helpers for preview. TDD recommended to verify that dry-run helpers are called without apply-mode side effects.
- Anchor public API helper exception handling: mocked Anchor helpers raising exceptions; adapter must catch and wrap into `AriaResult(ok=False, ...)`. TDD recommended to verify robust error handling.
- Anchor public API helper returning unexpected data shapes: adapter must handle gracefully, returning safe error results or fallback values. TDD recommended to verify defensive mapping.

### TDD approach

1. Write a failing test for the adapter method/behavior with mocked Anchor API.
2. Implement the minimum code to pass.
3. Refactor while keeping tests green.
4. Commit each adapter method group atomically.

## Implementation tasks

### Task 0: Confirm Anchor public API callable names

- [x] Examine the current Anchor public API module (e.g., `noqlen_anchor.public_api` or equivalent). — No `noqlen_anchor` package is available in this environment.
- [x] Confirm exact callable names for each candidate surface. — Used the candidate names from the planning context as adapter helper targets.
- [x] Document confirmed callable names in the implementation review.
- [x] For any candidate surface with no matching Anchor helper, document the gap and plan the `ANCHOR_HELPER_NOT_FOUND` error path.
- [x] Validate: confirmed names are documented; gap analysis is complete.

### Task 1: Create source file skeleton

- [x] Create `src/noqlen_aria/anchor_adapter.py` with module docstring, lazy import mechanism (`_get_anchor()`), and placeholder classes (`AnchorControlClient`, `AnchorResultMapper`).
- [x] Create `tests/test_anchor_adapter.py` with test imports, pytest markers, and mock setup utilities.
- [x] Validate: `python3 -m py_compile src/noqlen_aria/anchor_adapter.py` passes.
- [x] Validate: module importable when `noqlen_anchor` is not installed.
- [x] Validate: `AnchorControlClient.is_anchor_available()` returns `False` when `noqlen_anchor` is not installed.

### Task 2: Implement Anchor not-available behavior

- [x] Write TDD tests for `AnchorControlClient.ping()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.get_server_state()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.get_library_state()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.get_readiness()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.send_lifecycle_intent()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.get_permission_state()` when `noqlen_anchor` is not installed.
- [x] Write TDD tests for `AnchorControlClient.get_storage_access_state()` when `noqlen_anchor` is not installed.
- [x] Implement the `self._anchor is None` guard in every method, returning `ANCHOR_NOT_AVAILABLE` error.
- [x] Validate: all not-available tests pass.

### Task 3: Implement AnchorResultMapper

- [x] Write TDD tests for `AnchorResultMapper.to_server_view_state(...)` with mock Anchor server output.
- [x] Write TDD tests for `AnchorResultMapper.to_library_view_state(...)` with mock Anchor library output.
- [x] Write TDD tests for `AnchorResultMapper.to_readiness_view_state(...)` with mock Anchor readiness output.
- [x] Write TDD tests for `AnchorResultMapper.to_diagnostics_view_state(...)` with mock Anchor diagnostics output.
- [x] Write TDD tests for `AnchorResultMapper.to_permission_state(...)` with mock Anchor permission/integration output.
- [x] Write TDD tests for `AnchorResultMapper.to_storage_access_state(...)` with mock Anchor storage output.
- [x] Write TDD tests for each mapper method when mock Anchor output is `None`, malformed, or missing expected fields.
- [x] Implement `AnchorResultMapper` class with static mapping methods.
- [x] Validate: all mapper tests pass.

### Task 4: Implement AnchorControlClient server/lifecycle methods

- [x] Write TDD tests for `ping()` with mocked Anchor server status helper (success case).
- [x] Write TDD tests for `get_server_state()` with mocked Anchor server status/inspection helper.
- [x] Write TDD tests for `get_server_state()` when mocked Anchor helper returns unexpected data shape.
- [x] Write TDD tests for `get_server_state()` when mocked Anchor helper raises an exception.
- [x] Write TDD tests for `send_lifecycle_intent(INITIALIZE)` with mocked Anchor config dry-run helper (preview-only).
- [x] Write TDD tests for `send_lifecycle_intent(SHUTDOWN)` with mocked Anchor config dry-run helper.
- [x] Write TDD tests for `send_lifecycle_intent(RESET)` with mocked Anchor config dry-run helper.
- [x] Write TDD tests for `send_lifecycle_intent(...)` when Anchor dry-run helper is not available (returns `APPLY_MODE_BLOCKED`).
- [x] Write TDD tests confirming `send_lifecycle_intent` never calls real apply/execution helpers.
- [x] Implement `ping()`, `get_server_state()`, `send_lifecycle_intent()` in `AnchorControlClient`.
- [x] Validate: all tests pass.

### Task 5: Implement AnchorControlClient library/permissions/storage methods

- [x] Write TDD tests for `get_library_state()` with mocked Anchor Navidrome offline/dry-run helper.
- [x] Write TDD tests for `get_library_state()` when mocked Anchor helper raises an exception.
- [x] Write TDD tests for `get_permission_state()` with mocked Anchor Android integration report helper.
- [x] Write TDD tests for `get_permission_state()` when mocked Anchor helper returns unknown permission status.
- [x] Write TDD tests for `get_storage_access_state()` with mocked Anchor config dry-run/render helper.
- [x] Write TDD tests for `get_storage_access_state()` when mocked Anchor helper returns unexpected data.
- [x] Implement `get_library_state()`, `get_permission_state()`, `get_storage_access_state()` in `AnchorControlClient`.
- [x] Validate: all tests pass.

### Task 6: Implement AnchorControlClient readiness/diagnostics methods

- [x] Write TDD tests for `get_readiness()` with mocked Anchor readiness/safety summary helper (all-ready scenario).
- [x] Write TDD tests for `get_readiness()` with mocked Anchor helper returning partial readiness (server up, library down).
- [x] Write TDD tests for `get_readiness()` with mocked Anchor helper returning `control_configured=False`.
- [x] Write TDD tests for `get_readiness()` when mocked Anchor readiness helper raises an exception.
- [x] Write TDD tests for `get_readiness()` when mocked Anchor readiness helper returns unexpected data shape.
- [x] Write TDD tests for diagnostic warning collection via mocked Anchor helpers (via fallback composition in get_readiness).
- [x] Implement `get_readiness()` in `AnchorControlClient`.
- [x] Validate: all tests pass.

### Task 7: Integration tests with Aria services

- [x] Write integration tests: pass `AnchorControlClient` (mocked Anchor API) to `StatusService` and verify correct behavior.
- [x] Write integration tests: pass `AnchorControlClient` to `DiagnosticsService` and verify warning collection with mocked Anchor data.
- [x] Write integration tests: pass `AnchorControlClient` to `LifecycleIntentService` and verify preview flow.
- [x] Write integration tests: pass `AnchorControlClient` to `ReadinessService` and verify `all_ready` computation with mocked Anchor data.
- [x] Write integration tests: confirm services work identically whether the underlying `ControlClient` is `FakeControlClient` or `AnchorControlClient` (mocked) for equivalent data.
- [x] Validate: all integration tests pass; no regression in Bloco 2 tests (126 tests).

### Task 8: Final validation

- [x] Run full validation suite: `py_compile`, import check, pytest (all tests), contamination check.
- [x] Confirm no regression in Bloco 0 + Bloco 1 + Bloco 2 tests. — 229 tests pass (2 + 48 + 76 + 103).
- [x] Confirm no forbidden files tracked.
- [x] Update `docs/handoff.md` with Bloco 3 completion status note.
- [x] Commit implementation artifacts with focused commit message.

## Subagent packages

None required for Bloco 3. The implementation is a single adapter file, a single test file, and no modifications to existing source modules. If implementation complexity grows (e.g., multiple Anchor helper mapping variants, complex error recovery), subagent packages may be defined.

## Validation checklist

- [x] `pwd` — confirmed working directory.
- [x] `git status --short --branch` — only expected changes (anchor_adapter.py + test_anchor_adapter.py).
- [x] `git diff --check` — no whitespace issues.
- [x] `find aria/specs/features/anchor-control-dry-run-adapter -maxdepth 3 -type f | sort` — all spec files present.
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean (including anchor_adapter.py).
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [x] `python3 -m pytest` — all tests pass (229: 2 + 48 + 76 + 103).
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [x] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [x] Confirm non-goals: no Anchor provider internals, no Anchor CLI, no real Navidrome, no real apply operations, no real music library, no Android, no playback, no queue, no cache.
- [x] Confirm no source code changed outside spec scope.
- [x] Confirm no `pyproject.toml` changed.
- [x] Confirm Anchor public API callable names confirmed and documented. — Used candidate names from planning context; exact names require confirmation against real `noqlen_anchor` package when available.
- [x] Confirm all `ControlClient` protocol methods are implemented. — All 7 methods plus `is_anchor_available()` static check.
- [x] Confirm `send_lifecycle_intent` is blocked from real apply execution. — Returns `APPLY_MODE_BLOCKED` when dry-run helpers are absent; uses only `*_dry_run` helpers when available.
- [x] Confirm `ANCHOR_NOT_AVAILABLE` behavior when `noqlen_anchor` is not installed.
- [x] Confirm `AnchorResultMapper` handles unexpected/malformed Anchor outputs.
- [x] Confirm sanitized outputs: no secrets, raw logs, personal paths.
- [x] Confirm no local/private/tooling artifacts staged.
- [x] Confirm spec completeness: requirements, design, tasks, review all present.
- [x] Confirm TDD classification is explicit.
- [x] Confirm integration with existing Aria services works.
