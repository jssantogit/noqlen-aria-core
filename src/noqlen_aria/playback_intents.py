"""Aria Core playback, renderer and automation intent models and deterministic local services.

Bloco 13 — Playback, Renderer and Automation Intents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType

from noqlen_aria.contracts import AriaError, AriaResult
from noqlen_aria.now_playing import (
    NowPlayingState,
    NowPlayingStatus,
    PlaybackAvailabilityReason,
    PlaybackAvailabilityState,
    PlaybackPositionSnapshot,
)
from noqlen_aria.queue import QueueAvailabilityState, QueueItem, QueueRepeatMode, QueueState

# ── Playback intent types ─────────────────────────────────────

class PlaybackIntentType(Enum):
    PLAY = auto()
    PAUSE = auto()
    RESUME = auto()
    STOP = auto()
    SKIP_NEXT = auto()
    SKIP_PREVIOUS = auto()
    SEEK = auto()


class PlaybackBlockedReason(Enum):
    NONE = auto()
    PLAYBACK_NOT_CONFIGURED = auto()
    NO_CURRENT_ITEM = auto()
    MEDIA_UNAVAILABLE = auto()
    SOURCE_UNAVAILABLE = auto()
    QUEUE_EMPTY = auto()
    QUEUE_BOUNDARY = auto()
    INVALID_PARAMETER = auto()
    UNKNOWN = auto()


class SkipDirection(Enum):
    NEXT = auto()
    PREVIOUS = auto()


@dataclass(frozen=True)
class SeekTarget:
    position_seconds: int = 0
    duration_seconds: int | None = None


@dataclass(frozen=True)
class PlaybackIntent:
    intent_type: PlaybackIntentType
    seek_target: SeekTarget | None = None
    skip_direction: SkipDirection | None = None


@dataclass(frozen=True)
class PlaybackIntentValidationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PlaybackCommandPreview:
    intent_type: PlaybackIntentType
    can_execute: bool
    summary: str = ""
    blocked_reason: PlaybackBlockedReason = PlaybackBlockedReason.NONE


@dataclass(frozen=True)
class PlaybackIntentResult:
    allowed: bool
    intent: PlaybackIntent
    preview: PlaybackCommandPreview
    blocked_reason: PlaybackBlockedReason = PlaybackBlockedReason.NONE
    issues: tuple[PlaybackIntentValidationIssue, ...] = field(default_factory=tuple)


# ── Renderer intent types ─────────────────────────────────────

RendererId = NewType("RendererId", str)


class RendererType(Enum):
    PHONE = auto()
    USB_DAC = auto()
    BLUETOOTH = auto()
    REMOTE = auto()
    UNKNOWN = auto()


class RendererAvailabilityState(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    DISCONNECTED = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class RendererRef:
    renderer_id: RendererId
    display_name: str = ""
    renderer_type: RendererType = RendererType.UNKNOWN
    availability: RendererAvailabilityState = RendererAvailabilityState.UNKNOWN


@dataclass(frozen=True)
class RendererCapabilitySummary:
    supports_playback: bool = True
    supports_pause: bool = True
    supports_seek: bool = True
    supports_gapless: bool = False
    supports_crossfade: bool = False
    supports_remote_control: bool = False


@dataclass(frozen=True)
class RendererSelectionIntent:
    renderer_ref: RendererRef
    reason: str = ""


@dataclass(frozen=True)
class RendererSelectionResult:
    available: bool
    renderer_ref: RendererRef | None = None
    reason: str = ""
    message: str = ""


# ── Automation intent types ───────────────────────────────────

class AutomationIntentType(Enum):
    PLAY = auto()
    PAUSE = auto()
    RESUME = auto()
    STOP = auto()
    SKIP_NEXT = auto()
    SKIP_PREVIOUS = auto()
    SEEK = auto()
    SELECT_RENDERER = auto()
    TOGGLE_REPEAT = auto()
    TOGGLE_SHUFFLE = auto()


class AutomationIntentSource(Enum):
    PUBLIC_API = auto()
    INTERNAL = auto()
    UNKNOWN = auto()


class AutomationSafetyLevel(Enum):
    SAFE = auto()
    BOUNDARY = auto()
    UNSAFE = auto()


@dataclass(frozen=True)
class AutomationIntent:
    intent_type: AutomationIntentType
    source: AutomationIntentSource = AutomationIntentSource.UNKNOWN
    parameters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AutomationIntentResult:
    allowed: bool
    safety_level: AutomationSafetyLevel = AutomationSafetyLevel.UNSAFE
    message: str = ""
    mapped_intent: PlaybackIntent | None = None


# ── Playback Intent Service ───────────────────────────────────

class PlaybackIntentService:
    """Preview and validate playback intents without execution."""

    def preview(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
        queue: QueueState,
    ) -> AriaResult[PlaybackIntentResult]:
        if queue.current_position is None and intent.intent_type not in {PlaybackIntentType.PLAY, PlaybackIntentType.SKIP_NEXT, PlaybackIntentType.SKIP_PREVIOUS}:
            if now_playing.status == NowPlayingStatus.UNAVAILABLE:
                return self._preview_result(
                    intent,
                    False,
                    "Cannot perform intent: media is unavailable",
                    PlaybackBlockedReason.MEDIA_UNAVAILABLE,
                )
            return self._preview_result(
                intent,
                False,
                "No active playback for this intent",
                PlaybackBlockedReason.NO_CURRENT_ITEM,
            )

        if intent.intent_type == PlaybackIntentType.PLAY:
            return self._preview_play(intent, now_playing, queue)
        elif intent.intent_type == PlaybackIntentType.PAUSE:
            return self._preview_pause(intent, now_playing)
        elif intent.intent_type == PlaybackIntentType.RESUME:
            return self._preview_resume(intent, now_playing)
        elif intent.intent_type == PlaybackIntentType.STOP:
            return self._preview_stop(intent, now_playing)
        elif intent.intent_type == PlaybackIntentType.SKIP_NEXT:
            return self._preview_skip_next(intent, now_playing, queue)
        elif intent.intent_type == PlaybackIntentType.SKIP_PREVIOUS:
            return self._preview_skip_previous(intent, now_playing, queue)
        elif intent.intent_type == PlaybackIntentType.SEEK:
            return self._preview_seek(intent, now_playing)
        return self._preview_result(intent, False, "Unknown intent type", PlaybackBlockedReason.UNKNOWN)

    def _preview_play(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
        queue: QueueState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.playback_availability == PlaybackAvailabilityState.BLOCKED:
            return self._preview_result(
                intent, False, "Playback is blocked",
                PlaybackBlockedReason.PLAYBACK_NOT_CONFIGURED,
            )
        if now_playing.status in {NowPlayingStatus.UNAVAILABLE}:
            return self._preview_result(
                intent, False, "Current media is unavailable",
                PlaybackBlockedReason.MEDIA_UNAVAILABLE,
            )
        if not queue.items:
            return self._preview_result(
                intent, False, "Queue is empty",
                PlaybackBlockedReason.QUEUE_EMPTY,
            )
        if queue.current_position is None:
            return self._preview_result(
                intent, True, "Ready to play from first item",
            )
        current_item = queue.items[queue.current_position]
        if current_item.availability == QueueAvailabilityState.UNAVAILABLE:
            return self._preview_result(
                intent, False, "Current queue item is unavailable",
                PlaybackBlockedReason.MEDIA_UNAVAILABLE,
            )
        return self._preview_result(intent, True, "Ready to play")

    def _preview_pause(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status in {NowPlayingStatus.IDLE, NowPlayingStatus.UNAVAILABLE}:
            return self._preview_result(
                intent, False, "No active playback to pause",
                PlaybackBlockedReason.NO_CURRENT_ITEM,
            )
        return self._preview_result(intent, True, "Ready to pause")

    def _preview_resume(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status == NowPlayingStatus.IDLE:
            return self._preview_result(
                intent, False, "Nothing to resume",
                PlaybackBlockedReason.NO_CURRENT_ITEM,
            )
        if now_playing.status == NowPlayingStatus.UNAVAILABLE:
            return self._preview_result(
                intent, False, "Cannot resume unavailable media",
                PlaybackBlockedReason.MEDIA_UNAVAILABLE,
            )
        return self._preview_result(intent, True, "Ready to resume")

    def _preview_stop(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status in {NowPlayingStatus.IDLE, NowPlayingStatus.UNAVAILABLE}:
            return self._preview_result(
                intent, False, "No active playback to stop",
                PlaybackBlockedReason.NO_CURRENT_ITEM,
            )
        return self._preview_result(intent, True, "Ready to stop")

    def _preview_skip_next(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
        queue: QueueState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status == NowPlayingStatus.UNAVAILABLE and queue.current_position is None:
            return self._preview_result(
                intent, False, "Cannot skip: media unavailable and no queue position",
                PlaybackBlockedReason.MEDIA_UNAVAILABLE,
            )
        if not queue.items:
            return self._preview_result(
                intent, False, "Queue is empty",
                PlaybackBlockedReason.QUEUE_EMPTY,
            )
        current = queue.current_position if queue.current_position is not None else -1
        if current + 1 >= len(queue.items):
            if queue.repeat_mode != QueueRepeatMode.ALL:
                return self._preview_result(
                    intent, False, "Already at last item",
                    PlaybackBlockedReason.QUEUE_BOUNDARY,
                )
        return self._preview_result(intent, True, "Ready to skip next")

    def _preview_skip_previous(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
        queue: QueueState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status == NowPlayingStatus.UNAVAILABLE and queue.current_position is None:
            return self._preview_result(
                intent, False, "Cannot skip: media unavailable and no queue position",
                PlaybackBlockedReason.MEDIA_UNAVAILABLE,
            )
        if not queue.items:
            return self._preview_result(
                intent, False, "Queue is empty",
                PlaybackBlockedReason.QUEUE_EMPTY,
            )
        current = queue.current_position if queue.current_position is not None else 0
        if current <= 0:
            return self._preview_result(
                intent, False, "Already at first item",
                PlaybackBlockedReason.QUEUE_BOUNDARY,
            )
        return self._preview_result(intent, True, "Ready to skip previous")

    def _preview_seek(
        self,
        intent: PlaybackIntent,
        now_playing: NowPlayingState,
    ) -> AriaResult[PlaybackIntentResult]:
        if now_playing.status in {NowPlayingStatus.IDLE, NowPlayingStatus.UNAVAILABLE}:
            return self._preview_result(
                intent, False, "No active playback to seek within",
                PlaybackBlockedReason.NO_CURRENT_ITEM,
            )
        if intent.seek_target is None:
            return self._preview_result(
                intent, False, "Seek target is required",
                PlaybackBlockedReason.INVALID_PARAMETER,
            )
        target = intent.seek_target
        if target.position_seconds < 0:
            return self._preview_result(
                intent, False, "Seek position must not be negative",
                PlaybackBlockedReason.INVALID_PARAMETER,
            )
        if target.duration_seconds is not None and target.position_seconds > target.duration_seconds:
            return self._preview_result(
                intent, False, "Seek position exceeds known duration",
                PlaybackBlockedReason.INVALID_PARAMETER,
            )
        return self._preview_result(intent, True, "Ready to seek")

    def validate_seek(self, seek_target: SeekTarget) -> AriaResult[PlaybackIntentResult]:
        intent = PlaybackIntent(intent_type=PlaybackIntentType.SEEK, seek_target=seek_target)
        issues: list[PlaybackIntentValidationIssue] = []
        if seek_target.position_seconds < 0:
            issues.append(PlaybackIntentValidationIssue(
                code="SEEK_NEGATIVE_POSITION",
                message="Seek position must not be negative",
            ))
        if seek_target.duration_seconds is not None:
            if seek_target.duration_seconds < 0:
                issues.append(PlaybackIntentValidationIssue(
                    code="SEEK_INVALID_DURATION",
                    message="Duration must not be negative",
                ))
            elif seek_target.position_seconds > seek_target.duration_seconds:
                issues.append(PlaybackIntentValidationIssue(
                    code="SEEK_EXCEEDS_DURATION",
                    message="Seek position exceeds known duration",
                ))
        allowed = len(issues) == 0
        preview = PlaybackCommandPreview(
            intent_type=PlaybackIntentType.SEEK,
            can_execute=allowed,
            summary="Seek valid" if allowed else "Seek invalid",
            blocked_reason=PlaybackBlockedReason.NONE if allowed else PlaybackBlockedReason.INVALID_PARAMETER,
        )
        return self._ok(PlaybackIntentResult(
            allowed=allowed,
            intent=intent,
            preview=preview,
            blocked_reason=PlaybackBlockedReason.NONE if allowed else PlaybackBlockedReason.INVALID_PARAMETER,
            issues=tuple(issues),
        ))

    def _preview_result(
        self,
        intent: PlaybackIntent,
        allowed: bool,
        summary: str,
        blocked_reason: PlaybackBlockedReason = PlaybackBlockedReason.NONE,
    ) -> AriaResult[PlaybackIntentResult]:
        preview = PlaybackCommandPreview(
            intent_type=intent.intent_type,
            can_execute=allowed,
            summary=summary,
            blocked_reason=blocked_reason,
        )
        return self._ok(PlaybackIntentResult(
            allowed=allowed,
            intent=intent,
            preview=preview,
            blocked_reason=blocked_reason,
        ))

    def _ok(self, data: PlaybackIntentResult) -> AriaResult[PlaybackIntentResult]:
        return AriaResult(ok=True, data=data)

    def _err(self, code: str, message: str) -> AriaResult[PlaybackIntentResult]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


# ── Renderer Intent Service ───────────────────────────────────

class RendererIntentService:
    """Validate renderer selection without accessing real renderers."""

    def validate_selection(
        self,
        intent: RendererSelectionIntent,
        available_renderers: tuple[RendererRef, ...] | None = None,
    ) -> AriaResult[RendererSelectionResult]:
        renderer = intent.renderer_ref
        if renderer.availability in {RendererAvailabilityState.UNAVAILABLE, RendererAvailabilityState.DISCONNECTED}:
            return self._ok(RendererSelectionResult(
                available=False,
                renderer_ref=renderer,
                reason="renderer_unavailable",
                message=f"Renderer {renderer.display_name or renderer.renderer_id} is unavailable",
            ))
        if available_renderers is not None and renderer not in available_renderers:
            return self._ok(RendererSelectionResult(
                available=False,
                renderer_ref=renderer,
                reason="renderer_not_found",
                message=f"Renderer {renderer.display_name or renderer.renderer_id} not found in available renderers",
            ))
        return self._ok(RendererSelectionResult(
            available=True,
            renderer_ref=renderer,
            message=f"Renderer {renderer.display_name or renderer.renderer_id} selected",
        ))

    def validate_capability(
        self,
        renderer: RendererRef,
        capability: RendererCapabilitySummary,
        required: str,
    ) -> AriaResult[RendererSelectionResult]:
        supported = getattr(capability, required, None)
        if supported is None or not supported:
            return self._ok(RendererSelectionResult(
                available=False,
                renderer_ref=renderer,
                reason="capability_unsupported",
                message=f"Renderer does not support {required}",
            ))
        return self._ok(RendererSelectionResult(
            available=True,
            renderer_ref=renderer,
            message=f"Renderer supports {required}",
        ))

    def _ok(self, data: RendererSelectionResult) -> AriaResult[RendererSelectionResult]:
        return AriaResult(ok=True, data=data)

    def _err(self, code: str, message: str) -> AriaResult[RendererSelectionResult]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


# ── Automation Intent Service ─────────────────────────────────

class AutomationIntentService:
    """Validate automation intents and map to internal playback intents."""

    _AUTOMATION_TO_PLAYBACK = {
        AutomationIntentType.PLAY: PlaybackIntentType.PLAY,
        AutomationIntentType.PAUSE: PlaybackIntentType.PAUSE,
        AutomationIntentType.RESUME: PlaybackIntentType.RESUME,
        AutomationIntentType.STOP: PlaybackIntentType.STOP,
        AutomationIntentType.SKIP_NEXT: PlaybackIntentType.SKIP_NEXT,
        AutomationIntentType.SKIP_PREVIOUS: PlaybackIntentType.SKIP_PREVIOUS,
    }

    def validate(self, intent: AutomationIntent) -> AriaResult[AutomationIntentResult]:
        safety = self._classify_safety(intent.source)
        if safety == AutomationSafetyLevel.UNSAFE:
            return self._ok(AutomationIntentResult(
                allowed=False,
                safety_level=safety,
                message="Automation intent from unknown source is not allowed",
            ))
        if intent.intent_type == AutomationIntentType.SEEK:
            return self._validate_automation_seek(intent, safety)
        if intent.intent_type == AutomationIntentType.SELECT_RENDERER:
            return self._ok(AutomationIntentResult(
                allowed=True,
                safety_level=safety,
                message="Renderer selection intent accepted for further processing",
            ))
        if intent.intent_type in {AutomationIntentType.TOGGLE_REPEAT, AutomationIntentType.TOGGLE_SHUFFLE}:
            return self._ok(AutomationIntentResult(
                allowed=True,
                safety_level=safety,
                message=f"Automation intent {intent.intent_type.name} accepted",
            ))
        playback_type = self._AUTOMATION_TO_PLAYBACK.get(intent.intent_type)
        if playback_type is None:
            return self._ok(AutomationIntentResult(
                allowed=False,
                safety_level=safety,
                message=f"Automation intent type {intent.intent_type.name} is not mapped to a playback intent",
            ))
        mapped = PlaybackIntent(intent_type=playback_type)
        return self._ok(AutomationIntentResult(
            allowed=True,
            safety_level=safety,
            message=f"Automation intent {intent.intent_type.name} mapped to playback intent",
            mapped_intent=mapped,
        ))

    def _validate_automation_seek(
        self,
        intent: AutomationIntent,
        safety: AutomationSafetyLevel,
    ) -> AriaResult[AutomationIntentResult]:
        position_str = intent.parameters.get("position_seconds", "")
        duration_str = intent.parameters.get("duration_seconds", "")
        try:
            position = int(position_str)
        except (ValueError, TypeError):
            position = -1
        duration = None
        if duration_str:
            try:
                duration = int(duration_str)
            except (ValueError, TypeError):
                duration = None
        seek_target = SeekTarget(position_seconds=position, duration_seconds=duration)
        if position < 0:
            return self._ok(AutomationIntentResult(
                allowed=False,
                safety_level=safety,
                message="Automation seek position must not be negative",
                mapped_intent=PlaybackIntent(
                    intent_type=PlaybackIntentType.SEEK,
                    seek_target=seek_target,
                ),
            ))
        if duration is not None and position > duration:
            return self._ok(AutomationIntentResult(
                allowed=False,
                safety_level=safety,
                message="Automation seek position exceeds duration",
                mapped_intent=PlaybackIntent(
                    intent_type=PlaybackIntentType.SEEK,
                    seek_target=seek_target,
                ),
            ))
        return self._ok(AutomationIntentResult(
            allowed=True,
            safety_level=safety,
            message="Automation seek intent accepted",
            mapped_intent=PlaybackIntent(
                intent_type=PlaybackIntentType.SEEK,
                seek_target=seek_target,
            ),
        ))

    def _classify_safety(self, source: AutomationIntentSource) -> AutomationSafetyLevel:
        if source == AutomationIntentSource.PUBLIC_API:
            return AutomationSafetyLevel.SAFE
        if source == AutomationIntentSource.INTERNAL:
            return AutomationSafetyLevel.BOUNDARY
        return AutomationSafetyLevel.UNSAFE

    def _ok(self, data: AutomationIntentResult) -> AriaResult[AutomationIntentResult]:
        return AriaResult(ok=True, data=data)

    def _err(self, code: str, message: str) -> AriaResult[AutomationIntentResult]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


__all__ = [
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
]
