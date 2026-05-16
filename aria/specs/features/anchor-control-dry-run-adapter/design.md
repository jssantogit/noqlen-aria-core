# Design

## Summary

Create `src/noqlen_aria/anchor_adapter.py` containing the `AnchorControlClient` class — a concrete `ControlClient` adapter that delegates to Anchor public API helpers in offline/dry-run mode only. Create `tests/test_anchor_adapter.py` with mocked Anchor API tests. No other source or test files are created. No external dependencies are added to `pyproject.toml`. The adapter must work when `noqlen_anchor` is installed (calling real public API helpers) but must not crash when it is absent (returning safe error results). Tests use `unittest.mock` to fake Anchor public API helpers, requiring no real Anchor or Navidrome.

## Context files read

- `AGENTS.md`
- `docs/aria-core-handoff.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/architecture.md`
- `aria/context/conventions.md`
- `aria/context/forbidden-patterns.md`
- `aria/context/future-product-context.md`
- `aria/context/mistakes.md`
- `aria/review/validation-checklist.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/aria-core-contracts/requirements.md`
- `aria/specs/features/aria-core-contracts/design.md`
- `aria/specs/features/aria-core-contracts/tasks.md`
- `aria/specs/features/aria-core-contracts/review.md`
- `aria/specs/features/fake-control-state-mapping/requirements.md`
- `aria/specs/features/fake-control-state-mapping/design.md`
- `aria/specs/features/fake-control-state-mapping/tasks.md`
- `aria/specs/features/fake-control-state-mapping/review.md`
- `docs/handoff.md`
- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/cli.py`
- `tests/test_contracts.py`
- `tests/test_services.py`
- `tests/test_cli.py`

## Existing project context

Bloco 1 and Bloco 2 are complete. The `ControlClient` protocol defines seven source-agnostic methods (`ping`, `get_server_state`, `get_library_state`, `get_readiness`, `send_lifecycle_intent`, `get_permission_state`, `get_storage_access_state`). `FakeControlClient` provides deterministic fakes with 14 failure-injection/value-override hooks. The service layer (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) consumes `ControlClient` via constructor injection. 126 tests pass (2 Bloco 0 + 48 Bloco 1 + 76 Bloco 2).

`AnchorControlClient` is the first real `ControlClient` adapter. It bridges the gap between Aria's source-agnostic contracts and Anchor's public API helpers. The adapter must implement all seven `ControlClient` methods by calling Anchor public API helper functions and mapping their outputs into Aria contract types.

Anchor is a future external dependency. At spec time, the exact callable names in the Anchor public API are not confirmed. The adapter design must:

1. Document the candidate Anchor public API surfaces it expects to call.
2. Guard all Anchor imports so the module is importable without `noqlen_anchor` installed.
3. Use mocking in tests so no real Anchor package is needed.

Future flow:
```
Future UI/App -> Aria Core services -> ControlClient protocol
                                          |
                                          ├── FakeControlClient (Bloco 1/2, tests)
                                          └── AnchorControlClient adapter (Bloco 3+)
                                                   └── Anchor public API helpers
```

Bloco 3 is a spec/planning phase. Implementation is a later phase after spec review.

## Files to create

Source (targeted for implementation phase, not created now):

- `src/noqlen_aria/anchor_adapter.py` — `AnchorControlClient` class plus optional `AnchorResultMapper` helper class.

Tests (targeted for implementation phase, not created now):

- `tests/test_anchor_adapter.py` — tests using `unittest.mock` for all Anchor public API helpers.

Spec (created now):

- `aria/specs/features/anchor-control-dry-run-adapter/requirements.md`
- `aria/specs/features/anchor-control-dry-run-adapter/design.md`
- `aria/specs/features/anchor-control-dry-run-adapter/tasks.md`
- `aria/specs/features/anchor-control-dry-run-adapter/review.md`

## Files to modify

During implementation (not now):

- `docs/handoff.md` — update Bloco 3 status note (optional, tiny).

During implementation (not now):

- `aria/context/mistakes.md` — only if a real workflow mistake is discovered (optional).

During spec phase (now):

- None.

## Files that must not be touched

- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/__init__.py`
- `pyproject.toml`
- `tests/test_contracts.py`
- `tests/test_services.py`
- `tests/test_cli.py`
- All `docs/*.md` (except `docs/handoff.md` for optional status note during implementation)
- All `aria/context/*.md` (except `mistakes.md` if a real workflow mistake is discovered)
- All `aria/review/*.md`
- All `aria/specs/features/aria-core-contracts/*.md`
- All `aria/specs/features/fake-control-state-mapping/*.md`
- `AGENTS.md`
- `.git/info/exclude`
- Any `Android`, `Kotlin`, `Java`, `Gradle` files (none exist)
- Any secret, credential, log, cache, or temporary file

## Expected source module layout (`src/noqlen_aria/anchor_adapter.py`)

Proposed contents for implementation phase (not created now). Exact Anchor public API callable names are placeholders; they must be confirmed during implementation from the current Anchor public API module:

```python
"""Anchor Control Client adapter — dry-run/offline implementation of ControlClient.

All Anchor public API calls are guarded behind optional imports.
When noqlen_anchor is not installed, all methods return safe error results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    AriaWarning,
    ControlClient,
    DiagnosticsViewState,
    LibraryViewState,
    LifecycleIntent,
    PermissionState,
    ReadinessViewState,
    ServerViewState,
    StorageAccessState,
)

# ── Lazy Anchor import ──────────────────────────────────────────

_anchor_module: Any = None

def _get_anchor() -> Any:
    """Lazily import and cache the Anchor public API module.

    Returns the module object if available, otherwise None.
    Does NOT import Anchor provider internals.
    """
    global _anchor_module
    if _anchor_module is not None:
        return _anchor_module
    try:
        import noqlen_anchor.public_api as _anchor_module  # type: ignore[import-untyped]
    except ImportError:
        _anchor_module = None
    return _anchor_module


# ── AnchorResultMapper ──────────────────────────────────────────

class AnchorResultMapper:
    """Maps Anchor public API helper outputs into Aria contract types.

    Pure mapping functions; no side effects, no Anchor imports at class level.
    """

    @staticmethod
    def to_server_view_state(anchor_server_output: Any) -> ServerViewState:
        """Map Anchor server status output to ServerViewState."""
        ...

    @staticmethod
    def to_library_view_state(anchor_library_output: Any) -> LibraryViewState:
        """Map Anchor library metadata output to LibraryViewState."""
        ...

    @staticmethod
    def to_readiness_view_state(anchor_readiness_output: Any) -> ReadinessViewState:
        """Map Anchor readiness/safety summary output to ReadinessViewState."""
        ...

    @staticmethod
    def to_diagnostics_view_state(anchor_diagnostics_output: Any) -> DiagnosticsViewState:
        """Map Anchor diagnostics output to DiagnosticsViewState."""
        ...

    @staticmethod
    def to_lifecycle_preview(anchor_plan_output: Any, intent: LifecycleIntent) -> AriaResult[bool]:
        """Map Anchor config dry-run/plan output to a lifecycle preview result.

        Returns ok=True with data=True if the dry-run succeeds; never executes apply.
        """
        ...

    @staticmethod
    def to_permission_state(anchor_permission_output: Any) -> PermissionState:
        """Map Anchor permission/integration report output to PermissionState."""
        ...

    @staticmethod
    def to_storage_access_state(anchor_storage_output: Any) -> StorageAccessState:
        """Map Anchor storage/render output to StorageAccessState."""
        ...


# ── AnchorControlClient ─────────────────────────────────────────

class AnchorControlClient:
    """Concrete ControlClient adapter backed by Anchor public API helpers.

    Operates in offline/dry-run mode. All lifecycle methods return
    preview-only results; apply-mode is blocked.

    Does NOT call Anchor provider internals, Anchor CLI, or Navidrome directly.
    Does NOT access real music libraries.
    Sanitizes all outputs before returning.

    When noqlen_anchor is not installed, all methods return
    AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", ...)).
    """

    def __init__(self) -> None:
        self._anchor = _get_anchor()

    @staticmethod
    def is_anchor_available() -> bool:
        """Return True if the Anchor public API module is importable."""
        return _get_anchor() is not None

    def ping(self) -> AriaResult[bool]:
        """Check Anchor connectivity via public API server status helper."""
        ...

    def get_server_state(self) -> AriaResult[ServerViewState]:
        """Get server state via Anchor public API server status/inspection helper."""
        ...

    def get_library_state(self) -> AriaResult[LibraryViewState]:
        """Get library state via Anchor public API Navidrome offline/dry-run helper."""
        ...

    def get_readiness(self) -> AriaResult[ReadinessViewState]:
        """Get composite readiness via Anchor readiness/safety summary helpers."""
        ...

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        """Preview lifecycle intent via Anchor config dry-run/render helpers.

        IMPORTANT: This method does NOT execute real lifecycle operations.
        It uses Anchor dry-run helpers to produce a preview/simulation result.
        If no dry-run helper is available, returns AriaError(code="APPLY_MODE_BLOCKED").
        """
        ...

    def get_permission_state(self) -> AriaResult[PermissionState]:
        """Get permission state via Anchor Android integration report/plan helpers."""
        ...

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        """Get storage access state via Anchor config dry-run/render helpers."""
        ...
```

### Candidate Anchor public API surfaces to map

The following Anchor public API surfaces are expected to be available and will be confirmed during implementation from the current Anchor public API module. The adapter will call the corresponding helpers for each `ControlClient` method:

| ControlClient method | Candidate Anchor public API helper | Expected output shape |
|---|---|---|
| `ping()` | server status / health / inspection helper | boolean or server info dict |
| `get_server_state()` | server status / inspection helper | server metadata (URL, version, latency, errors) |
| `get_library_state()` | Navidrome offline/dry-run metadata helper | library metadata (artist/album/track counts, duration, last scan) |
| `get_readiness()` | readiness / safety summary helper | composite readiness with server + library + diagnostics |
| `send_lifecycle_intent()` | config dry-run / render helper | dry-run plan result (never executes apply) |
| `get_permission_state()` | Android integration report / plan helper | permission status report |
| `get_storage_access_state()` | config dry-run / render helper | storage/render access status |

Exact callable names are NOT defined in this spec. Implementation must:
1. Locate the current Anchor public API module.
2. Confirm the exact callable names matching the candidate surfaces above.
3. Document the confirmed callable names in the implementation review.
4. If a candidate surface has no matching Anchor helper, return `AriaResult(ok=False, error=AriaError(code="ANCHOR_HELPER_NOT_FOUND", ...))`.

## Data flow

```
Future UI/App
    |
    v
Aria Core services (StatusService, DiagnosticsService, etc.)
    |
    v
ControlClient (protocol)
    |
    ├── FakeControlClient (tests, deterministic fake data)
    │
    └── AnchorControlClient
            |
            ├── [noqlen_anchor installed]
            │       |
            │       v
            │   Anchor public API helpers
            │       |
            │       v
            │   AnchorResultMapper
            │       |
            │       v
            │   AriaResult-wrapped contract types
            │
            └── [noqlen_anchor NOT installed]
                    |
                    v
                AriaResult(ok=False, error=AriaError("ANCHOR_NOT_AVAILABLE"))
```

In Bloco 3 implementation:
1. Tests mock Anchor public API helpers via `unittest.mock.patch`.
2. Tests instantiate `AnchorControlClient` with mocked Anchor module.
3. Tests call `ControlClient` protocol methods on the adapter.
4. Tests assert that:
   - Returned values match `AriaResult`-wrapped Aria contract types.
   - Anchor mapped outputs correctly translate into `ServerViewState`, `LibraryViewState`, etc.
   - When mocked Anchor raises an exception, the adapter returns `AriaResult(ok=False, ...)`.
   - When mocked Anchor returns unexpected data shapes, the adapter returns safe error results.
   - `send_lifecycle_intent` never calls real apply (returns preview-only or `APPLY_MODE_BLOCKED`).
   - When `noqlen_anchor` is not importable, all methods return `ANCHOR_NOT_AVAILABLE` errors.
5. No real Anchor package, Navidrome, network, or filesystem is used.

## Adapter role within the ControlClient boundary

The `ControlClient` protocol is source-agnostic. Anchor is one future adapter among potentially many. The architecture enforces:

```
Aria Core services → ControlClient (protocol)
                         ↑
                         |
              +----------+-----------+
              |                      |
    FakeControlClient       AnchorControlClient (future)
    (deterministic, tests)  (offline/dry-run, real Anchor API)
```

- `AnchorControlClient` does NOT subclass `ControlClient`. It implements the protocol structurally (satisfies `@runtime_checkable`).
- `AnchorControlClient` does NOT import `ControlClient` for anything other than type annotations.
- The adapter's internal mapping logic (`AnchorResultMapper`) is separate from the adapter itself for independent testability.
- Services that consume `ControlClient` are unaware of whether they are talking to `FakeControlClient` or `AnchorControlClient`.
- No Anchor-specific types or naming conventions appear in the `ControlClient` protocol or Aria contract types.

## How Anchor outputs map through existing ResultMappingService

`AnchorResultMapper` is the primary translation layer. It converts Anchor public API output shapes into Aria contract types. For methods where additional normalization is needed:

1. `AnchorControlClient` calls Anchor public API helper.
2. `AnchorResultMapper` converts the raw Anchor output into the target Aria contract type.
3. If the Anchor call succeeds and mapping succeeds, `ResultMappingService.ok(mapped_data)` wraps the result.
4. If the Anchor call fails or mapping fails, `ResultMappingService.err(code, message)` wraps the error.
5. The `AriaResult` is returned to the caller.

This ensures consistent result shapes across all `ControlClient` implementations.

## Error handling

- All adapter methods return `AriaResult[...]`. No unhandled exceptions propagate to callers.
- `AnchorControlClient.__init__` lazily imports Anchor; if import fails, `self._anchor` is `None`.
- Every method checks `if self._anchor is None` and returns `AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", message="Anchor public API is not available"))`.
- When an Anchor public API helper is called but the helper is not found (no matching candidate surface), returns `AriaResult(ok=False, error=AriaError(code="ANCHOR_HELPER_NOT_FOUND", ...))`.
- When an Anchor public API helper raises an exception, the adapter catches it and returns `AriaResult(ok=False, error=AriaError(code="ANCHOR_CALL_FAILED", ...))`.
- When an Anchor public API helper returns unexpected data shapes, `AnchorResultMapper` returns safe fallback values where possible, or the adapter returns `AriaResult(ok=False, error=AriaError(code="ANCHOR_UNEXPECTED_OUTPUT", ...))`.
- `send_lifecycle_intent` always returns `AriaResult(ok=False, error=AriaError(code="APPLY_MODE_BLOCKED", message="Apply-mode lifecycle operations are blocked in dry-run adapter"))` if no Anchor dry-run helper is available for the intent. If a dry-run/plan helper is available, it returns a preview result without executing apply.
- All error codes use `UPPER_SNAKE_CASE` convention.
- Unsanitized data from Anchor is filtered before appearing in `AriaError.message` or `AriaWarning.message`.

## Security considerations

- No secrets, tokens, URLs, or credentials in adapter definitions.
- No network calls in the adapter code itself (Anchor API helpers are called, but the adapter does not initiate HTTP/network calls directly).
- No filesystem access in the adapter code.
- No subprocess execution in the adapter code.
- No real Navidrome access in any mode.
- `send_lifecycle_intent` is explicitly blocked from executing real apply operations.
- All Anchor return values are sanitized: no raw logs, no personal paths, no provider-internal error messages in output.
- When `noqlen_anchor` is not installed, the module imports cleanly with no side effects.

## Dependencies

- Runtime: Python 3.11+ standard library (`dataclasses`, `typing`, `unittest.mock` for tests only).
- Internal: `noqlen_aria.contracts` (already defined in Bloco 1).
- Optional (not required for import): `noqlen_anchor` public API module (lazily imported, guarded).
- No additions to `pyproject.toml`.
- No third-party packages.

## Risks

- R01: Anchor public API callable names are uncertain at spec time. Mitigation: spec documents candidate surfaces; implementation must confirm exact names from the current Anchor public API module before writing adapter code.
- R02: Anchor public API output shapes may not match the expected mapping targets. Mitigation: `AnchorResultMapper` handles unexpected shapes gracefully; implementation can add mapping cases for additional Anchor output variants.
- R03: Tests that mock Anchor API helpers may diverge from real Anchor API behavior if the Anchor public API evolves. Mitigation: tests mock the Anchor public API contract, not internal implementation; the spec explicitly requires confirmation from the current Anchor public API module before implementation.
- R04: `AnchorControlClient` may be misused in production if the dry-run safety is bypassed. Mitigation: `send_lifecycle_intent` is explicitly blocked with `APPLY_MODE_BLOCKED` error; a future apply-mode adapter block will handle real lifecycle operations.
- R05: `AnchorResultMapper` mapping logic may be incomplete for some ControlClient methods. Mitigation: implementation can add mapping methods incrementally; the spec documents candidate Anchor surfaces for each method.
- R06: The lazy import mechanism may cause confusing errors if Anchor is partially available (installed but broken). Mitigation: `_get_anchor()` catches `ImportError`; any other import error is also caught and returns `None`.

## Rollback strategy

If the adapter design is found to be incorrect during implementation, edit `anchor_adapter.py` and `test_anchor_adapter.py` in a focused commit. If the adapter approach is fundamentally wrong (e.g., Anchor public API surface is incompatible with the `ControlClient` contract), revert the implementation commit and redesign. The spec files may be updated to reflect corrected requirements.

Before implementation, the spec must be reviewed against the confirmed Anchor public API callable names. If the Anchor public API surface differs significantly from the candidate surfaces documented in this spec, the spec will be updated during implementation planning.

## Validation plan

During this spec-only phase:
1. Run existing Bloco 0 + Bloco 1 + Bloco 2 validation commands (CLI help, CLI doctor, py_compile, pytest — 126 tests).
2. Confirm no source/test files were created.
3. Run repository contamination check.
4. Confirm `git diff --check` is clean.
5. Commit spec files only.

During later implementation phase:
1. Confirm Anchor public API callable names from the current Anchor public API module.
2. Create `src/noqlen_aria/anchor_adapter.py`.
3. Run `python3 -m py_compile src/noqlen_aria/anchor_adapter.py`.
4. Run `PYTHONPATH=src python3 -c "import noqlen_aria.anchor_adapter"`.
5. Create `tests/test_anchor_adapter.py` with TDD mocked tests.
6. Run `python3 -m pytest tests/test_anchor_adapter.py -v`.
7. Run `python3 -m pytest tests/test_services.py -v` with `AnchorControlClient` (mocked) to confirm services work with the adapter.
8. Run full validation suite (py_compile, pytest all, contamination check).
9. Update `docs/handoff.md` with Bloco 3 status note.
