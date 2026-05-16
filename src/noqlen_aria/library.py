"""Aria Core library models and services."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, runtime_checkable

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning
from noqlen_aria.media_source import MediaId, MediaIdKind, MediaSourceClient, MediaSourceId


class LibraryBrowseCategory(Enum):
    ARTISTS = auto()
    ALBUMS = auto()
    TRACKS = auto()
    PLAYLISTS = auto()
    GENRES = auto()
    FOLDERS = auto()


@dataclass(frozen=True)
class LibraryBrowseRequest:
    category: LibraryBrowseCategory
    parent_id: MediaId | None = None


@dataclass(frozen=True)
class LibraryItemSummary:
    source_id: MediaSourceId
    item_id: MediaId
    item_kind: MediaIdKind
    display_name: str
    subtitle: str = ""


@dataclass(frozen=True)
class ArtistSummary:
    source_id: MediaSourceId
    artist_id: MediaId
    display_name: str
    album_count: int = 0
    track_count: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.artist_id,
            item_kind=MediaIdKind.ARTIST,
            display_name=self.display_name,
        )


@dataclass(frozen=True)
class AlbumSummary:
    source_id: MediaSourceId
    album_id: MediaId
    display_name: str
    artist_name: str = ""
    track_count: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.album_id,
            item_kind=MediaIdKind.ALBUM,
            display_name=self.display_name,
            subtitle=self.artist_name,
        )


@dataclass(frozen=True)
class TrackSummary:
    source_id: MediaSourceId
    track_id: MediaId
    display_name: str
    artist_name: str = ""
    album_name: str = ""
    duration_seconds: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        subtitle = self.artist_name or self.album_name
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.track_id,
            item_kind=MediaIdKind.TRACK,
            display_name=self.display_name,
            subtitle=subtitle,
        )


@dataclass(frozen=True)
class PlaylistSummary:
    source_id: MediaSourceId
    playlist_id: MediaId
    display_name: str
    track_count: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.playlist_id,
            item_kind=MediaIdKind.PLAYLIST,
            display_name=self.display_name,
        )


@dataclass(frozen=True)
class GenreSummary:
    source_id: MediaSourceId
    genre_id: MediaId
    display_name: str
    track_count: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.genre_id,
            item_kind=MediaIdKind.GENRE,
            display_name=self.display_name,
        )


@dataclass(frozen=True)
class FolderSummary:
    source_id: MediaSourceId
    folder_id: MediaId
    display_name: str
    child_count: int = 0

    def as_library_item(self) -> LibraryItemSummary:
        return LibraryItemSummary(
            source_id=self.source_id,
            item_id=self.folder_id,
            item_kind=MediaIdKind.FOLDER,
            display_name=self.display_name,
        )


LibraryBrowseItem = (
    ArtistSummary
    | AlbumSummary
    | TrackSummary
    | PlaylistSummary
    | GenreSummary
    | FolderSummary
)


@dataclass(frozen=True)
class LibraryBrowseResult:
    category: LibraryBrowseCategory
    items: tuple[LibraryBrowseItem, ...] = field(default_factory=tuple)
    available: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


@dataclass(frozen=True)
class LibrarySearchQuery:
    text: str
    categories: frozenset[LibraryBrowseCategory] = field(default_factory=frozenset)
    max_results: int = 50

    @property
    def normalized_text(self) -> str:
        return " ".join(self.text.split()).casefold()


@dataclass(frozen=True)
class LibrarySearchResult:
    query: LibrarySearchQuery
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    valid_query: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


class LibrarySortDirection(Enum):
    ASCENDING = auto()
    DESCENDING = auto()


@dataclass(frozen=True)
class LibraryFilter:
    field: str
    value: str

    @property
    def normalized_value(self) -> str:
        return " ".join(self.value.split()).casefold()


@dataclass(frozen=True)
class LibraryFilterSet:
    filters: tuple[LibraryFilter, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LibrarySortOption:
    field: str = "display_name"
    direction: LibrarySortDirection = LibrarySortDirection.ASCENDING


class LibraryActivityType(Enum):
    RECENTLY_ADDED = auto()
    RECENTLY_PLAYED = auto()


@dataclass(frozen=True)
class LibraryActivityRequest:
    activity_type: LibraryActivityType
    max_results: int = 50


@dataclass(frozen=True)
class LibraryActivityResult:
    request: LibraryActivityRequest
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


@dataclass(frozen=True)
class RecentlyAddedViewState:
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


@dataclass(frozen=True)
class RecentlyPlayedViewState:
    items: tuple[LibraryItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


@dataclass(frozen=True)
class FavoriteItemSummary:
    item: LibraryItemSummary
    favorite: bool = True


@dataclass(frozen=True)
class FavoritesViewState:
    items: tuple[FavoriteItemSummary, ...] = field(default_factory=tuple)
    available: bool = True
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    error: AriaError | None = None


@dataclass(frozen=True)
class LibraryHealthBadge:
    code: str
    label: str
    severity: str = "info"


@dataclass(frozen=True)
class LibraryReadinessBadge:
    code: str
    label: str
    ready: bool = True
    severity: str = "info"


@runtime_checkable
class LibraryBrowseCapable(Protocol):
    def browse_library(self, request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]: ...


@runtime_checkable
class LibrarySearchCapable(Protocol):
    def search_library(self, query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]: ...


@runtime_checkable
class LibraryActivityCapable(Protocol):
    def get_library_activity(self, request: LibraryActivityRequest) -> AriaResult[LibraryActivityResult]: ...


@runtime_checkable
class LibraryFavoritesCapable(Protocol):
    def get_favorites(self, max_results: int = 50) -> AriaResult[FavoritesViewState]: ...


class LibraryBrowseService:
    def __init__(self, source: MediaSourceClient) -> None:
        self._source = source

    def browse(self, request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]:
        return self._source.browse_library(request)


class LibrarySearchService:
    def __init__(self, source: MediaSourceClient) -> None:
        self._source = source

    def search(self, query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]:
        if not query.normalized_text or query.max_results < 1:
            return AriaResult(
                ok=True,
                data=LibrarySearchResult(
                    query=query,
                    valid_query=False,
                    error=AriaError(
                        code="INVALID_SEARCH_QUERY",
                        message="Search query must contain text and request at least one result",
                    ),
                ),
            )
        return self._source.search_library(query)


class LibraryFilterService:
    _SUPPORTED_FIELDS = frozenset({"display_name", "subtitle", "item_kind", "artist_name", "album_name"})

    def apply_filters(
        self,
        result: LibraryBrowseResult,
        filters: LibraryFilterSet = LibraryFilterSet(),
        sort: LibrarySortOption | None = None,
    ) -> AriaResult[LibraryBrowseResult]:
        unsupported_filter = next((item for item in filters.filters if item.field not in self._SUPPORTED_FIELDS), None)
        if unsupported_filter is not None:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="UNSUPPORTED_LIBRARY_FILTER",
                    message=f"Library filter field {unsupported_filter.field} is not supported",
                ),
            )
        if sort is not None and sort.field not in self._SUPPORTED_FIELDS:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="UNSUPPORTED_LIBRARY_SORT",
                    message=f"Library sort field {sort.field} is not supported",
                ),
            )

        items = tuple(item for item in result.items if self._matches_all(item, filters))
        if sort is not None:
            reverse = sort.direction == LibrarySortDirection.DESCENDING
            items = tuple(
                item
                for _, item in sorted(
                    enumerate(items),
                    key=lambda indexed: (self._field_value(indexed[1], sort.field), indexed[0]),
                    reverse=reverse,
                )
            )

        return AriaResult(
            ok=True,
            data=LibraryBrowseResult(
                category=result.category,
                items=items,
                available=result.available,
                warnings=result.warnings,
                error=result.error,
            ),
        )

    def _matches_all(self, item: LibraryBrowseItem, filters: LibraryFilterSet) -> bool:
        for library_filter in filters.filters:
            if library_filter.normalized_value not in self._field_value(item, library_filter.field):
                return False
        return True

    def _field_value(self, item: LibraryBrowseItem, field_name: str) -> str:
        library_item = item.as_library_item()
        if field_name == "display_name":
            return library_item.display_name.casefold()
        if field_name == "subtitle":
            return library_item.subtitle.casefold()
        if field_name == "item_kind":
            return library_item.item_kind.name.casefold()
        if field_name == "artist_name":
            return str(getattr(item, "artist_name", "")).casefold()
        if field_name == "album_name":
            return str(getattr(item, "album_name", "")).casefold()
        return ""


class LibraryActivityService:
    def __init__(self, source: MediaSourceClient) -> None:
        self._source = source

    def get_recently_added(self, max_results: int = 50) -> AriaResult[RecentlyAddedViewState]:
        result = self._source.get_library_activity(
            LibraryActivityRequest(LibraryActivityType.RECENTLY_ADDED, max_results=max_results)
        )
        if result.is_err():
            return AriaResult(ok=False, error=result.error)
        assert result.data is not None
        return AriaResult(
            ok=True,
            data=RecentlyAddedViewState(
                items=result.data.items,
                available=result.data.available,
                warnings=result.data.warnings,
                error=result.data.error,
            ),
        )

    def get_recently_played(self, max_results: int = 50) -> AriaResult[RecentlyPlayedViewState]:
        result = self._source.get_library_activity(
            LibraryActivityRequest(LibraryActivityType.RECENTLY_PLAYED, max_results=max_results)
        )
        if result.is_err():
            return AriaResult(ok=False, error=result.error)
        assert result.data is not None
        return AriaResult(
            ok=True,
            data=RecentlyPlayedViewState(
                items=result.data.items,
                available=result.data.available,
                warnings=result.data.warnings,
                error=result.data.error,
            ),
        )

    def build_readiness_badges(self) -> AriaResult[tuple[LibraryReadinessBadge, ...]]:
        info_result = self._source.get_source_info()
        if info_result.is_err():
            return AriaResult(ok=False, error=info_result.error)
        assert info_result.data is not None
        if info_result.data.availability.name == "UNAVAILABLE":
            return AriaResult(
                ok=True,
                data=(LibraryReadinessBadge("SOURCE_UNAVAILABLE", "Source unavailable", False, "error"),),
            )
        if info_result.data.availability.name == "DEGRADED":
            return AriaResult(
                ok=True,
                data=(LibraryReadinessBadge("SOURCE_DEGRADED", "Source degraded", False, "warning"),),
            )
        return AriaResult(
            ok=True,
            data=(LibraryReadinessBadge("SOURCE_READY", "Source ready", True, "info"),),
        )

    def build_health_badges(self) -> AriaResult[tuple[LibraryHealthBadge, ...]]:
        capabilities = self._source.get_capability_summary()
        if capabilities.is_err():
            return AriaResult(
                ok=True,
                data=(LibraryHealthBadge("CAPABILITY_CHECK_FAILED", "Capability check unavailable", "error"),),
            )
        assert capabilities.data is not None
        if capabilities.data.unavailable:
            return AriaResult(
                ok=True,
                data=(LibraryHealthBadge("LIMITED_CAPABILITIES", "Some library features unavailable", "warning"),),
            )
        return AriaResult(ok=True, data=(LibraryHealthBadge("LIBRARY_HEALTHY", "Library healthy", "info"),))


class LibraryFavoritesService:
    def __init__(self, source: MediaSourceClient) -> None:
        self._source = source

    def get_favorites(self, max_results: int = 50) -> AriaResult[FavoritesViewState]:
        return self._source.get_favorites(max_results=max_results)

    def request_favorite_mutation(self, item: LibraryItemSummary, favorite: bool) -> AriaResult[bool]:
        _ = (item, favorite)
        return AriaResult(
            ok=False,
            error=AriaError(
                code="FAVORITES_MUTATION_UNSUPPORTED",
                message="Favorites mutation is a future intent and is not performed by Aria Core",
            ),
        )


__all__ = [
    "AlbumSummary",
    "ArtistSummary",
    "FolderSummary",
    "FavoriteItemSummary",
    "FavoritesViewState",
    "GenreSummary",
    "LibraryActivityCapable",
    "LibraryActivityRequest",
    "LibraryActivityResult",
    "LibraryActivityService",
    "LibraryActivityType",
    "LibraryBrowseCapable",
    "LibraryBrowseCategory",
    "LibraryBrowseItem",
    "LibraryBrowseRequest",
    "LibraryBrowseResult",
    "LibraryBrowseService",
    "LibraryFilter",
    "LibraryFilterService",
    "LibraryFilterSet",
    "LibraryHealthBadge",
    "LibraryItemSummary",
    "LibraryFavoritesCapable",
    "LibraryFavoritesService",
    "LibraryReadinessBadge",
    "LibrarySortDirection",
    "LibrarySortOption",
    "LibrarySearchCapable",
    "LibrarySearchQuery",
    "LibrarySearchResult",
    "LibrarySearchService",
    "PlaylistSummary",
    "RecentlyAddedViewState",
    "RecentlyPlayedViewState",
    "TrackSummary",
]
