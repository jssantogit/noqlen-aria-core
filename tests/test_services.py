"""Tests for Aria Core services and FakeControlClient failure-injection hooks."""

import time

import pytest

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    AriaWarning,
    DiagnosticsViewState,
    FakeControlClient,
    LibraryViewState,
    LifecycleIntent,
    PermissionState,
    ReadinessViewState,
    ServerViewState,
    StorageAccessState,
)
from noqlen_aria.services import (
    DEFAULT_MAX_LATENCY_MS,
    DEFAULT_MAX_LIBRARY_STALENESS_SECONDS,
    DiagnosticsService,
    LifecycleIntentPreview,
    LifecycleIntentService,
    ReadinessService,
    ResultMappingError,
    ResultMappingService,
    StatusService,
)


@pytest.fixture
def fake() -> FakeControlClient:
    return FakeControlClient()


# ── FakeControlClient error injection ─────────────────────────


def test_fake_ping_error_injection(fake):
    err = AriaError(code="PING_FAILED", message="cannot reach server")
    fake._ping_error = err
    result = fake.ping()
    assert result.is_err()
    assert result.error is err
    assert result.data is None


def test_fake_server_state_error_injection(fake):
    err = AriaError(code="SERVER_DOWN", message="server is down")
    fake._server_state_error = err
    result = fake.get_server_state()
    assert result.is_err()
    assert result.error is err


def test_fake_library_state_error_injection(fake):
    err = AriaError(code="LIBRARY_UNAVAILABLE", message="library not found")
    fake._library_state_error = err
    result = fake.get_library_state()
    assert result.is_err()
    assert result.error is err


def test_fake_readiness_error_injection(fake):
    err = AriaError(code="READINESS_FAILED", message="cannot assess readiness")
    fake._readiness_error = err
    result = fake.get_readiness()
    assert result.is_err()
    assert result.error is err


def test_fake_lifecycle_error_injection(fake):
    err = AriaError(code="LIFECYCLE_BLOCKED", message="lifecycle operation blocked")
    fake._lifecycle_error = err
    for intent in LifecycleIntent:
        result = fake.send_lifecycle_intent(intent)
        assert result.is_err()
        assert result.error is err


def test_fake_permission_state_error_injection(fake):
    err = AriaError(code="PERMISSION_CHECK_FAILED", message="cannot check permissions")
    fake._permission_state_error = err
    result = fake.get_permission_state()
    assert result.is_err()
    assert result.error is err


def test_fake_storage_access_error_injection(fake):
    err = AriaError(code="STORAGE_CHECK_FAILED", message="cannot check storage")
    fake._storage_access_error = err
    result = fake.get_storage_access_state()
    assert result.is_err()
    assert result.error is err


# ── FakeControlClient value overrides ─────────────────────────


def test_fake_server_state_override(fake):
    custom = ServerViewState(
        connected=False, server_url="http://offline:4533", latency_ms=500
    )
    fake._server_state_override = custom
    result = fake.get_server_state()
    assert result.is_ok()
    assert result.data is custom
    assert result.data.connected is False
    assert result.data.latency_ms == 500


def test_fake_library_state_override(fake):
    custom = LibraryViewState(
        available=False, artist_count=0, album_count=0, track_count=0
    )
    fake._library_state_override = custom
    result = fake.get_library_state()
    assert result.is_ok()
    assert result.data is custom
    assert result.data.available is False


def test_fake_readiness_override(fake):
    custom = ReadinessViewState(
        server=ServerViewState(connected=False),
        library=LibraryViewState(available=False),
        control_configured=False,
        all_ready=False,
    )
    fake._readiness_override = custom
    result = fake.get_readiness()
    assert result.is_ok()
    assert result.data is custom
    assert result.data.all_ready is False


def test_fake_permission_state_override(fake):
    fake._permission_state_override = PermissionState.DENIED
    result = fake.get_permission_state()
    assert result.is_ok()
    assert result.data is PermissionState.DENIED


def test_fake_storage_access_override(fake):
    fake._storage_access_override = StorageAccessState.UNAVAILABLE
    result = fake.get_storage_access_state()
    assert result.is_ok()
    assert result.data is StorageAccessState.UNAVAILABLE


def test_fake_error_takes_priority_over_override(fake):
    err = AriaError(code="E", message="e")
    fake._server_state_error = err
    fake._server_state_override = ServerViewState(connected=True)
    result = fake.get_server_state()
    assert result.is_err()
    assert result.error is err


# ── FakeControlClient backward compatibility ──────────────────


def test_fake_untouched_returns_optimistic_defaults(fake):
    assert fake.ping().is_ok()
    assert fake.get_server_state().is_ok()
    assert fake.get_library_state().is_ok()
    assert fake.get_readiness().is_ok()
    assert fake.get_permission_state().is_ok()
    assert fake.get_storage_access_state().is_ok()


def test_fake_deterministic_with_hooks(fake):
    err = AriaError(code="E", message="m")
    fake._ping_error = err
    r1 = fake.ping()
    r2 = fake.ping()
    assert r1 == r2
    assert r1.error == r2.error


def test_fake_readiness_propagates_server_error(fake):
    err = AriaError(code="SERVER_DOWN", message="down")
    fake._server_state_error = err
    result = fake.get_readiness()
    assert result.is_err()
    assert result.error is err


def test_fake_readiness_propagates_library_error(fake):
    err = AriaError(code="LIB_DOWN", message="down")
    fake._library_state_error = err
    result = fake.get_readiness()
    assert result.is_err()
    assert result.error is err


# ── ResultMappingService ──────────────────────────────────────


def test_result_mapping_ok():
    result = ResultMappingService.ok(42)
    assert result.is_ok()
    assert result.data == 42
    assert result.error is None


def test_result_mapping_ok_with_none():
    result = ResultMappingService.ok(None)
    assert result.is_ok()
    assert result.data is None


def test_result_mapping_ok_with_complex_type():
    state = ServerViewState(connected=True, server_url="http://s:4533")
    result = ResultMappingService.ok(state)
    assert result.is_ok()
    assert result.data is state
    assert result.data.connected is True


def test_result_mapping_err():
    result = ResultMappingService.err("FAIL", "something went wrong")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "FAIL"
    assert result.error.message == "something went wrong"
    assert result.data is None


def test_result_mapping_unwrap_success():
    result = AriaResult(ok=True, data="hello")
    assert ResultMappingService.unwrap(result) == "hello"


def test_result_mapping_unwrap_failure_raises():
    result = AriaResult(
        ok=False,
        error=AriaError(code="FAIL", message="something went wrong"),
    )
    with pytest.raises(ResultMappingError, match="FAIL"):
        ResultMappingService.unwrap(result)


def test_result_mapping_unwrap_or_success():
    result = AriaResult(ok=True, data="hello")
    assert ResultMappingService.unwrap_or(result, "default") == "hello"


def test_result_mapping_unwrap_or_failure():
    result = AriaResult(
        ok=False,
        error=AriaError(code="FAIL", message="m"),
    )
    assert ResultMappingService.unwrap_or(result, "default") == "default"


def test_result_mapping_map_error_success_passes_through():
    result = AriaResult(ok=True, data=42)
    mapped = ResultMappingService.map_error(result, "NEW", "new message")
    assert mapped.is_ok()
    assert mapped.data == 42


def test_result_mapping_map_error_failure_rewrites():
    result = AriaResult(
        ok=False,
        error=AriaError(code="OLD", message="old message"),
    )
    mapped = ResultMappingService.map_error(result, "NEW", "new message")
    assert mapped.is_err()
    assert mapped.error is not None
    assert mapped.error.code == "NEW"
    assert mapped.error.message == "new message"


def test_result_mapping_map_error_preserves_data():
    result = AriaResult(ok=True, data=True)
    mapped = ResultMappingService.map_error(result, "X", "y")
    assert mapped.data is True


def test_result_mapping_unwrap_ok_with_none_data():
    result = AriaResult(ok=True, data=None)
    assert ResultMappingService.unwrap(result) is None


def test_result_mapping_unwrap_err_with_none_error():
    result = AriaResult(ok=False, error=None)
    with pytest.raises(ResultMappingError, match="unknown error"):
        ResultMappingService.unwrap(result)


# ── LifecycleIntentPreview ────────────────────────────────────


def test_lifecycle_intent_preview_construction():
    preview = LifecycleIntentPreview(
        intent=LifecycleIntent.INITIALIZE,
        description="Initialize the system",
        reversible=True,
        requires_apply=True,
    )
    assert preview.intent is LifecycleIntent.INITIALIZE
    assert preview.description == "Initialize the system"
    assert preview.reversible is True
    assert preview.requires_apply is True


def test_lifecycle_intent_preview_immutable():
    preview = LifecycleIntentPreview(
        intent=LifecycleIntent.SHUTDOWN,
        description="Shutdown",
        reversible=True,
        requires_apply=True,
    )
    with pytest.raises(Exception):
        preview.description = "changed"  # type: ignore[misc]


def test_lifecycle_intent_preview_equality():
    a = LifecycleIntentPreview(
        intent=LifecycleIntent.RESET, description="r", reversible=False, requires_apply=True
    )
    b = LifecycleIntentPreview(
        intent=LifecycleIntent.RESET, description="r", reversible=False, requires_apply=True
    )
    c = LifecycleIntentPreview(
        intent=LifecycleIntent.RESET, description="diff", reversible=False, requires_apply=True
    )
    assert a == b
    assert a != c


# ── LifecycleIntentService ────────────────────────────────────


@pytest.fixture
def lifecycle_svc(fake) -> LifecycleIntentService:
    return LifecycleIntentService(fake)


def test_lifecycle_preview_initialize(lifecycle_svc):
    result = lifecycle_svc.preview(LifecycleIntent.INITIALIZE)
    assert result.is_ok()
    preview = result.data
    assert preview.intent is LifecycleIntent.INITIALIZE
    assert "Initialize" in preview.description
    assert preview.reversible is True
    assert preview.requires_apply is True


def test_lifecycle_preview_shutdown(lifecycle_svc):
    result = lifecycle_svc.preview(LifecycleIntent.SHUTDOWN)
    assert result.is_ok()
    preview = result.data
    assert preview.intent is LifecycleIntent.SHUTDOWN
    assert "shut down" in preview.description.lower()
    assert preview.reversible is True
    assert preview.requires_apply is True


def test_lifecycle_preview_reset(lifecycle_svc):
    result = lifecycle_svc.preview(LifecycleIntent.RESET)
    assert result.is_ok()
    preview = result.data
    assert preview.intent is LifecycleIntent.RESET
    assert "Reset" in preview.description
    assert preview.reversible is False
    assert preview.requires_apply is True


def test_lifecycle_validate_valid_names(lifecycle_svc):
    for name in ("INITIALIZE", "SHUTDOWN", "RESET", "initialize", "shutdown", "reset"):
        result = lifecycle_svc.validate(name)
        assert result.is_ok(), f"Failed to validate: {name}"
        assert isinstance(result.data, LifecycleIntent)


def test_lifecycle_validate_invalid_name(lifecycle_svc):
    result = lifecycle_svc.validate("BOGUS")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_LIFECYCLE_INTENT"


def test_lifecycle_validate_empty_string(lifecycle_svc):
    result = lifecycle_svc.validate("")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_LIFECYCLE_INTENT"


def test_lifecycle_preview_does_not_call_send_lifecycle_intent(lifecycle_svc, fake):
    tracker = {"called": False}

    def tracked_send(intent):
        tracker["called"] = True
        return AriaResult(ok=True, data=True)

    fake.send_lifecycle_intent = tracked_send
    lifecycle_svc.preview(LifecycleIntent.INITIALIZE)
    assert tracker["called"] is False


def test_lifecycle_preview_deterministic(lifecycle_svc):
    r1 = lifecycle_svc.preview(LifecycleIntent.INITIALIZE)
    r2 = lifecycle_svc.preview(LifecycleIntent.INITIALIZE)
    assert r1 == r2


# ── StatusService ─────────────────────────────────────────────


@pytest.fixture
def status_svc(fake) -> StatusService:
    return StatusService(fake)


def test_status_connected(status_svc):
    result = status_svc.get_status()
    assert result.is_ok()
    assert isinstance(result.data, ServerViewState)
    assert result.data.connected is True
    assert result.data.server_url == "http://fake:4533"


def test_status_ping_failure(fake):
    fake._ping_error = AriaError(code="PING_FAILED", message="unreachable")
    svc = StatusService(fake)
    result = svc.get_status()
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "PING_FAILED"


def test_status_with_server_last_error(fake):
    err = AriaError(code="PREV_FAIL", message="previous failure")
    custom = ServerViewState(connected=True, last_error=err)
    fake._server_state_override = custom
    svc = StatusService(fake)
    result = svc.get_status()
    assert result.is_ok()
    assert result.data.last_error is err
    assert result.data.last_error.code == "PREV_FAIL"


def test_status_returns_server_view_state_instance(status_svc):
    result = status_svc.get_status()
    assert isinstance(result, AriaResult)
    if result.is_ok():
        assert isinstance(result.data, ServerViewState)


def test_status_uses_client_injection(fake):
    svc1 = StatusService(fake)
    svc2 = StatusService(fake)
    r1 = svc1.get_status()
    r2 = svc2.get_status()
    assert r1 == r2


# ── DiagnosticsService ────────────────────────────────────────


@pytest.fixture
def diag_svc(fake) -> DiagnosticsService:
    return DiagnosticsService(fake)


def test_diagnostics_all_green(fake):
    fresh_library = LibraryViewState(
        available=True,
        last_scan_timestamp=time.time() - 60,  # 1 minute ago, well within threshold
    )
    fake._library_state_override = fresh_library
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    assert result.data is not None
    assert result.data.warnings == []


def test_diagnostics_high_latency(fake):
    custom = ServerViewState(
        connected=True, latency_ms=500  # exceeds default 200ms threshold
    )
    fake._server_state_override = custom
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    assert len(result.data.warnings) >= 1
    latency_warnings = [w for w in result.data.warnings if w.code == "LATENCY_HIGH"]
    assert len(latency_warnings) == 1
    assert "500" in latency_warnings[0].message


def test_diagnostics_latency_within_threshold(diag_svc):
    result = diag_svc.collect()
    latency_warnings = [w for w in result.data.warnings if w.code == "LATENCY_HIGH"]
    assert len(latency_warnings) == 0


def test_diagnostics_stale_library(fake):
    old_ts = time.time() - 100_000  # ~27 hours ago, exceeds 24h threshold
    custom = LibraryViewState(
        available=True, last_scan_timestamp=old_ts
    )
    fake._library_state_override = custom
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    stale_warnings = [w for w in result.data.warnings if w.code == "LIBRARY_STALE"]
    assert len(stale_warnings) == 1


def test_diagnostics_fresh_library(fake):
    fresh_library = LibraryViewState(
        available=True,
        last_scan_timestamp=time.time() - 60,
    )
    fake._library_state_override = fresh_library
    svc = DiagnosticsService(fake)
    result = svc.collect()
    stale_warnings = [w for w in result.data.warnings if w.code == "LIBRARY_STALE"]
    assert len(stale_warnings) == 0


def test_diagnostics_never_scanned_library(fake):
    custom = LibraryViewState(available=True, last_scan_timestamp=None)
    fake._library_state_override = custom
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    never_scanned = [w for w in result.data.warnings if w.code == "LIBRARY_NEVER_SCANNED"]
    assert len(never_scanned) == 1


def test_diagnostics_server_unavailable(fake):
    fake._server_state_error = AriaError(code="DOWN", message="down")
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    server_unavailable = [
        w for w in result.data.warnings if w.code == "SERVER_STATE_UNAVAILABLE"
    ]
    assert len(server_unavailable) == 1


def test_diagnostics_library_unavailable(fake):
    fake._library_state_error = AriaError(code="LIB_DOWN", message="library down")
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    lib_unavailable = [
        w for w in result.data.warnings if w.code == "LIBRARY_STATE_UNAVAILABLE"
    ]
    assert len(lib_unavailable) == 1


def test_diagnostics_control_not_configured(fake):
    custom = ReadinessViewState(
        server=ServerViewState(connected=True),
        library=LibraryViewState(available=True),
        control_configured=False,
        all_ready=False,
    )
    fake._readiness_override = custom
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    not_configured = [
        w for w in result.data.warnings if w.code == "CONTROL_NOT_CONFIGURED"
    ]
    assert len(not_configured) == 1


def test_diagnostics_readiness_unavailable(fake):
    fake._readiness_error = AriaError(code="READY_FAIL", message="fail")
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    readiness_unavailable = [
        w for w in result.data.warnings if w.code == "READINESS_UNAVAILABLE"
    ]
    assert len(readiness_unavailable) == 1


def test_diagnostics_multiple_warnings(fake):
    custom_server = ServerViewState(connected=True, latency_ms=500)
    custom_library = LibraryViewState(available=True, last_scan_timestamp=None)
    fake._server_state_override = custom_server
    fake._library_state_override = custom_library
    svc = DiagnosticsService(fake)
    result = svc.collect()
    assert result.is_ok()
    codes = {w.code for w in result.data.warnings}
    assert "LATENCY_HIGH" in codes
    assert "LIBRARY_NEVER_SCANNED" in codes


def test_diagnostics_custom_thresholds(fake):
    custom = ServerViewState(connected=True, latency_ms=150)
    fake._server_state_override = custom
    svc = DiagnosticsService(fake, max_latency_ms=100)
    result = svc.collect()
    latency_warnings = [w for w in result.data.warnings if w.code == "LATENCY_HIGH"]
    assert len(latency_warnings) == 1
    assert "150" in latency_warnings[0].message


def test_diagnostics_custom_staleness_threshold(fake):
    old_ts = time.time() - 5_000  # ~1.4 hours old
    custom = LibraryViewState(available=True, last_scan_timestamp=old_ts)
    fake._library_state_override = custom
    svc = DiagnosticsService(fake, max_library_staleness_seconds=3_600)
    result = svc.collect()
    stale_warnings = [w for w in result.data.warnings if w.code == "LIBRARY_STALE"]
    assert len(stale_warnings) == 1


def test_diagnostics_always_returns_ok(diag_svc):
    result = diag_svc.collect()
    assert result.is_ok()
    result2 = DiagnosticsService(FakeControlClient()).collect()
    assert result2.is_ok()


def test_diagnostics_server_last_error_warning(fake):
    err = AriaError(code="PREV_FAIL", message="previous failure")
    custom = ServerViewState(connected=True, last_error=err)
    fake._server_state_override = custom
    svc = DiagnosticsService(fake)
    result = svc.collect()
    last_error_warnings = [
        w for w in result.data.warnings if w.code == "SERVER_LAST_ERROR"
    ]
    assert len(last_error_warnings) == 1
    assert "PREV_FAIL" in last_error_warnings[0].message


# ── ReadinessService ─────────────────────────────────────────


@pytest.fixture
def readiness_svc(fake) -> ReadinessService:
    return ReadinessService(fake)


def test_readiness_fully_ready(readiness_svc):
    result = readiness_svc.assess()
    assert result.is_ok()
    assert result.data.all_ready is True
    assert result.data.server.connected is True
    assert result.data.library.available is True
    assert result.data.control_configured is True


def test_readiness_server_disconnected(fake):
    fake._server_state_error = AriaError(code="SERVER_UNREACHABLE", message="unreachable")
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_err()


def test_readiness_library_unavailable(fake):
    custom = LibraryViewState(available=False)
    fake._library_state_override = custom
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_ok()
    assert result.data.all_ready is False
    assert result.data.library.available is False


def test_readiness_control_not_configured(fake):
    custom = ReadinessViewState(
        server=ServerViewState(connected=True),
        library=LibraryViewState(available=True),
        control_configured=False,
        all_ready=False,
    )
    fake._readiness_override = custom
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_ok()
    assert result.data.control_configured is False
    assert result.data.all_ready is False


def test_readiness_with_diagnostics_warnings(fake):
    custom = ReadinessViewState(
        server=ServerViewState(connected=True),
        library=LibraryViewState(available=True),
        diagnostics=DiagnosticsViewState(
            warnings=[AriaWarning(code="WARN", message="warning")]
        ),
        control_configured=True,
        all_ready=False,
    )
    fake._readiness_override = custom
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_ok()
    assert result.data.all_ready is False
    assert len(result.data.diagnostics.warnings) == 1


def test_readiness_partial_server_up_library_down(fake):
    custom = LibraryViewState(available=False)
    fake._library_state_override = custom
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_ok()
    assert result.data.server.connected is True
    assert result.data.library.available is False
    assert result.data.all_ready is False


def test_readiness_server_error_propagates(fake):
    fake._server_state_error = AriaError(code="SERVER_DOWN", message="down")
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "SERVER_DOWN"


def test_readiness_library_error_propagates(fake):
    fake._library_state_error = AriaError(code="LIB_DOWN", message="down")
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "LIB_DOWN"


def test_readiness_readiness_error_propagates(fake):
    fake._readiness_error = AriaError(code="READY_FAIL", message="fail")
    svc = ReadinessService(fake)
    result = svc.assess()
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "READY_FAIL"


def test_readiness_all_ready_requires_all_conditions(readiness_svc):
    result = readiness_svc.assess()
    assert result.is_ok()
    assert result.data.all_ready is True
    assert result.data.server.connected is True
    assert result.data.library.available is True
    assert result.data.control_configured is True
    assert result.data.diagnostics.warnings == []


def test_readiness_always_returns_result(readiness_svc):
    result = readiness_svc.assess()
    assert isinstance(result, AriaResult)


def test_readiness_deterministic(readiness_svc):
    r1 = readiness_svc.assess()
    r2 = readiness_svc.assess()
    assert r1 == r2


# ── ResultMappingService edge cases from spec ─────────────────


def test_result_mapping_ok_with_none_data_edge_case():
    result = ResultMappingService.ok(None)
    assert result.is_ok()
    assert result.data is None
    assert result.error is None


def test_result_mapping_err_with_empty_message():
    result = ResultMappingService.err("EMPTY", "")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "EMPTY"
    assert result.error.message == ""


def test_result_mapping_unwrap_or_with_complex_default():
    result = AriaResult(ok=False, error=AriaError(code="E", message="m"))
    default = ServerViewState(connected=True)
    assert ResultMappingService.unwrap_or(result, default) is default
