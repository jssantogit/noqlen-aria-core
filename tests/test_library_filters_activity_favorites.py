"""Tests for Bloco 10 library filters, activity, and favorites."""

from __future__ import annotations

from dataclasses import asdict

import inspect

import noqlen_aria.library as library
from noqlen_aria.contracts import AriaError, safe_serialize
from noqlen_aria.library import (
    FavoriteItemSummary,
    FavoritesViewState,
    LibraryActivityRequest,
    LibraryActivityResult,
    LibraryActivityService,
    LibraryActivityType,
    LibraryBrowseCategory,
    LibraryBrowseRequest,
    LibraryBrowseResult,
    LibraryBrowseService,
    LibraryFilter,
    LibraryFilterService,
    LibraryFilterSet,
    LibraryHealthBadge,
    LibraryItemSummary,
    LibraryFavoritesService,
    LibraryReadinessBadge,
    LibrarySortDirection,
    LibrarySortOption,
    RecentlyAddedViewState,
    RecentlyPlayedViewState,
)
from noqlen_aria.media_source import (
    FakeMediaSourceClient,
    MediaId,
    MediaIdKind,
    MediaSourceId,
    SourceAvailabilityState,
    SourceCapability,
)


def _browse_tracks(fake: FakeMediaSourceClient) -> LibraryBrowseResult:
    result = LibraryBrowseService(fake).browse(LibraryBrowseRequest(LibraryBrowseCategory.TRACKS))
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def test_filter_applies_to_app_facing_result_without_changing_source() -> None:
    fake = FakeMediaSourceClient.with_full_library()
    original = _browse_tracks(fake)

    result = LibraryFilterService().apply_filters(
        original,
        LibraryFilterSet((LibraryFilter("display_name", "First"),)),
    )

    assert result.ok
    assert [item.display_name for item in result.data.items] == ["First Difference"]
    assert [item.display_name for item in _browse_tracks(fake).items] == ["First Difference", "Safe Folder Song"]


def test_filter_supports_artists_albums_tracks_playlists_genres_and_folders() -> None:
    fake = FakeMediaSourceClient.with_full_library()
    expected = {
        LibraryBrowseCategory.ARTISTS: "Ada",
        LibraryBrowseCategory.ALBUMS: "Analytical",
        LibraryBrowseCategory.TRACKS: "Safe",
        LibraryBrowseCategory.PLAYLISTS: "Core",
        LibraryBrowseCategory.GENRES: "Instrumental",
        LibraryBrowseCategory.FOLDERS: "Source",
    }

    for category, query in expected.items():
        browse = LibraryBrowseService(fake).browse(LibraryBrowseRequest(category)).data
        filtered = LibraryFilterService().apply_filters(
            browse,
            LibraryFilterSet((LibraryFilter("display_name", query),)),
        )
        assert filtered.ok
        assert len(filtered.data.items) == 1


def test_unsupported_filter_field_returns_safe_error() -> None:
    result = LibraryFilterService().apply_filters(
        _browse_tracks(FakeMediaSourceClient.with_full_library()),
        LibraryFilterSet((LibraryFilter("provider_rating", "5"),)),
    )

    assert result.is_err()
    assert result.error.code == "UNSUPPORTED_LIBRARY_FILTER"


def test_sort_orders_deterministically_by_display_name() -> None:
    result = LibraryFilterService().apply_filters(
        _browse_tracks(FakeMediaSourceClient.with_full_library()),
        sort=LibrarySortOption("display_name", LibrarySortDirection.DESCENDING),
    )

    assert result.ok
    assert [item.display_name for item in result.data.items] == ["Safe Folder Song", "First Difference"]


def test_unsupported_sort_field_returns_safe_error() -> None:
    result = LibraryFilterService().apply_filters(
        _browse_tracks(FakeMediaSourceClient.with_full_library()),
        sort=LibrarySortOption("provider_sort_key"),
    )

    assert result.is_err()
    assert result.error.code == "UNSUPPORTED_LIBRARY_SORT"


def test_recently_added_supported_returns_normalized_items() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_recently_added()).get_recently_added()

    assert result.ok
    assert isinstance(result.data, RecentlyAddedViewState)
    assert result.data.available is True
    assert [item.item_id for item in result.data.items] == ["track-2", "track-1"]
    assert all(isinstance(item, LibraryItemSummary) for item in result.data.items)


def test_recently_played_unsupported_returns_safe_unavailable_result() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_recently_added()).get_recently_played()

    assert result.ok
    assert isinstance(result.data, RecentlyPlayedViewState)
    assert result.data.available is False
    assert result.data.error.code == "CAPABILITY_NOT_SUPPORTED"


def test_recently_played_supported_returns_normalized_items() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_activity_and_favorites()).get_recently_played()

    assert result.ok
    assert result.data.available is True
    assert [item.item_id for item in result.data.items] == ["track-1", "track-2"]


def test_favorites_supported_returns_normalized_favorite_summaries() -> None:
    result = LibraryFavoritesService(FakeMediaSourceClient.with_activity_and_favorites()).get_favorites()

    assert result.ok
    assert isinstance(result.data, FavoritesViewState)
    assert result.data.available is True
    assert result.data.items == (
        FavoriteItemSummary(
            LibraryItemSummary(
                MediaSourceId("fake-source-1"),
                MediaId("track-1"),
                MediaIdKind.TRACK,
                "First Difference",
                "Ada Quartet",
            )
        ),
    )


def test_favorites_unsupported_returns_safe_unavailable_result() -> None:
    result = LibraryFavoritesService(FakeMediaSourceClient.without_favorites()).get_favorites()

    assert result.ok
    assert result.data.available is False
    assert result.data.items == ()
    assert result.data.error.code == "CAPABILITY_NOT_SUPPORTED"


def test_favorites_mutation_is_blocked_and_does_not_change_fake_state() -> None:
    fake = FakeMediaSourceClient.with_activity_and_favorites()
    service = LibraryFavoritesService(fake)
    before = service.get_favorites().data

    mutation = service.request_favorite_mutation(before.items[0].item, favorite=False)
    after = service.get_favorites().data

    assert mutation.is_err()
    assert mutation.error.code == "FAVORITES_MUTATION_UNSUPPORTED"
    assert after == before


def test_readiness_badges_report_ready_source() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_activity_and_favorites()).build_readiness_badges()

    assert result.ok
    assert result.data == (LibraryReadinessBadge("SOURCE_READY", "Source ready", True, "info"),)


def test_degraded_source_returns_warning_badges_without_crashing() -> None:
    fake = FakeMediaSourceClient.degraded_with_warnings()
    fake.supported_capabilities = fake.supported_capabilities | frozenset({SourceCapability.RECENTLY_ADDED})
    result = LibraryActivityService(fake).build_readiness_badges()

    assert result.ok
    assert result.data == (LibraryReadinessBadge("SOURCE_DEGRADED", "Source degraded", False, "warning"),)


def test_health_badges_report_limited_capabilities() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_recently_added()).build_health_badges()

    assert result.ok
    assert result.data == (LibraryHealthBadge("LIMITED_CAPABILITIES", "Some library features unavailable", "warning"),)


def test_unavailable_source_activity_and_favorites_return_safe_errors() -> None:
    activity = LibraryActivityService(FakeMediaSourceClient.unavailable()).get_recently_added()
    favorites = LibraryFavoritesService(FakeMediaSourceClient.unavailable()).get_favorites()

    assert activity.is_err()
    assert activity.error.code == "SOURCE_UNAVAILABLE"
    assert favorites.is_err()
    assert favorites.error.code == "SOURCE_UNAVAILABLE"


def test_empty_activity_and_empty_favorites_are_available_when_supported() -> None:
    fake = FakeMediaSourceClient.with_empty_activity_and_favorites()

    recently_added = LibraryActivityService(fake).get_recently_added()
    favorites = LibraryFavoritesService(fake).get_favorites()

    assert recently_added.ok
    assert recently_added.data.available is True
    assert recently_added.data.items == ()
    assert favorites.ok
    assert favorites.data.available is True
    assert favorites.data.items == ()


def test_activity_request_respects_max_results() -> None:
    result = LibraryActivityService(FakeMediaSourceClient.with_activity_and_favorites()).get_recently_played(max_results=1)

    assert result.ok
    assert [item.item_id for item in result.data.items] == ["track-1"]


def test_library_activity_result_model_is_source_agnostic() -> None:
    request = LibraryActivityRequest(LibraryActivityType.RECENTLY_ADDED, max_results=1)
    result = LibraryActivityResult(request=request)

    assert result.request == request
    assert result.items == ()
    assert result.available is True


def test_models_safe_serialize_to_app_facing_data() -> None:
    result = LibraryFavoritesService(FakeMediaSourceClient.with_activity_and_favorites()).get_favorites().data
    serialized = safe_serialize(result)

    assert serialized["items"][0]["item"]["display_name"] == "First Difference"
    assert serialized["items"][0]["favorite"] is True


def test_ui_consumes_aria_core_models_only_for_favorites() -> None:
    result = LibraryFavoritesService(FakeMediaSourceClient.with_activity_and_favorites()).get_favorites().data

    assert all(item.__class__.__module__ == "noqlen_aria.library" for item in result.items)
    assert all(item.item.__class__.__module__ == "noqlen_aria.library" for item in result.items)


def test_library_module_exports_bloco_10_names_intentionally() -> None:
    for name in {
        "FavoriteItemSummary",
        "FavoritesViewState",
        "LibraryActivityRequest",
        "LibraryActivityResult",
        "LibraryActivityService",
        "LibraryActivityType",
        "LibraryFilter",
        "LibraryFilterService",
        "LibraryFilterSet",
        "LibraryHealthBadge",
        "LibraryFavoritesService",
        "LibraryReadinessBadge",
        "LibrarySortDirection",
        "LibrarySortOption",
        "RecentlyAddedViewState",
        "RecentlyPlayedViewState",
    }:
        assert name in library.__all__


def test_no_provider_internals_exposed_in_bloco_10_models() -> None:
    model = FavoriteItemSummary(
        LibraryItemSummary(MediaSourceId("src"), MediaId("track"), MediaIdKind.TRACK, "Track")
    )

    names = set(asdict(model)) | set(asdict(model.item))
    for key in names:
        lowered = key.lower()
        assert "navidrome" not in lowered
        assert "jellyfin" not in lowered
        assert "emby" not in lowered
        assert "anchor" not in lowered


def test_fake_source_has_no_provider_or_filesystem_dependency_for_bloco_10() -> None:
    members = dict(inspect.getmembers(FakeMediaSourceClient))

    for name in members:
        lowered = name.lower()
        assert "provider_api" not in lowered
        assert "filesystem" not in lowered
        assert "walk" not in lowered


def test_error_injection_for_activity_and_favorites_is_deterministic() -> None:
    fake = FakeMediaSourceClient.with_activity_and_favorites()
    fake._library_activity_error = AriaError("ACTIVITY_FAILED", "activity failed")
    fake._favorites_error = AriaError("FAVORITES_FAILED", "favorites failed")

    for _ in range(3):
        activity = LibraryActivityService(fake).get_recently_added()
        favorites = LibraryFavoritesService(fake).get_favorites()
        assert activity.is_err()
        assert activity.error.code == "ACTIVITY_FAILED"
        assert favorites.is_err()
        assert favorites.error.code == "FAVORITES_FAILED"


def test_activity_and_favorites_do_not_expose_queue_playback_cache_methods() -> None:
    service_names = set(dir(LibraryActivityService)) | set(dir(LibraryFavoritesService))

    for forbidden in ("queue", "playback", "now_playing", "offline", "cache", "smart"):
        assert all(forbidden not in name.lower() for name in service_names)
