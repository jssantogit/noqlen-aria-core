# Review

## Summary

Bloco 1 implementation (Aria Core Contracts) is complete. The implementation delivers all 12 contract types defined by the spec, plus comprehensive TDD tests, using a single `contracts.py` module and a single `test_contracts.py` file. No external dependencies were added. All 50 tests pass.

### Naming refinement (Bloco 1 refinement)

After initial Bloco 1 implementation, contract names were generalized to avoid Anchor-centric architecture:

| Original name | Refined name | Reason |
|---|---|---|
| `AnchorClient` | `ControlClient` | Source-agnostic control-plane boundary; Anchor is a future adapter |
| `FakeAnchorClient` | `FakeControlClient` | Deterministic fake for the generic boundary |
| `ReadinessViewState.anchor_configured` | `ReadinessViewState.control_configured` | Field reflects control client status, not Anchor-specific config |

Anchor-specific naming (`AnchorControlClient`, Anchor API adapter) is reserved for future adapter documentation only. No `AnchorControlClient` code exists. Media source boundaries (`MediaSourceClient`) are separate future contracts.

## Requirements coverage

All functional requirements (FR01–FR14) and non-functional requirements (NFR01–NFR06) are addressed.

| FR | Requirement | Status |
|----|-------------|--------|
| FR01 | `AriaResult` structured result type | Implemented |
| FR02 | `AriaError` with code and message | Implemented |
| FR03 | `AriaWarning` structured warning type | Implemented |
| FR04 | `ServerViewState` server connectivity | Implemented |
| FR05 | `LibraryViewState` library metadata | Implemented |
| FR06 | `DiagnosticsViewState` diagnostic snapshots | Implemented |
| FR07 | `ReadinessViewState` composite readiness | Implemented |
| FR08 | `LifecycleIntent` enum for lifecycle | Implemented |
| FR09 | `PermissionState` permission status | Implemented |
| FR10 | `StorageAccessState` storage availability | Implemented |
| FR11 | `ControlClient` protocol/interface (source-agnostic) | Implemented |
| FR12 | `FakeControlClient` deterministic fake | Implemented |
| FR13 | Dedicated module under `src/noqlen_aria/` | Implemented |
| FR14 | No network/filesystem/external process calls | Implemented |

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR01 | UI-independent contracts only | No UI code |
| NFR02 | Fake-first: FakeControlClient for all local tests | All tests use fake |
| NFR03 | No runtime deps beyond Python 3.11+ stdlib | Only `dataclasses`, `enum`, `typing` |
| NFR04 | Importable as `noqlen_aria.contracts` | Verified |
| NFR05 | Public names explicit, stable, documented | Docstrings on all types |
| NFR06 | No Android/Navidrome/Anchor internals leaked | No such references |

## Files changed

Implementation commit. Files created:

- `src/noqlen_aria/contracts.py` — all contract definitions (165 lines)
- `tests/test_contracts.py` — comprehensive tests (50 test cases)

Files modified:

- `aria/specs/features/aria-core-contracts/tasks.md` — all tasks marked complete
- `aria/specs/features/aria-core-contracts/review.md` — updated with implementation review

No source files, test files, or configuration files modified outside spec scope.

## Validation performed

Implementation validation:

- `git status --short --branch` — only expected untracked files
- `git diff --check` — no whitespace issues
- `python3 -m py_compile src/noqlen_aria/*.py` — compiles clean
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help` — works
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` — works
- `python3 -m pytest` — 50/50 passed (2 Bloco 0 + 48 Bloco 1 tests)
- Repository contamination check — clean

## Contract implementation details

### AriaResult[T]
- Generic dataclass with `ok: bool`, `data: T | None`, `error: AriaError | None`
- `is_ok()` / `is_err()` convenience methods
- Frozen for immutability
- 10 tests covering success, failure, generics, edge cases

### AriaError / AriaWarning
- Frozen dataclasses with `code: str` and `message: str`
- `code` uses `UPPER_SNAKE_CASE` convention
- 5 tests covering construction, immutability, equality

### View states
- `ServerViewState`: connected, server_url, server_version, latency_ms, last_error
- `LibraryViewState`: available, artist/album/track counts, duration, last_scan
- `DiagnosticsViewState`: warnings list with `field(default_factory=list)`
- `ReadinessViewState`: composite of server, library, diagnostics + anchor_configured + all_ready
- All frozen dataclasses with sensible defaults
- 10 tests covering defaults, explicit values, composition, immutability

### LifecycleIntent
- Enum: INITIALIZE, SHUTDOWN, RESET
- Uses `auto()` for values
- 5 tests covering membership, distinct values, unknown value rejection, string roundtrip

### PermissionState / StorageAccessState
- PermissionState: UNKNOWN, GRANTED, DENIED, NOT_APPLICABLE
- StorageAccessState: UNKNOWN, AVAILABLE, UNAVAILABLE
- 5 tests covering membership, distinct values

### ControlClient
- `@runtime_checkable Protocol` with 7 methods (source-agnostic boundary; Anchor is one future adapter)
- `ping`, `get_server_state`, `get_library_state`, `get_readiness`, `send_lifecycle_intent`, `get_permission_state`, `get_storage_access_state`
- `@runtime_checkable` decorator added for runtime isinstance checks (slight deviation from design spec which didn't mention it, but necessary for TDD structural typing tests per tasks.md)
- 2 tests covering structural typing and method presence

### FakeControlClient
- Non-frozen dataclass implementing all ControlClient methods
- Deterministic: returns same values on every call with same inputs
- No network/filesystem/external process calls
- 12 tests covering each method, determinism, calls-before-setup, mutability, compositional consistency

## Non-goals check

| Non-goal | Status |
|---|---|
| No real Anchor integration | Pass — fake only |
| No Anchor provider internals | Pass |
| No Anchor CLI as integration layer | Pass |
| No direct Navidrome access | Pass |
| No Android SDK or UI | Pass |
| No playback implementation | Pass |
| No queue implementation | Pass |
| No cache/offline implementation | Pass |
| No real music library access | Pass |
| No UI/product behavior | Pass |

## Known limitations

- `ControlClient` method set is source-agnostic and may expand in later blocks (per R01 in design).
- `FakeControlClient` returns optimistic defaults (always connected, always available). No failure-injection hooks yet. Left for future blocks.
- `DiagnosticsViewState` only carries warnings; no performance metrics or health scores.
- No `__init__.py` re-exports — consumers import directly from `noqlen_aria.contracts`.

## Follow-up items

- Bloco 2: build services on top of source-agnostic `ControlClient` boundary.
- Bloco 3: AnchorControlClient adapter (offline/dry-run only).
- Bloco 2+: Consider adding failure-injection hooks to FakeControlClient.
- Bloco 2+: Consider adding `AriaResult.ok(data)` / `AriaResult.err(error)` factory functions.
- Bloco 2+: Consider expanding `DiagnosticsViewState` with additional diagnostics fields as needed.

## Aria context updates needed

- `aria/context/architecture.md`: Updated `AnchorClient` boundary to generic `ControlClient` boundary; clarified Anchor is a future adapter.
- `docs/aria-core-handoff.md`: Updated Bloco 1 target names and ecosystem position language.
- `docs/handoff.md`: Updated Bloco 1 status note with generic naming.
- `aria/specs/features/aria-core-contracts/`: All spec files updated with naming refinement rationale.
