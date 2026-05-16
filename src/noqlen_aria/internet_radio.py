"""Aria Core internet radio foundation — data-only radio models and deterministic services.

Bloco 15 — Internet Radio Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning

RadioStationId = NewType("RadioStationId", str)


class RadioStreamKind(Enum):
    MP3 = auto()
    AAC = auto()
    OGG = auto()
    OPUS = auto()
    HLS = auto()
    DASH = auto()
    SHOUTCAST = auto()
    UNKNOWN = auto()


class RadioSourceCapability(Enum):
    MANUAL_STATIONS = auto()
    DIRECTORY_READ = auto()
    STREAM_HANDLES = auto()
    METADATA_READ = auto()
    ICY_METADATA_READ = auto()
    ARTWORK_READ = auto()
    FAVORITES_READ = auto()
    FAVORITES_MUTATION = auto()


class RadioImportSource(Enum):
    MANUAL = auto()
    DIRECTORY = auto()
    PROVIDER_EXPORT = auto()
    UNKNOWN = auto()


class RadioUnavailableReason(Enum):
    NONE = auto()
    UNSUPPORTED_STREAM_KIND = auto()
    SOURCE_UNAVAILABLE = auto()
    STATION_UNAVAILABLE = auto()
    STREAM_MISSING = auto()
    PLAYBACK_NOT_CONFIGURED = auto()
    FAVORITE_MUTATION_UNSUPPORTED = auto()
    VALIDATION_FAILED = auto()
    UNKNOWN = auto()


class RadioValidationIssue(Enum):
    EMPTY_NAME = auto()
    MISSING_STREAM_URL = auto()
    UNSUPPORTED_URL_SCHEME = auto()
    MALFORMED_URL = auto()
    UNSUPPORTED_STREAM_KIND = auto()


@dataclass(frozen=True)
class RadioDirectoryRef:
    directory_id: str
    display_name: str
    homepage_hint: str = ""


@dataclass(frozen=True)
class RadioStationRef:
    station_id: RadioStationId
    display_name: str
    directory: RadioDirectoryRef | None = None
    source_label: str = ""


@dataclass(frozen=True)
class ManualRadioStationInput:
    display_name: str
    stream_url: str
    stream_kind: RadioStreamKind = RadioStreamKind.UNKNOWN
    homepage_hint: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RadioStreamHandle:
    handle_id: str
    station_id: RadioStationId
    stream_kind: RadioStreamKind
    declared_uri: str
    label: str = ""
    format_hint: str = ""


@dataclass(frozen=True)
class IcyMetadataState:
    stream_title: str = ""
    icy_name: str = ""
    icy_genre: str = ""
    icy_url: str = ""
    bitrate_kbps: int | None = None
    metadata_interval: int | None = None


@dataclass(frozen=True)
class RadioMetadataState:
    title: str = ""
    artist: str = ""
    album: str = ""
    program_name: str = ""
    is_live: bool = True
    icy: IcyMetadataState | None = None


@dataclass(frozen=True)
class RadioArtworkState:
    artwork_uri: str = ""
    thumbnail_uri: str = ""
    alt_text: str = ""
    attribution: str = ""


@dataclass(frozen=True)
class RadioFavoriteState:
    is_favorite: bool = False
    source_supports_read: bool = False
    mutation_supported: bool = False
    future_intent_only: bool = True
    unavailable_reason: RadioUnavailableReason = RadioUnavailableReason.NONE


@dataclass(frozen=True)
class RadioPlaybackAvailability:
    available: bool = False
    degraded: bool = False
    reason: RadioUnavailableReason = RadioUnavailableReason.PLAYBACK_NOT_CONFIGURED
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RadioStationSummary:
    station_id: RadioStationId
    display_name: str
    stream: RadioStreamHandle
    import_source: RadioImportSource = RadioImportSource.UNKNOWN
    directory: RadioDirectoryRef | None = None
    metadata: RadioMetadataState = field(default_factory=RadioMetadataState)
    artwork: RadioArtworkState | None = None
    favorite: RadioFavoriteState = field(default_factory=RadioFavoriteState)
    playback_availability: RadioPlaybackAvailability = field(default_factory=RadioPlaybackAvailability)
    tags: tuple[str, ...] = field(default_factory=tuple)

    def as_ref(self) -> RadioStationRef:
        return RadioStationRef(
            station_id=self.station_id,
            display_name=self.display_name,
            directory=self.directory,
        )


class InternetRadioService:
    """Build internet radio state from explicit data only.

    No method opens network connections, parses stream protocols, starts playback,
    calls providers, mutates backends, or reads the filesystem.
    """

    _SUPPORTED_SCHEMES = frozenset({"http", "https"})
    _SUPPORTED_STREAM_KINDS = frozenset({
        RadioStreamKind.MP3,
        RadioStreamKind.AAC,
        RadioStreamKind.OGG,
        RadioStreamKind.OPUS,
    })

    def validate_manual_station_input(
        self,
        manual_input: ManualRadioStationInput,
    ) -> AriaResult[tuple[RadioStationSummary, tuple[RadioValidationIssue, ...]]]:
        issues = self._validate_manual_input(manual_input)
        if issues:
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="INVALID_RADIO_STATION",
                    message="Manual radio station input is invalid",
                ),
                data=(self._invalid_summary(manual_input), issues),
            )

        summary = self.build_station_summary(
            station_id=self.station_id_from_url(manual_input.stream_url),
            display_name=manual_input.display_name.strip(),
            stream_url=manual_input.stream_url.strip(),
            stream_kind=manual_input.stream_kind,
            import_source=RadioImportSource.MANUAL,
            tags=tuple(tag.strip() for tag in manual_input.tags if tag.strip()),
        )
        if summary.is_err():
            return AriaResult(ok=False, error=summary.error)
        return AriaResult(ok=True, data=(summary.data, ()))

    def build_station_summary(
        self,
        *,
        station_id: RadioStationId,
        display_name: str,
        stream_url: str,
        stream_kind: RadioStreamKind = RadioStreamKind.UNKNOWN,
        import_source: RadioImportSource = RadioImportSource.UNKNOWN,
        directory: RadioDirectoryRef | None = None,
        metadata: RadioMetadataState | None = None,
        artwork: RadioArtworkState | None = None,
        favorite: RadioFavoriteState | None = None,
        capabilities: frozenset[RadioSourceCapability] = frozenset({RadioSourceCapability.STREAM_HANDLES}),
        source_available: bool = True,
        station_available: bool = True,
        degraded: bool = False,
        warnings: tuple[AriaWarning, ...] = (),
        tags: tuple[str, ...] = (),
    ) -> AriaResult[RadioStationSummary]:
        if not str(station_id).strip():
            return self._err("RADIO_STATION_ID_REQUIRED", "Radio station id is required")
        if not display_name.strip():
            return self._err("RADIO_STATION_NAME_REQUIRED", "Radio station display name is required")
        handle_result = self.build_stream_handle(station_id, stream_url, stream_kind)
        if handle_result.is_err():
            return AriaResult(ok=False, error=handle_result.error)

        availability = self.evaluate_playback_availability(
            stream_kind=stream_kind,
            stream_url=stream_url,
            capabilities=capabilities,
            source_available=source_available,
            station_available=station_available,
            degraded=degraded,
            warnings=warnings,
        )
        if availability.is_err():
            return AriaResult(ok=False, error=availability.error)

        return self._ok(RadioStationSummary(
            station_id=station_id,
            display_name=display_name.strip(),
            stream=handle_result.data,
            import_source=import_source,
            directory=directory,
            metadata=metadata or RadioMetadataState(),
            artwork=artwork,
            favorite=favorite or RadioFavoriteState(),
            playback_availability=availability.data,
            tags=tuple(tag.strip() for tag in tags if tag.strip()),
        ))

    def build_stream_handle(
        self,
        station_id: RadioStationId,
        stream_url: str,
        stream_kind: RadioStreamKind,
    ) -> AriaResult[RadioStreamHandle]:
        declared_uri = stream_url.strip()
        if not declared_uri:
            return self._err("RADIO_STREAM_URL_REQUIRED", "Radio stream URL is required")
        return self._ok(RadioStreamHandle(
            handle_id=f"radio-stream-{station_id}",
            station_id=station_id,
            stream_kind=stream_kind,
            declared_uri=declared_uri,
            label="Declared radio stream handle",
            format_hint=stream_kind.name.lower() if stream_kind != RadioStreamKind.UNKNOWN else "",
        ))

    def evaluate_playback_availability(
        self,
        *,
        stream_kind: RadioStreamKind,
        stream_url: str = "",
        capabilities: frozenset[RadioSourceCapability] = frozenset({RadioSourceCapability.STREAM_HANDLES}),
        source_available: bool = True,
        station_available: bool = True,
        degraded: bool = False,
        warnings: tuple[AriaWarning, ...] = (),
    ) -> AriaResult[RadioPlaybackAvailability]:
        if not source_available:
            return self._ok(RadioPlaybackAvailability(reason=RadioUnavailableReason.SOURCE_UNAVAILABLE))
        if not station_available:
            return self._ok(RadioPlaybackAvailability(reason=RadioUnavailableReason.STATION_UNAVAILABLE))
        if not stream_url.strip():
            return self._ok(RadioPlaybackAvailability(reason=RadioUnavailableReason.STREAM_MISSING))
        if RadioSourceCapability.STREAM_HANDLES not in capabilities:
            return self._ok(RadioPlaybackAvailability(reason=RadioUnavailableReason.SOURCE_UNAVAILABLE))
        if stream_kind not in self._SUPPORTED_STREAM_KINDS:
            return self._ok(RadioPlaybackAvailability(reason=RadioUnavailableReason.UNSUPPORTED_STREAM_KIND))
        return self._ok(RadioPlaybackAvailability(
            available=True,
            degraded=degraded,
            reason=RadioUnavailableReason.NONE,
            warnings=warnings,
        ))

    def build_metadata_state(
        self,
        *,
        title: str = "",
        artist: str = "",
        album: str = "",
        program_name: str = "",
        is_live: bool = True,
        icy: IcyMetadataState | None = None,
    ) -> AriaResult[RadioMetadataState]:
        return self._ok(RadioMetadataState(
            title=title.strip(),
            artist=artist.strip(),
            album=album.strip(),
            program_name=program_name.strip(),
            is_live=is_live,
            icy=icy,
        ))

    def build_icy_metadata_state(
        self,
        *,
        stream_title: str = "",
        icy_name: str = "",
        icy_genre: str = "",
        icy_url: str = "",
        bitrate_kbps: int | None = None,
        metadata_interval: int | None = None,
    ) -> AriaResult[IcyMetadataState]:
        if bitrate_kbps is not None and bitrate_kbps < 0:
            return self._err("INVALID_ICY_BITRATE", "ICY bitrate must not be negative")
        if metadata_interval is not None and metadata_interval < 0:
            return self._err("INVALID_ICY_INTERVAL", "ICY metadata interval must not be negative")
        return self._ok(IcyMetadataState(
            stream_title=stream_title.strip(),
            icy_name=icy_name.strip(),
            icy_genre=icy_genre.strip(),
            icy_url=icy_url.strip(),
            bitrate_kbps=bitrate_kbps,
            metadata_interval=metadata_interval,
        ))

    def build_artwork_state(
        self,
        *,
        artwork_uri: str = "",
        thumbnail_uri: str = "",
        alt_text: str = "",
        attribution: str = "",
    ) -> AriaResult[RadioArtworkState]:
        return self._ok(RadioArtworkState(
            artwork_uri=artwork_uri.strip(),
            thumbnail_uri=thumbnail_uri.strip(),
            alt_text=alt_text.strip(),
            attribution=attribution.strip(),
        ))

    def build_favorite_state(
        self,
        *,
        is_favorite: bool = False,
        source_supports_read: bool = True,
        mutation_supported: bool = False,
    ) -> AriaResult[RadioFavoriteState]:
        return self._ok(RadioFavoriteState(
            is_favorite=is_favorite,
            source_supports_read=source_supports_read,
            mutation_supported=mutation_supported,
            future_intent_only=not mutation_supported,
            unavailable_reason=(
                RadioUnavailableReason.NONE
                if mutation_supported
                else RadioUnavailableReason.FAVORITE_MUTATION_UNSUPPORTED
            ),
        ))

    def preview_favorite_mutation(self, station: RadioStationRef) -> AriaResult[RadioFavoriteState]:
        if not str(station.station_id).strip():
            return self._err("RADIO_STATION_ID_REQUIRED", "Radio station id is required")
        return self._ok(RadioFavoriteState(
            is_favorite=False,
            source_supports_read=True,
            mutation_supported=False,
            future_intent_only=True,
            unavailable_reason=RadioUnavailableReason.FAVORITE_MUTATION_UNSUPPORTED,
        ))

    def station_id_from_url(self, stream_url: str) -> RadioStationId:
        normalized = stream_url.strip().lower().removeprefix("https://").removeprefix("http://")
        normalized = "-".join(part for part in normalized.replace("/", "-").split("-") if part)
        return RadioStationId(normalized or "manual-radio-station")

    def _validate_manual_input(self, manual_input: ManualRadioStationInput) -> tuple[RadioValidationIssue, ...]:
        issues: list[RadioValidationIssue] = []
        name = manual_input.display_name.strip()
        url = manual_input.stream_url.strip()
        if not name:
            issues.append(RadioValidationIssue.EMPTY_NAME)
        if not url:
            issues.append(RadioValidationIssue.MISSING_STREAM_URL)
        else:
            scheme = url.split(":", 1)[0].lower() if ":" in url else ""
            if scheme not in self._SUPPORTED_SCHEMES:
                issues.append(RadioValidationIssue.UNSUPPORTED_URL_SCHEME)
            if "://" not in url or not url.split("://", 1)[1].strip() or " " in url:
                issues.append(RadioValidationIssue.MALFORMED_URL)
        if manual_input.stream_kind not in self._SUPPORTED_STREAM_KINDS:
            issues.append(RadioValidationIssue.UNSUPPORTED_STREAM_KIND)
        return tuple(dict.fromkeys(issues))

    def _invalid_summary(self, manual_input: ManualRadioStationInput) -> RadioStationSummary:
        station_id = self.station_id_from_url(manual_input.stream_url)
        handle = RadioStreamHandle(
            handle_id=f"radio-stream-{station_id}",
            station_id=station_id,
            stream_kind=manual_input.stream_kind,
            declared_uri=manual_input.stream_url.strip(),
        )
        return RadioStationSummary(
            station_id=station_id,
            display_name=manual_input.display_name.strip(),
            stream=handle,
            import_source=RadioImportSource.MANUAL,
            playback_availability=RadioPlaybackAvailability(
                reason=RadioUnavailableReason.VALIDATION_FAILED,
            ),
        )

    def _ok(self, data):
        return AriaResult(ok=True, data=data)

    def _err(self, code: str, message: str):
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


class FakeRadioScenarios:
    """Deterministic internet radio scenarios for tests and future UI samples."""

    _service = InternetRadioService()

    @classmethod
    def valid_manual_station(cls) -> RadioStationSummary:
        result = cls._service.validate_manual_station_input(ManualRadioStationInput(
            display_name="Aria Test Radio",
            stream_url="https://radio.example.test/live.mp3",
            stream_kind=RadioStreamKind.MP3,
            tags=("test", "live"),
        ))
        return result.data[0]

    @classmethod
    def invalid_manual_station_url(cls) -> AriaResult[tuple[RadioStationSummary, tuple[RadioValidationIssue, ...]]]:
        return cls._service.validate_manual_station_input(ManualRadioStationInput(
            display_name="Broken Radio",
            stream_url="not a stream",
            stream_kind=RadioStreamKind.MP3,
        ))

    @classmethod
    def station_with_icy_metadata(cls) -> RadioStationSummary:
        icy = cls._service.build_icy_metadata_state(
            stream_title="Example Artist - Example Track",
            icy_name="Aria Test Radio",
            icy_genre="Mixed",
            bitrate_kbps=128,
            metadata_interval=16000,
        ).data
        metadata = cls._service.build_metadata_state(
            title="Example Track",
            artist="Example Artist",
            program_name="Live Test Program",
            icy=icy,
        ).data
        return cls._service.build_station_summary(
            station_id=RadioStationId("station-icy"),
            display_name="ICY Metadata Radio",
            stream_url="https://radio.example.test/icy.mp3",
            stream_kind=RadioStreamKind.MP3,
            metadata=metadata,
        ).data

    @classmethod
    def station_with_artwork_metadata(cls) -> RadioStationSummary:
        artwork = cls._service.build_artwork_state(
            artwork_uri="https://radio.example.test/artwork.jpg",
            thumbnail_uri="https://radio.example.test/thumb.jpg",
            alt_text="Station artwork",
        ).data
        return cls._service.build_station_summary(
            station_id=RadioStationId("station-artwork"),
            display_name="Artwork Radio",
            stream_url="https://radio.example.test/artwork.mp3",
            stream_kind=RadioStreamKind.MP3,
            artwork=artwork,
        ).data

    @classmethod
    def unsupported_stream_kind(cls) -> RadioStationSummary:
        return cls._service.build_station_summary(
            station_id=RadioStationId("station-hls"),
            display_name="Unsupported Radio",
            stream_url="https://radio.example.test/live.m3u8",
            stream_kind=RadioStreamKind.HLS,
        ).data

    @classmethod
    def unavailable_station(cls) -> RadioStationSummary:
        return cls._service.build_station_summary(
            station_id=RadioStationId("station-unavailable"),
            display_name="Unavailable Radio",
            stream_url="https://radio.example.test/offline.mp3",
            stream_kind=RadioStreamKind.MP3,
            station_available=False,
        ).data

    @classmethod
    def degraded_station_with_warnings(cls) -> RadioStationSummary:
        return cls._service.build_station_summary(
            station_id=RadioStationId("station-degraded"),
            display_name="Degraded Radio",
            stream_url="https://radio.example.test/degraded.mp3",
            stream_kind=RadioStreamKind.MP3,
            degraded=True,
            warnings=(AriaWarning(code="RADIO_DEGRADED", message="Radio state is degraded"),),
        ).data

    @classmethod
    def favorite_read_state(cls) -> RadioFavoriteState:
        return cls._service.build_favorite_state(is_favorite=True, source_supports_read=True).data

    @classmethod
    def favorite_mutation_unsupported(cls) -> RadioFavoriteState:
        station = RadioStationRef(RadioStationId("favorite-station"), "Favorite Station")
        return cls._service.preview_favorite_mutation(station).data


__all__ = [
    "FakeRadioScenarios",
    "IcyMetadataState",
    "InternetRadioService",
    "ManualRadioStationInput",
    "RadioArtworkState",
    "RadioDirectoryRef",
    "RadioFavoriteState",
    "RadioImportSource",
    "RadioMetadataState",
    "RadioPlaybackAvailability",
    "RadioSourceCapability",
    "RadioStationId",
    "RadioStationRef",
    "RadioStationSummary",
    "RadioStreamHandle",
    "RadioStreamKind",
    "RadioUnavailableReason",
    "RadioValidationIssue",
]
