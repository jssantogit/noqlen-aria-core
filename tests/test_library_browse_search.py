"""Tests for Bloco 9 library browse/search foundation."""

from __future__ import annotations

from dataclasses import asdict

import noqlen_aria.library as library
from noqlen_aria.contracts import AriaError, safe_serialize
from noqlen_aria.library import (
    AlbumSummary,
    ArtistSummary,
    FolderSummary,
    GenreSummary,
    LibraryBrowseCategory,
    LibraryBrowseRequest,
    LibraryBrowseResult,
    LibraryBrowseService,
    LibraryItemSummary,
    LibrarySearchQuery,
    LibrarySearchResult,
    LibrarySearchService,
    PlaylistSummary,
    TrackSummary,
)
from noqlen_aria.media_source import (
    FakeMediaSourceClient,
    MediaId,
    MediaIdKind,
    MediaSourceId,
    SourceAvailabilityState,
    SourceCapability,
)


def _browse(fake: FakeMediaSourceClient, category: LibraryBrowseCategory) -> LibraryBrowseResult:
    result = LibraryBrowseService(fake).browse(LibraryBrowseRequest(category))
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def _search(fake: FakeMediaSourceClient, text: str) -> LibrarySearchResult:
    result = LibrarySearchService(fake).search(LibrarySearchQuery(text))
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def test_browse_category_values_are_bloco_9_only() -> None:
    assert {category.name for category in LibraryBrowseCategory} == {
        "ARTISTS",
        "ALBUMS",
        "TRACKS",
        "PLAYLISTS",
        "GENRES",
        "FOLDERS",
    }


def test_artist_summary_converts_to_source_agnostic_item() -> None:
    summary = ArtistSummary(MediaSourceId("src"), MediaId("artist"), "Artist", album_count=1)
    item = summary.as_library_item()

    assert item == LibraryItemSummary(
        source_id=MediaSourceId("src"),
        item_id=MediaId("artist"),
        item_kind=MediaIdKind.ARTIST,
        display_name="Artist",
    )


def test_album_track_playlist_genre_folder_summaries_convert_to_items() -> None:
    source_id = MediaSourceId("src")
    summaries = (
        AlbumSummary(source_id, MediaId("album"), "Album", artist_name="Artist"),
        TrackSummary(source_id, MediaId("track"), "Track", artist_name="Artist"),
        PlaylistSummary(source_id, MediaId("playlist"), "Playlist"),
        GenreSummary(source_id, MediaId("genre"), "Genre"),
        FolderSummary(source_id, MediaId("folder"), "Folder"),
    )

    items = tuple(summary.as_library_item() for summary in summaries)

    assert [item.item_kind for item in items] == [
        MediaIdKind.ALBUM,
        MediaIdKind.TRACK,
        MediaIdKind.PLAYLIST,
        MediaIdKind.GENRE,
        MediaIdKind.FOLDER,
    ]


def test_browse_artists_returns_normalized_artist_summaries() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.ARTISTS)

    assert result.available is True
    assert result.error is None
    assert result.items == (
        ArtistSummary(
            MediaSourceId("fake-source-1"),
            MediaId("artist-1"),
            "Ada Quartet",
            album_count=1,
            track_count=2,
        ),
    )


def test_browse_albums_returns_source_agnostic_app_facing_items() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.ALBUMS)

    assert isinstance(result.items[0], AlbumSummary)
    assert result.items[0].as_library_item().item_kind == MediaIdKind.ALBUM
    assert result.items[0].display_name == "Analytical Engines"


def test_browse_tracks_returns_source_agnostic_app_facing_items() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.TRACKS)

    assert [track.track_id for track in result.items] == ["track-1", "track-2"]
    assert all(track.as_library_item().source_id == "fake-source-1" for track in result.items)


def test_browse_playlists_returns_playlist_summaries() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.PLAYLISTS)

    assert result.items == (
        PlaylistSummary(MediaSourceId("fake-source-1"), MediaId("playlist-1"), "Core Favorites", track_count=2),
    )


def test_browse_genres_returns_genre_summaries() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.GENRES)

    assert result.items == (
        GenreSummary(MediaSourceId("fake-source-1"), MediaId("genre-1"), "Instrumental", track_count=2),
    )


def test_browse_folders_treats_entries_as_source_metadata_only() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.FOLDERS)

    folder = result.items[0]
    assert isinstance(folder, FolderSummary)
    assert folder.folder_id == "folder-1"
    assert folder.display_name == "Source Folder"
    assert "/" not in folder.folder_id
    assert "\\" not in folder.folder_id
    assert folder.as_library_item().item_kind == MediaIdKind.FOLDER


def test_unsupported_playlists_return_safe_unavailable_result() -> None:
    result = _browse(FakeMediaSourceClient.without_playlists(), LibraryBrowseCategory.PLAYLISTS)

    assert result.available is False
    assert result.items == ()
    assert result.error is not None
    assert result.error.code == "CAPABILITY_NOT_SUPPORTED"


def test_unsupported_folders_return_safe_unavailable_result() -> None:
    result = _browse(FakeMediaSourceClient.without_folders(), LibraryBrowseCategory.FOLDERS)

    assert result.available is False
    assert result.error is not None
    assert result.error.code == "CAPABILITY_NOT_SUPPORTED"


def test_empty_library_browse_returns_empty_lists() -> None:
    fake = FakeMediaSourceClient.empty_library()

    for category in LibraryBrowseCategory:
        result = _browse(fake, category)
        assert result.available is True
        assert result.items == ()


def test_valid_search_query_returns_matching_results() -> None:
    result = _search(FakeMediaSourceClient.with_full_library(), "Ada")

    assert result.valid_query is True
    assert {item.item_kind for item in result.items} >= {MediaIdKind.ARTIST, MediaIdKind.ALBUM, MediaIdKind.TRACK}
    assert all(isinstance(item, LibraryItemSummary) for item in result.items)


def test_search_query_normalizes_whitespace_and_case() -> None:
    result = _search(FakeMediaSourceClient.with_full_library(), "  aDa   quartet ")

    assert result.valid_query is True
    assert len(result.items) >= 1


def test_empty_search_query_returns_safe_validation_result() -> None:
    result = LibrarySearchService(FakeMediaSourceClient.with_full_library()).search(LibrarySearchQuery("   "))

    assert result.ok
    assert result.data is not None
    assert result.data.valid_query is False
    assert result.data.items == ()
    assert result.data.error is not None
    assert result.data.error.code == "INVALID_SEARCH_QUERY"


def test_invalid_search_max_results_returns_safe_validation_result() -> None:
    result = LibrarySearchService(FakeMediaSourceClient.with_full_library()).search(
        LibrarySearchQuery("Ada", max_results=0)
    )

    assert result.ok
    assert result.data.valid_query is False
    assert result.data.error.code == "INVALID_SEARCH_QUERY"


def test_no_match_search_returns_valid_empty_result() -> None:
    result = _search(FakeMediaSourceClient.with_full_library(), "not-present")

    assert result.valid_query is True
    assert result.items == ()
    assert result.error is None


def test_search_respects_max_results_without_sorting_or_filters() -> None:
    result = LibrarySearchService(FakeMediaSourceClient.with_full_library()).search(
        LibrarySearchQuery("Ada", max_results=1)
    )

    assert result.ok
    assert len(result.data.items) == 1


def test_search_can_limit_categories_without_filter_feature_surface() -> None:
    result = LibrarySearchService(FakeMediaSourceClient.with_full_library()).search(
        LibrarySearchQuery("Ada", categories=frozenset({LibraryBrowseCategory.ARTISTS}))
    )

    assert result.ok
    assert {item.item_kind for item in result.data.items} == {MediaIdKind.ARTIST}


def test_search_unsupported_capability_returns_safe_result() -> None:
    fake = FakeMediaSourceClient.with_full_library()
    fake.supported_capabilities = frozenset(
        cap for cap in fake.supported_capabilities if cap != SourceCapability.SEARCH
    )

    result = LibrarySearchService(fake).search(LibrarySearchQuery("Ada"))

    assert result.ok
    assert result.data.error is not None
    assert result.data.error.code == "CAPABILITY_NOT_SUPPORTED"
    assert result.data.items == ()


def test_degraded_source_preserves_browse_warnings() -> None:
    result = _browse(FakeMediaSourceClient.degraded_with_warnings(), LibraryBrowseCategory.ARTISTS)

    assert result.available is True
    assert result.warnings
    assert result.warnings[0].code == "SOURCE_DEGRADED"


def test_degraded_source_preserves_search_warnings() -> None:
    result = _search(FakeMediaSourceClient.degraded_with_warnings(), "Ada")

    assert result.valid_query is True
    assert result.warnings
    assert result.warnings[0].code == "SOURCE_DEGRADED"


def test_unavailable_source_browse_returns_safe_error() -> None:
    result = LibraryBrowseService(FakeMediaSourceClient.unavailable()).browse(
        LibraryBrowseRequest(LibraryBrowseCategory.ARTISTS)
    )

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "SOURCE_UNAVAILABLE"


def test_unavailable_source_search_returns_safe_error() -> None:
    result = LibrarySearchService(FakeMediaSourceClient.unavailable()).search(LibrarySearchQuery("Ada"))

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "SOURCE_UNAVAILABLE"


def test_fake_browse_error_injection_is_deterministic() -> None:
    fake = FakeMediaSourceClient.with_full_library()
    fake._browse_library_error = AriaError("BROWSE_FAILED", "browse failed")

    for _ in range(3):
        result = LibraryBrowseService(fake).browse(LibraryBrowseRequest(LibraryBrowseCategory.ARTISTS))
        assert result.is_err()
        assert result.error.code == "BROWSE_FAILED"


def test_fake_search_error_injection_is_deterministic() -> None:
    fake = FakeMediaSourceClient.with_full_library()
    fake._search_library_error = AriaError("SEARCH_FAILED", "search failed")

    for _ in range(3):
        result = LibrarySearchService(fake).search(LibrarySearchQuery("Ada"))
        assert result.is_err()
        assert result.error.code == "SEARCH_FAILED"


def test_ui_consumes_aria_core_models_only() -> None:
    result = _search(FakeMediaSourceClient.with_full_library(), "Ada")

    assert isinstance(result, LibrarySearchResult)
    assert all(isinstance(item, LibraryItemSummary) for item in result.items)
    assert all(item.__class__.__module__ == "noqlen_aria.library" for item in result.items)


def test_models_safe_serialize_to_app_facing_data() -> None:
    result = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.ARTISTS)
    serialized = safe_serialize(result)

    assert serialized["category"] == "ARTISTS"
    assert serialized["items"][0]["display_name"] == "Ada Quartet"
    assert serialized["available"] is True


def test_library_module_exports_are_intentional() -> None:
    assert set(library.__all__) == {
        "AlbumSummary",
        "ArtistSummary",
        "FolderSummary",
        "GenreSummary",
        "LibraryBrowseCapable",
        "LibraryBrowseCategory",
        "LibraryBrowseItem",
        "LibraryBrowseRequest",
        "LibraryBrowseResult",
        "LibraryBrowseService",
        "LibraryItemSummary",
        "LibrarySearchCapable",
        "LibrarySearchQuery",
        "LibrarySearchResult",
        "LibrarySearchService",
        "PlaylistSummary",
        "TrackSummary",
    }


def test_no_provider_internals_exposed_in_library_models() -> None:
    model = LibraryItemSummary(
        MediaSourceId("src"),
        MediaId("item"),
        MediaIdKind.TRACK,
        "Track",
    )

    for key in asdict(model):
        lowered = key.lower()
        assert "navidrome" not in lowered
        assert "jellyfin" not in lowered
        assert "emby" not in lowered
        assert "anchor" not in lowered


def test_folder_summary_has_no_path_field() -> None:
    folder = FolderSummary(MediaSourceId("src"), MediaId("folder"), "Folder")

    assert set(asdict(folder)) == {"source_id", "folder_id", "display_name", "child_count"}
    assert not hasattr(folder, "path")
    assert not hasattr(folder, "local_path")


def test_services_do_not_expose_filter_sort_favorite_or_activity_methods() -> None:
    service_names = set(dir(LibraryBrowseService)) | set(dir(LibrarySearchService))

    for forbidden in ("filter", "sort", "favorite", "recent", "activity"):
        assert all(forbidden not in name.lower() for name in service_names)


def test_services_do_not_expose_queue_playback_cache_methods() -> None:
    service_names = set(dir(LibraryBrowseService)) | set(dir(LibrarySearchService))

    for forbidden in ("queue", "playback", "now_playing", "offline", "cache"):
        assert all(forbidden not in name.lower() for name in service_names)


def test_fake_scenarios_are_deterministic() -> None:
    first = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.TRACKS)
    second = _browse(FakeMediaSourceClient.with_full_library(), LibraryBrowseCategory.TRACKS)

    assert first == second


def test_empty_library_search_returns_valid_empty_result() -> None:
    result = _search(FakeMediaSourceClient.empty_library(), "Ada")

    assert result.valid_query is True
    assert result.items == ()


def test_source_availability_degraded_does_not_block_safe_output() -> None:
    fake = FakeMediaSourceClient.degraded_with_warnings()

    assert fake.availability == SourceAvailabilityState.DEGRADED
    assert _browse(fake, LibraryBrowseCategory.TRACKS).items
