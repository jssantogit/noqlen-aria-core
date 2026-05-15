# Design

## Summary

Create a single `src/noqlen_aria/services.py` module containing five services (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) and a corresponding `tests/test_services.py` test file. Extend `FakeControlClient` with failure-injection hooks (mutable attributes) for service testing. No other source or test files are created. No external dependencies are added. All services are deterministic and local-only when used with `FakeControlClient`.

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
- `aria/context/android-player-reference.md`
- `aria/context/allowed-tools.md`
- `aria/context/context-hygiene.md`
- `aria/context/mistakes.md`
- `aria/review/validation-checklist.md`
- `aria/specs/features/aria-core-contracts/requirements.md`
- `aria/specs/features/aria-core-contracts/design.md`
- `aria/specs/features/aria-core-contracts/tasks.md`
- `aria/specs/features/aria-core-contracts/review.md`
- `docs/handoff.md`
- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/cli.py`
- `tests/test_contracts.py`
- `tests/test_cli.py`

## Existing project context

Bloco 1 is complete: `src/noqlen_aria/contracts.py` defines all 12 contract types (`AriaResult[T]`, `AriaError`, `AriaWarning`, `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState`, `LifecycleIntent`, `PermissionState`, `StorageAccessState`, `ControlClient`, `FakeControlClient`). `tests/test_contracts.py` has 50 passing tests. `FakeControlClient` returns optimistic defaults (always connected, always available) with no failure-injection hooks. `ControlClient` is a source-agnostic `@runtime_checkable Protocol`. Anchor is a future adapter only.

Future flow: `Future UI/App -> Aria Core services -> ControlClient -> FakeControlClient (Bloco 2) | AnchorControlClient adapter (future Bloco 3)`

Bloco 2 is the first service layer. It only builds a deterministic fake-driven mapping layer. It does not implement real Anchor integration, media source boundaries, playback, queue, cache, or UI.

## Files to create

Source (targeted for implementation phase, not created now):

- `src/noqlen_aria/services.py` — single module with all five service classes.
- (included within) `FakeControlClient` failure-injection hooks: mutable attributes on the existing `FakeControlClient` class in `contracts.py`.

Tests (targeted for implementation phase, not created now):

- `tests/test_services.py` — tests for all services using `FakeControlClient` with failure-injection hooks.

Spec (created now):

- `aria/specs/features/fake-control-state-mapping/requirements.md`
- `aria/specs/features/fake-control-state-mapping/design.md`
- `aria/specs/features/fake-control-state-mapping/tasks.md`
- `aria/specs/features/fake-control-state-mapping/review.md`

## Files to modify

During implementation (not now):

- `src/noqlen_aria/contracts.py` — add failure-injection hooks to `FakeControlClient`.

During implementation (not now):

- `docs/handoff.md` — update Bloco 2 status note (optional, tiny).

During implementation (not now):

- `aria/context/mistakes.md` — only if a real workflow mistake is discovered (optional).

During spec phase (now):

- None.

## Files that must not be touched

- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/__init__.py`
- `pyproject.toml`
- `tests/test_cli.py`
- `tests/test_contracts.py`
- All `docs/*.md` (except `docs/handoff.md` for optional status note during implementation)
- All `aria/context/*.md` (except `mistakes.md` if a real workflow mistake is discovered)
- All `aria/review/*.md`
- All `aria/specs/features/aria-core-contracts/*.md`
- `AGENTS.md`
- `.git/info/exclude`
- Any `Android`, `Kotlin`, `Java`, `Gradle` files (none exist)
- Any secret, credential, log, cache, or temporary file

## Expected service module layout (`src/noqlen_aria/services.py`)

Proposed contents for implementation phase (not created now):

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from noqlen_aria.contracts import ControlClient

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    AriaWarning,
    DiagnosticsViewState,
    LibraryViewState,
    LifecycleIntent,
    ReadinessViewState,
    ServerViewState,
)

# ── ResultMappingService ─────────────────────────────────────

class ResultMappingService:
    """Normalizes and creates AriaResult instances for app-facing use.

    Provides factory helpers for creating ok/err results and unwrapping
    helpers for extracting data or errors from raw ControlClient results.
    """

    @staticmethod
    def ok(data: T) -> AriaResult[T]:
        """Create a successful result."""
        ...

    @staticmethod
    def err(code: str, message: str) -> AriaResult:
        """Create a failure result with an AriaError."""
        ...

    @staticmethod
    def unwrap(result: AriaResult[T]) -> T:
        """Extract data from a result, raising if result is an error."""
        ...

    @staticmethod
    def unwrap_or(result: AriaResult[T], default: T) -> T:
        """Extract data from a result, returning default on error."""
        ...

    @staticmethod
    def map_error(result: AriaResult, code: str, message: str) -> AriaResult:
        """If result is an error, replace its error code/message."""
        ...


# ── LifecycleIntentPreview ───────────────────────────────────

@dataclass(frozen=True)
class LifecycleIntentPreview:
    """Structured preview of a lifecycle intent effect without execution."""
    intent: LifecycleIntent
    description: str
    reversible: bool
    requires_apply: bool


# ── StatusService ────────────────────────────────────────────

class StatusService:
    """Composes server status into a high-level connectivity response."""

    def __init__(self, client: ControlClient) -> None:
        ...

    def get_status(self) -> AriaResult[ServerViewState]:
        """Ping the server and return the server view state."""
        ...


# ── DiagnosticsService ───────────────────────────────────────

DEFAULT_MAX_LATENCY_MS: int = 200
DEFAULT_MAX_LIBRARY_STALENESS_SECONDS: int = 86400  # 24 hours


class DiagnosticsService:
    """Collects warnings from multiple ControlClient calls into a single
    DiagnosticsViewState aggregate.
    """

    def __init__(
        self,
        client: ControlClient,
        max_latency_ms: int = DEFAULT_MAX_LATENCY_MS,
        max_library_staleness_seconds: int = DEFAULT_MAX_LIBRARY_STALENESS_SECONDS,
    ) -> None:
        ...

    def collect(self) -> AriaResult[DiagnosticsViewState]:
        """Collect and normalize all diagnostic warnings."""
        ...


# ── LifecycleIntentService ───────────────────────────────────

class LifecycleIntentService:
    """Validates and previews lifecycle intents without execution."""

    def __init__(self, client: ControlClient) -> None:
        ...

    def preview(self, intent: LifecycleIntent) -> AriaResult[LifecycleIntentPreview]:
        """Preview the effect of a lifecycle intent without executing it.

        Returns a LifecycleIntentPreview describing the intent.
        Does NOT call ControlClient.send_lifecycle_intent().
        """
        ...

    def validate(self, intent_name: str) -> AriaResult[LifecycleIntent]:
        """Validate a lifecycle intent name string and return the enum value."""
        ...


# ── ReadinessService ─────────────────────────────────────────

class ReadinessService:
    """Produces a composite ReadinessViewState from ControlClient data."""

    def __init__(self, client: ControlClient) -> None:
        ...

    def assess(self) -> AriaResult[ReadinessViewState]:
        """Compute composite readiness from server, library, and diagnostics.

        all_ready is True when:
        - server.connected is True
        - library.available is True
        - diagnostics.warnings is empty
        - control_configured is True
        """
        ...
```

## FakeControlClient failure-injection hooks (extending contracts.py)

Proposed additions to `FakeControlClient` during implementation (not now):

```python
@dataclass
class FakeControlClient:
    # Existing methods remain unchanged.

    # Failure-injection hooks (mutable attributes):
    _ping_error: AriaError | None = field(default=None, repr=False)
    _server_state_error: AriaError | None = field(default=None, repr=False)
    _library_state_error: AriaError | None = field(default=None, repr=False)
    _readiness_error: AriaError | None = field(default=None, repr=False)
    _lifecycle_error: AriaError | None = field(default=None, repr=False)
    _permission_state_error: AriaError | None = field(default=None, repr=False)
    _storage_access_error: AriaError | None = field(default=None, repr=False)

    # Optional: custom return value overrides for fine-grained testing
    _server_state_override: ServerViewState | None = field(default=None, repr=False)
    _library_state_override: LibraryViewState | None = field(default=None, repr=False)
    _readiness_override: ReadinessViewState | None = field(default=None, repr=False)
    _permission_state_override: PermissionState | None = field(default=None, repr=False)
    _storage_access_override: StorageAccessState | None = field(default=None, repr=False)

    # Each method checks its error hook first; if set, returns AriaResult(ok=False, error=...)
    # If no error, checks its override hook; if set, returns the override value.
    # If neither, returns the original optimistic default.
```

This design keeps `FakeControlClient` a regular (non-frozen) dataclass so tests can set `fake._ping_error = AriaError(...)` directly. All injected state is prefixed with `_` and excluded from `repr()`.

## Data flow

```
Future UI -> Aria Core services
                |
                v
         Service receives ControlClient via constructor
                |
                v
         Service calls ControlClient methods
                |
                v
         FakeControlClient returns deterministic data (or injected errors)
                |
                v
         Service normalizes, maps, or composes the data
                |
                v
         Service returns AriaResult-wrapped contract types
                |
                v
         Future UI receives app-facing state
```

In Bloco 2:
1. Tests create `FakeControlClient`, optionally set failure-injection hooks.
2. Tests instantiate services with `FakeControlClient`.
3. Tests call service methods and assert return types, values, and edge cases.
4. No real network, filesystem, or external process is involved.

## Error handling

- Every service method returns `AriaResult[...]`.
- `ResultMappingService.ok()` / `.err()` are the canonical factories for creating results.
- `ResultMappingService.unwrap()` raises on error; `unwrap_or()` provides a safe alternative.
- `ResultMappingService.map_error()` allows propagating a result while rewriting its error.
- `StatusService.get_status()` returns `AriaResult(ok=False, ...)` if ping fails.
- `DiagnosticsService.collect()` always returns `ok=True` (warnings are informational, not failures), but wraps the result in `AriaResult` for API consistency.
- `LifecycleIntentService.preview()` returns `AriaResult(ok=False, ...)` for invalid intents.
- `LifecycleIntentService.validate()` returns `AriaResult(ok=False, ...)` for unknown intent strings.
- `ReadinessService.assess()` returns `AriaResult(ok=False, ...)` if any underlying `ControlClient` call returns an error.
- `FakeControlClient` error hooks use the existing `AriaError` type with `UPPER_SNAKE_CASE` codes.
- Service methods never raise exceptions for product-level errors; they return `AriaResult(ok=False, ...)`.

## Security considerations

- No secrets, tokens, URLs, or credentials in service definitions.
- No network calls in any service method.
- No filesystem access in any service method.
- No subprocess execution in any service method.
- No real Anchor or Navidrome access.
- `FakeControlClient` failure-injection hooks do not expose or persist sensitive data.

## Dependencies

- Runtime: Python 3.11+ standard library (`dataclasses`, `typing`).
- Internal: `noqlen_aria.contracts` (already defined in Bloco 1).
- No additions to `pyproject.toml`.
- No third-party packages.

## Risks

- R01: `FakeControlClient` failure-injection hooks may be misused in production if the fake accidentally reaches production code. Mitigation: `FakeControlClient` is explicitly documented as test-only; production code will use `AnchorControlClient` adapter (future Bloco 3).
- R02: Service method set may be incomplete for future blocks. Mitigation: services are independent classes; adding methods is non-breaking.
- R03: `DiagnosticsService` thresholds (latency, staleness) may need tuning. Mitigation: thresholds are constructor parameters with sensible defaults.
- R04: `LifecycleIntentService.preview()` descriptions are hardcoded and may become stale if lifecycle intents change. Mitigation: preview descriptions are derived from the `LifecycleIntent` enum values; tests enforce consistency.
- R05: `ReadinessService` `all_ready` computation may need additional criteria in future blocks. Mitigation: the `all_ready` logic is isolated in a single method, easy to extend.

## Rollback strategy

If services are found to be incorrect during implementation, edit `services.py` and `test_services.py` in a focused commit. If the service design is fundamentally wrong, revert the implementation commit. The spec files may be updated to reflect corrected requirements.

If `FakeControlClient` failure-injection hooks cause regressions in Bloco 1 tests, revert the `contracts.py` changes and redesign the hooks (e.g., separate test-only subclass instead of modifying the base class).

## Validation plan

During this spec-only phase:
1. Run existing Bloco 0 + Bloco 1 validation commands (CLI help, CLI doctor, py_compile, pytest).
2. Confirm no source/test files were created.
3. Run repository contamination check.
4. Confirm `git diff --check` is clean.
5. Commit spec files only.

During later implementation phase:
1. Add `FakeControlClient` failure-injection hooks to `contracts.py`.
2. Run `python3 -m pytest tests/test_contracts.py -v` to confirm no regressions.
3. Create `src/noqlen_aria/services.py`.
4. Run `python3 -m py_compile src/noqlen_aria/services.py`.
5. Run `PYTHONPATH=src python3 -c "import noqlen_aria.services"`.
6. Create `tests/test_services.py` with TDD tests.
7. Run `python3 -m pytest tests/test_services.py -v`.
8. Run full validation suite (py_compile, pytest all, contamination check).
9. Update `docs/handoff.md` with Bloco 2 status note.
