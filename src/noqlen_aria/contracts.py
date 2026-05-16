"""Aria Core contracts — UI-independent type definitions for app-facing operations."""

from __future__ import annotations

from dataclasses import fields, is_dataclass, dataclass, field
from enum import Enum, auto
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")

SAFE_DETAIL_UNAVAILABLE = "Details are unavailable in safe output"

_UNSAFE_TEXT_MARKERS = (
    "traceback",
    "password",
    "passwd",
    "token",
    "secret",
    "credential",
    "authorization",
    "api_key",
    "apikey",
    "/home/",
    "/users/",
    "/var/",
    "c:\\",
    "provider exception",
    "raw provider",
    "music library",
)


def sanitize_text(value: object) -> str:
    """Return display-safe text for app-facing errors and warnings."""

    text = "" if value is None else str(value)
    lowered = text.lower()
    if any(marker in lowered for marker in _UNSAFE_TEXT_MARKERS):
        return SAFE_DETAIL_UNAVAILABLE
    if "\n" in text or "\r" in text:
        return " ".join(text.split())
    return text


def safe_serialize(value: Any) -> Any:
    """Convert Aria values into stdlib-only, app-facing safe data."""

    if isinstance(value, Enum):
        return value.name
    if isinstance(value, (str, int, float, bool)) or value is None:
        return sanitize_text(value) if isinstance(value, str) else value
    if is_dataclass(value):
        return {field.name: safe_serialize(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, list):
        return [safe_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [safe_serialize(item) for item in value]
    if isinstance(value, dict):
        return {safe_serialize(key): safe_serialize(item) for key, item in value.items()}
    return SAFE_DETAIL_UNAVAILABLE


@dataclass(frozen=True)
class AriaError:
    """Structured error for app-facing operations."""

    code: str
    message: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", sanitize_text(self.code))
        object.__setattr__(self, "message", sanitize_text(self.message))


@dataclass(frozen=True)
class AriaWarning:
    """Structured non-fatal warning for diagnostics."""

    code: str
    message: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", sanitize_text(self.code))
        object.__setattr__(self, "message", sanitize_text(self.message))


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
    control_configured: bool = False
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
class ControlClient(Protocol):
    """Stable contract for app/core control-plane operations.

    Aria must interact with any core controller through this boundary only.
    Future real implementations (e.g. AnchorControlClient adapter) must
    satisfy this protocol.

    Anchor is one future adapter; the contract is source-agnostic.
    """

    def ping(self) -> AriaResult[bool]:
        """Check control-plane connectivity."""
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
        """Send a lifecycle intent to the control service."""
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

    Returns known fake data. Never calls network, filesystem, or external
    process. Not a frozen dataclass so tests can optionally mutate it for
    edge-case scenarios.

    Failure-injection hooks (set to an AriaError to simulate failures):
        _ping_error, _server_state_error, _library_state_error,
        _readiness_error, _lifecycle_error, _permission_state_error,
        _storage_access_error

    Value overrides (set to override the default return data):
        _server_state_override, _library_state_override,
        _readiness_override, _permission_state_override,
        _storage_access_override
    """

    _ping_error: AriaError | None = field(default=None, repr=False)
    _server_state_error: AriaError | None = field(default=None, repr=False)
    _library_state_error: AriaError | None = field(default=None, repr=False)
    _readiness_error: AriaError | None = field(default=None, repr=False)
    _lifecycle_error: AriaError | None = field(default=None, repr=False)
    _permission_state_error: AriaError | None = field(default=None, repr=False)
    _storage_access_error: AriaError | None = field(default=None, repr=False)

    _server_state_override: ServerViewState | None = field(default=None, repr=False)
    _library_state_override: LibraryViewState | None = field(default=None, repr=False)
    _readiness_override: ReadinessViewState | None = field(default=None, repr=False)
    _permission_state_override: PermissionState | None = field(default=None, repr=False)
    _storage_access_override: StorageAccessState | None = field(default=None, repr=False)

    def ping(self) -> AriaResult[bool]:
        if self._ping_error is not None:
            return AriaResult(ok=False, error=self._ping_error)
        return AriaResult(ok=True, data=True)

    def get_server_state(self) -> AriaResult[ServerViewState]:
        if self._server_state_error is not None:
            return AriaResult(ok=False, error=self._server_state_error)
        if self._server_state_override is not None:
            return AriaResult(ok=True, data=self._server_state_override)
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
        if self._library_state_error is not None:
            return AriaResult(ok=False, error=self._library_state_error)
        if self._library_state_override is not None:
            return AriaResult(ok=True, data=self._library_state_override)
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
        if self._readiness_error is not None:
            return AriaResult(ok=False, error=self._readiness_error)
        if self._readiness_override is not None:
            return AriaResult(ok=True, data=self._readiness_override)
        server_result = self.get_server_state()
        if server_result.is_err():
            return AriaResult(ok=False, error=server_result.error)
        library_result = self.get_library_state()
        if library_result.is_err():
            return AriaResult(ok=False, error=library_result.error)
        return AriaResult(
            ok=True,
            data=ReadinessViewState(
                server=server_result.data,
                library=library_result.data,
                diagnostics=DiagnosticsViewState(),
                control_configured=True,
                all_ready=True,
            ),
        )

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        if self._lifecycle_error is not None:
            return AriaResult(ok=False, error=self._lifecycle_error)
        return AriaResult(ok=True, data=True)

    def get_permission_state(self) -> AriaResult[PermissionState]:
        if self._permission_state_error is not None:
            return AriaResult(ok=False, error=self._permission_state_error)
        if self._permission_state_override is not None:
            return AriaResult(ok=True, data=self._permission_state_override)
        return AriaResult(ok=True, data=PermissionState.GRANTED)

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        if self._storage_access_error is not None:
            return AriaResult(ok=False, error=self._storage_access_error)
        if self._storage_access_override is not None:
            return AriaResult(ok=True, data=self._storage_access_override)
        return AriaResult(ok=True, data=StorageAccessState.AVAILABLE)


__all__ = [
    "AriaError",
    "AriaResult",
    "AriaWarning",
    "ControlClient",
    "DiagnosticsViewState",
    "FakeControlClient",
    "LibraryViewState",
    "LifecycleIntent",
    "PermissionState",
    "ReadinessViewState",
    "ServerViewState",
    "StorageAccessState",
    "safe_serialize",
    "sanitize_text",
]
