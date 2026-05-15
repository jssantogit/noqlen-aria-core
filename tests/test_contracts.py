"""Tests for Aria Core contracts and FakeControlClient."""

import pytest

from noqlen_aria.contracts import (
    ControlClient,
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


# ── AriaError ──────────────────────────────────────────────────


def test_aria_error_construction():
    err = AriaError(code="SERVER_UNREACHABLE", message="Cannot reach server")
    assert err.code == "SERVER_UNREACHABLE"
    assert err.message == "Cannot reach server"


def test_aria_error_immutable():
    err = AriaError(code="E", message="m")
    with pytest.raises(Exception):
        err.code = "X"  # type: ignore[misc]


def test_aria_error_equality():
    a = AriaError(code="E1", message="m1")
    b = AriaError(code="E1", message="m1")
    c = AriaError(code="E2", message="m2")
    assert a == b
    assert a != c


# ── AriaWarning ────────────────────────────────────────────────


def test_aria_warning_construction():
    w = AriaWarning(code="STALE_DATA", message="Library scan is older than 24h")
    assert w.code == "STALE_DATA"
    assert w.message == "Library scan is older than 24h"


def test_aria_warning_equality():
    a = AriaWarning(code="W1", message="m")
    b = AriaWarning(code="W1", message="m")
    assert a == b


# ── AriaResult ─────────────────────────────────────────────────


def test_aria_result_ok_success():
    result = AriaResult(ok=True, data=42)
    assert result.ok is True
    assert result.is_ok() is True
    assert result.is_err() is False
    assert result.data == 42
    assert result.error is None


def test_aria_result_ok_failure():
    err = AriaError(code="FAIL", message="something went wrong")
    result = AriaResult(ok=False, error=err)
    assert result.ok is False
    assert result.is_ok() is False
    assert result.is_err() is True
    assert result.data is None
    assert result.error is err


def test_aria_result_with_none_data():
    result = AriaResult(ok=True, data=None)
    assert result.ok is True
    assert result.data is None
    assert result.error is None


def test_aria_result_immutable():
    result = AriaResult(ok=True, data="hello")
    with pytest.raises(Exception):
        result.ok = False  # type: ignore[misc]


def test_aria_result_generic_string():
    result = AriaResult(ok=True, data="success")
    assert result.data == "success"


def test_aria_result_generic_bool():
    result = AriaResult(ok=True, data=True)
    assert result.data is True


def test_aria_result_generic_custom_type():
    """AriaResult must support custom data types via Generic[T]."""
    state = ServerViewState(connected=True, server_url="http://x:4533")
    result: AriaResult[ServerViewState] = AriaResult(ok=True, data=state)
    assert result.data is state
    assert result.data.connected is True


def test_aria_result_ok_with_error_is_invalid_state():
    """When ok=True, error should be None (caller convention)."""
    result = AriaResult(ok=True, data=42, error=AriaError(code="X", message="?"))
    assert result.ok is True
    assert result.is_ok() is True
    # The spec says ok discriminates; data is present when ok=True.
    assert result.data == 42


def test_aria_result_err_with_data_is_invalid_state():
    """When ok=False, data should be None (caller convention)."""
    err = AriaError(code="E", message="m")
    result = AriaResult(ok=False, data="leftover", error=err)
    assert result.is_err() is True
    assert result.error is err


# ── ServerViewState ────────────────────────────────────────────


def test_server_view_state_defaults():
    s = ServerViewState()
    assert s.connected is False
    assert s.server_url == ""
    assert s.server_version == ""
    assert s.latency_ms is None
    assert s.last_error is None


def test_server_view_state_explicit():
    err = AriaError(code="CONN_REFUSED", message="Connection refused")
    s = ServerViewState(
        connected=True,
        server_url="http://localhost:4533",
        server_version="0.52.5",
        latency_ms=12,
        last_error=err,
    )
    assert s.connected is True
    assert s.server_url == "http://localhost:4533"
    assert s.server_version == "0.52.5"
    assert s.latency_ms == 12
    assert s.last_error is err


def test_server_view_state_immutable():
    s = ServerViewState(connected=True)
    with pytest.raises(Exception):
        s.connected = False  # type: ignore[misc]


# ── LibraryViewState ───────────────────────────────────────────


def test_library_view_state_defaults():
    lib = LibraryViewState()
    assert lib.available is False
    assert lib.artist_count == 0
    assert lib.album_count == 0
    assert lib.track_count == 0
    assert lib.total_duration_seconds == 0
    assert lib.last_scan_timestamp is None


def test_library_view_state_explicit():
    lib = LibraryViewState(
        available=True,
        artist_count=42,
        album_count=100,
        track_count=2000,
        total_duration_seconds=360000,
        last_scan_timestamp=1_700_000_000.5,
    )
    assert lib.available is True
    assert lib.artist_count == 42
    assert lib.album_count == 100
    assert lib.track_count == 2000
    assert lib.total_duration_seconds == 360000
    assert lib.last_scan_timestamp == 1_700_000_000.5


# ── DiagnosticsViewState ───────────────────────────────────────


def test_diagnostics_view_state_defaults():
    d = DiagnosticsViewState()
    assert d.warnings == []


def test_diagnostics_view_state_with_warnings():
    w1 = AriaWarning(code="LATENCY_HIGH", message="Latency exceeds threshold")
    w2 = AriaWarning(code="VERSION_MISMATCH", message="Server version mismatch")
    d = DiagnosticsViewState(warnings=[w1, w2])
    assert len(d.warnings) == 2
    assert d.warnings[0] is w1
    assert d.warnings[1] is w2


def test_diagnostics_view_state_warnings_are_independent():
    """Each DiagnosticsViewState gets its own list."""
    d1 = DiagnosticsViewState(
        warnings=[AriaWarning(code="W", message="m")]
    )
    d2 = DiagnosticsViewState()
    assert len(d1.warnings) == 1
    assert d2.warnings == []


# ── ReadinessViewState ─────────────────────────────────────────


def test_readiness_view_state_defaults():
    r = ReadinessViewState()
    assert isinstance(r.server, ServerViewState)
    assert isinstance(r.library, LibraryViewState)
    assert isinstance(r.diagnostics, DiagnosticsViewState)
    assert r.server.connected is False
    assert r.library.available is False
    assert r.control_configured is False
    assert r.all_ready is False


def test_readiness_view_state_composed():
    srv = ServerViewState(connected=True, server_url="http://x:4533")
    lib = LibraryViewState(available=True)
    diag = DiagnosticsViewState(
        warnings=[AriaWarning(code="OK", message="all green")]
    )
    r = ReadinessViewState(
        server=srv,
        library=lib,
        diagnostics=diag,
        control_configured=True,
        all_ready=True,
    )
    assert r.server is srv
    assert r.library is lib
    assert r.diagnostics is diag
    assert r.control_configured is True
    assert r.all_ready is True


def test_readiness_view_state_partial_readiness():
    """Server connected but library not available, anchor not configured."""
    r = ReadinessViewState(
        server=ServerViewState(connected=True),
        library=LibraryViewState(available=False),
        control_configured=False,
        all_ready=False,
    )
    assert r.server.connected is True
    assert r.library.available is False
    assert r.control_configured is False
    assert r.all_ready is False


# ── LifecycleIntent ────────────────────────────────────────────


def test_lifecycle_intent_members():
    intents = set(LifecycleIntent)
    assert LifecycleIntent.INITIALIZE in intents
    assert LifecycleIntent.SHUTDOWN in intents
    assert LifecycleIntent.RESET in intents
    assert len(intents) == 3


def test_lifecycle_intent_values_are_distinct():
    vals = {m.value for m in LifecycleIntent}
    assert len(vals) == 3


def test_lifecycle_intent_unknown_value_raises():
    """Enum constructor rejects unknown values."""
    with pytest.raises(ValueError):
        LifecycleIntent("BOGUS")


def test_lifecycle_intent_string_roundtrip():
    assert LifecycleIntent.INITIALIZE.name == "INITIALIZE"
    assert LifecycleIntent["SHUTDOWN"] is LifecycleIntent.SHUTDOWN


def test_lifecycle_intent_is_enum():
    assert issubclass(LifecycleIntent, __import__("enum").Enum)


# ── PermissionState ────────────────────────────────────────────


def test_permission_state_members():
    members = set(PermissionState)
    assert PermissionState.UNKNOWN in members
    assert PermissionState.GRANTED in members
    assert PermissionState.DENIED in members
    assert PermissionState.NOT_APPLICABLE in members
    assert len(members) == 4


def test_permission_state_values_are_distinct():
    vals = {m.value for m in PermissionState}
    assert len(vals) == 4


# ── StorageAccessState ─────────────────────────────────────────


def test_storage_access_state_members():
    members = set(StorageAccessState)
    assert StorageAccessState.UNKNOWN in members
    assert StorageAccessState.AVAILABLE in members
    assert StorageAccessState.UNAVAILABLE in members
    assert len(members) == 3


def test_storage_access_state_values_are_distinct():
    vals = {m.value for m in StorageAccessState}
    assert len(vals) == 3


# ── ControlClient protocol ─────────────────────────────────────


def test_fake_control_client_is_control_client():
    """FakeControlClient structurally conforms to ControlClient protocol."""
    fake = FakeControlClient()
    assert isinstance(fake, ControlClient)


def test_control_client_protocol_methods_exist():
    """ControlClient protocol defines all expected methods."""
    expected = {
        "ping",
        "get_server_state",
        "get_library_state",
        "get_readiness",
        "send_lifecycle_intent",
        "get_permission_state",
        "get_storage_access_state",
    }
    actual = {
        name
        for name in dir(ControlClient)
        if not name.startswith("_") and callable(getattr(ControlClient, name, None))
    }
    for method in expected:
        assert method in actual, f"Missing method: {method}"


# ── FakeControlClient ──────────────────────────────────────────


@pytest.fixture
def fake() -> FakeControlClient:
    return FakeControlClient()


def test_fake_ping(fake):
    result = fake.ping()
    assert result.ok is True
    assert result.is_ok()
    assert result.data is True
    assert result.error is None


def test_fake_get_server_state(fake):
    result = fake.get_server_state()
    assert result.ok is True
    state = result.data
    assert isinstance(state, ServerViewState)
    assert state.connected is True
    assert state.server_url == "http://fake:4533"
    assert state.server_version == "0.52.5-fake"
    assert state.latency_ms == 1
    assert state.last_error is None


def test_fake_get_library_state(fake):
    result = fake.get_library_state()
    assert result.ok is True
    state = result.data
    assert isinstance(state, LibraryViewState)
    assert state.available is True
    assert state.artist_count == 5
    assert state.album_count == 10
    assert state.track_count == 120
    assert state.total_duration_seconds == 36000
    assert state.last_scan_timestamp == 1_700_000_000.0


def test_fake_get_readiness(fake):
    result = fake.get_readiness()
    assert result.ok is True
    readiness = result.data
    assert isinstance(readiness, ReadinessViewState)
    assert readiness.control_configured is True
    assert readiness.all_ready is True
    assert readiness.server.connected is True
    assert readiness.library.available is True
    assert readiness.diagnostics.warnings == []


def test_fake_send_lifecycle_intent(fake):
    for intent in LifecycleIntent:
        result = fake.send_lifecycle_intent(intent)
        assert result.ok is True
        assert result.data is True
        assert result.error is None


def test_fake_get_permission_state(fake):
    result = fake.get_permission_state()
    assert result.ok is True
    assert result.data is PermissionState.GRANTED


def test_fake_get_storage_access_state(fake):
    result = fake.get_storage_access_state()
    assert result.ok is True
    assert result.data is StorageAccessState.AVAILABLE


def test_fake_repeated_calls_deterministic(fake):
    """Repeated calls with identical inputs must return identical results."""
    for _ in range(5):
        r1 = fake.ping()
        r2 = fake.ping()
        assert r1 == r2
        assert r1.data == r2.data

    for _ in range(5):
        r1 = fake.get_permission_state()
        r2 = fake.get_permission_state()
        assert r1 == r2
        assert r1.data == r2.data

    for _ in range(5):
        r1 = fake.get_storage_access_state()
        r2 = fake.get_storage_access_state()
        assert r1 == r2
        assert r1.data == r2.data


def test_fake_calls_before_any_setup(fake):
    """FakeControlClient must handle calls before any setup/configuration."""
    assert fake.ping().ok is True
    assert fake.get_server_state().ok is True
    assert fake.get_library_state().ok is True
    assert fake.get_readiness().ok is True
    assert fake.get_permission_state().ok is True
    assert fake.get_storage_access_state().ok is True


def test_fake_control_client_mutable():
    """FakeControlClient is not frozen; tests may mutate it."""
    fake = FakeControlClient()
    fake.custom_flag = True  # type: ignore[attr-defined]
    assert fake.custom_flag is True


def test_fake_readiness_composes_fake_server_and_library(fake):
    """Readiness snapshot is internally consistent with server/library states."""
    readiness = fake.get_readiness().data
    server = fake.get_server_state().data
    library = fake.get_library_state().data

    assert readiness.server == server
    assert readiness.library == library


def test_fake_send_lifecycle_intent_all_values(fake):
    """send_lifecycle_intent must accept every LifecycleIntent value."""
    for intent in LifecycleIntent:
        result = fake.send_lifecycle_intent(intent)
        assert isinstance(result, AriaResult)
        assert result.ok is True
