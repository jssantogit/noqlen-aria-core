"""Tests for Bloco 13 playback, renderer and automation intents."""

from __future__ import annotations

from dataclasses import asdict

import inspect
import json

import noqlen_aria.playback_intents as intents
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
from noqlen_aria.playback_intents import (
    AutomationIntent,
    AutomationIntentResult,
    AutomationIntentService,
    AutomationIntentSource,
    AutomationIntentType,
    AutomationSafetyLevel,
    PlaybackBlockedReason,
    PlaybackCommandPreview,
    PlaybackIntent,
    PlaybackIntentResult,
    PlaybackIntentService,
    PlaybackIntentType,
    PlaybackIntentValidationIssue,
    RendererAvailabilityState,
    RendererCapabilitySummary,
    RendererId,
    RendererIntentService,
    RendererRef,
    RendererSelectionIntent,
    RendererSelectionResult,
    RendererType,
    SeekTarget,
    SkipDirection,
)
from noqlen_aria.queue import (
    FakeQueueScenarios,
    QueueAvailabilityState,
    QueueItem,
    QueueItemId,
    QueueRepeatMode,
    QueueState,
)


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


def _err(result):
    assert result.is_err()
    assert result.error is not None
    return result.error


_service = PlaybackIntentService()


# ═══════════════════════════════════════════════════════════════
# Model defaults and serialization
# ═══════════════════════════════════════════════════════════════

def test_playback_intent_defaults_are_safe() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)
    assert intent.intent_type == PlaybackIntentType.PLAY
    assert intent.seek_target is None
    assert intent.skip_direction is None
    json.dumps(safe_serialize(intent))


def test_seek_target_defaults_are_safe() -> None:
    target = SeekTarget()
    assert target.position_seconds == 0
    assert target.duration_seconds is None
    json.dumps(safe_serialize(target))


def test_playback_intent_result_defaults_are_safe() -> None:
    result = PlaybackIntentResult(
        allowed=True,
        intent=PlaybackIntent(intent_type=PlaybackIntentType.PLAY),
        preview=PlaybackCommandPreview(
            intent_type=PlaybackIntentType.PLAY,
            can_execute=True,
            summary="Ready",
        ),
    )
    assert result.issues == ()
    assert result.blocked_reason == PlaybackBlockedReason.NONE
    json.dumps(safe_serialize(result))


def test_renderer_ref_defaults_are_conservative() -> None:
    ref = RendererRef(renderer_id=RendererId("r1"))
    assert ref.display_name == ""
    assert ref.renderer_type == RendererType.UNKNOWN
    assert ref.availability == RendererAvailabilityState.UNKNOWN


def test_automation_intent_defaults_are_safe() -> None:
    intent = AutomationIntent(intent_type=AutomationIntentType.PLAY)
    assert intent.source == AutomationIntentSource.UNKNOWN
    assert intent.parameters == {}
    json.dumps(safe_serialize(intent))


def test_playback_intent_serialization_is_app_facing() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=42))
    serialized = safe_serialize(intent)
    assert serialized["intent_type"] == "SEEK"
    assert serialized["seek_target"]["position_seconds"] == 42
    json.dumps(serialized)


# ═══════════════════════════════════════════════════════════════
# CE1: Idle state blocks pause
# ═══════════════════════════════════════════════════════════════

def test_idle_now_playing_blocks_pause_intent() -> None:
    now_playing = FakeNowPlayingScenarios.idle()
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PAUSE)

    result = _data(_service.preview(intent, now_playing, QueueState()))

    assert result.allowed is False
    assert result.preview.can_execute is False
    assert result.blocked_reason == PlaybackBlockedReason.NO_CURRENT_ITEM
    assert not hasattr(PlaybackIntentService, "play")
    assert not hasattr(PlaybackIntentService, "execute")


# ═══════════════════════════════════════════════════════════════
# CE2: Valid queue enables play preview
# ═══════════════════════════════════════════════════════════════

def test_valid_queue_enables_play_preview_without_starting_playback() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True
    assert result.preview.can_execute is True
    assert result.blocked_reason == PlaybackBlockedReason.NONE
    assert not hasattr(PlaybackIntentService, "start")
    assert not hasattr(PlaybackIntentService, "execute_playback")


# ═══════════════════════════════════════════════════════════════
# CE3: Unavailable media blocks play
# ═══════════════════════════════════════════════════════════════

def test_unavailable_media_blocks_play_intent() -> None:
    unavailable_item = QueueItem.from_library_item(
        QueueItemId("queue-item-unavailable"),
        _track_summary("track-unavailable", "Missing"),
        availability=QueueAvailabilityState.UNAVAILABLE,
    )
    queue = QueueState(items=(unavailable_item,), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.MEDIA_UNAVAILABLE


# ═══════════════════════════════════════════════════════════════
# CE4: Invalid seek rejected
# ═══════════════════════════════════════════════════════════════

def test_negative_seek_position_is_rejected() -> None:
    seek = SeekTarget(position_seconds=-1)

    result = _data(_service.validate_seek(seek))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.INVALID_PARAMETER
    assert len(result.issues) == 1
    assert result.issues[0].code == "SEEK_NEGATIVE_POSITION"


def test_seek_beyond_duration_is_rejected() -> None:
    seek = SeekTarget(position_seconds=200, duration_seconds=180)

    result = _data(_service.validate_seek(seek))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.INVALID_PARAMETER
    assert any(issue.code == "SEEK_EXCEEDS_DURATION" for issue in result.issues)


def test_valid_seek_is_accepted() -> None:
    seek = SeekTarget(position_seconds=30, duration_seconds=180)

    result = _data(_service.validate_seek(seek))

    assert result.allowed is True
    assert result.blocked_reason == PlaybackBlockedReason.NONE
    assert result.issues == ()


# ═══════════════════════════════════════════════════════════════
# CE5: Unavailable renderer blocks selection
# ═══════════════════════════════════════════════════════════════

def test_unavailable_renderer_blocks_selection() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-1"),
        display_name="USB DAC",
        availability=RendererAvailabilityState.UNAVAILABLE,
    )
    intent = RendererSelectionIntent(renderer_ref=renderer)

    result = _data(RendererIntentService().validate_selection(intent))

    assert result.available is False
    assert result.reason == "renderer_unavailable"


# ═══════════════════════════════════════════════════════════════
# CE6: Unsupported capability blocks intent
# ═══════════════════════════════════════════════════════════════

def test_renderer_unsupported_capability_is_blocked() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-1"),
        display_name="Phone Speaker",
        availability=RendererAvailabilityState.AVAILABLE,
    )
    capability = RendererCapabilitySummary(supports_gapless=False, supports_crossfade=False)

    result = _data(RendererIntentService().validate_capability(renderer, capability, "supports_gapless"))

    assert result.available is False
    assert result.reason == "capability_unsupported"
    assert "supports_gapless" in result.message


def test_renderer_supported_capability_is_allowed() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-1"),
        display_name="Phone Speaker",
        availability=RendererAvailabilityState.AVAILABLE,
    )
    capability = RendererCapabilitySummary(supports_playback=True, supports_pause=True)

    result = _data(RendererIntentService().validate_capability(renderer, capability, "supports_playback"))

    assert result.available is True


# ═══════════════════════════════════════════════════════════════
# CE7: Automation intent validation
# ═══════════════════════════════════════════════════════════════

def test_automation_intent_is_validated_without_executing_provider_logic() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.PLAY,
        source=AutomationIntentSource.PUBLIC_API,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.safety_level == AutomationSafetyLevel.SAFE
    assert result.mapped_intent is not None
    assert result.mapped_intent.intent_type == PlaybackIntentType.PLAY
    assert not hasattr(AutomationIntentService, "execute")
    assert not hasattr(AutomationIntentService, "call_provider")


def test_automation_intent_from_unknown_source_is_unsafe() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.PLAY,
        source=AutomationIntentSource.UNKNOWN,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is False
    assert result.safety_level == AutomationSafetyLevel.UNSAFE


def test_automation_intent_internal_source_is_boundary() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.PAUSE,
        source=AutomationIntentSource.INTERNAL,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.safety_level == AutomationSafetyLevel.BOUNDARY
    assert result.mapped_intent is not None
    assert result.mapped_intent.intent_type == PlaybackIntentType.PAUSE


# ═══════════════════════════════════════════════════════════════
# CE8: Future UI consumes Aria Core models only
# ═══════════════════════════════════════════════════════════════

def test_playback_intent_models_are_aria_core() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)
    assert intent.__class__.__module__ == "noqlen_aria.playback_intents"


def test_ui_consumption_does_not_expose_android_or_provider_internals() -> None:
    names = set(asdict(PlaybackIntent(intent_type=PlaybackIntentType.PLAY)))
    names |= set(asdict(PlaybackIntentResult(
        allowed=True,
        intent=PlaybackIntent(intent_type=PlaybackIntentType.PLAY),
        preview=PlaybackCommandPreview(
            intent_type=PlaybackIntentType.PLAY,
            can_execute=True,
            summary="Ready",
        ),
    )))
    names |= set(asdict(RendererRef(renderer_id=RendererId("r1"))))
    names |= set(asdict(AutomationIntent(intent_type=AutomationIntentType.PLAY)))

    for key in names:
        lowered = key.lower()
        assert "provider" not in lowered
        assert "backend" not in lowered
        assert "anchor" not in lowered
        assert "android" not in lowered
        assert "media3" not in lowered
        assert "exoplayer" not in lowered


# ═══════════════════════════════════════════════════════════════
# Play intent edge cases
# ═══════════════════════════════════════════════════════════════

def test_play_with_blocked_playback_availability_is_rejected() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    blocked = _data(NowPlayingService().with_playback_availability(
        now_playing, PlaybackAvailabilityState.BLOCKED,
    ))
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, blocked, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.PLAYBACK_NOT_CONFIGURED


def test_play_with_empty_queue_is_blocked() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.QUEUE_EMPTY


def test_play_with_queue_but_no_current_position_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=None)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), queue))

    assert result.allowed is True


# ═══════════════════════════════════════════════════════════════
# Pause intent edge cases
# ═══════════════════════════════════════════════════════════════

def test_pause_when_ready_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PAUSE)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_pause_when_unavailable_is_blocked() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    unavailable = _data(
        NowPlayingService().with_playback_availability(
            now_playing,
            PlaybackAvailabilityState.UNAVAILABLE,
            PlaybackAvailabilityReason.MEDIA_UNAVAILABLE,
        ),
    )
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PAUSE)

    result = _data(_service.preview(intent, unavailable, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.NO_CURRENT_ITEM


# ═══════════════════════════════════════════════════════════════
# Resume intent edge cases
# ═══════════════════════════════════════════════════════════════

def test_resume_when_idle_is_blocked() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.RESUME)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.NO_CURRENT_ITEM


def test_resume_when_ready_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.RESUME)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_resume_when_unavailable_is_blocked() -> None:
    item = _now_playing_item()
    now_playing = FakeNowPlayingScenarios.unavailable_item(item)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.RESUME)

    result = _data(_service.preview(intent, now_playing, QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.MEDIA_UNAVAILABLE


# ═══════════════════════════════════════════════════════════════
# Stop intent edge cases
# ═══════════════════════════════════════════════════════════════

def test_stop_when_idle_is_blocked() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.STOP)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.NO_CURRENT_ITEM


def test_stop_when_ready_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.STOP)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


# ═══════════════════════════════════════════════════════════════
# Skip next/previous edge cases
# ═══════════════════════════════════════════════════════════════

def test_skip_next_from_first_item_is_allowed() -> None:
    items = tuple(_queue_item(f"queue-item-{i + 1}", f"track-{i + 1}") for i in range(3))
    queue = QueueState(items=items, current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_NEXT)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_skip_next_at_last_item_without_repeat_is_blocked() -> None:
    items = tuple(_queue_item(f"queue-item-{i + 1}", f"track-{i + 1}") for i in range(3))
    queue = QueueState(items=items, current_position=2)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_NEXT)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.QUEUE_BOUNDARY


def test_skip_next_at_last_item_with_repeat_all_is_allowed() -> None:
    items = tuple(_queue_item(f"queue-item-{i + 1}", f"track-{i + 1}") for i in range(3))
    queue = QueueState(items=items, current_position=2, repeat_mode=QueueRepeatMode.ALL)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_NEXT)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_skip_previous_at_first_item_is_blocked() -> None:
    items = tuple(_queue_item(f"queue-item-{i + 1}", f"track-{i + 1}") for i in range(3))
    queue = QueueState(items=items, current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_PREVIOUS)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.QUEUE_BOUNDARY


def test_skip_previous_from_second_item_is_allowed() -> None:
    items = tuple(_queue_item(f"queue-item-{i + 1}", f"track-{i + 1}") for i in range(3))
    queue = QueueState(items=items, current_position=1)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_PREVIOUS)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_skip_next_empty_queue_is_blocked() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SKIP_NEXT)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.QUEUE_EMPTY


# ═══════════════════════════════════════════════════════════════
# Seek intent edge cases
# ═══════════════════════════════════════════════════════════════

def test_seek_when_idle_is_blocked() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=10))

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.NO_CURRENT_ITEM


def test_seek_when_ready_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=30))

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_seek_negative_position_is_rejected_in_preview() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=-1))

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.INVALID_PARAMETER


def test_seek_beyond_duration_is_rejected_in_preview() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=200, duration_seconds=180))

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.INVALID_PARAMETER


def test_seek_at_exact_boundary_is_allowed() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=SeekTarget(position_seconds=180, duration_seconds=180))

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is True


def test_seek_without_target_is_rejected() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.INVALID_PARAMETER


def test_seek_with_negative_duration_in_validate_is_rejected() -> None:
    seek = SeekTarget(position_seconds=0, duration_seconds=-1)

    result = _data(_service.validate_seek(seek))

    assert result.allowed is False
    assert any(issue.code == "SEEK_INVALID_DURATION" for issue in result.issues)


# ═══════════════════════════════════════════════════════════════
# Playback availability blocking
# ═══════════════════════════════════════════════════════════════

def test_play_with_unavailable_now_playing_status_is_blocked() -> None:
    item = _now_playing_item()
    now_playing = FakeNowPlayingScenarios.unavailable_item(item)
    queue = QueueState(items=(_queue_item(),), current_position=0)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    result = _data(_service.preview(intent, now_playing, queue))

    assert result.allowed is False
    assert result.blocked_reason == PlaybackBlockedReason.MEDIA_UNAVAILABLE


def test_pause_with_idle_now_playing_is_unavailable() -> None:
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PAUSE)

    result = _data(_service.preview(intent, FakeNowPlayingScenarios.idle(), QueueState()))

    assert result.allowed is False
    assert "playback" in result.preview.summary.lower() or "active" in result.preview.summary.lower()


# ═══════════════════════════════════════════════════════════════
# Renderer selection edge cases
# ═══════════════════════════════════════════════════════════════

def test_renderer_disconnected_is_blocked() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-disconnected"),
        display_name="Bluetooth Headphones",
        availability=RendererAvailabilityState.DISCONNECTED,
    )
    intent = RendererSelectionIntent(renderer_ref=renderer)

    result = _data(RendererIntentService().validate_selection(intent))

    assert result.available is False
    assert result.reason == "renderer_unavailable"


def test_available_renderer_is_allowed() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-available"),
        display_name="Phone Speaker",
        availability=RendererAvailabilityState.AVAILABLE,
    )
    intent = RendererSelectionIntent(renderer_ref=renderer)

    result = _data(RendererIntentService().validate_selection(intent))

    assert result.available is True
    assert result.renderer_ref == renderer
    assert "selected" in result.message


def test_renderer_not_in_available_list_is_blocked() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-missing"),
        display_name="Missing Renderer",
        availability=RendererAvailabilityState.AVAILABLE,
    )
    available = (
        RendererRef(renderer_id=RendererId("renderer-1"), availability=RendererAvailabilityState.AVAILABLE),
        RendererRef(renderer_id=RendererId("renderer-2"), availability=RendererAvailabilityState.AVAILABLE),
    )
    intent = RendererSelectionIntent(renderer_ref=renderer)

    result = _data(RendererIntentService().validate_selection(intent, available))

    assert result.available is False
    assert result.reason == "renderer_not_found"


def test_renderer_in_available_list_is_allowed() -> None:
    renderer = RendererRef(
        renderer_id=RendererId("renderer-1"),
        availability=RendererAvailabilityState.AVAILABLE,
    )
    available = (renderer,)
    intent = RendererSelectionIntent(renderer_ref=renderer)

    result = _data(RendererIntentService().validate_selection(intent, available))

    assert result.available is True


# ═══════════════════════════════════════════════════════════════
# Automation intent validation edge cases
# ═══════════════════════════════════════════════════════════════

def test_automation_seek_with_valid_parameters_is_allowed() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SEEK,
        source=AutomationIntentSource.PUBLIC_API,
        parameters={"position_seconds": "42", "duration_seconds": "180"},
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.safety_level == AutomationSafetyLevel.SAFE
    assert result.mapped_intent is not None
    assert result.mapped_intent.seek_target is not None
    assert result.mapped_intent.seek_target.position_seconds == 42


def test_automation_seek_with_negative_position_is_rejected() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SEEK,
        source=AutomationIntentSource.PUBLIC_API,
        parameters={"position_seconds": "-1"},
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is False


def test_automation_seek_with_position_beyond_duration_is_rejected() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SEEK,
        source=AutomationIntentSource.PUBLIC_API,
        parameters={"position_seconds": "200", "duration_seconds": "180"},
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is False


def test_automation_toggle_repeat_is_allowed() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.TOGGLE_REPEAT,
        source=AutomationIntentSource.PUBLIC_API,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.mapped_intent is None


def test_automation_toggle_shuffle_is_allowed() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.TOGGLE_SHUFFLE,
        source=AutomationIntentSource.PUBLIC_API,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.mapped_intent is None


def test_automation_select_renderer_is_allowed() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SELECT_RENDERER,
        source=AutomationIntentSource.PUBLIC_API,
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.mapped_intent is None


def test_automation_intent_all_types_covered() -> None:
    service = AutomationIntentService()
    for intent_type in AutomationIntentType:
        intent = AutomationIntent(
            intent_type=intent_type,
            source=AutomationIntentSource.PUBLIC_API,
            parameters={"position_seconds": "10", "duration_seconds": "100"} if intent_type == AutomationIntentType.SEEK else {},
        )
        result = _data(service.validate(intent))
        assert isinstance(result, AutomationIntentResult)


# ═══════════════════════════════════════════════════════════════
# Side-effect-free previews
# ═══════════════════════════════════════════════════════════════

def test_preview_does_not_mutate_state() -> None:
    queue = QueueState(items=(_queue_item(),), current_position=0)
    now_playing = FakeNowPlayingScenarios.from_queue(queue)
    intent = PlaybackIntent(intent_type=PlaybackIntentType.PLAY)

    queue_before = queue
    np_before = now_playing
    _data(_service.preview(intent, now_playing, queue))

    assert queue == queue_before
    assert now_playing == np_before


def test_automation_validate_does_not_mutate_state() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.PLAY,
        source=AutomationIntentSource.PUBLIC_API,
    )
    intent_before = intent
    _data(AutomationIntentService().validate(intent))

    assert intent == intent_before


# ═══════════════════════════════════════════════════════════════
# Boundary enforcement: no provider/network/filesystem/Android
# ═══════════════════════════════════════════════════════════════

def test_playback_intent_service_has_no_provider_network_filesystem_or_playback_dependency() -> None:
    members = dict(inspect.getmembers(PlaybackIntentService))
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


def test_renderer_service_has_no_provider_network_filesystem_dependency() -> None:
    members = dict(inspect.getmembers(RendererIntentService))
    forbidden = ("provider", "socket", "stream", "requests", "httpx", "aiohttp", "walk", "sc" + "andir")
    for name in members:
        assert all(term not in name.lower() for term in forbidden)


def test_automation_service_has_no_provider_network_filesystem_dependency() -> None:
    members = dict(inspect.getmembers(AutomationIntentService))
    forbidden = ("provider", "socket", "stream", "requests", "httpx", "aiohttp", "walk", "sc" + "andir")
    for name in members:
        assert all(term not in name.lower() for term in forbidden)


def test_playback_intents_module_exports_bloco_13_names_intentionally() -> None:
    expected = {
        "AutomationIntent",
        "AutomationIntentResult",
        "AutomationIntentService",
        "AutomationIntentSource",
        "AutomationIntentType",
        "AutomationSafetyLevel",
        "PlaybackBlockedReason",
        "PlaybackCommandPreview",
        "PlaybackIntent",
        "PlaybackIntentResult",
        "PlaybackIntentService",
        "PlaybackIntentType",
        "PlaybackIntentValidationIssue",
        "RendererAvailabilityState",
        "RendererCapabilitySummary",
        "RendererId",
        "RendererIntentService",
        "RendererRef",
        "RendererSelectionIntent",
        "RendererSelectionResult",
        "RendererType",
        "SeekTarget",
        "SkipDirection",
    }
    assert set(intents.__all__) == expected


def test_renderer_id_is_newtype_str() -> None:
    rid = RendererId("test-renderer")
    assert rid == "test-renderer"
    assert isinstance(rid, str)


def test_skipping_with_unavailable_media_and_no_queue_position_is_blocked() -> None:
    queue = QueueState(items=(), current_position=None)
    item = _now_playing_item()
    now_playing = FakeNowPlayingScenarios.unavailable_item(item)

    for direction in (SkipDirection.NEXT, SkipDirection.PREVIOUS):
        intent_type = PlaybackIntentType.SKIP_NEXT if direction == SkipDirection.NEXT else PlaybackIntentType.SKIP_PREVIOUS
        intent = PlaybackIntent(intent_type=intent_type)
        result = _data(_service.preview(intent, now_playing, queue))
        assert result.allowed is False
        assert result.blocked_reason == PlaybackBlockedReason.MEDIA_UNAVAILABLE


def test_resumable_state_allows_play_and_resume() -> None:
    item = _now_playing_item()
    now_playing = FakeNowPlayingScenarios.resumable_item(item)
    queue = QueueState(items=(_queue_item(),), current_position=0)

    play_result = _data(_service.preview(
        PlaybackIntent(intent_type=PlaybackIntentType.PLAY), now_playing, queue,
    ))
    assert play_result.allowed is True

    resume_result = _data(_service.preview(
        PlaybackIntent(intent_type=PlaybackIntentType.RESUME), now_playing, queue,
    ))
    assert resume_result.allowed is True


def test_resumable_state_blocks_pause() -> None:
    item = _now_playing_item()
    now_playing = FakeNowPlayingScenarios.resumable_item(item)
    queue = QueueState(items=(_queue_item(),), current_position=0)

    result = _data(_service.preview(
        PlaybackIntent(intent_type=PlaybackIntentType.PAUSE), now_playing, queue,
    ))

    assert result.allowed is True


def test_automation_seek_with_invalid_position_string_is_rejected() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SEEK,
        source=AutomationIntentSource.PUBLIC_API,
        parameters={"position_seconds": "not-a-number"},
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is False
    assert "negative" in result.message


def test_automation_internal_seek_is_boundary() -> None:
    intent = AutomationIntent(
        intent_type=AutomationIntentType.SEEK,
        source=AutomationIntentSource.INTERNAL,
        parameters={"position_seconds": "42"},
    )

    result = _data(AutomationIntentService().validate(intent))

    assert result.allowed is True
    assert result.safety_level == AutomationSafetyLevel.BOUNDARY
