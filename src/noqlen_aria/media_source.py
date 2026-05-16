"""Aria Core media source foundation — UI-independent contracts, fakes, and capability models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType, Protocol, runtime_checkable

from noqlen_aria.contracts import AriaError, AriaResult

if TYPE_CHECKING:
    from noqlen_aria.library import (
        FavoritesViewState,
        LibraryActivityRequest,
        LibraryActivityResult,
        LibraryBrowseRequest,
        LibraryBrowseResult,
        LibrarySearchQuery,
        LibrarySearchResult,
    )

# ── Media source identity ────────────────────────────────────

MediaSourceId = NewType("MediaSourceId", str)


class MediaSourceType(Enum):
    REMOTE_SERVER = auto()
    LOCAL_LIBRARY = auto()
    CLOUD_STORAGE = auto()


class SourceAvailabilityState(Enum):
    AVAILABLE = auto()
    DEGRADED = auto()
    UNAVAILABLE = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class MediaSourceInfo:
    source_id: MediaSourceId
    display_name: str
    source_type: MediaSourceType
    availability: SourceAvailabilityState = SourceAvailabilityState.UNKNOWN


# ── Abstract media IDs ───────────────────────────────────────

MediaId = NewType("MediaId", str)


class MediaIdKind(Enum):
    ARTIST = auto()
    ALBUM = auto()
    TRACK = auto()
    PLAYLIST = auto()
    GENRE = auto()
    FOLDER = auto()
    STREAM = auto()


# ── Source capabilities ──────────────────────────────────────

class SourceCapability(Enum):
    ARTISTS = auto()
    ALBUMS = auto()
    TRACKS = auto()
    PLAYLISTS = auto()
    GENRES = auto()
    FOLDERS = auto()
    SEARCH = auto()
    STREAM = auto()
    RATINGS = auto()
    SCROBBLING = auto()
    LYRICS = auto()
    RECENTLY_ADDED = auto()
    RECENTLY_PLAYED = auto()
    FAVORITES_READ = auto()


@dataclass(frozen=True)
class SourceCapabilitySummary:
    supported: frozenset[SourceCapability] = field(default_factory=frozenset)
    unavailable: frozenset[SourceCapability] = field(default_factory=frozenset)


# ── Stream handle ────────────────────────────────────────────

class StreamAvailability(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    STREAM_NOT_RESOLVED = auto()


@dataclass(frozen=True)
class StreamHandle:
    stream_id: str
    media_id: MediaId
    source_id: MediaSourceId
    availability: StreamAvailability = StreamAvailability.STREAM_NOT_RESOLVED
    format_hint: str | None = None
    quality_hint: str | None = None


# ── Provider capability ──────────────────────────────────────

class ProviderAvailabilityState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    AUTH_REQUIRED = auto()
    ERROR = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class ProviderCapability:
    capabilities: frozenset[SourceCapability] = field(default_factory=frozenset)
    availability: ProviderAvailabilityState = ProviderAvailabilityState.UNKNOWN


# ── MediaSourceClient ────────────────────────────────────────

@runtime_checkable
class MediaSourceClient(Protocol):
    """Stable contract for media/library-layer boundary.

    Aria must interact with any media source through this boundary only.
    Future real implementations must satisfy this protocol.

    This protocol is source-agnostic and provider-agnostic.
    It must not expose provider internals or assume Anchor is multi-provider.
    """

    def get_source_info(self) -> AriaResult[MediaSourceInfo]:
        """Get media source identity and availability."""
        ...

    def get_capability_summary(self) -> AriaResult[SourceCapabilitySummary]:
        """Get normalized capability summary for this source."""
        ...

    def request_stream(self, media_id: MediaId) -> AriaResult[StreamHandle]:
        """Request a stream handle for a given media ID."""
        ...

    def browse_library(self, request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]:
        """Browse app-facing library metadata through the source boundary."""
        ...

    def search_library(self, query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]:
        """Search app-facing library metadata through the source boundary."""
        ...

    def get_library_activity(self, request: LibraryActivityRequest) -> AriaResult[LibraryActivityResult]:
        """Get read-only source-derived library activity."""
        ...

    def get_favorites(self, max_results: int = 50) -> AriaResult[FavoritesViewState]:
        """Get read-only source-derived favorites state."""
        ...


# ── FakeMediaSourceClient ────────────────────────────────────

@dataclass
class FakeMediaSourceClient:
    """Deterministic fake media source client for local tests and early development.

    Returns configurable fake data. Never calls network, filesystem,
    or external process. Not a frozen dataclass so tests can optionally
    mutate it for edge-case scenarios.

    Failure-injection hooks (set to an AriaError to simulate failures):
        _get_source_info_error, _get_capability_summary_error,
        _request_stream_error

    Value overrides (set to override the default return data):
        _source_info_override, _capability_summary_override,
        _stream_handle_override
    """

    source_id: MediaSourceId = MediaSourceId("fake-source-1")
    display_name: str = "Fake Media Source"
    source_type: MediaSourceType = MediaSourceType.REMOTE_SERVER
    availability: SourceAvailabilityState = SourceAvailabilityState.AVAILABLE
    supported_capabilities: frozenset[SourceCapability] = field(default_factory=frozenset)

    _get_source_info_error: AriaError | None = field(default=None, repr=False)
    _get_capability_summary_error: AriaError | None = field(default=None, repr=False)
    _request_stream_error: AriaError | None = field(default=None, repr=False)

    _source_info_override: MediaSourceInfo | None = field(default=None, repr=False)
    _capability_summary_override: SourceCapabilitySummary | None = field(default=None, repr=False)
    _stream_handle_override: StreamHandle | None = field(default=None, repr=False)

    _library_browse_items: dict[Any, tuple[Any, ...]] = field(default_factory=dict, repr=False)
    _recently_added_items: tuple[Any, ...] = field(default_factory=tuple, repr=False)
    _recently_played_items: tuple[Any, ...] = field(default_factory=tuple, repr=False)
    _favorite_items: tuple[Any, ...] = field(default_factory=tuple, repr=False)
    _library_warnings: tuple[Any, ...] = field(default_factory=tuple, repr=False)
    _browse_library_error: AriaError | None = field(default=None, repr=False)
    _search_library_error: AriaError | None = field(default=None, repr=False)
    _library_activity_error: AriaError | None = field(default=None, repr=False)
    _favorites_error: AriaError | None = field(default=None, repr=False)

    _default_stream_availability: StreamAvailability = field(
        default=StreamAvailability.STREAM_NOT_RESOLVED, repr=False
    )

    @classmethod
    def with_full_library(cls) -> FakeMediaSourceClient:
        from noqlen_aria.library import (
            AlbumSummary,
            ArtistSummary,
            FolderSummary,
            GenreSummary,
            LibraryBrowseCategory,
            PlaylistSummary,
            TrackSummary,
        )

        source_id = MediaSourceId("fake-source-1")
        return cls(
            supported_capabilities=frozenset({
                SourceCapability.ARTISTS,
                SourceCapability.ALBUMS,
                SourceCapability.TRACKS,
                SourceCapability.PLAYLISTS,
                SourceCapability.GENRES,
                SourceCapability.FOLDERS,
                SourceCapability.SEARCH,
            }),
            _library_browse_items={
                LibraryBrowseCategory.ARTISTS: (
                    ArtistSummary(source_id, MediaId("artist-1"), "Ada Quartet", album_count=1, track_count=2),
                ),
                LibraryBrowseCategory.ALBUMS: (
                    AlbumSummary(source_id, MediaId("album-1"), "Analytical Engines", artist_name="Ada Quartet", track_count=2),
                ),
                LibraryBrowseCategory.TRACKS: (
                    TrackSummary(source_id, MediaId("track-1"), "First Difference", artist_name="Ada Quartet", album_name="Analytical Engines", duration_seconds=180),
                    TrackSummary(source_id, MediaId("track-2"), "Safe Folder Song", artist_name="Ada Quartet", album_name="Analytical Engines", duration_seconds=210),
                ),
                LibraryBrowseCategory.PLAYLISTS: (
                    PlaylistSummary(source_id, MediaId("playlist-1"), "Core Favorites", track_count=2),
                ),
                LibraryBrowseCategory.GENRES: (
                    GenreSummary(source_id, MediaId("genre-1"), "Instrumental", track_count=2),
                ),
                LibraryBrowseCategory.FOLDERS: (
                    FolderSummary(source_id, MediaId("folder-1"), "Source Folder", child_count=2),
                ),
            },
        )

    @classmethod
    def without_playlists(cls) -> FakeMediaSourceClient:
        fake = cls.with_full_library()
        fake.supported_capabilities = frozenset(
            cap for cap in fake.supported_capabilities if cap != SourceCapability.PLAYLISTS
        )
        return fake

    @classmethod
    def without_folders(cls) -> FakeMediaSourceClient:
        fake = cls.with_full_library()
        fake.supported_capabilities = frozenset(
            cap for cap in fake.supported_capabilities if cap != SourceCapability.FOLDERS
        )
        return fake

    @classmethod
    def degraded_with_warnings(cls) -> FakeMediaSourceClient:
        from noqlen_aria.contracts import AriaWarning

        fake = cls.with_full_library()
        fake.availability = SourceAvailabilityState.DEGRADED
        fake._library_warnings = (
            AriaWarning(code="SOURCE_DEGRADED", message="Source is degraded; results may be partial"),
        )
        return fake

    @classmethod
    def unavailable(cls) -> FakeMediaSourceClient:
        fake = cls.with_full_library()
        fake.availability = SourceAvailabilityState.UNAVAILABLE
        return fake

    @classmethod
    def empty_library(cls) -> FakeMediaSourceClient:
        return cls(
            supported_capabilities=frozenset({
                SourceCapability.ARTISTS,
                SourceCapability.ALBUMS,
                SourceCapability.TRACKS,
                SourceCapability.PLAYLISTS,
                SourceCapability.GENRES,
                SourceCapability.FOLDERS,
                SourceCapability.SEARCH,
            })
        )

    @classmethod
    def with_activity_and_favorites(cls) -> FakeMediaSourceClient:
        from noqlen_aria.library import LibraryBrowseCategory

        fake = cls.with_full_library()
        fake.supported_capabilities = fake.supported_capabilities | frozenset({
            SourceCapability.RECENTLY_ADDED,
            SourceCapability.RECENTLY_PLAYED,
            SourceCapability.FAVORITES_READ,
        })
        tracks = fake._library_browse_items.get(LibraryBrowseCategory.TRACKS, ())
        fake._recently_added_items = tuple(reversed(tracks))
        fake._recently_played_items = tuple(tracks)
        fake._favorite_items = tuple(tracks[:1])
        return fake

    @classmethod
    def with_recently_added(cls) -> FakeMediaSourceClient:
        from noqlen_aria.library import LibraryBrowseCategory

        fake = cls.with_full_library()
        fake.supported_capabilities = fake.supported_capabilities | frozenset({SourceCapability.RECENTLY_ADDED})
        tracks = fake._library_browse_items.get(LibraryBrowseCategory.TRACKS, ())
        fake._recently_added_items = tuple(reversed(tracks))
        return fake

    @classmethod
    def with_empty_activity_and_favorites(cls) -> FakeMediaSourceClient:
        fake = cls.empty_library()
        fake.supported_capabilities = fake.supported_capabilities | frozenset({
            SourceCapability.RECENTLY_ADDED,
            SourceCapability.RECENTLY_PLAYED,
            SourceCapability.FAVORITES_READ,
        })
        return fake

    @classmethod
    def without_favorites(cls) -> FakeMediaSourceClient:
        fake = cls.with_full_library()
        fake.supported_capabilities = fake.supported_capabilities - frozenset({SourceCapability.FAVORITES_READ})
        return fake

    def _build_capability_summary(self) -> SourceCapabilitySummary:
        all_caps = frozenset(SourceCapability)
        unavailable = all_caps - self.supported_capabilities
        return SourceCapabilitySummary(
            supported=self.supported_capabilities,
            unavailable=unavailable,
        )

    def get_source_info(self) -> AriaResult[MediaSourceInfo]:
        if self._get_source_info_error is not None:
            return AriaResult(ok=False, error=self._get_source_info_error)
        if self._source_info_override is not None:
            return AriaResult(ok=True, data=self._source_info_override)
        return AriaResult(
            ok=True,
            data=MediaSourceInfo(
                source_id=self.source_id,
                display_name=self.display_name,
                source_type=self.source_type,
                availability=self.availability,
            ),
        )

    def get_capability_summary(self) -> AriaResult[SourceCapabilitySummary]:
        if self._get_capability_summary_error is not None:
            return AriaResult(ok=False, error=self._get_capability_summary_error)
        if self._capability_summary_override is not None:
            return AriaResult(ok=True, data=self._capability_summary_override)
        if self.availability == SourceAvailabilityState.UNAVAILABLE:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="SOURCE_UNAVAILABLE",
                    message=f"Source {self.source_id} is unavailable",
                ),
            )
        return AriaResult(ok=True, data=self._build_capability_summary())

    def request_stream(self, media_id: MediaId) -> AriaResult[StreamHandle]:
        if self._request_stream_error is not None:
            return AriaResult(ok=False, error=self._request_stream_error)
        if self._stream_handle_override is not None:
            return AriaResult(ok=True, data=self._stream_handle_override)
        return AriaResult(
            ok=True,
            data=StreamHandle(
                stream_id=f"stream-{media_id}",
                media_id=media_id,
                source_id=self.source_id,
                availability=self._default_stream_availability,
            ),
        )

    def browse_library(self, request: LibraryBrowseRequest) -> AriaResult[LibraryBrowseResult]:
        from noqlen_aria.library import LibraryBrowseCategory, LibraryBrowseResult

        if self._browse_library_error is not None:
            return AriaResult(ok=False, error=self._browse_library_error)
        if self.availability == SourceAvailabilityState.UNAVAILABLE:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="SOURCE_UNAVAILABLE",
                    message=f"Source {self.source_id} is unavailable",
                ),
            )
        capability_by_category = {
            LibraryBrowseCategory.ARTISTS: SourceCapability.ARTISTS,
            LibraryBrowseCategory.ALBUMS: SourceCapability.ALBUMS,
            LibraryBrowseCategory.TRACKS: SourceCapability.TRACKS,
            LibraryBrowseCategory.PLAYLISTS: SourceCapability.PLAYLISTS,
            LibraryBrowseCategory.GENRES: SourceCapability.GENRES,
            LibraryBrowseCategory.FOLDERS: SourceCapability.FOLDERS,
        }
        capability = capability_by_category[request.category]
        if capability not in self.supported_capabilities:
            return AriaResult(
                ok=True,
                data=LibraryBrowseResult(
                    category=request.category,
                    available=False,
                    warnings=self._library_warnings,
                    error=AriaError(
                        code="CAPABILITY_NOT_SUPPORTED",
                        message=f"Library browse category {request.category.name} is not supported",
                    ),
                ),
            )
        return AriaResult(
            ok=True,
            data=LibraryBrowseResult(
                category=request.category,
                items=tuple(self._library_browse_items.get(request.category, ())),
                available=True,
                warnings=self._library_warnings,
            ),
        )

    def search_library(self, query: LibrarySearchQuery) -> AriaResult[LibrarySearchResult]:
        from noqlen_aria.library import LibrarySearchResult

        if self._search_library_error is not None:
            return AriaResult(ok=False, error=self._search_library_error)
        if self.availability == SourceAvailabilityState.UNAVAILABLE:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="SOURCE_UNAVAILABLE",
                    message=f"Source {self.source_id} is unavailable",
                ),
            )
        if SourceCapability.SEARCH not in self.supported_capabilities:
            return AriaResult(
                ok=True,
                data=LibrarySearchResult(
                    query=query,
                    valid_query=True,
                    warnings=self._library_warnings,
                    error=AriaError(
                        code="CAPABILITY_NOT_SUPPORTED",
                        message="Library search is not supported",
                    ),
                ),
            )
        categories = query.categories or frozenset(self._library_browse_items.keys())
        candidates = []
        for category in categories:
            for item in self._library_browse_items.get(category, ()):
                library_item = item.as_library_item()
                searchable = f"{library_item.display_name} {library_item.subtitle}".casefold()
                if query.normalized_text in searchable:
                    candidates.append(library_item)
        return AriaResult(
            ok=True,
            data=LibrarySearchResult(
                query=query,
                items=tuple(candidates[: query.max_results]),
                valid_query=True,
                warnings=self._library_warnings,
            ),
        )

    def get_library_activity(self, request: LibraryActivityRequest) -> AriaResult[LibraryActivityResult]:
        from noqlen_aria.library import LibraryActivityResult, LibraryActivityType

        if self._library_activity_error is not None:
            return AriaResult(ok=False, error=self._library_activity_error)
        if self.availability == SourceAvailabilityState.UNAVAILABLE:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="SOURCE_UNAVAILABLE",
                    message=f"Source {self.source_id} is unavailable",
                ),
            )
        capability = (
            SourceCapability.RECENTLY_ADDED
            if request.activity_type == LibraryActivityType.RECENTLY_ADDED
            else SourceCapability.RECENTLY_PLAYED
        )
        if capability not in self.supported_capabilities:
            return AriaResult(
                ok=True,
                data=LibraryActivityResult(
                    request=request,
                    available=False,
                    warnings=self._library_warnings,
                    error=AriaError(
                        code="CAPABILITY_NOT_SUPPORTED",
                        message=f"Library activity {request.activity_type.name} is not supported",
                    ),
                ),
            )
        raw_items = (
            self._recently_added_items
            if request.activity_type == LibraryActivityType.RECENTLY_ADDED
            else self._recently_played_items
        )
        items = tuple(item.as_library_item() for item in raw_items)[: request.max_results]
        return AriaResult(
            ok=True,
            data=LibraryActivityResult(
                request=request,
                items=items,
                available=True,
                warnings=self._library_warnings,
            ),
        )

    def get_favorites(self, max_results: int = 50) -> AriaResult[FavoritesViewState]:
        from noqlen_aria.library import FavoriteItemSummary, FavoritesViewState

        if self._favorites_error is not None:
            return AriaResult(ok=False, error=self._favorites_error)
        if self.availability == SourceAvailabilityState.UNAVAILABLE:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="SOURCE_UNAVAILABLE",
                    message=f"Source {self.source_id} is unavailable",
                ),
            )
        if SourceCapability.FAVORITES_READ not in self.supported_capabilities:
            return AriaResult(
                ok=True,
                data=FavoritesViewState(
                    available=False,
                    warnings=self._library_warnings,
                    error=AriaError(
                        code="CAPABILITY_NOT_SUPPORTED",
                        message="Favorites read state is not supported",
                    ),
                ),
            )
        favorites = tuple(
            FavoriteItemSummary(item=item.as_library_item()) for item in self._favorite_items
        )[:max_results]
        return AriaResult(
            ok=True,
            data=FavoritesViewState(
                items=favorites,
                available=True,
                warnings=self._library_warnings,
            ),
        )


__all__ = [
    "FakeMediaSourceClient",
    "MediaId",
    "MediaIdKind",
    "MediaSourceClient",
    "MediaSourceId",
    "MediaSourceInfo",
    "MediaSourceType",
    "ProviderAvailabilityState",
    "ProviderCapability",
    "SourceAvailabilityState",
    "SourceCapability",
    "SourceCapabilitySummary",
    "StreamAvailability",
    "StreamHandle",
]
