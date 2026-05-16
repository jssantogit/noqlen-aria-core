# Tasks

## Preparation checklist

- [ ] Read `aria/specs/features/anchor-control-dry-run-adapter/requirements.md`.
- [ ] Read `aria/specs/features/anchor-control-dry-run-adapter/design.md`.
- [ ] Confirm Bloco 0 + Bloco 1 + Bloco 2 validation passes (CLI help, doctor, py_compile, pytest — 126 tests).
- [ ] Confirm `src/noqlen_aria/anchor_adapter.py` and `tests/test_anchor_adapter.py` do not exist yet.
- [ ] Confirm `pyproject.toml` has no external dependencies to add.
- [ ] Locate and confirm Anchor public API callable names from the current Anchor public API module (`noqlen_anchor.public_api` or equivalent).
- [ ] Confirm which candidate Anchor public API surfaces have matching helpers and which are absent.

## TDD classification

### Required for TDD

- `AnchorResultMapper` output mapping: translating Anchor output shapes into Aria contract types (`ServerViewState`, `LibraryViewState`, `ReadinessViewState`, `DiagnosticsViewState`, `PermissionState`, `StorageAccessState`). TDD is required because incorrect mapping silently produces wrong app-facing states that downstream consumers rely on. Every mapping function must be verified against known Anchor output shapes.
- `AnchorControlClient` behavior when `noqlen_anchor` is not installed: every method must return `AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", ...))`. TDD is required because missing dependency handling must never crash the application and must produce consistent error results.
- `AnchorControlClient.send_lifecycle_intent` apply-mode blocking: must never execute real lifecycle operations. Must return preview-only result or `APPLY_MODE_BLOCKED` error. TDD is required because accidental apply-mode execution could trigger destructive real-world operations.

### Recommended for TDD

- `AnchorControlClient` diagnostics/readiness adapter flows: methods like `get_readiness()` and `get_diagnostics()` call multiple Anchor helpers and compose their outputs. TDD recommended to verify composition correctness, error propagation, and warning collection.
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

- [ ] Examine the current Anchor public API module (e.g., `noqlen_anchor.public_api` or equivalent).
- [ ] Confirm exact callable names for each candidate surface: server status/health, library metadata (Navidrome offline/dry-run), readiness/safety summary, diagnostics, config dry-run/render, Android integration report, storage access report.
- [ ] Document confirmed callable names in the implementation review.
- [ ] For any candidate surface with no matching Anchor helper, document the gap and plan the `ANCHOR_HELPER_NOT_FOUND` error path.
- [ ] Validate: confirmed names are documented; gap analysis is complete.

### Task 1: Create source file skeleton

- [ ] Create `src/noqlen_aria/anchor_adapter.py` with module docstring, lazy import mechanism (`_get_anchor()`), and placeholder classes (`AnchorControlClient`, `AnchorResultMapper`).
- [ ] Create `tests/test_anchor_adapter.py` with test imports, pytest markers, and mock setup utilities.
- [ ] Validate: `python3 -m py_compile src/noqlen_aria/anchor_adapter.py` passes.
- [ ] Validate: module importable when `noqlen_anchor` is not installed.
- [ ] Validate: `AnchorControlClient.is_anchor_available()` returns `False` when `noqlen_anchor` is not installed.

### Task 2: Implement Anchor not-available behavior

- [ ] Write TDD tests for `AnchorControlClient.ping()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.get_server_state()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.get_library_state()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.get_readiness()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.send_lifecycle_intent()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.get_permission_state()` when `noqlen_anchor` is not installed.
- [ ] Write TDD tests for `AnchorControlClient.get_storage_access_state()` when `noqlen_anchor` is not installed.
- [ ] Implement the `self._anchor is None` guard in every method, returning `ANCHOR_NOT_AVAILABLE` error.
- [ ] Validate: all not-available tests pass.

### Task 3: Implement AnchorResultMapper

- [ ] Write TDD tests for `AnchorResultMapper.to_server_view_state(...)` with mock Anchor server output.
- [ ] Write TDD tests for `AnchorResultMapper.to_library_view_state(...)` with mock Anchor library output.
- [ ] Write TDD tests for `AnchorResultMapper.to_readiness_view_state(...)` with mock Anchor readiness output.
- [ ] Write TDD tests for `AnchorResultMapper.to_diagnostics_view_state(...)` with mock Anchor diagnostics output.
- [ ] Write TDD tests for `AnchorResultMapper.to_lifecycle_preview(...)` with mock Anchor plan/dry-run output.
- [ ] Write TDD tests for `AnchorResultMapper.to_permission_state(...)` with mock Anchor permission/integration output.
- [ ] Write TDD tests for `AnchorResultMapper.to_storage_access_state(...)` with mock Anchor storage output.
- [ ] Write TDD tests for each mapper method when mock Anchor output is `None`, malformed, or missing expected fields.
- [ ] Implement `AnchorResultMapper` class with static mapping methods.
- [ ] Validate: all mapper tests pass.

### Task 4: Implement AnchorControlClient server/lifecycle methods

- [ ] Write TDD tests for `ping()` with mocked Anchor server status helper (success case).
- [ ] Write TDD tests for `get_server_state()` with mocked Anchor server status/inspection helper.
- [ ] Write TDD tests for `get_server_state()` when mocked Anchor helper returns unexpected data shape.
- [ ] Write TDD tests for `get_server_state()` when mocked Anchor helper raises an exception.
- [ ] Write TDD tests for `send_lifecycle_intent(INITIALIZE)` with mocked Anchor config dry-run helper (preview-only).
- [ ] Write TDD tests for `send_lifecycle_intent(SHUTDOWN)` with mocked Anchor config dry-run helper.
- [ ] Write TDD tests for `send_lifecycle_intent(RESET)` with mocked Anchor config dry-run helper.
- [ ] Write TDD tests for `send_lifecycle_intent(...)` when Anchor dry-run helper is not available (returns `APPLY_MODE_BLOCKED`).
- [ ] Write TDD tests confirming `send_lifecycle_intent` never calls real apply/execution helpers.
- [ ] Implement `ping()`, `get_server_state()`, `send_lifecycle_intent()` in `AnchorControlClient`.
- [ ] Validate: all tests pass.

### Task 5: Implement AnchorControlClient library/permissions/storage methods

- [ ] Write TDD tests for `get_library_state()` with mocked Anchor Navidrome offline/dry-run helper.
- [ ] Write TDD tests for `get_library_state()` when mocked Anchor helper raises an exception.
- [ ] Write TDD tests for `get_permission_state()` with mocked Anchor Android integration report helper.
- [ ] Write TDD tests for `get_permission_state()` when mocked Anchor helper returns unknown permission status.
- [ ] Write TDD tests for `get_storage_access_state()` with mocked Anchor config dry-run/render helper.
- [ ] Write TDD tests for `get_storage_access_state()` when mocked Anchor helper returns unexpected data.
- [ ] Implement `get_library_state()`, `get_permission_state()`, `get_storage_access_state()` in `AnchorControlClient`.
- [ ] Validate: all tests pass.

### Task 6: Implement AnchorControlClient readiness/diagnostics methods

- [ ] Write TDD tests for `get_readiness()` with mocked Anchor readiness/safety summary helper (all-ready scenario).
- [ ] Write TDD tests for `get_readiness()` with mocked Anchor helper returning partial readiness (server up, library down).
- [ ] Write TDD tests for `get_readiness()` with mocked Anchor helper returning `control_configured=False`.
- [ ] Write TDD tests for `get_readiness()` when mocked Anchor readiness helper raises an exception.
- [ ] Write TDD tests for `get_readiness()` when mocked Anchor readiness helper returns unexpected data shape.
- [ ] Write TDD tests for diagnostic warning collection via mocked Anchor helpers.
- [ ] Implement `get_readiness()` in `AnchorControlClient`.
- [ ] Validate: all tests pass.

### Task 7: Integration tests with Aria services

- [ ] Write integration tests: pass `AnchorControlClient` (mocked Anchor API) to `StatusService` and verify correct behavior.
- [ ] Write integration tests: pass `AnchorControlClient` to `DiagnosticsService` and verify warning collection with mocked Anchor data.
- [ ] Write integration tests: pass `AnchorControlClient` to `LifecycleIntentService` and verify preview flow.
- [ ] Write integration tests: pass `AnchorControlClient` to `ReadinessService` and verify `all_ready` computation with mocked Anchor data.
- [ ] Write integration tests: confirm services work identically whether the underlying `ControlClient` is `FakeControlClient` or `AnchorControlClient` (mocked) for equivalent data.
- [ ] Validate: all integration tests pass; no regression in Bloco 2 tests (126 tests).

### Task 8: Final validation

- [ ] Run full validation suite: `py_compile`, import check, pytest (all tests), contamination check.
- [ ] Confirm no regression in Bloco 0 + Bloco 1 + Bloco 2 tests.
- [ ] Confirm no forbidden files tracked.
- [ ] Update `docs/handoff.md` with Bloco 3 completion status note.
- [ ] Commit implementation artifacts with focused commit message.

## Subagent packages

None required for Bloco 3. The implementation is a single adapter file, a single test file, and no modifications to existing source modules. If implementation complexity grows (e.g., multiple Anchor helper mapping variants, complex error recovery), subagent packages may be defined.

## Validation checklist

- [ ] `pwd` — confirmed working directory.
- [ ] `git status --short --branch` — only expected changes (anchor_adapter.py + test_anchor_adapter.py).
- [ ] `git diff --check` — no whitespace issues.
- [ ] `find aria/specs/features/anchor-control-dry-run-adapter -maxdepth 3 -type f | sort` — all spec files present.
- [ ] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean (including anchor_adapter.py).
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [ ] `python3 -m pytest` — all tests pass (Bloco 0 + 1 + 2 + 3).
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [ ] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [ ] Confirm non-goals: no Anchor provider internals, no Anchor CLI, no real Navidrome, no real apply operations, no real music library, no Android, no playback, no queue, no cache.
- [ ] Confirm no source code changed outside spec scope (during spec phase: no source changes at all).
- [ ] Confirm no `pyproject.toml` changed.
- [ ] Confirm Anchor public API callable names confirmed and documented.
- [ ] Confirm all `ControlClient` protocol methods are implemented.
- [ ] Confirm `send_lifecycle_intent` is blocked from real apply execution.
- [ ] Confirm `ANCHOR_NOT_AVAILABLE` behavior when `noqlen_anchor` is not installed.
- [ ] Confirm `AnchorResultMapper` handles unexpected/malformed Anchor outputs.
- [ ] Confirm sanitized outputs: no secrets, raw logs, personal paths.
- [ ] Confirm no local/private/tooling artifacts staged.
- [ ] Confirm spec completeness: requirements, design, tasks, review all present.
- [ ] Confirm TDD classification is explicit.
- [ ] Confirm integration with existing Aria services works.
