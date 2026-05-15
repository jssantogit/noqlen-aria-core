# Design

## Summary

Create a single `src/noqlen_aria/contracts.py` module containing all Aria Core contract definitions (data classes, enums, protocols) and a corresponding `tests/test_contracts.py` test file. No other source or test files are created. No external dependencies are added. The control client boundary is source-agnostic; Anchor is one future adapter.

## Context files read

- `AGENTS.md`
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
- `aria/review/block-audit-checklist.md`
- `aria/review/bloco-0-audit-checklist.md`
- `aria/review/code-review-spec.md`
- `aria/review/repository-hygiene-checklist.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/bloco-0-bootstrap/requirements.md`
- `aria/specs/features/bloco-0-bootstrap/design.md`
- `aria/specs/features/bloco-0-bootstrap/tasks.md`
- `aria/specs/features/bloco-0-bootstrap/review.md`
- `docs/architecture.md`
- `docs/anchor-integration.md`
- `docs/safety.md`
- `docs/handoff.md`
- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/cli.py`

## Existing project context

Bloco 0 is complete: the repository has a minimal Python package (`noqlen_aria`) with a `doctor` CLI command, workflow context files, spec templates, and local smoke tests. The package has zero runtime dependencies. No product contracts exist yet.

Future flow: `Future UI/App -> Aria Core -> Anchor Client -> Anchor Core API -> Navidrome`

Bloco 1 is the first product-level block. It only defines contracts and a fake client. It does not implement real Anchor integration or any UI/product behavior.

## Files to create

Source (targeted for implementation phase, not created now):

- `src/noqlen_aria/contracts.py` — single module with all contract definitions.

Tests (targeted for implementation phase, not created now):

- `tests/test_contracts.py` — tests for contracts and FakeAnchorClient.

Spec (created now):

- `aria/specs/features/aria-core-contracts/requirements.md`
- `aria/specs/features/aria-core-contracts/design.md`
- `aria/specs/features/aria-core-contracts/tasks.md`
- `aria/specs/features/aria-core-contracts/review.md`

## Files to modify

None in this spec-only phase. During later implementation, `tests/test_contracts.py` and `src/noqlen_aria/contracts.py` will be created.

## Files that must not be touched

- `src/noqlen_aria/__init__.py` (may be considered for contract namespace re-export in implementation, but not in this spec)
- `src/noqlen_aria/cli.py`
- `pyproject.toml`
- `tests/test_cli.py`
- All `docs/*.md`
- All `aria/context/*.md` (except `mistakes.md` if a real workflow mistake is discovered)
- All `aria/review/*.md`
- `AGENTS.md`
- `.git/info/exclude`
- Any `Android`, `Kotlin`, `Java`, `Gradle` files (none exist)
- `docs/development/` (none exist)
- Any secret, credential, log, cache, or temporary file

## Expected source module layout (`src/noqlen_aria/contracts.py`)

Proposed contents for implementation phase (not created now):

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generic, Protocol, TypeVar

# ── Result types ──────────────────────────────────────────────

T = TypeVar("T")

@dataclass(frozen=True)
class AriaResult(Generic[T]):
    """Explicit success-or-failure result for app-facing operations."""
    ok: bool
    data: T | None = None
    error: AriaError | None = None

    def is_ok(self) -> bool:
        return self.ok

    def is_err(self) -> bool:
        return not self.ok

@dataclass(frozen=True)
class AriaError:
    """Structured error for app-facing operations."""
    code: str
    message: str

@dataclass(frozen=True)
class AriaWarning:
    """Structured non-fatal warning for diagnostics."""
    code: str
    message: str

# ── View states ──────────────────────────────────────────────

@dataclass(frozen=True)
class ServerViewState:
    """Stable server connectivity view independent of UI."""
    connected: bool = False
    server_url: str = ""
    server_version: str = ""
    latency_ms: int | None = None
    last_error: AriaError | None = None

@dataclass(frozen=True)
class LibraryViewState:
    """Stable music library metadata view independent of UI."""
    available: bool = False
    artist_count: int = 0
    album_count: int = 0
    track_count: int = 0
    total_duration_seconds: int = 0
    last_scan_timestamp: float | None = None

@dataclass(frozen=True)
class DiagnosticsViewState:
    """Safe diagnostic snapshot independent of UI."""
    warnings: list[AriaWarning] = field(default_factory=list)

@dataclass(frozen=True)
class ReadinessViewState:
    """Composite snapshot of system readiness."""
    server: ServerViewState = field(default_factory=ServerViewState)
    library: LibraryViewState = field(default_factory=LibraryViewState)
    diagnostics: DiagnosticsViewState = field(default_factory=DiagnosticsViewState)
    control_configured: bool = False
    all_ready: bool = False

# ── Lifecycle ────────────────────────────────────────────────

class LifecycleIntent(Enum):
    """Lifecycle transitions that future UI may request."""
    INITIALIZE = auto()
    SHUTDOWN = auto()
    RESET = auto()

# ── Permissions and storage ──────────────────────────────────

class PermissionState(Enum):
    """Runtime permission status, independent of Android API."""
    UNKNOWN = auto()
    GRANTED = auto()
    DENIED = auto()
    NOT_APPLICABLE = auto()

class StorageAccessState(Enum):
    """Storage/library availability, independent of OS API."""
    UNKNOWN = auto()
    AVAILABLE = auto()
    UNAVAILABLE = auto()

# ── Anchor client contract ───────────────────────────────────

class ControlClient(Protocol):
    """Stable contract for control-plane operations.

    Aria must interact with any core controller through this boundary only.
    Future real implementations (e.g. AnchorControlClient adapter) must
    satisfy this protocol. Anchor is one future adapter; the contract is
    source-agnostic.
    """

    def ping(self) -> AriaResult[bool]:
        """Check Anchor connectivity."""
        ...

    def get_server_state(self) -> AriaResult[ServerViewState]:
        """Get current server view state."""
        ...

    def get_library_state(self) -> AriaResult[LibraryViewState]:
        """Get current library view state."""
        ...

    def get_readiness(self) -> AriaResult[ReadinessViewState]:
        """Get composite readiness snapshot."""
        ...

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        """Send a lifecycle intent to Anchor."""
        ...

    def get_permission_state(self) -> AriaResult[PermissionState]:
        """Get current permission state."""
        ...

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        """Get current storage access state."""
        ...


@dataclass
class FakeControlClient:
    """Deterministic fake control client for local tests and early development.

    Returns known fake data. Never calls network, filesystem, or external process.
    """

    def ping(self) -> AriaResult[bool]:
        """Always returns ok=True with data=True."""
        ...

    def get_server_state(self) -> AriaResult[ServerViewState]:
        """Returns a fake connected server state."""
        ...

    def get_library_state(self) -> AriaResult[LibraryViewState]:
        """Returns a fake small library state."""
        ...

    def get_readiness(self) -> AriaResult[ReadinessViewState]:
        """Returns a fake fully-ready snapshot."""
        ...

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        """Acknowledges any lifecycle intent."""
        ...

    def get_permission_state(self) -> AriaResult[PermissionState]:
        """Returns PermissionState.GRANTED."""
        ...

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        """Returns StorageAccessState.AVAILABLE."""
        ...
```

Note: This is a design proposal. Exact field lists, method signatures, and defaults are subject to refinement during implementation. The `FakeControlClient` is not a frozen dataclass so that tests can optionally mutate it for edge-case scenarios. The contract was generalized from `AnchorClient`/`FakeAnchorClient` to `ControlClient`/`FakeControlClient` during Bloco 1 refinement to avoid Anchor-centric architecture; Anchor is a future adapter only.

## Data flow

```
Future UI -> Aria Core -> ControlClient (protocol) -> FakeControlClient (in Bloco 1)
                                                      -> AnchorControlClient adapter (future block)
```

In Bloco 1:
1. Tests instantiate `FakeControlClient`.
2. Tests call `ControlClient` protocol methods on the fake.
3. Tests assert return types and values match expected contracts.
4. No real network, filesystem, or external process is involved.

## Error handling

- `AriaResult.ok` is the single discriminator for success vs failure.
- `AriaError.code` uses `UPPER_SNAKE_CASE` convention (e.g., `"SERVER_UNREACHABLE"`, `"LIBRARY_NOT_AVAILABLE"`).
- `FakeControlClient` never returns errors by default; tests may configure it to return errors for edge-case testing.
- `AriaWarning` is informational only and never blocks operations.
- Unknown `LifecycleIntent` values: if using `Enum`, the Python `Enum` constructor handles validation; if passed as a string, the receiver must validate.

## Security considerations

- No secrets, tokens, URLs, or credentials in contract definitions.
- No network calls in `FakeControlClient`.
- No filesystem access in `FakeControlClient`.
- No subprocess execution in `FakeControlClient`.
- No real Anchor or Navidrome access.

## Dependencies

- No runtime dependencies beyond Python 3.11+ standard library (`dataclasses`, `enum`, `typing`).
- No additions to `pyproject.toml`.

## Risks

- R01: Contract method set may be incomplete for future blocks. Mitigation: `ControlClient` is a `Protocol`, so adding methods is non-breaking for structural typing consumers.
- R02: `AriaResult[T]` generic may introduce complexity for consumers unfamiliar with generics. Mitigation: provide helper constructors (e.g., `AriaResult.ok(data)`, `AriaResult.err(error)`) or factory functions.
- R03: `FakeControlClient` defaults may be too optimistic (always connected, always available). Mitigation: expose configuration hooks for tests to simulate failure states.

## Rollback strategy

If contracts are found to be incorrect during implementation, edit `contracts.py` and `test_contracts.py` in a focused commit. If contracts are fundamentally wrong, revert the implementation commit. The spec files in `aria/specs/` may be updated to reflect corrected requirements.

## Validation plan

During this spec-only phase:
1. Run existing Bloco 0 validation commands (CLI help, CLI doctor, py_compile, pytest).
2. Confirm no source/test files were created.
3. Run repository contamination check.
4. Confirm `git diff --check` is clean.
5. Commit spec files only.

During later implementation phase:
1. Run `python3 -m py_compile src/noqlen_aria/contracts.py`.
2. Run `PYTHONPATH=src python3 -c "import noqlen_aria.contracts"`.
3. Run `python3 -m pytest tests/test_contracts.py -v`.
4. Run full Bloco 0 + Bloco 1 validation suite.
