"""Anchor Control Client adapter — dry-run/offline implementation of ControlClient.

All Anchor public API calls are guarded behind optional imports.
When noqlen_anchor is not installed, all methods return safe error results.
"""

from __future__ import annotations

from typing import Any

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    AriaWarning,
    DiagnosticsViewState,
    LibraryViewState,
    LifecycleIntent,
    PermissionState,
    ReadinessViewState,
    ServerViewState,
    StorageAccessState,
)
from noqlen_aria.services import ResultMappingService

_ANCHOR_NOT_AVAILABLE = AriaError(
    code="ANCHOR_NOT_AVAILABLE",
    message="Anchor public API is not available",
)

_APPLY_MODE_BLOCKED = AriaError(
    code="APPLY_MODE_BLOCKED",
    message="Apply-mode lifecycle operations are blocked in dry-run adapter",
)

_ANCHOR_HELPER_NOT_FOUND = AriaError(
    code="ANCHOR_HELPER_NOT_FOUND",
    message="The requested Anchor public API helper is not available",
)

_ANCHOR_CALL_FAILED = AriaError(
    code="ANCHOR_CALL_FAILED",
    message="An Anchor public API helper call failed",
)

_ANCHOR_UNEXPECTED_OUTPUT = AriaError(
    code="ANCHOR_UNEXPECTED_OUTPUT",
    message="Anchor public API helper returned unexpected output",
)

_LIFECYCLE_DRY_RUN_MAP: dict[LifecycleIntent, str] = {
    LifecycleIntent.INITIALIZE: "start_navidrome_dry_run",
    LifecycleIntent.SHUTDOWN: "stop_navidrome_dry_run",
    LifecycleIntent.RESET: "restart_navidrome_dry_run",
}

_anchor_module_cache: Any = None


_SENTINEL_MISSING: Any = False


def _get_anchor() -> Any:
    """Lazily import and cache the Anchor public API module.

    Returns the module object if available, otherwise None.
    Does NOT import Anchor provider internals.
    """
    global _anchor_module_cache
    if _anchor_module_cache is not None and _anchor_module_cache is not _SENTINEL_MISSING:
        return _anchor_module_cache
    try:
        import noqlen_anchor.public_api as _anchor_module_cache  # type: ignore[import-untyped]
    except ImportError:
        _anchor_module_cache = _SENTINEL_MISSING
    return _anchor_module_cache if _anchor_module_cache is not _SENTINEL_MISSING else None


class AnchorResultMapper:
    """Maps Anchor public API helper outputs into Aria contract types.

    Pure mapping functions; no side effects, no Anchor imports at class level.
    All methods handle None, missing keys, and unexpected shapes gracefully.
    """

    @staticmethod
    def _safe_bool(value: Any) -> bool:
        return bool(value)

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_float_or_none(value: Any) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    @staticmethod
    def to_server_view_state(anchor_server_output: Any) -> ServerViewState:
        """Map Anchor server status output to ServerViewState."""
        if not isinstance(anchor_server_output, dict):
            return ServerViewState()
        return ServerViewState(
            connected=AnchorResultMapper._safe_bool(
                anchor_server_output.get("connected", False)
            ),
            server_url=AnchorResultMapper._safe_str(
                anchor_server_output.get("url", "")
            ),
            server_version=AnchorResultMapper._safe_str(
                anchor_server_output.get("version", "")
            ),
            latency_ms=(
                AnchorResultMapper._safe_int(raw_latency)
                if (raw_latency := anchor_server_output.get("latency_ms")) is not None
                else None
            ),
            last_error=(
                AriaError(
                    code=AnchorResultMapper._safe_str(
                        anchor_server_output.get("last_error", {}).get("code", "UNKNOWN")
                    ),
                    message=AnchorResultMapper._safe_str(
                        anchor_server_output.get("last_error", {}).get("message", "")
                    ),
                )
                if isinstance(anchor_server_output.get("last_error"), dict)
                else None
            ),
        )

    @staticmethod
    def to_library_view_state(anchor_library_output: Any) -> LibraryViewState:
        """Map Anchor library metadata output to LibraryViewState."""
        if not isinstance(anchor_library_output, dict):
            return LibraryViewState()
        return LibraryViewState(
            available=AnchorResultMapper._safe_bool(
                anchor_library_output.get("available", False)
            ),
            artist_count=AnchorResultMapper._safe_int(
                anchor_library_output.get("artist_count", 0)
            ),
            album_count=AnchorResultMapper._safe_int(
                anchor_library_output.get("album_count", 0)
            ),
            track_count=AnchorResultMapper._safe_int(
                anchor_library_output.get("track_count", 0)
            ),
            total_duration_seconds=AnchorResultMapper._safe_int(
                anchor_library_output.get("total_duration_seconds", 0)
            ),
            last_scan_timestamp=AnchorResultMapper._safe_float_or_none(
                anchor_library_output.get("last_scan_timestamp")
            ),
        )

    @staticmethod
    def to_readiness_view_state(anchor_readiness_output: Any) -> ReadinessViewState:
        """Map Anchor readiness/safety summary output to ReadinessViewState."""
        if not isinstance(anchor_readiness_output, dict):
            return ReadinessViewState()
        server_data = anchor_readiness_output.get("server")
        library_data = anchor_readiness_output.get("library")
        diagnostics_data = anchor_readiness_output.get("diagnostics")
        return ReadinessViewState(
            server=AnchorResultMapper.to_server_view_state(server_data),
            library=AnchorResultMapper.to_library_view_state(library_data),
            diagnostics=AnchorResultMapper.to_diagnostics_view_state(diagnostics_data),
            control_configured=AnchorResultMapper._safe_bool(
                anchor_readiness_output.get("control_configured", False)
            ),
            all_ready=AnchorResultMapper._safe_bool(
                anchor_readiness_output.get("all_ready", False)
            ),
        )

    @staticmethod
    def to_diagnostics_view_state(
        anchor_diagnostics_output: Any,
    ) -> DiagnosticsViewState:
        """Map Anchor diagnostics output to DiagnosticsViewState."""
        if not isinstance(anchor_diagnostics_output, dict):
            return DiagnosticsViewState()
        raw_warnings = anchor_diagnostics_output.get("warnings", [])
        if not isinstance(raw_warnings, list):
            return DiagnosticsViewState()
        warnings: list[AriaWarning] = []
        for w in raw_warnings:
            if isinstance(w, dict):
                warnings.append(
                    AriaWarning(
                        code=AnchorResultMapper._safe_str(w.get("code", "UNKNOWN")),
                        message=AnchorResultMapper._safe_str(
                            w.get("message", "")
                        ),
                    )
                )
        return DiagnosticsViewState(warnings=warnings)

    @staticmethod
    def to_permission_state(anchor_permission_output: Any) -> PermissionState:
        """Map Anchor permission/integration report output to PermissionState."""
        if not isinstance(anchor_permission_output, dict):
            return PermissionState.UNKNOWN
        granted = anchor_permission_output.get("permissions_granted")
        if granted is True:
            return PermissionState.GRANTED
        if granted is False:
            return PermissionState.DENIED
        status = AnchorResultMapper._safe_str(
            anchor_permission_output.get("permission_status", "")
        ).upper()
        if status == "GRANTED":
            return PermissionState.GRANTED
        if status == "DENIED":
            return PermissionState.DENIED
        if status == "NOT_APPLICABLE":
            return PermissionState.NOT_APPLICABLE
        return PermissionState.UNKNOWN

    @staticmethod
    def to_storage_access_state(anchor_storage_output: Any) -> StorageAccessState:
        """Map Anchor storage/render output to StorageAccessState."""
        if not isinstance(anchor_storage_output, dict):
            return StorageAccessState.UNKNOWN
        available = anchor_storage_output.get("storage_available")
        if available is True:
            return StorageAccessState.AVAILABLE
        if available is False:
            return StorageAccessState.UNAVAILABLE
        status = AnchorResultMapper._safe_str(
            anchor_storage_output.get("storage_status", "")
        ).upper()
        if status == "AVAILABLE":
            return StorageAccessState.AVAILABLE
        if status == "UNAVAILABLE":
            return StorageAccessState.UNAVAILABLE
        return StorageAccessState.UNKNOWN


class AnchorControlClient:
    """Concrete ControlClient adapter backed by Anchor public API helpers.

    Operates in offline/dry-run mode. All lifecycle methods return
    preview-only results; apply-mode is blocked.

    Does NOT call Anchor provider internals, Anchor CLI, or Navidrome directly.
    Does NOT access real music libraries.
    Sanitizes all outputs before returning.

    When noqlen_anchor is not installed, all methods return
    AriaResult(ok=False, error=AriaError(code="ANCHOR_NOT_AVAILABLE", ...)).

    Supports dependency injection of the Anchor module via constructor
    for testing with mocked/fake Anchor API.
    """

    def __init__(self, anchor_module: Any = None) -> None:
        self._anchor = (
            anchor_module if anchor_module is not None else _get_anchor()
        )

    @staticmethod
    def is_anchor_available() -> bool:
        """Return True if the Anchor public API module is importable."""
        return _get_anchor() is not None

    def _not_available(self) -> bool:
        """Return True if Anchor is not available."""
        return self._anchor is None

    def _guard_not_available(self) -> AriaResult[Any] | None:
        """Return an ANCHOR_NOT_AVAILABLE result if Anchor is missing."""
        if self._not_available():
            return AriaResult(ok=False, error=_ANCHOR_NOT_AVAILABLE)
        return None

    def _call_anchor_helper(
        self, helper_name: str, *args: Any, **kwargs: Any
    ) -> AriaResult[Any]:
        """Safely call a named helper on the Anchor public API module.

        Returns (ok, raw_output or error). Does NOT propagate exceptions.
        """
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        helper = getattr(self._anchor, helper_name, None)
        if helper is None:
            return ResultMappingService.err(
                _ANCHOR_HELPER_NOT_FOUND.code,
                f"{_ANCHOR_HELPER_NOT_FOUND.message}: {helper_name}",
            )
        try:
            raw = helper(*args, **kwargs)
            return ResultMappingService.ok(raw)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_CALL_FAILED.code,
                f"{_ANCHOR_CALL_FAILED.message}: {helper_name}: {exc}",
            )

    def ping(self) -> AriaResult[bool]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        server_result = self._call_anchor_helper("inspect_fake_server")
        if server_result.is_err():
            return AriaResult(ok=False, error=server_result.error)
        try:
            sv = AnchorResultMapper.to_server_view_state(server_result.data)
            return AriaResult(ok=True, data=sv.connected)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_UNEXPECTED_OUTPUT.code,
                f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
            )

    def get_server_state(self) -> AriaResult[ServerViewState]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        server_result = self._call_anchor_helper("inspect_fake_server")
        if server_result.is_err():
            return AriaResult(ok=False, error=server_result.error)
        try:
            sv = AnchorResultMapper.to_server_view_state(server_result.data)
            return AriaResult(ok=True, data=sv)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_UNEXPECTED_OUTPUT.code,
                f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
            )

    def get_library_state(self) -> AriaResult[LibraryViewState]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        library_result = self._call_anchor_helper("inspect_navidrome_offline")
        if library_result.is_err():
            return AriaResult(ok=False, error=library_result.error)
        try:
            lv = AnchorResultMapper.to_library_view_state(library_result.data)
            return AriaResult(ok=True, data=lv)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_UNEXPECTED_OUTPUT.code,
                f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
            )

    def get_readiness(self) -> AriaResult[ReadinessViewState]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard

        helper_name = "get_readiness_report"
        helper = getattr(self._anchor, helper_name, None)
        if helper is not None:
            readiness_result = self._call_anchor_helper(helper_name)
            if readiness_result.is_ok():
                try:
                    rv = AnchorResultMapper.to_readiness_view_state(
                        readiness_result.data
                    )
                    return AriaResult(ok=True, data=rv)
                except Exception as exc:
                    return ResultMappingService.err(
                        _ANCHOR_UNEXPECTED_OUTPUT.code,
                        f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
                    )
            return AriaResult(ok=False, error=readiness_result.error)

        server_result = self.get_server_state()
        if server_result.is_err():
            return AriaResult(ok=False, error=server_result.error)
        library_result = self.get_library_state()
        if library_result.is_err():
            return AriaResult(ok=False, error=library_result.error)

        server = server_result.data
        library = library_result.data
        diagnostics = DiagnosticsViewState()
        warnings: list[AriaWarning] = []

        if server is not None and not server.connected:
            warnings.append(
                AriaWarning(
                    code="SERVER_DISCONNECTED",
                    message="Server is not connected",
                )
            )
        if library is not None and not library.available:
            warnings.append(
                AriaWarning(
                    code="LIBRARY_UNAVAILABLE",
                    message="Library is not available",
                )
            )
        if warnings:
            diagnostics = DiagnosticsViewState(warnings=warnings)

        all_ready = bool(
            (server is not None and server.connected)
            and (library is not None and library.available)
            and self._anchor is not None
            and len(diagnostics.warnings) == 0
        )

        return AriaResult(
            ok=True,
            data=ReadinessViewState(
                server=server if server is not None else ServerViewState(),
                library=library if library is not None else LibraryViewState(),
                diagnostics=diagnostics,
                control_configured=self._anchor is not None,
                all_ready=all_ready,
            ),
        )

    def send_lifecycle_intent(self, intent: LifecycleIntent) -> AriaResult[bool]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard

        helper_name = _LIFECYCLE_DRY_RUN_MAP.get(intent)
        if helper_name is None:
            return AriaResult(ok=False, error=_APPLY_MODE_BLOCKED)

        dry_run_helper = getattr(self._anchor, helper_name, None)
        if dry_run_helper is None:
            return AriaResult(ok=False, error=_APPLY_MODE_BLOCKED)

        dry_run_result = self._call_anchor_helper(helper_name)
        if dry_run_result.is_ok():
            return AriaResult(ok=True, data=True)
        return AriaResult(ok=False, error=dry_run_result.error)

    def get_permission_state(self) -> AriaResult[PermissionState]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        perm_result = self._call_anchor_helper("get_android_integration_report")
        if perm_result.is_err():
            return AriaResult(ok=False, error=perm_result.error)
        try:
            ps = AnchorResultMapper.to_permission_state(perm_result.data)
            return AriaResult(ok=True, data=ps)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_UNEXPECTED_OUTPUT.code,
                f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
            )

    def get_storage_access_state(self) -> AriaResult[StorageAccessState]:
        guard = self._guard_not_available()
        if guard is not None:
            return guard
        storage_result = self._call_anchor_helper("render_config_dry_run")
        if storage_result.is_err():
            return AriaResult(ok=False, error=storage_result.error)
        try:
            sas = AnchorResultMapper.to_storage_access_state(storage_result.data)
            return AriaResult(ok=True, data=sas)
        except Exception as exc:
            return ResultMappingService.err(
                _ANCHOR_UNEXPECTED_OUTPUT.code,
                f"{_ANCHOR_UNEXPECTED_OUTPUT.message}: {exc}",
            )
