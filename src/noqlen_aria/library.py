"""Aria Core library browse/search models and services."""

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


@runtime_checkable
class LibraryBrowseCapable(Protocol):
    def browse_library(self, request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]: ...


@runtime_checkable
class LibrarySearchCapable(Protocol):
    def search_library(self, query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]: ...


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


__all__ = [
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
]
