# Tasks

## Preparation checklist

- [x] Read `aria/specs/features/fake-control-state-mapping/requirements.md`.
- [x] Read `aria/specs/features/fake-control-state-mapping/design.md`.
- [x] Confirm Bloco 0 + Bloco 1 validation passes (CLI help, doctor, py_compile, pytest — 50 tests).
- [x] Confirm `src/noqlen_aria/services.py` and `tests/test_services.py` do not exist yet.
- [x] Confirm `pyproject.toml` has no external dependencies to add.
- [x] Confirm `FakeControlClient` currently has no failure-injection hooks.

## TDD classification

### Required for TDD

- `ResultMappingService`: result normalization, factory helpers (`ok`, `err`), unwrap/unwrap_or, and error mapping. TDD is required because incorrect result mapping silently breaks all downstream consumers. Every service depends on consistent result shapes.
- `LifecycleIntentService` preview behavior: intent validation, preview generation, and rejection of invalid intents. TDD is required because lifecycle bugs cause unrecoverable application states. The preview must accurately describe each intent and validate identity without side effects.

### Recommended for TDD

- `StatusService`: server status composition and ping-to-state mapping. TDD recommended to ensure connectivity status is correctly derived from ControlClient data, including error propagation.
- `DiagnosticsService`: warning collection, threshold-based warning generation (latency, staleness), and aggregate composition. TDD recommended because diagnostic accuracy is critical for debugging and readiness assessment.
- `ReadinessService`: composite readiness from server, library, and diagnostics. TDD recommended because `all_ready` is a critical gate for downstream operations.
- `FakeControlClient` scenario behavior: failure-injection hooks and override values. TDD recommended because the fake is the foundation for all service tests; incorrect hook behavior invalidates every downstream test.

### TDD approach

1. Write a failing test for the service/behavior.
2. Implement the minimum code to pass.
3. Refactor while keeping tests green.
4. Commit each service group atomically.

## Implementation tasks

### Task 1: Add failure-injection hooks to FakeControlClient

- [x] Add `_*_error` fields to `FakeControlClient` for each `ControlClient` method (ping, server_state, library_state, readiness, lifecycle, permission_state, storage_access).
- [x] Add `_*_override` fields for fine-grained value overrides (server_state, library_state, readiness, permission_state, storage_access).
- [x] Update each `FakeControlClient` method: check error hook first, then override hook, then return default.
- [x] Write tests verifying error-injection and override-injection behavior.
- [x] Write tests verifying backward compatibility: untouched fake still returns optimistic defaults.
- [x] Write tests verifying determinism is preserved when hooks are set.
- [x] Validate: all existing 48 Bloco 1 tests still pass; new FakeControlClient hook tests pass.

### Task 2: Implement ResultMappingService

- [x] Write TDD tests for `ResultMappingService.ok(data)` — creates successful result.
- [x] Write TDD tests for `ResultMappingService.err(code, message)` — creates failure result.
- [x] Write TDD tests for `ResultMappingService.unwrap(result)` — extracts data on success, raises on error.
- [x] Write TDD tests for `ResultMappingService.unwrap_or(result, default)` — extracts data or returns default.
- [x] Write TDD tests for `ResultMappingService.map_error(result, code, message)` — rewrites error on failure, passes through on success.
- [x] Implement `ResultMappingService` class with static methods.
- [x] Validate: all tests pass.

### Task 3: Implement LifecycleIntentPreview and LifecycleIntentService

- [x] Write TDD tests for `LifecycleIntentPreview` construction and immutability.
- [x] Write TDD tests for `LifecycleIntentService.preview(INITIALIZE)` — returns correct preview.
- [x] Write TDD tests for `LifecycleIntentService.preview(SHUTDOWN)` — returns correct preview.
- [x] Write TDD tests for `LifecycleIntentService.preview(RESET)` — returns correct preview.
- [x] Write TDD tests for `LifecycleIntentService.validate("INITIALIZE")` — returns enum value.
- [x] Write TDD tests for `LifecycleIntentService.validate("SHUTDOWN")` — returns enum value.
- [x] Write TDD tests for `LifecycleIntentService.validate("RESET")` — returns enum value.
- [x] Write TDD tests for `LifecycleIntentService.validate("BOGUS")` — returns error result.
- [x] Write TDD tests confirming preview does NOT call `ControlClient.send_lifecycle_intent`.
- [x] Implement `LifecycleIntentPreview` frozen dataclass.
- [x] Implement `LifecycleIntentService` class.
- [x] Validate: all tests pass.

### Task 4: Implement StatusService

- [x] Write TDD tests for `StatusService` with connected `FakeControlClient`.
- [x] Write TDD tests for `StatusService` with disconnected `FakeControlClient` (injected ping error).
- [x] Write TDD tests for `StatusService` when server returns `last_error`.
- [x] Write TDD tests confirming `get_status()` returns `AriaResult[ServerViewState]`.
- [x] Implement `StatusService` class.
- [x] Validate: all tests pass.

### Task 5: Implement DiagnosticsService

- [x] Write TDD tests for `DiagnosticsService` with all-green `FakeControlClient` (no warnings).
- [x] Write TDD tests for latency exceeding threshold (injects high-latency override via FakeControlClient).
- [x] Write TDD tests for library staleness exceeding threshold (injects old last_scan_timestamp override).
- [x] Write TDD tests for server error scenario (injects server_state_error on FakeControlClient).
- [x] Write TDD tests for missing library scan timestamp (`last_scan_timestamp=None`).
- [x] Write TDD tests for configurable thresholds (non-default max_latency_ms, max_library_staleness_seconds).
- [x] Write TDD tests confirming multiple warnings are collected together.
- [x] Implement `DiagnosticsService` class.
- [x] Validate: all tests pass.

### Task 6: Implement ReadinessService

- [x] Write TDD tests for `ReadinessService.assess()` with fully-ready `FakeControlClient`.
- [x] Write TDD tests for `ReadinessService.assess()` when server is disconnected (injected server_state_error).
- [x] Write TDD tests for `ReadinessService.assess()` when library is unavailable (injected library_state_override with available=False).
- [x] Write TDD tests for `ReadinessService.assess()` when `control_configured=False` (injected readiness_override).
- [x] Write TDD tests for `ReadinessService.assess()` when diagnostics has warnings.
- [x] Write TDD tests for partial readiness scenarios (server up but library down, library up but server down).
- [x] Write TDD tests confirming `all_ready` is True only when all conditions are met.
- [x] Write TDD tests for error propagation when underlying `ControlClient` call fails.
- [x] Implement `ReadinessService` class.
- [x] Validate: all tests pass.

### Task 7: Final validation

- [x] Run full validation suite: `py_compile`, import check, pytest (all tests), contamination check.
- [x] Confirm no regression in Bloco 0 + Bloco 1 tests.
- [x] Confirm no forbidden files tracked.
- [x] Update `docs/handoff.md` with Bloco 2 completion status note.
- [x] Commit implementation artifacts with focused commit message.

## Subagent packages

None required for Bloco 2. The implementation is a single service file, a single test file, and minimal additions to `contracts.py`. If implementation complexity grows, subagent packages may be defined in a future block.

## Validation checklist

- [x] `pwd` — confirmed working directory.
- [x] `git status --short --branch` — only expected changes (contracts.py modified, services.py + test_services.py untracked).
- [x] `git diff --check` — no whitespace issues.
- [x] `find aria/specs/features/fake-control-state-mapping -maxdepth 3 -type f | sort` — all spec files present.
- [x] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [x] `python3 -m pytest` — 126/126 passed (2 Bloco 0 + 48 Bloco 1 + 76 Bloco 2).
- [x] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.

## Review checklist

- [x] Confirm non-goals: no real Anchor, no Navidrome, no Android, no playback, no queue, no cache.
- [x] Confirm no source code changed outside spec scope.
- [x] Confirm no pyproject.toml changed.
- [x] Confirm no local/private/tooling artifacts staged.
- [x] Confirm spec completeness: requirements, design, tasks, review all present.
- [x] Confirm TDD classification is explicit.
- [x] Confirm service list matches requirements (5 services).
- [x] Confirm FakeControlClient failure-injection design is defined.
