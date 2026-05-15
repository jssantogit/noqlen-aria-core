# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/aria-core-contracts/requirements.md`.
- [x] Read `aria/specs/features/aria-core-contracts/design.md`.
- [x] Confirm Bloco 0 validation passes (CLI help, doctor, py_compile, pytest).
- [x] Confirm no source/test files exist at `src/noqlen_aria/contracts.py` or `tests/test_contracts.py`.
- [x] Confirm `pyproject.toml` has no external dependencies to add.

## TDD classification

### Required for TDD

- `AriaResult` mapping: ok/failure discrimination and error propagation. TDD is required because incorrect result mapping silently breaks all downstream consumers.
- `LifecycleIntent` behavior: enum completeness and dispatch correctness. TDD is required because lifecycle bugs cause unrecoverable application states.

### Recommended for TDD

- View-state constructors and defaults: `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState`. TDD recommended to ensure default values are consistent and composable.
- `FakeAnchorClient` behavior: return types, return values, and deterministic behavior. TDD recommended because the fake is the foundation for all local tests in later blocks.

### TDD approach

1. Write a failing test for the contract/behavior.
2. Implement the minimum code to pass.
3. Refactor while keeping tests green.
4. Commit each contract/group atomically.

## Implementation tasks

### Task 1: Create source file skeleton

- [x] Create `src/noqlen_aria/contracts.py` with module docstring and imports.
- [x] Create `tests/test_contracts.py` with test imports and pytest markers.
- [x] Validate: `python3 -m py_compile src/noqlen_aria/contracts.py` passes.

### Task 2: Implement AriaResult, AriaError, AriaWarning

- [x] Define `AriaError`, `AriaWarning` dataclasses.
- [x] Define `AriaResult[T]` with `ok`, `data`, `error` fields.
- [x] Write TDD tests for success case, error case, and edge cases.
- [x] Validate: pytest passes for result/error/warning tests.

### Task 3: Implement view-state contracts

- [x] Define `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState` dataclasses.
- [x] Write tests for default values and composition.
- [x] Validate: imports work, tests pass.

### Task 4: Implement LifecycleIntent enum

- [x] Define `LifecycleIntent` enum with `INITIALIZE`, `SHUTDOWN`, `RESET`.
- [x] Write tests for enum membership and value handling.
- [x] Validate: tests pass.

### Task 5: Implement PermissionState and StorageAccessState enums

- [x] Define `PermissionState` enum with `UNKNOWN`, `GRANTED`, `DENIED`, `NOT_APPLICABLE`.
- [x] Define `StorageAccessState` enum with `UNKNOWN`, `AVAILABLE`, `UNAVAILABLE`.
- [x] Write tests for enum membership and default factory usage.
- [x] Validate: tests pass.

### Task 6: Implement AnchorClient protocol

- [x] Define `AnchorClient` as a `typing.Protocol` with all proposed methods.
- [x] Decorated with `@runtime_checkable` for structural typing verification at runtime.
- [x] Write structural typing verification tests (e.g., `isinstance(FakeAnchorClient(), AnchorClient)`).
- [x] Validate: tests pass.

### Task 7: Implement FakeAnchorClient

- [x] Implement `FakeAnchorClient` with deterministic fake returns for all `AnchorClient` methods.
- [x] Write TDD tests for each method: verify return type, return values, and determinism.
- [x] Test edge cases: repeated calls, calls before any setup.
- [x] Validate: all FakeAnchorClient tests pass.

### Task 8: Final validation

- [x] Run full validation suite: `py_compile`, import check, pytest, contamination check.
- [x] Confirm no regression in Bloco 0 tests.
- [x] Confirm no forbidden files tracked.
- [x] Commit implementation artifacts.

## Subagent packages

None required for Bloco 1. The implementation is a single source file and a single test file. If implementation complexity grows, subagent packages may be defined in a future block.

## Validation checklist

- [x] `pwd` — confirmed working directory.
- [x] `git status --short --branch` — clean or only expected changes.
- [x] `git diff --check` — no whitespace issues.
- [x] `find aria/specs/features/aria-core-contracts -maxdepth 3 -type f | sort` — all spec files present.
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [x] `python3 -m pytest` — 50/50 passed.
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [x] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [x] Confirm non-goals: no real Anchor, no Navidrome, no Android, no playback, no queue, no cache.
- [x] Confirm no source code changed outside spec scope.
- [x] Confirm no pyproject.toml changed.
- [x] Confirm no local/private/tooling artifacts staged.
- [x] Confirm spec completeness: requirements, design, tasks, review all present.
- [x] Confirm TDD classification is explicit.
- [x] Confirm contract list matches requirements.
