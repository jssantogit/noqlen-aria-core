"""Aria Core media source foundation — UI-independent contracts, fakes, and capability models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType, Protocol, runtime_checkable

from noqlen_aria.contracts import AriaError, AriaResult

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

    _default_stream_availability: StreamAvailability = field(
        default=StreamAvailability.STREAM_NOT_RESOLVED, repr=False
    )

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
