# Review

## Status

Complete — Bloco 2 implementation is finished. 126 tests pass (2 Bloco 0 + 48 Bloco 1 + 76 Bloco 2).

## Summary

Bloco 2 implementation delivers all five services defined by the spec (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) plus `LifecycleIntentPreview` in a single `services.py` module. `FakeControlClient` was extended with 14 failure-injection/value-override hooks. All 76 service tests pass using only `FakeControlClient`. No external dependencies were added. No real Anchor, Navidrome, Android, playback, queue, or cache code exists.

## Requirements coverage

All functional requirements (FR01–FR14) and non-functional requirements (NFR01–NFR07) are addressed.

| FR | Requirement | Status |
|----|-------------|--------|
| FR01 | `ResultMappingService` normalizes raw results | Implemented |
| FR02 | `StatusService` composes server state | Implemented |
| FR03 | `DiagnosticsService` collects warnings | Implemented |
| FR04 | `LifecycleIntentService` validates/previews | Implemented |
| FR05 | `ReadinessService` produces composite readiness | Implemented |
| FR06 | Constructor injection of `ControlClient` | Implemented |
| FR07 | All returns are `AriaResult`-wrapped | Implemented |
| FR08 | Services work with `FakeControlClient` | Implemented |
| FR09 | `FakeControlClient` failure-injection hooks | Implemented |
| FR10 | `ResultMappingService` factory helpers | Implemented |
| FR11 | `LifecycleIntentPreview` without execution | Implemented |
| FR12 | `DiagnosticsService` warning thresholds | Implemented |
| FR13 | Dedicated module under `src/noqlen_aria/` | Implemented |
| FR14 | No network/filesystem/external process calls | Implemented |

## Non-functional requirements

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | No extra deps beyond Python 3.11+ stdlib | Only `dataclasses`, `typing`, `time`, `TYPE_CHECKING` |
| NFR02 | Testable with `FakeControlClient` only | All 76 tests use `FakeControlClient` |
| NFR03 | Simple attribute-assignment hooks | `fake._ping_error = AriaError(...)` |
| NFR04 | Bloco 1 contract types as I/O | All signatures use `contracts.py` types |
| NFR05 | Stable, documented public names | Docstrings on all classes and methods |
| NFR06 | Importable without side effects | `from noqlen_aria.services import StatusService` works |
| NFR07 | Deterministic tests | Repeated runs produce identical results |

## Files changed

Implementation:

Created:

- `src/noqlen_aria/services.py` — all five services + `LifecycleIntentPreview` (artifacts: 227 lines)
- `tests/test_services.py` — comprehensive service tests (76 test cases)

Modified:

- `src/noqlen_aria/contracts.py` — added 14 failure-injection/value-override hooks to `FakeControlClient`
- `aria/specs/features/fake-control-state-mapping/tasks.md` — all tasks marked complete
- `aria/specs/features/fake-control-state-mapping/review.md` — updated with implementation review
- `docs/handoff.md` — Bloco 2 status note (tiny)

No source files, test files, or configuration files modified outside spec scope.

## Validation performed

Implementation validation:

- `git status --short --branch` — only expected changes
- `git diff --check` — no whitespace issues
- `find` — all source, test, and spec files present
- `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean (including services.py)
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works
- `python3 -m pytest` — 126/126 passed
- Repository contamination check — clean

## Non-goals check

| Non-goal | Status |
|---|---|
| No real Anchor adapter | Pass — fake only |
| No media source integration | Pass |
| No Navidrome/Jellyfin/Emby integration | Pass |
| No playback engine | Pass |
| No queue implementation | Pass |
| No now playing implementation | Pass |
| No cache/offline implementation | Pass |
| No Android SDK or UI | Pass |
| No CLI expansion | Pass |
| No real music library access | Pass |

## Implementation details

### FakeControlClient hooks (14 new fields)

- 7 error-injection fields: `_ping_error`, `_server_state_error`, `_library_state_error`, `_readiness_error`, `_lifecycle_error`, `_permission_state_error`, `_storage_access_error`
- 5 value-override fields: `_server_state_override`, `_library_state_override`, `_readiness_override`, `_permission_state_override`, `_storage_access_override`
- Priority: error hook > override hook > default
- Error propagation: `get_readiness()` propagates errors from `get_server_state()` and `get_library_state()`
- All hooks are `field(default=None, repr=False)` for clean repr output

### ResultMappingService

- Static methods: `ok(data)`, `err(code, message)`, `unwrap(result)`, `unwrap_or(result, default)`, `map_error(result, code, message)`
- `unwrap()` raises `ResultMappingError` on failure
- `map_error()` rewrites error on failure, passes through on success
- Handles edge cases: ok=True with data=None, ok=False with error=None

### LifecycleIntentPreview + LifecycleIntentService

- `LifecycleIntentPreview`: frozen dataclass with `intent`, `description`, `reversible`, `requires_apply`
- `LifecycleIntentService.preview(intent)`: returns structured preview from hardcoded descriptions; does NOT call `send_lifecycle_intent`
- `LifecycleIntentService.validate(name)`: case-insensitive string-to-enum conversion with error result for invalid names

### StatusService

- `get_status()`: pings via `ControlClient.ping()`, then returns server state via `ControlClient.get_server_state()`
- Error propagation: if ping fails, returns error result

### DiagnosticsService

- `collect()`: checks server latency, server last_error, library staleness, library scan presence, and control configuration
- Configurable thresholds via constructor (`max_latency_ms`, `max_library_staleness_seconds`)
- Always returns `ok=True` (warnings are informational)
- Generates warnings with codes: `LATENCY_HIGH`, `SERVER_LAST_ERROR`, `SERVER_STATE_UNAVAILABLE`, `LIBRARY_NEVER_SCANNED`, `LIBRARY_STALE`, `LIBRARY_STATE_UNAVAILABLE`, `CONTROL_NOT_CONFIGURED`, `READINESS_UNAVAILABLE`

### ReadinessService

- `assess()`: calls `get_server_state()`, `get_library_state()`, `get_readiness()`
- Computes `all_ready` as: server.connected AND library.available AND control_configured AND no diagnostics warnings
- Error propagation: if any underlying call fails, returns error result
- Partial readiness scenarios handled correctly

## Known limitations

- `FakeControlClient` default `last_scan_timestamp` (`1_700_000_000.0`) is from 2023 and triggers library staleness warnings in `DiagnosticsService` by default. Tests override with fresh timestamps when needed. Not fixed in the fake to preserve determinism for other tests.
- `DiagnosticsService` thresholds are constructor parameters; no thread-safe dynamic reconfiguration.
- `LifecycleIntentService` preview descriptions are hardcoded.
- `ReadinessService` recomputes `all_ready` from raw sub-states rather than delegating to `get_readiness()` result. This is intentional to validate the service's own logic.
- No `ResultMappingService` helper for creating results from raw `ControlClient` calls (e.g., `from_client_call`). Consumers call services directly.

## Follow-up items

- Bloco 3: `AnchorControlClient` adapter (offline/dry-run only).
- Bloco 3+: Real `ControlClient` integration with Anchor public API.
- Bloco 4: Android boundary contracts.
- Future: `MediaSourceClient` boundary for library/search/stream/playlists.
- Future: Lifecycle intent execution with explicit apply-mode protection (currently preview-only).
- Bloco 3+: Consider adding `to_dict()` serialization on `LifecycleIntentPreview`.
- Bloco 3+: Consider adding `DiagnosticsService` thread-safe dynamic threshold reconfiguration.

## Aria context updates needed

- `docs/handoff.md`: Updated Bloco 2 status note.
- `aria/specs/features/fake-control-state-mapping/`: All spec files updated with implementation details.

## Spec approval

- [x] Spec reviewed and approved for implementation.
