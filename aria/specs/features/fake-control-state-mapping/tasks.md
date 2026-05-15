# Tasks

## Preparation checklist

- [ ] Read `aria/specs/features/fake-control-state-mapping/requirements.md`.
- [ ] Read `aria/specs/features/fake-control-state-mapping/design.md`.
- [ ] Confirm Bloco 0 + Bloco 1 validation passes (CLI help, doctor, py_compile, pytest — 50 tests).
- [ ] Confirm `src/noqlen_aria/services.py` and `tests/test_services.py` do not exist yet.
- [ ] Confirm `pyproject.toml` has no external dependencies to add.
- [ ] Confirm `FakeControlClient` currently has no failure-injection hooks.

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

- [ ] Add `_*_error` fields to `FakeControlClient` for each `ControlClient` method (ping, server_state, library_state, readiness, lifecycle, permission_state, storage_access).
- [ ] Add `_*_override` fields for fine-grained value overrides (server_state, library_state, readiness, permission_state, storage_access).
- [ ] Update each `FakeControlClient` method: check error hook first, then override hook, then return default.
- [ ] Write tests verifying error-injection and override-injection behavior.
- [ ] Write tests verifying backward compatibility: untouched fake still returns optimistic defaults.
- [ ] Write tests verifying determinism is preserved when hooks are set.
- [ ] Validate: all existing 50 Bloco 1 tests still pass; new FakeControlClient hook tests pass.

### Task 2: Implement ResultMappingService

- [ ] Write TDD tests for `ResultMappingService.ok(data)` — creates successful result.
- [ ] Write TDD tests for `ResultMappingService.err(code, message)` — creates failure result.
- [ ] Write TDD tests for `ResultMappingService.unwrap(result)` — extracts data on success, raises on error.
- [ ] Write TDD tests for `ResultMappingService.unwrap_or(result, default)` — extracts data or returns default.
- [ ] Write TDD tests for `ResultMappingService.map_error(result, code, message)` — rewrites error on failure, passes through on success.
- [ ] Implement `ResultMappingService` class with static methods.
- [ ] Validate: all tests pass.

### Task 3: Implement LifecycleIntentPreview and LifecycleIntentService

- [ ] Write TDD tests for `LifecycleIntentPreview` construction and immutability.
- [ ] Write TDD tests for `LifecycleIntentService.preview(INITIALIZE)` — returns correct preview.
- [ ] Write TDD tests for `LifecycleIntentService.preview(SHUTDOWN)` — returns correct preview.
- [ ] Write TDD tests for `LifecycleIntentService.preview(RESET)` — returns correct preview.
- [ ] Write TDD tests for `LifecycleIntentService.validate("INITIALIZE")` — returns enum value.
- [ ] Write TDD tests for `LifecycleIntentService.validate("SHUTDOWN")` — returns enum value.
- [ ] Write TDD tests for `LifecycleIntentService.validate("RESET")` — returns enum value.
- [ ] Write TDD tests for `LifecycleIntentService.validate("BOGUS")` — returns error result.
- [ ] Write TDD tests confirming preview does NOT call `ControlClient.send_lifecycle_intent`.
- [ ] Implement `LifecycleIntentPreview` frozen dataclass.
- [ ] Implement `LifecycleIntentService` class.
- [ ] Validate: all tests pass.

### Task 4: Implement StatusService

- [ ] Write TDD tests for `StatusService` with connected `FakeControlClient`.
- [ ] Write TDD tests for `StatusService` with disconnected `FakeControlClient` (injected ping error).
- [ ] Write TDD tests for `StatusService` when server returns `last_error`.
- [ ] Write TDD tests confirming `get_status()` returns `AriaResult[ServerViewState]`.
- [ ] Implement `StatusService` class.
- [ ] Validate: all tests pass.

### Task 5: Implement DiagnosticsService

- [ ] Write TDD tests for `DiagnosticsService` with all-green `FakeControlClient` (no warnings).
- [ ] Write TDD tests for latency exceeding threshold (injects high-latency override via FakeControlClient).
- [ ] Write TDD tests for library staleness exceeding threshold (injects old last_scan_timestamp override).
- [ ] Write TDD tests for server error scenario (injects server_state_error on FakeControlClient).
- [ ] Write TDD tests for missing library scan timestamp (`last_scan_timestamp=None`).
- [ ] Write TDD tests for configurable thresholds (non-default max_latency_ms, max_library_staleness_seconds).
- [ ] Write TDD tests confirming multiple warnings are collected together.
- [ ] Implement `DiagnosticsService` class.
- [ ] Validate: all tests pass.

### Task 6: Implement ReadinessService

- [ ] Write TDD tests for `ReadinessService.assess()` with fully-ready `FakeControlClient`.
- [ ] Write TDD tests for `ReadinessService.assess()` when server is disconnected (injected ping error).
- [ ] Write TDD tests for `ReadinessService.assess()` when library is unavailable (injected library_state_override with available=False).
- [ ] Write TDD tests for `ReadinessService.assess()` when `control_configured=False` (injected readiness_override).
- [ ] Write TDD tests for `ReadinessService.assess()` when diagnostics has warnings.
- [ ] Write TDD tests for partial readiness scenarios (server up but library down, library up but server down, etc.).
- [ ] Write TDD tests confirming `all_ready` is True only when all conditions are met.
- [ ] Write TDD tests for error propagation when underlying `ControlClient` call fails.
- [ ] Implement `ReadinessService` class.
- [ ] Validate: all tests pass.

### Task 7: Final validation

- [ ] Run full validation suite: `py_compile`, import check, pytest (all tests), contamination check.
- [ ] Confirm no regression in Bloco 0 + Bloco 1 tests.
- [ ] Confirm no forbidden files tracked.
- [ ] Update `docs/handoff.md` with Bloco 2 completion status note.
- [ ] Commit implementation artifacts with focused commit message.

## Subagent packages

None required for Bloco 2. The implementation is a single service file, a single test file, and minimal additions to `contracts.py`. If implementation complexity grows, subagent packages may be defined in a future block.

## Validation checklist

- [ ] `pwd` — confirmed working directory.
- [ ] `git status --short --branch` — clean or only expected changes.
- [ ] `git diff --check` — no whitespace issues.
- [ ] `find aria/specs/features/fake-control-state-mapping -maxdepth 3 -type f | sort` — all spec files present.
- [ ] `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works.
- [ ] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works.
- [ ] `python3 -m pytest` — all tests pass (50 Bloco 0 + Bloco 1; services tests not yet written).
- [ ] `git ls-files | grep -E '(^\.opencode/|^\.skills/|opencode\.json|docs/development|audit-report|model-routing|\.env|credentials\.json|\.secrets)' || true` — clean.
- [ ] `git show --name-only --oneline --stat HEAD` — only expected files.

## Review checklist

- [ ] Confirm non-goals: no real Anchor, no Navidrome, no Android, no playback, no queue, no cache.
- [ ] Confirm no source code changed outside spec scope (spec phase).
- [ ] Confirm no pyproject.toml changed.
- [ ] Confirm no local/private/tooling artifacts staged.
- [ ] Confirm spec completeness: requirements, design, tasks, review all present.
- [ ] Confirm TDD classification is explicit.
- [ ] Confirm service list matches requirements (5 services).
- [ ] Confirm FakeControlClient failure-injection design is defined.
