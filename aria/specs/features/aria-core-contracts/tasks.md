# Tasks

## Preparation checklist

- [ ] Read `aria/specs/features/aria-core-contracts/requirements.md`.
- [ ] Read `aria/specs/features/aria-core-contracts/design.md`.
- [ ] Confirm Bloco 0 validation passes (CLI help, doctor, py_compile, pytest).
- [ ] Confirm no source/test files exist at `src/noqlen_aria/contracts.py` or `tests/test_contracts.py`.
- [ ] Confirm `pyproject.toml` has no external dependencies to add.

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

- Create `src/noqlen_aria/contracts.py` with module docstring and imports.
- Create `tests/test_contracts.py` with test imports and pytest markers.
- Validate: `python3 -m py_compile src/noqlen_aria/contracts.py` passes.

### Task 2: Implement AriaResult, AriaError, AriaWarning

- Define `AriaError`, `AriaWarning` dataclasses.
- Define `AriaResult[T]` with `ok`, `data`, `error` fields.
- Write TDD tests for success case, error case, and edge cases.
- Validate: pytest passes for result/error/warning tests.

### Task 3: Implement view-state contracts

- Define `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState` dataclasses.
- Write tests for default values and composition.
- Validate: imports work, tests pass.

### Task 4: Implement LifecycleIntent enum

- Define `LifecycleIntent` enum with `INITIALIZE`, `SHUTDOWN`, `RESET`.
- Write tests for enum membership and value handling.
- Validate: tests pass.

### Task 5: Implement PermissionState and StorageAccessState enums

- Define `PermissionState` enum with `UNKNOWN`, `GRANTED`, `DENIED`, `NOT_APPLICABLE`.
- Define `StorageAccessState` enum with `UNKNOWN`, `AVAILABLE`, `UNAVAILABLE`.
- Write tests for enum membership and default factory usage.
- Validate: tests pass.

### Task 6: Implement AnchorClient protocol

- Define `AnchorClient` as a `typing.Protocol` with all proposed methods.
- Write structural typing verification tests (e.g., `isinstance(FakeAnchorClient(), AnchorClient)` or type-checker tests).
- Validate: tests pass.

### Task 7: Implement FakeAnchorClient

- Implement `FakeAnchorClient` with deterministic fake returns for all `AnchorClient` methods.
- Write TDD tests for each method: verify return type, return values, and determinism.
- Test edge cases: repeated calls, calls before any setup.
- Validate: all FakeAnchorClient tests pass.

### Task 8: Final validation

- Run full validation suite: `py_compile`, import check, pytest, contamination check.
- Confirm no regression in Bloco 0 tests.
- Confirm no forbidden files tracked.
- Commit implementation artifacts.

## Subagent packages

None required for Bloco 1. The implementation is a single source file and a single test file. If implementation complexity grows, subagent packages may be defined in a future block.

## Validation checklist

- [ ] `pwd` — confirmed working directory.
- [ ] `git status --short --branch` — clean or only expected changes.
- [ ] `git diff --check` — no whitespace issues.
- [ ] `find aria/specs/features/aria-core-contracts -maxdepth 3 -type f | sort` — all spec files present.
- [ ] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [ ] `python3 -m pytest` — passes when available.
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [ ] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [ ] Confirm non-goals: no real Anchor, no Navidrome, no Android, no playback, no queue, no cache.
- [ ] Confirm no source code changed (spec-only phase).
- [ ] Confirm no tests changed (spec-only phase).
- [ ] Confirm no pyproject.toml changed.
- [ ] Confirm no local/private/tooling artifacts staged.
- [ ] Confirm spec completeness: requirements, design, tasks, review all present.
- [ ] Confirm TDD classification is explicit.
- [ ] Confirm contract list matches requirements.
