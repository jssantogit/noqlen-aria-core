"""Tests for Bloco 12 now-playing foundation."""

from __future__ import annotations

from dataclasses import asdict

import inspect
import json

import noqlen_aria.now_playing as now_playing
from noqlen_aria.contracts import safe_serialize
from noqlen_aria.library import LibraryItemSummary
from noqlen_aria.media_source import MediaId, MediaIdKind, MediaSourceId
from noqlen_aria.now_playing import (
    FakeNowPlayingScenarios,
    NowPlayingItem,
    NowPlayingService,
    NowPlayingState,
    NowPlayingStatus,
    PlaybackAvailabilityReason,
    PlaybackAvailabilityState,
    PlaybackPositionSnapshot,
)
from noqlen_aria.queue import QueueAvailabilityState, QueueItem, QueueItemId, QueueState


def _track_summary(track_id: str = "track-1", name: str = "First Difference") -> LibraryItemSummary:
    return LibraryItemSummary(
        source_id=MediaSourceId("fake-source-1"),
        item_id=MediaId(track_id),
        item_kind=MediaIdKind.TRACK,
        display_name=name,
        subtitle="Ada Quartet",
    )


def _queue_item(item_id: str = "queue-item-1", track_id: str = "track-1") -> QueueItem:
    return QueueItem.from_library_item(QueueItemId(item_id), _track_summary(track_id=track_id))


def _now_playing_item() -> NowPlayingItem:
    return NowPlayingItem.from_queue_item(_queue_item())


def _data(result):
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def test_idle_defaults_are_safe_and_empty() -> None:
    state = _data(NowPlayingService().idle_state())

    assert state == NowPlayingState()
    assert state.status == NowPlayingStatus.IDLE
    assert state.item is None
    assert state.playback_availability == PlaybackAvailabilityState.UNAVAILABLE
    assert state.playback_availability_reason == PlaybackAvailabilityReason.NO_CURRENT_ITEM
    assert state.position == PlaybackPositionSnapshot()
    json.dumps(safe_serialize(state))


def test_now_playing_from_queue_current_item_references_item_without_playing_audio() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)

    state = _data(NowPlayingService().build_from_queue(queue))

    assert state.status == NowPlayingStatus.READY
    assert state.item is not None
    assert state.item.queue_item_id == "queue-item-1"
    assert state.item.library_item == _track_summary()
    assert state.item.media_id == "track-1"
    assert state.item.source_id == "fake-source-1"
    assert state.playback_availability == PlaybackAvailabilityState.AVAILABLE
    assert state.playback_availability_reason == PlaybackAvailabilityReason.NONE
    assert not hasattr(NowPlayingService, "play")
    assert not hasattr(NowPlayingService, "pause")
    assert not hasattr(NowPlayingService, "seek")


def test_queue_without_current_item_returns_idle_state() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=None)

    state = _data(NowPlayingService().build_from_queue(queue))

    assert state.status == NowPlayingStatus.IDLE
    assert state.item is None
    assert state.playback_availability_reason == PlaybackAvailabilityReason.NO_CURRENT_ITEM


def test_invalid_queue_current_position_returns_safe_error() -> None:
    result = NowPlayingService().build_from_queue(QueueState(items=(_queue_item(),), current_position=4))

    assert result.is_err()
    assert result.error.code == "INVALID_NOW_PLAYING_QUEUE_POSITION"


def test_unavailable_media_state_is_explicit_and_safe() -> None:
    unavailable_item = QueueItem.from_library_item(
        QueueItemId("queue-item-unavailable"),
        _track_summary("track-unavailable", "Missing Track"),
        availability=QueueAvailabilityState.UNAVAILABLE,
        availability_reason="Source reports unavailable",
    )
    queue = QueueState(items=(unavailable_item,), current_position=0)

    state = _data(NowPlayingService().build_from_queue(queue))

    assert state.status == NowPlayingStatus.UNAVAILABLE
    assert state.playback_availability == PlaybackAvailabilityState.UNAVAILABLE
    assert state.playback_availability_reason == PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
    assert state.unavailable_media is not None
    assert state.unavailable_media.media_id == "track-unavailable"
    assert state.unavailable_media.reason == PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
    assert state.unavailable_media.message == "Source reports unavailable"


def test_build_unavailable_state_normalizes_missing_reason() -> None:
    state = _data(
        NowPlayingService().build_unavailable_state(
            _now_playing_item(),
            reason=PlaybackAvailabilityReason.NONE,
            message="",
        )
    )

    assert state.unavailable_media is not None
    assert state.playback_availability_reason == PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
    assert state.unavailable_media.reason == PlaybackAvailabilityReason.MEDIA_UNAVAILABLE
    assert state.unavailable_media.message == "Media is unavailable"


def test_resumable_state_and_position_snapshot_serialize_explicitly() -> None:
    state = _data(
        NowPlayingService().build_resumable_state(
            _now_playing_item(),
            PlaybackPositionSnapshot(position_seconds=42, duration_seconds=180),
        )
    )

    serialized = safe_serialize(state)
    assert state.status == NowPlayingStatus.RESUMABLE
    assert state.resumable is not None
    assert state.resumable.can_resume is True
    assert serialized["resumable"]["position"]["position_seconds"] == 42
    assert serialized["resumable"]["position"]["duration_seconds"] == 180
    json.dumps(serialized)


def test_resumable_state_requires_item() -> None:
    result = NowPlayingService().build_resumable_state(None, PlaybackPositionSnapshot(position_seconds=5))

    assert result.is_err()
    assert result.error.code == "RESUMABLE_ITEM_REQUIRED"


def test_playback_position_snapshot_validation_rejects_negative_position() -> None:
    result = NowPlayingService().validate_position_snapshot(PlaybackPositionSnapshot(position_seconds=-1))

    assert result.is_err()
    assert result.error.code == "INVALID_PLAYBACK_POSITION"


def test_playback_position_snapshot_validation_rejects_negative_duration() -> None:
    result = NowPlayingService().validate_position_snapshot(
        PlaybackPositionSnapshot(position_seconds=0, duration_seconds=-1)
    )

    assert result.is_err()
    assert result.error.code == "INVALID_PLAYBACK_DURATION"


def test_position_exceeding_known_duration_is_rejected() -> None:
    result = NowPlayingService().validate_position_snapshot(
        PlaybackPositionSnapshot(position_seconds=181, duration_seconds=180)
    )

    assert result.is_err()
    assert result.error.code == "PLAYBACK_POSITION_EXCEEDS_DURATION"


def test_position_snapshot_accepts_unknown_duration() -> None:
    snapshot = PlaybackPositionSnapshot(position_seconds=9, duration_seconds=None)

    assert _data(NowPlayingService().validate_position_snapshot(snapshot)) == snapshot


def test_build_from_queue_rejects_invalid_position_snapshot() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)

    result = NowPlayingService().build_from_queue(queue, PlaybackPositionSnapshot(position_seconds=-5))

    assert result.is_err()
    assert result.error.code == "INVALID_PLAYBACK_POSITION"


def test_playback_availability_states_are_explicit() -> None:
    service = NowPlayingService()
    ready = _data(service.build_from_queue(QueueState(items=(_queue_item(),), current_position=0)))

    blocked = _data(service.with_playback_availability(ready, PlaybackAvailabilityState.BLOCKED))
    unavailable = _data(
        service.with_playback_availability(
            ready,
            PlaybackAvailabilityState.UNAVAILABLE,
            PlaybackAvailabilityReason.SOURCE_UNAVAILABLE,
        )
    )
    unknown = _data(service.with_playback_availability(ready, PlaybackAvailabilityState.UNKNOWN))
    available = _data(
        service.with_playback_availability(
            ready,
            PlaybackAvailabilityState.AVAILABLE,
            PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
        )
    )

    assert blocked.playback_availability_reason == PlaybackAvailabilityReason.PLAYBACK_NOT_CONFIGURED
    assert unavailable.playback_availability_reason == PlaybackAvailabilityReason.SOURCE_UNAVAILABLE
    assert unknown.playback_availability_reason == PlaybackAvailabilityReason.UNKNOWN
    assert available.playback_availability_reason == PlaybackAvailabilityReason.NONE


def test_blocked_playback_availability_does_not_start_playback() -> None:
    ready = _data(NowPlayingService().build_from_queue(QueueState(items=(_queue_item(),), current_position=0)))
    blocked = _data(NowPlayingService().with_playback_availability(ready, PlaybackAvailabilityState.BLOCKED))

    assert blocked.status == NowPlayingStatus.UNAVAILABLE
    assert blocked.playback_availability == PlaybackAvailabilityState.BLOCKED
    assert not hasattr(NowPlayingService, "start")
    assert not hasattr(NowPlayingService, "execute")


def test_fake_now_playing_scenarios_are_deterministic() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    item = _now_playing_item()

    assert FakeNowPlayingScenarios.idle() == FakeNowPlayingScenarios.idle()
    assert FakeNowPlayingScenarios.from_queue(queue) == FakeNowPlayingScenarios.from_queue(queue)
    assert FakeNowPlayingScenarios.unavailable_item(item) == FakeNowPlayingScenarios.unavailable_item(item)
    assert FakeNowPlayingScenarios.resumable_item(item) == FakeNowPlayingScenarios.resumable_item(item)


def test_ui_consumes_aria_core_now_playing_models_only() -> None:
    state = _data(NowPlayingService().build_from_queue(QueueState(items=(_queue_item(),), current_position=0)))

    assert state.__class__.__module__ == "noqlen_aria.now_playing"
    assert state.item.__class__.__module__ == "noqlen_aria.now_playing"
    assert state.item.library_item.__class__.__module__ == "noqlen_aria.library"


def test_now_playing_models_do_not_expose_provider_internals() -> None:
    names = set(asdict(_now_playing_item())) | set(asdict(NowPlayingState()))

    for key in names:
        lowered = key.lower()
        assert "provider" not in lowered
        assert "backend" not in lowered
        assert "anchor" not in lowered


def test_now_playing_service_has_no_provider_network_filesystem_or_playback_dependency() -> None:
    members = dict(inspect.getmembers(NowPlayingService))
    forbidden = (
        "provider",
        "media_source",
        "request_stream",
        "stream",
        "requests",
        "httpx",
        "aiohttp",
        "socket",
        "walk",
        "sc" + "andir",
        "start_playback",
        "execute_playback",
        "pause_playback",
        "seek_to",
        "skip_to",
        "offline",
        "cache",
        "smart_playlist",
    )

    for name in members:
        assert all(term not in name.lower() for term in forbidden)


def test_now_playing_module_exports_bloco_12_names_intentionally() -> None:
    expected = {
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
    }

    assert set(now_playing.__all__) == expected
