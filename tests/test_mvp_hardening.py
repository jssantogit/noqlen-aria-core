"""Tests for Bloco 6 Aria MVP hardening expectations."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import noqlen_aria
import noqlen_aria.android_boundaries as android_boundaries
import noqlen_aria.anchor_adapter as anchor_adapter
import noqlen_aria.contracts as contracts
import noqlen_aria.services as services
from noqlen_aria import safe_serialize
from noqlen_aria.anchor_adapter import AnchorControlClient
from noqlen_aria.contracts import (
    SAFE_DETAIL_UNAVAILABLE,
    AriaError,
    AriaResult,
    AriaWarning,
    DiagnosticsViewState,
    FakeControlClient,
    LifecycleIntent,
    ReadinessViewState,
    ServerViewState,
    sanitize_text,
)
from noqlen_aria.services import DiagnosticsService, ReadinessService


def _mock_anchor_with_apply_helpers() -> MagicMock:
    mock = MagicMock()
    mock.inspect_fake_server = MagicMock(return_value={"connected": True})
    mock.inspect_navidrome_offline = MagicMock(return_value={"available": True})
    mock.start_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.stop_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.restart_navidrome_dry_run = MagicMock(return_value={"dry_run": "ok"})
    mock.start_navidrome_apply = MagicMock()
    mock.stop_navidrome_apply = MagicMock()
    mock.restart_navidrome_apply = MagicMock()
    mock.render_navidrome_config_apply = MagicMock()
    return mock


def test_top_level_public_exports_are_intentional() -> None:
    expected = {
        "__version__",
        "AnchorControlClient",
        "AlbumSummary",
        "AriaError",
        "AriaResult",
        "AriaWarning",
        "ArtistSummary",
        "ControlClient",
        "DiagnosticsService",
        "DiagnosticsViewState",
        "FavoriteItemSummary",
        "FavoritesViewState",
        "FakeControlClient",
        "FolderSummary",
        "GenreSummary",
        "LibraryActivityRequest",
        "LibraryActivityResult",
        "LibraryActivityService",
        "LibraryActivityType",
        "LibraryBrowseCategory",
        "LibraryBrowseRequest",
        "LibraryBrowseResult",
        "LibraryBrowseService",
        "LibraryFilter",
        "LibraryFilterService",
        "LibraryFilterSet",
        "LibraryHealthBadge",
        "LibraryFavoritesService",
        "LibraryItemSummary",
        "LibraryReadinessBadge",
        "LibrarySortDirection",
        "LibrarySortOption",
        "LibrarySearchQuery",
        "LibrarySearchResult",
        "LibrarySearchService",
        "LibraryViewState",
        "LifecycleIntent",
        "LifecycleIntentPreview",
        "LifecycleIntentService",
        "PermissionState",
        "PlaylistSummary",
        "RecentlyAddedViewState",
        "RecentlyPlayedViewState",
        "ReadinessService",
        "ReadinessViewState",
        "ResultMappingService",
        "ServerViewState",
        "StatusService",
        "StorageAccessState",
        "TrackSummary",
        "safe_serialize",
        "sanitize_text",
    }

    assert set(noqlen_aria.__all__) == expected
    assert "AnchorResultMapper" not in noqlen_aria.__all__
    assert "AndroidBoundarySnapshot" not in noqlen_aria.__all__
    assert all(
        name == "__version__" or not name.startswith("_")
        for name in noqlen_aria.__all__
    )


def test_public_modules_define_intentional_wildcard_exports() -> None:
    assert "Any" not in contracts.__all__
    assert "Generic" not in contracts.__all__
    assert "T" not in contracts.__all__
    assert "ControlClient" in contracts.__all__
    assert "safe_serialize" in contracts.__all__

    assert "TYPE_CHECKING" not in services.__all__
    assert "ResultMappingService" in services.__all__
    assert "StatusService" in services.__all__

    assert anchor_adapter.__all__ == ["AnchorControlClient"]
    assert "AnchorResultMapper" not in anchor_adapter.__all__

    assert "AndroidBoundarySnapshot" in android_boundaries.__all__
    assert "FakePlaybackEngineBridge" in android_boundaries.__all__
    assert "Protocol" not in android_boundaries.__all__


def test_safe_serialize_returns_json_compatible_app_facing_data() -> None:
    result = AriaResult(
        ok=False,
        error=AriaError(
            code="RAW_FAILURE",
            message="Traceback in /home/user/music-library/token.txt",
        ),
    )

    serialized = safe_serialize(result)

    assert serialized == {
        "ok": False,
        "data": None,
        "error": {
            "code": "RAW_FAILURE",
            "message": SAFE_DETAIL_UNAVAILABLE,
        },
    }
    json.dumps(serialized)


def test_safe_serialize_serializes_nested_readiness_enums_and_warnings() -> None:
    readiness = ReadinessViewState(
        server=ServerViewState(
            connected=False,
            last_error=AriaError(code="NO_ANCHOR", message="Anchor unavailable"),
        ),
        diagnostics=DiagnosticsViewState(
            warnings=[AriaWarning(code="WARN", message="Safe warning")]
        ),
    )

    serialized = safe_serialize(readiness)

    assert serialized["server"]["connected"] is False
    assert serialized["server"]["last_error"]["message"] == "Anchor unavailable"
    assert serialized["diagnostics"]["warnings"][0]["message"] == "Safe warning"
    json.dumps(serialized)


def test_sanitized_error_and_warning_hide_raw_details() -> None:
    error = AriaError(code="FAIL", message="password in /Users/me/.secrets")
    warning = AriaWarning(code="WARN", message="provider exception token=abc123")

    assert error.message == SAFE_DETAIL_UNAVAILABLE
    assert warning.message == SAFE_DETAIL_UNAVAILABLE
    assert sanitize_text("safe display message") == "safe display message"


def test_diagnostics_warning_uses_sanitized_last_error_message() -> None:
    fake = FakeControlClient()
    fake._server_state_override = ServerViewState(
        connected=True,
        last_error=AriaError(code="RAW", message="Traceback /home/user/.env"),
    )

    result = DiagnosticsService(fake).collect()

    warning = next(w for w in result.data.warnings if w.code == "SERVER_LAST_ERROR")
    assert SAFE_DETAIL_UNAVAILABLE in warning.message
    assert "/home" not in warning.message
    assert "Traceback" not in warning.message


def test_missing_anchor_dependency_is_safe_for_readiness() -> None:
    adapter = AnchorControlClient(anchor_module=None)
    result = ReadinessService(adapter).assess()

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "ANCHOR_NOT_AVAILABLE"
    assert "ImportError" not in result.error.message
    assert "/" not in result.error.message


def test_anchor_helper_exception_does_not_leak_raw_exception_details() -> None:
    mock = MagicMock()
    mock.inspect_fake_server = MagicMock(
        side_effect=RuntimeError("Traceback /home/user/.env token=abc")
    )
    adapter = AnchorControlClient(anchor_module=mock)

    result = adapter.ping()

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "ANCHOR_CALL_FAILED"
    assert SAFE_DETAIL_UNAVAILABLE in result.error.message
    assert "/home" not in result.error.message
    assert "token" not in result.error.message.lower()


def test_lifecycle_apply_helpers_remain_unavailable() -> None:
    mock = _mock_anchor_with_apply_helpers()
    adapter = AnchorControlClient(anchor_module=mock)

    for intent in LifecycleIntent:
        assert adapter.send_lifecycle_intent(intent).is_ok()

    mock.start_navidrome_apply.assert_not_called()
    mock.stop_navidrome_apply.assert_not_called()
    mock.restart_navidrome_apply.assert_not_called()
    mock.render_navidrome_config_apply.assert_not_called()


def test_no_anchor_cli_or_provider_internals_are_needed() -> None:
    mock = _mock_anchor_with_apply_helpers()
    adapter = AnchorControlClient(anchor_module=mock)

    adapter.get_server_state()
    adapter.get_library_state()
    adapter.get_permission_state()
    adapter.get_storage_access_state()

    called_names = {call[0] for call in mock.method_calls}
    assert "cli" not in called_names
    assert "provider" not in called_names
    assert "providers" not in called_names
