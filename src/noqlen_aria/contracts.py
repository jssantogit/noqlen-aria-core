"""Aria Core contracts — UI-independent type definitions for app-facing operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


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


@dataclass(frozen=True)
class AriaResult(Generic[T]):
    """Explicit success-or-failure result for app-facing operations.

    ``ok`` is the single discriminator: True means success (``data`` is valid),
    False means failure (``error`` is valid).
    """

    ok: bool
    data: T | None = None
    error: AriaError | None = None

    def is_ok(self) -> bool:
        return self.ok

    def is_err(self) -> bool:
        return not self.ok


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
    anchor_configured: bool = False
    all_ready: bool = False


class LifecycleIntent(Enum):
    """Lifecycle transitions that future UI may request."""

    INITIALIZE = auto()
    SHUTDOWN = auto()
    RESET = auto()


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


@runtime_checkable
class AnchorClient(Protocol):
    """Stable contract for Anchor integration.

    Aria must interact with Anchor through this boundary only.
    Future real implementations must satisfy this protocol.
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
class FakeAnchorClient:
    """Deterministic fake Anchor client for local tests and early development.

    Returns known fake data. Never calls network, filesystem, or external
    process. Not a frozen dataclass so tests can optionally mutate it for
    edge-case scenarios.
    """

    def ping(self) -> AriaResult[bool]:
        return AriaResult(ok=True, data=True)

    def get_server_state(self) -> AriaResult[ServerViewState]:
        return AriaResult(
            ok=True,
            data=ServerViewState(
                connected=True,
                server_url="http://fake:4533",
                server_version="0.52.5-fake",
                latency_ms=1,
            ),
        )

    def get_library_state(self) -> AriaResult[LibraryViewState]:
        return AriaResult(
            ok=True,
            data=LibraryViewState(
                available=True,
                artist_count=5,
                album_count=10,
                track_count=120,
                total_duration_seconds=36000,
                last_scan_timestamp=1_700_000_000.0,
            ),
        )

    def get_readiness(self) -> AriaResult[ReadinessViewState]:
        return AriaResult(
            ok=True,
            data=ReadinessViewState(
                server=self.get_server_state().data,
                library=self.get_library_state().data,
                diagnostics=DiagnosticsViewState(),
                anchor_configured=True,
                all_ready=True,
            ),
        )

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        return AriaResult(ok=True, data=True)

    def get_permission_state(self) -> AriaResult[PermissionState]:
        return AriaResult(ok=True, data=PermissionState.GRANTED)

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        return AriaResult(ok=True, data=StorageAccessState.AVAILABLE)
