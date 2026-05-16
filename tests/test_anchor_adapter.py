"""Tests for AnchorControlClient adapter — dry-run/offline implementation.

All tests use unittest.mock to fake Anchor public API helpers.
No real Anchor package, Navidrome, network, or filesystem is required.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from noqlen_aria.anchor_adapter import (
    AnchorControlClient,
    AnchorResultMapper,
)
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

# ── Helpers ──────────────────────────────────────────────────────────

MOCK_SERVER_OK = {
    "connected": True,
    "url": "http://mock:4533",
    "version": "0.52.5",
    "latency_ms": 5,
}

MOCK_SERVER_DISCONNECTED = {
    "connected": False,
    "url": "",
    "version": "",
    "latency_ms": None,
}

MOCK_SERVER_WITH_ERROR = {
    "connected": True,
    "url": "http://mock:4533",
    "version": "0.52.5",
    "latency_ms": 150,
    "last_error": {"code": "TIMEOUT", "message": "Request timed out"},
}

MOCK_LIBRARY_OK = {
    "available": True,
    "artist_count": 25,
    "album_count": 50,
    "track_count": 300,
    "total_duration_seconds": 72000,
    "last_scan_timestamp": 1_750_000_000.0,
}

MOCK_LIBRARY_EMPTY = {
    "available": False,
    "artist_count": 0,
    "album_count": 0,
    "track_count": 0,
    "total_duration_seconds": 0,
    "last_scan_timestamp": None,
}

MOCK_DIAGNOSTICS_OK = {"warnings": []}

MOCK_DIAGNOSTICS_WITH_WARNINGS = {
    "warnings": [
        {"code": "LATENCY_HIGH", "message": "Latency exceeds threshold"},
        {"code": "STALE_LIBRARY", "message": "Library scan is old"},
    ]
}

MOCK_READINESS_ALL_OK = {
    "server": MOCK_SERVER_OK,
    "library": MOCK_LIBRARY_OK,
    "diagnostics": MOCK_DIAGNOSTICS_OK,
    "control_configured": True,
    "all_ready": True,
}

MOCK_READINESS_PARTIAL = {
    "server": MOCK_SERVER_OK,
    "library": MOCK_LIBRARY_EMPTY,
    "diagnostics": MOCK_DIAGNOSTICS_OK,
    "control_configured": True,
    "all_ready": False,
}

MOCK_PERMISSION_GRANTED = {"permissions_granted": True}

MOCK_PERMISSION_DENIED = {"permissions_granted": False}

MOCK_PERMISSION_UNKNOWN = {"permissions_granted": None}

MOCK_STORAGE_AVAILABLE = {"storage_available": True}

MOCK_STORAGE_UNAVAILABLE = {"storage_available": False}

MOCK_STORAGE_UNKNOWN = {"storage_available": None}


def _make_mock_anchor(**overrides):
    """Create a mock Anchor public API module with standard helpers.

    Each helper can be overridden via keyword arguments.
    """
    mock = MagicMock()
    mock.inspect_fake_server = MagicMock(return_value=MOCK_SERVER_OK)
    mock.inspect_navidrome_offline = MagicMock(return_value=MOCK_LIBRARY_OK)
    mock.get_readiness_report = MagicMock(return_value=MOCK_READINESS_ALL_OK)
    mock.start_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.stop_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.restart_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.get_android_integration_report = MagicMock(
        return_value=MOCK_PERMISSION_GRANTED
    )
    mock.render_config_dry_run = MagicMock(return_value=MOCK_STORAGE_AVAILABLE)
    for name, value in overrides.items():
        setattr(mock, name, value)
    return mock


def _make_adapter(anchor_module=None):
    """Create an AnchorControlClient, optionally with a specific anchor module."""
    return AnchorControlClient(anchor_module=anchor_module)


# ── AnchorResultMapper tests ────────────────────────────────────────


class TestAnchorResultMapperServer:
    """TDD: AnchorResultMapper.to_server_view_state"""

    def test_maps_connected_server(self):
        result = AnchorResultMapper.to_server_view_state(MOCK_SERVER_OK)
        assert result.connected is True
        assert result.server_url == "http://mock:4533"
        assert result.server_version == "0.52.5"
        assert result.latency_ms == 5
        assert result.last_error is None

    def test_maps_disconnected_server(self):
        result = AnchorResultMapper.to_server_view_state(MOCK_SERVER_DISCONNECTED)
        assert result.connected is False
        assert result.server_url == ""
        assert result.server_version == ""
        assert result.latency_ms is None
        assert result.last_error is None

    def test_maps_server_with_last_error(self):
        result = AnchorResultMapper.to_server_view_state(MOCK_SERVER_WITH_ERROR)
        assert result.connected is True
        assert result.last_error is not None
        assert result.last_error.code == "TIMEOUT"
        assert result.last_error.message == "Request timed out"

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_server_view_state(None)
        assert result.connected is False
        assert result.server_url == ""

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_server_view_state({})
        assert result.connected is False
        assert result.server_url == ""
        assert result.latency_ms is None

    def test_handles_non_dict_input(self):
        result = AnchorResultMapper.to_server_view_state("bad")
        assert result.connected is False

    def test_handles_missing_keys(self):
        result = AnchorResultMapper.to_server_view_state({"connected": True})
        assert result.connected is True
        assert result.server_url == ""

    def test_returns_frozen_dataclass(self):
        result = AnchorResultMapper.to_server_view_state(MOCK_SERVER_OK)
        with pytest.raises(Exception):
            result.connected = False  # type: ignore[misc]


class TestAnchorResultMapperLibrary:
    """TDD: AnchorResultMapper.to_library_view_state"""

    def test_maps_available_library(self):
        result = AnchorResultMapper.to_library_view_state(MOCK_LIBRARY_OK)
        assert result.available is True
        assert result.artist_count == 25
        assert result.album_count == 50
        assert result.track_count == 300
        assert result.total_duration_seconds == 72000
        assert result.last_scan_timestamp == 1_750_000_000.0

    def test_maps_unavailable_library(self):
        result = AnchorResultMapper.to_library_view_state(MOCK_LIBRARY_EMPTY)
        assert result.available is False
        assert result.artist_count == 0
        assert result.last_scan_timestamp is None

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_library_view_state(None)
        assert result.available is False
        assert result.artist_count == 0

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_library_view_state({})
        assert result.available is False

    def test_handles_non_dict_input(self):
        result = AnchorResultMapper.to_library_view_state("bad")
        assert result.available is False

    def test_handles_invalid_counts(self):
        result = AnchorResultMapper.to_library_view_state(
            {"available": True, "artist_count": "not_a_number"}
        )
        assert result.artist_count == 0


class TestAnchorResultMapperReadiness:
    """TDD: AnchorResultMapper.to_readiness_view_state"""

    def test_maps_all_ready(self):
        result = AnchorResultMapper.to_readiness_view_state(MOCK_READINESS_ALL_OK)
        assert result.server.connected is True
        assert result.library.available is True
        assert result.control_configured is True
        assert result.all_ready is True
        assert len(result.diagnostics.warnings) == 0

    def test_maps_partial_readiness(self):
        result = AnchorResultMapper.to_readiness_view_state(MOCK_READINESS_PARTIAL)
        assert result.server.connected is True
        assert result.library.available is False
        assert result.all_ready is False

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_readiness_view_state(None)
        assert result.control_configured is False
        assert result.all_ready is False

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_readiness_view_state({})
        assert result.control_configured is False
        assert result.all_ready is False


class TestAnchorResultMapperDiagnostics:
    """TDD: AnchorResultMapper.to_diagnostics_view_state"""

    def test_maps_no_warnings(self):
        result = AnchorResultMapper.to_diagnostics_view_state(MOCK_DIAGNOSTICS_OK)
        assert len(result.warnings) == 0

    def test_maps_warnings(self):
        result = AnchorResultMapper.to_diagnostics_view_state(
            MOCK_DIAGNOSTICS_WITH_WARNINGS
        )
        assert len(result.warnings) == 2
        assert result.warnings[0].code == "LATENCY_HIGH"
        assert result.warnings[1].code == "STALE_LIBRARY"

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_diagnostics_view_state(None)
        assert len(result.warnings) == 0

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_diagnostics_view_state({})
        assert len(result.warnings) == 0

    def test_handles_non_list_warnings(self):
        result = AnchorResultMapper.to_diagnostics_view_state({"warnings": "bad"})
        assert len(result.warnings) == 0

    def test_handles_non_dict_entries(self):
        result = AnchorResultMapper.to_diagnostics_view_state(
            {"warnings": ["not_a_dict"]}
        )
        assert len(result.warnings) == 0


class TestAnchorResultMapperPermission:
    """TDD: AnchorResultMapper.to_permission_state"""

    def test_maps_granted_by_bool(self):
        result = AnchorResultMapper.to_permission_state(MOCK_PERMISSION_GRANTED)
        assert result == PermissionState.GRANTED

    def test_maps_denied_by_bool(self):
        result = AnchorResultMapper.to_permission_state(MOCK_PERMISSION_DENIED)
        assert result == PermissionState.DENIED

    def test_maps_unknown_by_none(self):
        result = AnchorResultMapper.to_permission_state(MOCK_PERMISSION_UNKNOWN)
        assert result == PermissionState.UNKNOWN

    def test_maps_granted_by_status_string(self):
        result = AnchorResultMapper.to_permission_state(
            {"permission_status": "GRANTED"}
        )
        assert result == PermissionState.GRANTED

    def test_maps_denied_by_status_string(self):
        result = AnchorResultMapper.to_permission_state(
            {"permission_status": "denied"}
        )
        assert result == PermissionState.DENIED

    def test_maps_not_applicable(self):
        result = AnchorResultMapper.to_permission_state(
            {"permission_status": "NOT_APPLICABLE"}
        )
        assert result == PermissionState.NOT_APPLICABLE

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_permission_state(None)
        assert result == PermissionState.UNKNOWN

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_permission_state({})
        assert result == PermissionState.UNKNOWN

    def test_handles_non_dict_input(self):
        result = AnchorResultMapper.to_permission_state("bad")
        assert result == PermissionState.UNKNOWN


class TestAnchorResultMapperStorage:
    """TDD: AnchorResultMapper.to_storage_access_state"""

    def test_maps_available_by_bool(self):
        result = AnchorResultMapper.to_storage_access_state(MOCK_STORAGE_AVAILABLE)
        assert result == StorageAccessState.AVAILABLE

    def test_maps_unavailable_by_bool(self):
        result = AnchorResultMapper.to_storage_access_state(MOCK_STORAGE_UNAVAILABLE)
        assert result == StorageAccessState.UNAVAILABLE

    def test_maps_unknown_by_none(self):
        result = AnchorResultMapper.to_storage_access_state(MOCK_STORAGE_UNKNOWN)
        assert result == StorageAccessState.UNKNOWN

    def test_maps_available_by_status_string(self):
        result = AnchorResultMapper.to_storage_access_state(
            {"storage_status": "AVAILABLE"}
        )
        assert result == StorageAccessState.AVAILABLE

    def test_maps_unavailable_by_status_string(self):
        result = AnchorResultMapper.to_storage_access_state(
            {"storage_status": "unavailable"}
        )
        assert result == StorageAccessState.UNAVAILABLE

    def test_handles_none_input(self):
        result = AnchorResultMapper.to_storage_access_state(None)
        assert result == StorageAccessState.UNKNOWN

    def test_handles_empty_dict(self):
        result = AnchorResultMapper.to_storage_access_state({})
        assert result == StorageAccessState.UNKNOWN

    def test_handles_non_dict_input(self):
        result = AnchorResultMapper.to_storage_access_state(123)
        assert result == StorageAccessState.UNKNOWN


# ── AnchorControlClient protocol conformance ────────────────────────


class TestAnchorControlClientProtocol:
    """TDD: AnchorControlClient satisfies the ControlClient protocol."""

    def test_is_instance_of_control_client(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        assert isinstance(adapter, ControlClient)

    def test_has_all_protocol_methods(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        assert hasattr(adapter, "ping")
        assert hasattr(adapter, "get_server_state")
        assert hasattr(adapter, "get_library_state")
        assert hasattr(adapter, "get_readiness")
        assert hasattr(adapter, "send_lifecycle_intent")
        assert hasattr(adapter, "get_permission_state")
        assert hasattr(adapter, "get_storage_access_state")

    def test_is_anchor_available_false_without_anchor(self):
        with patch(
            "noqlen_aria.anchor_adapter._get_anchor", return_value=None
        ):
            assert AnchorControlClient.is_anchor_available() is False

    def test_is_anchor_available_with_mocked_anchor(self):
        with patch(
            "noqlen_aria.anchor_adapter._anchor_module_cache", object()
        ):
            assert AnchorControlClient.is_anchor_available() is True


# ── AnchorControlClient not-available behavior ──────────────────────


class TestAnchorControlClientNotAvailable:
    """TDD: All methods return ANCHOR_NOT_AVAILABLE when noqlen_anchor is absent."""

    def test_ping_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.ping()
        _assert_not_available(result)

    def test_get_server_state_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.get_server_state()
        _assert_not_available(result)

    def test_get_library_state_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.get_library_state()
        _assert_not_available(result)

    def test_get_readiness_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.get_readiness()
        _assert_not_available(result)

    def test_send_lifecycle_intent_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE)
        _assert_not_available(result)

    def test_get_permission_state_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.get_permission_state()
        _assert_not_available(result)

    def test_get_storage_access_state_returns_not_available(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.get_storage_access_state()
        _assert_not_available(result)


def _assert_not_available(result: AriaResult):
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "ANCHOR_NOT_AVAILABLE"


# ── AnchorControlClient ping ────────────────────────────────────────


class TestAnchorControlClientPing:
    def test_ping_returns_true_when_server_connected(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.ping()
        assert result.is_ok()
        assert result.data is True

    def test_ping_returns_false_when_server_disconnected(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(return_value=MOCK_SERVER_DISCONNECTED)
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.ping()
        assert result.is_ok()
        assert result.data is False

    def test_ping_call_failed_when_helper_raises(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                side_effect=RuntimeError("connection refused")
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.ping()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"

    def test_ping_helper_not_found(self):
        mock = _make_mock_anchor()
        del mock.inspect_fake_server
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.ping()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_HELPER_NOT_FOUND"


# ── AnchorControlClient server state ────────────────────────────────


class TestAnchorControlClientServerState:
    def test_returns_server_view_state(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.get_server_state()
        assert result.is_ok()
        assert isinstance(result.data, ServerViewState)
        assert result.data.connected is True
        assert result.data.server_url == "http://mock:4533"

    def test_returns_disconnected_state(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                return_value=MOCK_SERVER_DISCONNECTED
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_server_state()
        assert result.is_ok()
        assert result.data.connected is False

    def test_handles_helper_exception(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                side_effect=Exception("boom")
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_server_state()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"

    def test_handles_unexpected_output(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                return_value="not_a_dict_but_wont_crash"
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_server_state()
        assert result.is_ok()
        assert result.data.connected is False


# ── AnchorControlClient library state ───────────────────────────────


class TestAnchorControlClientLibraryState:
    def test_returns_library_view_state(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.get_library_state()
        assert result.is_ok()
        assert isinstance(result.data, LibraryViewState)
        assert result.data.available is True
        assert result.data.artist_count == 25

    def test_returns_unavailable_library(self):
        mock = _make_mock_anchor(
            inspect_navidrome_offline=MagicMock(
                return_value=MOCK_LIBRARY_EMPTY
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_library_state()
        assert result.is_ok()
        assert result.data.available is False

    def test_handles_helper_exception(self):
        mock = _make_mock_anchor(
            inspect_navidrome_offline=MagicMock(
                side_effect=Exception("nav error")
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_library_state()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"


# ── AnchorControlClient readiness ───────────────────────────────────


class TestAnchorControlClientReadiness:
    def test_returns_all_ready(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.get_readiness()
        assert result.is_ok()
        assert isinstance(result.data, ReadinessViewState)
        assert result.data.all_ready is True
        assert result.data.control_configured is True

    def test_returns_partial_readiness(self):
        mock = _make_mock_anchor(
            get_readiness_report=MagicMock(
                return_value=MOCK_READINESS_PARTIAL
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_ok()
        assert result.data.all_ready is False
        assert result.data.server.connected is True
        assert result.data.library.available is False

    def test_falls_back_to_composed_readiness(self):
        mock = _make_mock_anchor()
        del mock.get_readiness_report
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_ok()
        assert result.data.all_ready is True

    def test_fallback_with_disconnected_server(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                return_value=MOCK_SERVER_DISCONNECTED
            )
        )
        del mock.get_readiness_report
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_ok()
        assert result.data.all_ready is False

    def test_fallback_with_unavailable_library(self):
        mock = _make_mock_anchor(
            inspect_navidrome_offline=MagicMock(
                return_value=MOCK_LIBRARY_EMPTY
            )
        )
        del mock.get_readiness_report
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_ok()
        assert result.data.all_ready is False

    def test_readiness_report_helper_exception(self):
        mock = _make_mock_anchor(
            get_readiness_report=MagicMock(side_effect=Exception("boom"))
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"

    def test_readiness_report_unexpected_output(self):
        mock = _make_mock_anchor(
            get_readiness_report=MagicMock(return_value="not_a_dict")
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_readiness()
        assert result.is_ok()
        assert result.data.control_configured is False


# ── AnchorControlClient lifecycle intent ────────────────────────────


class TestAnchorControlClientLifecycleIntent:
    """TDD: send_lifecycle_intent must never execute real apply operations."""

    def test_initialize_calls_dry_run_not_apply(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE)
        assert result.is_ok()
        assert result.data is True
        mock.start_navidrome_dry_run.assert_called_once()

    def test_shutdown_calls_dry_run(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.SHUTDOWN)
        assert result.is_ok()
        assert result.data is True
        mock.stop_navidrome_dry_run.assert_called_once()

    def test_reset_calls_dry_run(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.RESET)
        assert result.is_ok()
        assert result.data is True
        mock.restart_navidrome_dry_run.assert_called_once()

    def test_dry_run_helper_not_found_blocks_apply(self):
        mock = _make_mock_anchor()
        del mock.start_navidrome_dry_run
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE)
        _assert_apply_blocked(result)

    def test_dry_run_helper_exception(self):
        mock = _make_mock_anchor(
            start_navidrome_dry_run=MagicMock(
                side_effect=Exception("config error")
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE)
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"

    def test_never_calls_apply_helpers(self):
        mock = _make_mock_anchor()
        mock.start_navidrome_apply = MagicMock()
        adapter = _make_adapter(anchor_module=mock)
        adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE)
        mock.start_navidrome_apply.assert_not_called()

    def test_apply_mode_blocked_when_dry_run_not_available(self):
        mock = _make_mock_anchor()
        del mock.start_navidrome_dry_run
        del mock.stop_navidrome_dry_run
        del mock.restart_navidrome_dry_run
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.send_lifecycle_intent(LifecycleIntent.SHUTDOWN)
        _assert_apply_blocked(result)


def _assert_apply_blocked(result: AriaResult):
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "APPLY_MODE_BLOCKED"


# ── AnchorControlClient permission state ────────────────────────────


class TestAnchorControlClientPermission:
    def test_returns_granted(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.get_permission_state()
        assert result.is_ok()
        assert result.data == PermissionState.GRANTED

    def test_returns_denied(self):
        mock = _make_mock_anchor(
            get_android_integration_report=MagicMock(
                return_value=MOCK_PERMISSION_DENIED
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_permission_state()
        assert result.is_ok()
        assert result.data == PermissionState.DENIED

    def test_handles_helper_exception(self):
        mock = _make_mock_anchor(
            get_android_integration_report=MagicMock(
                side_effect=Exception("boom")
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_permission_state()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"

    def test_handles_unexpected_output(self):
        mock = _make_mock_anchor(
            get_android_integration_report=MagicMock(
                return_value="bad_data"
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_permission_state()
        assert result.is_ok()
        assert result.data == PermissionState.UNKNOWN


# ── AnchorControlClient storage state ───────────────────────────────


class TestAnchorControlClientStorage:
    def test_returns_available(self):
        adapter = _make_adapter(anchor_module=_make_mock_anchor())
        result = adapter.get_storage_access_state()
        assert result.is_ok()
        assert result.data == StorageAccessState.AVAILABLE

    def test_returns_unavailable(self):
        mock = _make_mock_anchor(
            render_config_dry_run=MagicMock(
                return_value=MOCK_STORAGE_UNAVAILABLE
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_storage_access_state()
        assert result.is_ok()
        assert result.data == StorageAccessState.UNAVAILABLE

    def test_handles_helper_exception(self):
        mock = _make_mock_anchor(
            render_config_dry_run=MagicMock(side_effect=Exception("boom"))
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_storage_access_state()
        assert result.is_err()
        assert result.error is not None
        assert result.error.code == "ANCHOR_CALL_FAILED"


# ── AnchorControlClient determinism ─────────────────────────────────


class TestAnchorControlClientDeterminism:
    """TDD: Repeated calls with identical mock state produce identical results."""

    def test_repeated_ping_returns_same(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        r1 = adapter.ping()
        r2 = adapter.ping()
        assert r1 == r2
        assert r1.data == r2.data

    def test_repeated_server_state_returns_same(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        r1 = adapter.get_server_state()
        r2 = adapter.get_server_state()
        assert r1 == r2

    def test_repeated_readiness_returns_same(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        r1 = adapter.get_readiness()
        r2 = adapter.get_readiness()
        assert r1 == r2


# ── Integration with Aria services ──────────────────────────────────


class TestAnchorControlClientServiceIntegration:
    """TDD: AnchorControlClient works with existing Aria services."""

    def test_status_service_with_anchor_adapter(self):
        from noqlen_aria.services import StatusService

        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        service = StatusService(adapter)
        result = service.get_status()
        assert result.is_ok()
        assert isinstance(result.data, ServerViewState)
        assert result.data.connected is True

    def test_status_service_with_disconnected_anchor(self):
        from noqlen_aria.services import StatusService

        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                return_value=MOCK_SERVER_DISCONNECTED
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        service = StatusService(adapter)
        result = service.get_status()
        assert result.is_ok()
        assert result.data.connected is False

    def test_diagnostics_service_with_anchor_adapter(self):
        from noqlen_aria.services import DiagnosticsService

        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        service = DiagnosticsService(adapter)
        result = service.collect()
        assert result.is_ok()
        assert isinstance(result.data, DiagnosticsViewState)

    def test_lifecycle_intent_service_preview_with_anchor(self):
        from noqlen_aria.services import LifecycleIntentService

        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        service = LifecycleIntentService(adapter)
        result = service.preview(LifecycleIntent.INITIALIZE)
        assert result.is_ok()
        assert result.data.intent == LifecycleIntent.INITIALIZE

    def test_readiness_service_with_anchor_adapter(self):
        from noqlen_aria.services import ReadinessService

        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        service = ReadinessService(adapter)
        result = service.assess()
        assert result.is_ok()
        assert isinstance(result.data, ReadinessViewState)
        assert result.data.all_ready is True

    def test_readiness_service_with_degraded_anchor(self):
        from noqlen_aria.services import ReadinessService

        mock = _make_mock_anchor(
            inspect_navidrome_offline=MagicMock(
                return_value=MOCK_LIBRARY_EMPTY
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        service = ReadinessService(adapter)
        result = service.assess()
        assert result.is_ok()
        assert result.data.library.available is False

    def test_adapter_and_fake_client_equivalent_for_same_data(self):
        from noqlen_aria.contracts import FakeControlClient
        from noqlen_aria.services import StatusService

        fake = FakeControlClient()
        fake._server_state_override = ServerViewState(
            connected=True,
            server_url="http://mock:4533",
            server_version="0.52.5",
            latency_ms=5,
        )
        anchor = _make_adapter(anchor_module=_make_mock_anchor())

        fake_service = StatusService(fake)
        anchor_service = StatusService(anchor)

        fake_result = fake_service.get_status()
        anchor_result = anchor_service.get_status()

        assert fake_result.is_ok()
        assert anchor_result.is_ok()
        assert fake_result.data.connected == anchor_result.data.connected


# ── Sanitization ────────────────────────────────────────────────────


class TestAnchorControlClientSanitization:
    """TDD: Outputs are sanitized — no secrets, raw logs, personal paths."""

    def test_server_state_excludes_raw_internals(self):
        mock = _make_mock_anchor(
            inspect_fake_server=MagicMock(
                return_value={
                    "connected": True,
                    "url": "http://ok",
                    "version": "1.0",
                    "_internal_token": "secret123",
                    "_provider_config": "/home/user/config",
                }
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_server_state()
        assert result.is_ok()
        state = result.data
        assert state.connected is True
        assert state.server_url == "http://ok"

    def test_error_message_does_not_contain_paths(self):
        adapter = _make_adapter(anchor_module=None)
        result = adapter.ping()
        assert result.is_err()
        assert "/home" not in result.error.message
        assert "\\" not in result.error.message

    def test_library_state_sanitized(self):
        mock = _make_mock_anchor(
            inspect_navidrome_offline=MagicMock(
                return_value={
                    "available": True,
                    "artist_count": 5,
                    "_raw_db_path": "/var/navidrome/db",
                }
            )
        )
        adapter = _make_adapter(anchor_module=mock)
        result = adapter.get_library_state()
        assert result.is_ok()
        assert result.data.artist_count == 5


# ── Edge cases ──────────────────────────────────────────────────────


class TestAnchorControlClientEdgeCases:
    """TDD: Adapter handles edge cases gracefully."""

    def test_anchor_module_is_none_after_init(self):
        adapter = _make_adapter(anchor_module=None)
        assert adapter._not_available() is True

    def test_all_methods_with_none_module_return_error(self):
        adapter = _make_adapter(anchor_module=None)
        for method_name in [
            "ping",
            "get_server_state",
            "get_library_state",
            "get_readiness",
            "get_permission_state",
            "get_storage_access_state",
        ]:
            method = getattr(adapter, method_name)
            result = method()
            assert result.is_err(), f"{method_name} should return error"
            assert (
                result.error.code == "ANCHOR_NOT_AVAILABLE"
            ), f"{method_name}: {result.error.code}"

    def test_constructor_with_explicit_none(self):
        adapter = AnchorControlClient(anchor_module=None)
        assert adapter._not_available() is True

    def test_constructor_with_custom_module(self):
        custom = MagicMock()
        custom.inspect_fake_server = MagicMock(
            return_value={"connected": False}
        )
        custom.inspect_navidrome_offline = MagicMock(
            return_value={"available": False}
        )
        custom.render_config_dry_run = MagicMock(
            return_value={"storage_available": True}
        )
        custom.get_android_integration_report = MagicMock(
            return_value={"permissions_granted": True}
        )
        custom.start_navidrome_dry_run = MagicMock(
            return_value={"dry_run": "ok"}
        )
        custom.stop_navidrome_dry_run = MagicMock(
            return_value={"dry_run": "ok"}
        )
        custom.restart_navidrome_dry_run = MagicMock(
            return_value={"dry_run": "ok"}
        )
        adapter = AnchorControlClient(anchor_module=custom)
        assert adapter._not_available() is False
        r = adapter.ping()
        assert r.is_ok()
        assert r.data is False


# ── Safety: no provider internals or CLI ────────────────────────────


class TestAnchorControlClientSafety:
    """TDD: Adapter never calls provider internals or Anchor CLI."""

    def test_no_subprocess_calls(self):
        mock = _make_mock_anchor()
        adapter = _make_adapter(anchor_module=mock)
        for method in [
            lambda: adapter.ping(),
            lambda: adapter.get_server_state(),
            lambda: adapter.get_library_state(),
            lambda: adapter.get_readiness(),
            lambda: adapter.get_permission_state(),
            lambda: adapter.get_storage_access_state(),
            lambda: adapter.send_lifecycle_intent(LifecycleIntent.INITIALIZE),
        ]:
            method()

    def test_does_not_import_provider_internals(self):
        import sys

        assert "noqlen_anchor.provider" not in sys.modules
        assert "noqlen_anchor.core" not in sys.modules
        assert "noqlen_anchor.internal" not in sys.modules
