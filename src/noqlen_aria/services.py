"""Aria Core services — fake-driven mapping layer on top of ControlClient."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

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

T = TypeVar("T")

DEFAULT_MAX_LATENCY_MS: int = 200
DEFAULT_MAX_LIBRARY_STALENESS_SECONDS: int = 86400

_LIFECYCLE_PREVIEWS: dict[LifecycleIntent, tuple[str, bool, bool]] = {
    LifecycleIntent.INITIALIZE: (
        "Initialize the control service and establish connectivity",
        True,
        True,
    ),
    LifecycleIntent.SHUTDOWN: (
        "Gracefully shut down the control service and disconnect clients",
        True,
        True,
    ),
    LifecycleIntent.RESET: (
        "Reset the control service to its default configuration state",
        False,
        True,
    ),
}


class ResultMappingError(Exception):
    """Raised when unwrapping a failed AriaResult."""


@dataclass(frozen=True)
class LifecycleIntentPreview:
    """Structured preview of a lifecycle intent effect without execution."""

    intent: LifecycleIntent
    description: str
    reversible: bool
    requires_apply: bool


class ResultMappingService:
    """Normalizes and creates AriaResult instances for app-facing use.

    Provides factory helpers for creating ok/err results and unwrapping
    helpers for extracting data or errors from raw ControlClient results.
    """

    @staticmethod
    def ok(data: T) -> AriaResult[T]:
        return AriaResult(ok=True, data=data)

    @staticmethod
    def err(code: str, message: str) -> AriaResult[Any]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))

    @staticmethod
    def unwrap(result: AriaResult[T]) -> T:
        if result.is_err():
            err = result.error
            detail = f"{err.code}: {err.message}" if err else "unknown error"
            raise ResultMappingError(f"Cannot unwrap failed result: {detail}")
        return result.data  # type: ignore[return-value]

    @staticmethod
    def unwrap_or(result: AriaResult[T], default: T) -> T:
        if result.is_err():
            return default
        return result.data  # type: ignore[return-value]

    @staticmethod
    def map_error(
        result: AriaResult[T], code: str, message: str
    ) -> AriaResult[T]:
        if result.is_err():
            return AriaResult(ok=False, error=AriaError(code=code, message=message))
        return result


class StatusService:
    """Composes server status into a high-level connectivity response."""

    def __init__(self, client: ControlClient) -> None:
        self._client = client

    def get_status(self) -> AriaResult[ServerViewState]:
        ping_result = self._client.ping()
        if ping_result.is_err():
            return AriaResult(
                ok=False,
                error=ping_result.error,
            )
        server_result = self._client.get_server_state()
        return server_result


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
        self._client = client
        self._max_latency_ms = max_latency_ms
        self._max_library_staleness_seconds = max_library_staleness_seconds

    def collect(self) -> AriaResult[DiagnosticsViewState]:
        warnings: list[AriaWarning] = []

        server_result = self._client.get_server_state()
        if server_result.is_ok() and server_result.data is not None:
            server = server_result.data
            if (
                server.latency_ms is not None
                and server.latency_ms > self._max_latency_ms
            ):
                warnings.append(
                    AriaWarning(
                        code="LATENCY_HIGH",
                        message=f"Server latency {server.latency_ms}ms exceeds threshold {self._max_latency_ms}ms",
                    )
                )
            if server.last_error is not None:
                warnings.append(
                    AriaWarning(
                        code="SERVER_LAST_ERROR",
                        message=f"Server reported last error: {server.last_error.code}: {server.last_error.message}",
                    )
                )
        elif server_result.is_err():
            warnings.append(
                AriaWarning(
                    code="SERVER_STATE_UNAVAILABLE",
                    message="Cannot retrieve server state for diagnostics",
                )
            )

        library_result = self._client.get_library_state()
        if library_result.is_ok() and library_result.data is not None:
            library = library_result.data
            if library.last_scan_timestamp is None:
                warnings.append(
                    AriaWarning(
                        code="LIBRARY_NEVER_SCANNED",
                        message="Library has never been scanned",
                    )
                )
            else:
                staleness = time.time() - library.last_scan_timestamp
                if staleness > self._max_library_staleness_seconds:
                    warnings.append(
                        AriaWarning(
                            code="LIBRARY_STALE",
                            message=f"Last library scan is {int(staleness)} seconds old, exceeds threshold of {self._max_library_staleness_seconds}s",
                        )
                    )
        elif library_result.is_err():
            warnings.append(
                AriaWarning(
                    code="LIBRARY_STATE_UNAVAILABLE",
                    message="Cannot retrieve library state for diagnostics",
                )
            )

        readiness_result = self._client.get_readiness()
        if readiness_result.is_ok() and readiness_result.data is not None:
            readiness = readiness_result.data
            if not readiness.control_configured:
                warnings.append(
                    AriaWarning(
                        code="CONTROL_NOT_CONFIGURED",
                        message="Control client is not configured",
                    )
                )
        elif readiness_result.is_err():
            warnings.append(
                AriaWarning(
                    code="READINESS_UNAVAILABLE",
                    message="Cannot retrieve readiness for diagnostics",
                )
            )

        return AriaResult(ok=True, data=DiagnosticsViewState(warnings=warnings))


class LifecycleIntentService:
    """Validates and previews lifecycle intents without execution."""

    def __init__(self, client: ControlClient) -> None:
        self._client = client

    def preview(
        self, intent: LifecycleIntent
    ) -> AriaResult[LifecycleIntentPreview]:
        info = _LIFECYCLE_PREVIEWS.get(intent)
        if info is None:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="UNKNOWN_LIFECYCLE_INTENT",
                    message=f"Unknown lifecycle intent: {intent}",
                ),
            )
        description, reversible, requires_apply = info
        return AriaResult(
            ok=True,
            data=LifecycleIntentPreview(
                intent=intent,
                description=description,
                reversible=reversible,
                requires_apply=requires_apply,
            ),
        )

    def validate(self, intent_name: str) -> AriaResult[LifecycleIntent]:
        try:
            intent = LifecycleIntent[intent_name.upper()]
        except KeyError:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="INVALID_LIFECYCLE_INTENT",
                    message=f"Invalid lifecycle intent name: {intent_name}",
                ),
            )
        return AriaResult(ok=True, data=intent)


class ReadinessService:
    """Produces a composite ReadinessViewState from ControlClient data."""

    def __init__(self, client: ControlClient) -> None:
        self._client = client

    def assess(self) -> AriaResult[ReadinessViewState]:
        server_result = self._client.get_server_state()
        if server_result.is_err():
            return AriaResult(ok=False, error=server_result.error)

        library_result = self._client.get_library_state()
        if library_result.is_err():
            return AriaResult(ok=False, error=library_result.error)

        readiness_result = self._client.get_readiness()
        if readiness_result.is_err():
            return AriaResult(ok=False, error=readiness_result.error)

        server = server_result.data
        library = library_result.data
        existing = readiness_result.data

        control_configured = (
            existing.control_configured if existing is not None else False
        )
        diagnostics = existing.diagnostics if existing is not None else DiagnosticsViewState()

        all_ready = bool(
            (server is not None and server.connected)
            and (library is not None and library.available)
            and control_configured
            and len(diagnostics.warnings) == 0
        )

        return AriaResult(
            ok=True,
            data=ReadinessViewState(
                server=server if server is not None else ServerViewState(),
                library=library if library is not None else LibraryViewState(),
                diagnostics=diagnostics,
                control_configured=control_configured,
                all_ready=all_ready,
            ),
        )
