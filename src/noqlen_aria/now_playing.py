"""Aria Core now-playing foundation models and deterministic local service."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum, auto

from noqlen_aria.contracts import AriaError, AriaResult
from noqlen_aria.library import LibraryItemSummary
from noqlen_aria.media_source import MediaId, MediaSourceId
from noqlen_aria.queue import QueueAvailabilityState, QueueItem, QueueItemId, QueueState


class NowPlayingStatus(Enum):
    IDLE = auto()
    READY = auto()
    PAUSED = auto()
    UNAVAILABLE = auto()
    RESUMABLE = auto()


class PlaybackAvailabilityState(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    BLOCKED = auto()
    UNKNOWN = auto()


class PlaybackAvailabilityReason(Enum):
    NONE = auto()
    NO_CURRENT_ITEM = auto()
    MEDIA_UNAVAILABLE = auto()
    SOURCE_UNAVAILABLE = auto()
    PLAYBACK_NOT_CONFIGURED = auto()
    UNSUPPORTED_MEDIA = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class PlaybackPositionSnapshot:
    position_seconds: int = 0
    duration_seconds: int | None = None


@dataclass(frozen=True)
class NowPlayingItem:
    queue_item_id: QueueItemId | None = None
    library_item: LibraryItemSummary | None = None
    media_id: MediaId | None = None
    source_id: MediaSourceId | None = None
    display_name: str = ""
    subtitle: str = ""

    @classmethod
    def from_queue_item(cls, item: QueueItem) -> NowPlayingItem:
        subtitle = item.library_item.subtitle if item.library_item is not None else ""
        return cls(
            queue_item_id=item.item_id,
            library_item=item.library_item,
            media_id=item.media_id,
            source_id=item.source_id,
            display_name=item.display_name,
            subtitle=subtitle,
        )


@dataclass(frozen=True)
class UnavailableMediaState:
    media_id: MediaId | None = None
    source_id: MediaSourceId | None = None
    reason: PlaybackAvailabilityReason = PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
    message: str = "Media is unavailable"


@dataclass(frozen=True)
class ResumablePlaybackState:
    item: NowPlayingItem
    position: PlaybackPositionSnapshot = field(default_factory=PlaybackPositionSnapshot)
    can_resume: bool = True


@dataclass(frozen=True)
class NowPlayingState:
    status: NowPlayingStatus = NowPlayingStatus.IDLE
    item: NowPlayingItem | None = None
    playback_availability: PlaybackAvailabilityState = PlaybackAvailabilityState.UNAVAILABLE
    playback_availability_reason: PlaybackAvailabilityReason = PlaybackAvailabilityReason.NO_CURRENT_ITEM
    position: PlaybackPositionSnapshot = field(default_factory=PlaybackPositionSnapshot)
    resumable: ResumablePlaybackState | None = None
    unavailable_media: UnavailableMediaState | None = None


class NowPlayingService:
    """Build local now-playing snapshots without playback side effects."""

    def idle_state(self) -> AriaResult[NowPlayingState]:
        return AriaResult(ok=True, data=NowPlayingState())

    def build_from_queue(
        self,
        queue: QueueState,
        position: PlaybackPositionSnapshot | None = None,
    ) -> AriaResult[NowPlayingState]:
        if queue.current_position is None:
            return self.idle_state()
        if queue.current_position < 0 or queue.current_position >= len(queue.items):
            return self._err(
                "INVALID_NOW_PLAYING_QUEUE_POSITION",
                f"Queue current position {queue.current_position} is out of bounds",
            )

        queue_item = queue.items[queue.current_position]
        item = NowPlayingItem.from_queue_item(queue_item)
        position_result = self.validate_position_snapshot(position or PlaybackPositionSnapshot())
        if position_result.is_err():
            return AriaResult(ok=False, error=position_result.error)
        assert position_result.data is not None

        if queue_item.availability == QueueAvailabilityState.UNAVAILABLE:
            unavailable = self.build_unavailable_media_state(
                item,
                reason=PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
                message=queue_item.availability_reason or "Media is unavailable",
            )
            assert unavailable.data is not None
            return AriaResult(
                ok=True,
                data=NowPlayingState(
                    status=NowPlayingStatus.UNAVAILABLE,
                    item=item,
                    playback_availability=PlaybackAvailabilityState.UNAVAILABLE,
                    playback_availability_reason=PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
                    position=position_result.data,
                    unavailable_media=unavailable.data,
                ),
            )

        return AriaResult(
            ok=True,
            data=NowPlayingState(
                status=NowPlayingStatus.READY,
                item=item,
                playback_availability=PlaybackAvailabilityState.AVAILABLE,
                playback_availability_reason=PlaybackAvailabilityReason.NONE,
                position=position_result.data,
            ),
        )

    def build_unavailable_state(
        self,
        item: NowPlayingItem,
        reason: PlaybackAvailabilityReason = PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
        message: str = "Media is unavailable",
    ) -> AriaResult[NowPlayingState]:
        unavailable = self.build_unavailable_media_state(item, reason=reason, message=message)
        assert unavailable.data is not None
        availability_reason = reason if reason != PlaybackAvailabilityReason.NONE else PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
        return AriaResult(
            ok=True,
            data=NowPlayingState(
                status=NowPlayingStatus.UNAVAILABLE,
                item=item,
                playback_availability=PlaybackAvailabilityState.UNAVAILABLE,
                playback_availability_reason=availability_reason,
                unavailable_media=unavailable.data,
            ),
        )

    def build_resumable_state(
        self,
        item: NowPlayingItem | None,
        position: PlaybackPositionSnapshot,
    ) -> AriaResult[NowPlayingState]:
        if item is None:
            return self._err("RESUMABLE_ITEM_REQUIRED", "A resumable now-playing item is required")
        position_result = self.validate_position_snapshot(position)
        if position_result.is_err():
            return AriaResult(ok=False, error=position_result.error)
        assert position_result.data is not None
        resumable = ResumablePlaybackState(item=item, position=position_result.data)
        return AriaResult(
            ok=True,
            data=NowPlayingState(
                status=NowPlayingStatus.RESUMABLE,
                item=item,
                playback_availability=PlaybackAvailabilityState.AVAILABLE,
                playback_availability_reason=PlaybackAvailabilityReason.NONE,
                position=position_result.data,
                resumable=resumable,
            ),
        )

    def build_unavailable_media_state(
        self,
        item: NowPlayingItem,
        reason: PlaybackAvailabilityReason = PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
        message: str = "Media is unavailable",
    ) -> AriaResult[UnavailableMediaState]:
        safe_reason = reason if reason != PlaybackAvailabilityReason.NONE else PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
        return AriaResult(
            ok=True,
            data=UnavailableMediaState(
                media_id=item.media_id,
                source_id=item.source_id,
                reason=safe_reason,
                message=message or "Media is unavailable",
            ),
        )

    def with_playback_availability(
        self,
        state: NowPlayingState,
        availability: PlaybackAvailabilityState,
        reason: PlaybackAvailabilityReason = PlaybackAvailabilityReason.NONE,
    ) -> AriaResult[NowPlayingState]:
        safe_reason = self._safe_availability_reason(availability, reason)
        status = state.status
        if availability in {PlaybackAvailabilityState.UNAVAILABLE, PlaybackAvailabilityState.BLOCKED}:
            status = NowPlayingStatus.UNAVAILABLE if state.item is not None else NowPlayingStatus.IDLE
        return AriaResult(
            ok=True,
            data=replace(
                state,
                status=status,
                playback_availability=availability,
                playback_availability_reason=safe_reason,
            ),
        )

    def validate_position_snapshot(
        self,
        snapshot: PlaybackPositionSnapshot,
    ) -> AriaResult[PlaybackPositionSnapshot]:
        if snapshot.position_seconds < 0:
            return self._err("INVALID_PLAYBACK_POSITION", "Playback position must not be negative")
        if snapshot.duration_seconds is not None and snapshot.duration_seconds < 0:
            return self._err("INVALID_PLAYBACK_DURATION", "Playback duration must not be negative")
        if snapshot.duration_seconds is not None and snapshot.position_seconds > snapshot.duration_seconds:
            return self._err("PLAYBACK_POSITION_EXCEEDS_DURATION", "Playback position exceeds known duration")
        return AriaResult(ok=True, data=snapshot)

    def _safe_availability_reason(
        self,
        availability: PlaybackAvailabilityState,
        reason: PlaybackAvailabilityReason,
    ) -> PlaybackAvailabilityReason:
        if availability == PlaybackAvailabilityState.AVAILABLE:
            return PlaybackAvailabilityReason.NONE
        if reason != PlaybackAvailabilityReason.NONE:
            return reason
        if availability == PlaybackAvailabilityState.BLOCKED:
            return PlaybackAvailabilityReason.PLAYBACK_NOT_CONFIGURED
        if availability == PlaybackAvailabilityState.UNAVAILABLE:
            return PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
        return PlaybackAvailabilityReason.UNKNOWN

    def _err(self, code: str, message: str):
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


class FakeNowPlayingScenarios:
    @staticmethod
    def idle() -> NowPlayingState:
        result = NowPlayingService().idle_state()
        assert result.data is not None
        return result.data

    @staticmethod
    def from_queue(queue: QueueState) -> NowPlayingState:
        result = NowPlayingService().build_from_queue(queue)
        assert result.data is not None
        return result.data

    @staticmethod
    def unavailable_item(item: NowPlayingItem) -> NowPlayingState:
        result = NowPlayingService().build_unavailable_state(item)
        assert result.data is not None
        return result.data

    @staticmethod
    def resumable_item(item: NowPlayingItem, position_seconds: int = 30) -> NowPlayingState:
        result = NowPlayingService().build_resumable_state(item, PlaybackPositionSnapshot(position_seconds))
        assert result.data is not None
        return result.data


__all__ = [
    "FakeNowPlayingScenarios",
    "NowPlayingItem",
    "NowPlayingService",
    "NowPlayingState",
    "NowPlayingStatus",
    "PlaybackAvailabilityReason",
    "PlaybackAvailabilityState",
    "PlaybackPositionSnapshot",
    "ResumablePlaybackState",
    "UnavailableMediaState",
]
