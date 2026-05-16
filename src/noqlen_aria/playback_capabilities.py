"""Aria Core playback capability and audio output readiness models.

Bloco 17 — Playback Capability Models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning


class PlaybackCapabilityUnavailableReason(Enum):
    NONE = auto()
    SOURCE_UNSUPPORTED = auto()
    ROUTE_UNSUPPORTED = auto()
    METADATA_MISSING = auto()
    NOT_REQUESTED = auto()
    NON_EXCLUSIVE_OUTPUT = auto()
    UNSUPPORTED_SAMPLE_RATE = auto()
    UNSUPPORTED_BIT_DEPTH = auto()
    UNSUPPORTED_FORMAT = auto()
    ROUTE_UNAVAILABLE = auto()
    DEVICE_UNAVAILABLE = auto()
    EXCLUSIVE_OUTPUT_UNAVAILABLE = auto()
    BIT_PERFECT_UNSUPPORTED = auto()
    SIGNAL_PROCESSING_DISABLED = auto()
    INVALID_FADE_TIMING = auto()
    INVALID_DECLARATION = auto()


class AudioOutputBlockedReason(Enum):
    NONE = auto()
    ROUTE_UNAVAILABLE = auto()
    ROUTE_DEGRADED = auto()
    DEVICE_UNAVAILABLE = auto()
    DEVICE_DEGRADED = auto()
    NON_EXCLUSIVE_OUTPUT = auto()
    EXCLUSIVE_OUTPUT_UNAVAILABLE = auto()
    USB_DAC_UNAVAILABLE = auto()
    UNSUPPORTED_SAMPLE_RATE = auto()
    UNSUPPORTED_BIT_DEPTH = auto()
    UNSUPPORTED_FORMAT = auto()
    INVALID_DECLARATION = auto()


class AudioOutputRouteType(Enum):
    UNKNOWN = auto()
    SYSTEM_AUDIO = auto()
    USB_DAC = auto()
    BLUETOOTH = auto()
    REMOTE_RENDERER = auto()
    UNAVAILABLE = auto()


class PlaybackQualityPreference(Enum):
    AUTOMATIC = auto()
    DATA_SAVER = auto()
    BALANCED = auto()
    HIGH_QUALITY = auto()
    BIT_PERFECT = auto()


class FadeMode(Enum):
    FADE_IN = auto()
    FADE_OUT = auto()
    FADE_IN_OUT = auto()


class FadeAvailabilityState(Enum):
    AVAILABLE = auto()
    UNAVAILABLE = auto()
    DEGRADED = auto()
    NOT_REQUESTED = auto()


class FadeUnavailableReason(Enum):
    NONE = auto()
    NOT_REQUESTED = auto()
    SOURCE_UNSUPPORTED = auto()
    ROUTE_UNSUPPORTED = auto()
    SIGNAL_PROCESSING_DISABLED = auto()
    INVALID_TIMING = auto()


@dataclass(frozen=True)
class PlaybackCapabilityWarning:
    code: str
    message: str


@dataclass(frozen=True)
class GaplessCapabilityState:
    available: bool = False
    source_supported: bool = False
    route_supported: bool = False
    reason: PlaybackCapabilityUnavailableReason = PlaybackCapabilityUnavailableReason.SOURCE_UNSUPPORTED
    summary: str = "Capability state only; no audio was played"


@dataclass(frozen=True)
class LoudnessNormalizationCapabilityState:
    available: bool = False
    metadata_present: bool = False
    reason: PlaybackCapabilityUnavailableReason = PlaybackCapabilityUnavailableReason.METADATA_MISSING
    summary: str = "Metadata awareness only; no gain was applied"


@dataclass(frozen=True)
class ReplayGainAwarenessState:
    aware: bool = False
    metadata_present: bool = False
    track_gain_present: bool = False
    album_gain_present: bool = False
    summary: str = "ReplayGain metadata awareness only; no gain was applied"


@dataclass(frozen=True)
class CrossfadeCapabilityState:
    available: bool = False
    requested: bool = False
    source_supported: bool = False
    route_supported: bool = False
    reason: PlaybackCapabilityUnavailableReason = PlaybackCapabilityUnavailableReason.NOT_REQUESTED
    summary: str = "Capability state only; no crossfade was performed"


@dataclass(frozen=True)
class FadeTimingPreference:
    fade_in_ms: int = 0
    fade_out_ms: int = 0


@dataclass(frozen=True)
class FadeCapabilityState:
    mode: FadeMode = FadeMode.FADE_IN_OUT
    availability: FadeAvailabilityState = FadeAvailabilityState.NOT_REQUESTED
    requested: bool = False
    source_supported: bool = False
    route_supported: bool = False
    timing: FadeTimingPreference = field(default_factory=FadeTimingPreference)
    reason: FadeUnavailableReason = FadeUnavailableReason.NOT_REQUESTED
    summary: str = "Fade capability state only; no fade processing was performed"


@dataclass(frozen=True)
class SampleRateSupport:
    supported_rates_hz: frozenset[int] = frozenset()
    unknown: bool = False

    def supports(self, sample_rate_hz: int | None) -> bool:
        if sample_rate_hz is None or self.unknown or not self.supported_rates_hz:
            return True
        return sample_rate_hz in self.supported_rates_hz


@dataclass(frozen=True)
class BitDepthSupport:
    supported_bits: frozenset[int] = frozenset()
    unknown: bool = False

    def supports(self, bit_depth: int | None) -> bool:
        if bit_depth is None or self.unknown or not self.supported_bits:
            return True
        return bit_depth in self.supported_bits


@dataclass(frozen=True)
class AudioFormatSupport:
    supported_formats: frozenset[str] = frozenset()
    unknown: bool = False

    def supports(self, audio_format: str) -> bool:
        if not audio_format or self.unknown or not self.supported_formats:
            return True
        return audio_format.lower() in {item.lower() for item in self.supported_formats}


@dataclass(frozen=True)
class UsbDacCapabilityState:
    available: bool = False
    degraded: bool = False
    reason: AudioOutputBlockedReason = AudioOutputBlockedReason.NONE
    summary: str = "USB DAC capability is declared state only; no device was controlled"


@dataclass(frozen=True)
class ExclusiveOutputCapabilityState:
    available: bool = False
    degraded: bool = False
    reason: AudioOutputBlockedReason = AudioOutputBlockedReason.EXCLUSIVE_OUTPUT_UNAVAILABLE
    summary: str = "Exclusive output capability is declared state only; no driver was invoked"


@dataclass(frozen=True)
class AudioOutputRouteState:
    route_type: AudioOutputRouteType = AudioOutputRouteType.UNKNOWN
    available: bool = False
    degraded: bool = False
    supports_gapless: bool = False
    supports_crossfade: bool = False
    supports_fade: bool = False
    supports_bit_perfect: bool = False
    sample_rate_support: SampleRateSupport = field(default_factory=SampleRateSupport)
    bit_depth_support: BitDepthSupport = field(default_factory=BitDepthSupport)
    format_support: AudioFormatSupport = field(default_factory=AudioFormatSupport)
    usb_dac: UsbDacCapabilityState = field(default_factory=UsbDacCapabilityState)
    exclusive_output: ExclusiveOutputCapabilityState = field(default_factory=ExclusiveOutputCapabilityState)


@dataclass(frozen=True)
class AudioOutputDeviceState:
    available: bool = False
    degraded: bool = False
    sample_rate_support: SampleRateSupport = field(default_factory=SampleRateSupport)
    bit_depth_support: BitDepthSupport = field(default_factory=BitDepthSupport)
    format_support: AudioFormatSupport = field(default_factory=AudioFormatSupport)
    summary: str = "Device capability is declared state only"


@dataclass(frozen=True)
class AudioOutputReadinessState:
    ready: bool = False
    degraded: bool = False
    blocked_reason: AudioOutputBlockedReason = AudioOutputBlockedReason.ROUTE_UNAVAILABLE
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    summary: str = "Output readiness is state only; no audio output was opened"


@dataclass(frozen=True)
class BitPerfectCapabilityState:
    available: bool = False
    desired: bool = False
    degraded: bool = False
    reason: PlaybackCapabilityUnavailableReason = PlaybackCapabilityUnavailableReason.NOT_REQUESTED
    sample_rate_hz: int | None = None
    bit_depth: int | None = None
    audio_format: str = ""
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    summary: str = "Bit-perfect readiness state only; no output was controlled"


@dataclass(frozen=True)
class PlaybackCapabilitySummary:
    gapless: GaplessCapabilityState = field(default_factory=GaplessCapabilityState)
    loudness_normalization: LoudnessNormalizationCapabilityState = field(default_factory=LoudnessNormalizationCapabilityState)
    replay_gain: ReplayGainAwarenessState = field(default_factory=ReplayGainAwarenessState)
    crossfade: CrossfadeCapabilityState = field(default_factory=CrossfadeCapabilityState)
    fade: FadeCapabilityState = field(default_factory=FadeCapabilityState)
    bit_perfect: BitPerfectCapabilityState = field(default_factory=BitPerfectCapabilityState)
    quality_preference: PlaybackQualityPreference = PlaybackQualityPreference.AUTOMATIC
    warnings: tuple[PlaybackCapabilityWarning, ...] = field(default_factory=tuple)
    summary: str = "Playback capability summary only; no playback was started"


class AudioOutputCapabilityService:
    """Evaluate output readiness from caller-provided declarations only."""

    def check_format_support(
        self,
        *,
        route: AudioOutputRouteState | None = None,
        device: AudioOutputDeviceState | None = None,
        sample_rate_hz: int | None = None,
        bit_depth: int | None = None,
        audio_format: str = "",
    ) -> AriaResult[AudioOutputReadinessState]:
        invalid = self._validate_format(sample_rate_hz, bit_depth, audio_format)
        if invalid is not None:
            return invalid
        route = route or AudioOutputRouteState()
        device = device or AudioOutputDeviceState()
        route_reason = self._first_support_block(route, sample_rate_hz, bit_depth, audio_format)
        device_reason = self._first_support_block(device, sample_rate_hz, bit_depth, audio_format)
        reason = route_reason or device_reason
        if reason is not None:
            return self._readiness(False, True, reason)
        return self.evaluate_output_readiness(route=route, device=device)

    def evaluate_output_readiness(
        self,
        *,
        route: AudioOutputRouteState | None = None,
        device: AudioOutputDeviceState | None = None,
    ) -> AriaResult[AudioOutputReadinessState]:
        route = route or AudioOutputRouteState()
        device = device or AudioOutputDeviceState()
        invalid = self._validate_declared_support(route, device)
        if invalid is not None:
            return invalid
        if not route.available or route.route_type == AudioOutputRouteType.UNAVAILABLE:
            return self._readiness(False, False, AudioOutputBlockedReason.ROUTE_UNAVAILABLE)
        if route.route_type == AudioOutputRouteType.USB_DAC and not route.usb_dac.available:
            return self._readiness(False, route.usb_dac.degraded, AudioOutputBlockedReason.USB_DAC_UNAVAILABLE)
        if not device.available:
            return self._readiness(False, False, AudioOutputBlockedReason.DEVICE_UNAVAILABLE)
        if route.degraded:
            return self._readiness(True, True, AudioOutputBlockedReason.ROUTE_DEGRADED)
        if device.degraded:
            return self._readiness(True, True, AudioOutputBlockedReason.DEVICE_DEGRADED)
        return self._readiness(True, False, AudioOutputBlockedReason.NONE)

    def evaluate_bit_perfect_readiness(
        self,
        *,
        desired: bool,
        route: AudioOutputRouteState | None = None,
        device: AudioOutputDeviceState | None = None,
        sample_rate_hz: int | None = None,
        bit_depth: int | None = None,
        audio_format: str = "",
    ) -> AriaResult[BitPerfectCapabilityState]:
        invalid = self._validate_format(sample_rate_hz, bit_depth, audio_format)
        if invalid is not None:
            return AriaResult(ok=False, error=invalid.error)
        if not desired:
            return AriaResult(ok=True, data=BitPerfectCapabilityState(desired=False))
        route = route or AudioOutputRouteState()
        device = device or AudioOutputDeviceState()
        output = self.evaluate_output_readiness(route=route, device=device)
        if output.is_err():
            return AriaResult(ok=False, error=output.error)
        if output.data is not None and not output.data.ready:
            return self._bit_perfect(False, True, self._playback_reason(output.data.blocked_reason), sample_rate_hz, bit_depth, audio_format, output.data.warnings)
        if not route.supports_bit_perfect:
            return self._bit_perfect(False, True, PlaybackCapabilityUnavailableReason.BIT_PERFECT_UNSUPPORTED, sample_rate_hz, bit_depth, audio_format)
        if not route.exclusive_output.available:
            return self._bit_perfect(False, True, PlaybackCapabilityUnavailableReason.EXCLUSIVE_OUTPUT_UNAVAILABLE, sample_rate_hz, bit_depth, audio_format)
        if route.route_type == AudioOutputRouteType.SYSTEM_AUDIO:
            return self._bit_perfect(False, True, PlaybackCapabilityUnavailableReason.NON_EXCLUSIVE_OUTPUT, sample_rate_hz, bit_depth, audio_format)
        route_reason = self._first_support_block(route, sample_rate_hz, bit_depth, audio_format)
        device_reason = self._first_support_block(device, sample_rate_hz, bit_depth, audio_format)
        reason = route_reason or device_reason
        if reason is not None:
            return self._bit_perfect(False, True, self._playback_reason(reason), sample_rate_hz, bit_depth, audio_format)
        degraded = bool(output.data and output.data.degraded) or route.exclusive_output.degraded
        return self._bit_perfect(True, degraded, PlaybackCapabilityUnavailableReason.NONE, sample_rate_hz, bit_depth, audio_format)

    def _first_support_block(
        self,
        output: AudioOutputRouteState | AudioOutputDeviceState,
        sample_rate_hz: int | None,
        bit_depth: int | None,
        audio_format: str,
    ) -> AudioOutputBlockedReason | None:
        if not output.sample_rate_support.supports(sample_rate_hz):
            return AudioOutputBlockedReason.UNSUPPORTED_SAMPLE_RATE
        if not output.bit_depth_support.supports(bit_depth):
            return AudioOutputBlockedReason.UNSUPPORTED_BIT_DEPTH
        if not output.format_support.supports(audio_format):
            return AudioOutputBlockedReason.UNSUPPORTED_FORMAT
        return None

    def _validate_declared_support(
        self,
        route: AudioOutputRouteState,
        device: AudioOutputDeviceState,
    ) -> AriaResult[AudioOutputReadinessState] | None:
        for sample_rate in route.sample_rate_support.supported_rates_hz | device.sample_rate_support.supported_rates_hz:
            if sample_rate <= 0:
                return self._invalid("INVALID_SAMPLE_RATE", "Sample rates must be positive")
        for bit_depth in route.bit_depth_support.supported_bits | device.bit_depth_support.supported_bits:
            if bit_depth <= 0:
                return self._invalid("INVALID_BIT_DEPTH", "Bit depths must be positive")
        return None

    def _validate_format(
        self,
        sample_rate_hz: int | None,
        bit_depth: int | None,
        audio_format: str,
    ) -> AriaResult[AudioOutputReadinessState] | None:
        if sample_rate_hz is not None and sample_rate_hz <= 0:
            return self._invalid("INVALID_SAMPLE_RATE", "Sample rate must be positive")
        if bit_depth is not None and bit_depth <= 0:
            return self._invalid("INVALID_BIT_DEPTH", "Bit depth must be positive")
        if "\n" in audio_format or "\r" in audio_format:
            return self._invalid("INVALID_FORMAT", "Audio format must be single-line text")
        return None

    def _invalid(self, code: str, message: str) -> AriaResult[AudioOutputReadinessState]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))

    def _readiness(
        self,
        ready: bool,
        degraded: bool,
        reason: AudioOutputBlockedReason,
    ) -> AriaResult[AudioOutputReadinessState]:
        warnings = ()
        if reason != AudioOutputBlockedReason.NONE:
            warnings = (AriaWarning(code=reason.name, message="Output readiness is limited by declared state"),)
        return AriaResult(
            ok=True,
            data=AudioOutputReadinessState(
                ready=ready,
                degraded=degraded,
                blocked_reason=reason,
                warnings=warnings,
            ),
        )

    def _bit_perfect(
        self,
        available: bool,
        degraded: bool,
        reason: PlaybackCapabilityUnavailableReason,
        sample_rate_hz: int | None,
        bit_depth: int | None,
        audio_format: str,
        warnings: tuple[AriaWarning, ...] = (),
    ) -> AriaResult[BitPerfectCapabilityState]:
        if reason != PlaybackCapabilityUnavailableReason.NONE and not warnings:
            warnings = (AriaWarning(code=reason.name, message="Bit-perfect readiness is limited by declared state"),)
        return AriaResult(
            ok=True,
            data=BitPerfectCapabilityState(
                available=available,
                desired=True,
                degraded=degraded,
                reason=reason,
                sample_rate_hz=sample_rate_hz,
                bit_depth=bit_depth,
                audio_format=audio_format,
                warnings=warnings,
            ),
        )

    def _playback_reason(self, reason: AudioOutputBlockedReason) -> PlaybackCapabilityUnavailableReason:
        mapping = {
            AudioOutputBlockedReason.ROUTE_UNAVAILABLE: PlaybackCapabilityUnavailableReason.ROUTE_UNAVAILABLE,
            AudioOutputBlockedReason.DEVICE_UNAVAILABLE: PlaybackCapabilityUnavailableReason.DEVICE_UNAVAILABLE,
            AudioOutputBlockedReason.NON_EXCLUSIVE_OUTPUT: PlaybackCapabilityUnavailableReason.NON_EXCLUSIVE_OUTPUT,
            AudioOutputBlockedReason.EXCLUSIVE_OUTPUT_UNAVAILABLE: PlaybackCapabilityUnavailableReason.EXCLUSIVE_OUTPUT_UNAVAILABLE,
            AudioOutputBlockedReason.UNSUPPORTED_SAMPLE_RATE: PlaybackCapabilityUnavailableReason.UNSUPPORTED_SAMPLE_RATE,
            AudioOutputBlockedReason.UNSUPPORTED_BIT_DEPTH: PlaybackCapabilityUnavailableReason.UNSUPPORTED_BIT_DEPTH,
            AudioOutputBlockedReason.UNSUPPORTED_FORMAT: PlaybackCapabilityUnavailableReason.UNSUPPORTED_FORMAT,
        }
        return mapping.get(reason, PlaybackCapabilityUnavailableReason.INVALID_DECLARATION)


class PlaybackCapabilityService:
    """Evaluate playback capability state without performing playback."""

    def evaluate_gapless(self, *, source_supported: bool, route_supported: bool) -> AriaResult[GaplessCapabilityState]:
        if source_supported and route_supported:
            return AriaResult(ok=True, data=GaplessCapabilityState(True, True, True, PlaybackCapabilityUnavailableReason.NONE))
        reason = PlaybackCapabilityUnavailableReason.SOURCE_UNSUPPORTED
        if source_supported and not route_supported:
            reason = PlaybackCapabilityUnavailableReason.ROUTE_UNSUPPORTED
        return AriaResult(ok=True, data=GaplessCapabilityState(False, source_supported, route_supported, reason))

    def evaluate_loudness(self, *, metadata_present: bool) -> AriaResult[LoudnessNormalizationCapabilityState]:
        if metadata_present:
            return AriaResult(ok=True, data=LoudnessNormalizationCapabilityState(True, True, PlaybackCapabilityUnavailableReason.NONE))
        return AriaResult(ok=True, data=LoudnessNormalizationCapabilityState())

    def evaluate_replay_gain(
        self,
        *,
        track_gain_present: bool = False,
        album_gain_present: bool = False,
    ) -> AriaResult[ReplayGainAwarenessState]:
        metadata_present = track_gain_present or album_gain_present
        return AriaResult(
            ok=True,
            data=ReplayGainAwarenessState(
                aware=metadata_present,
                metadata_present=metadata_present,
                track_gain_present=track_gain_present,
                album_gain_present=album_gain_present,
            ),
        )

    def evaluate_crossfade(
        self,
        *,
        requested: bool,
        source_supported: bool,
        route_supported: bool,
        signal_processing_allowed: bool = True,
    ) -> AriaResult[CrossfadeCapabilityState]:
        if not requested:
            return AriaResult(ok=True, data=CrossfadeCapabilityState(requested=False, source_supported=source_supported, route_supported=route_supported))
        if not signal_processing_allowed:
            return AriaResult(
                ok=True,
                data=CrossfadeCapabilityState(
                    False,
                    True,
                    source_supported,
                    route_supported,
                    PlaybackCapabilityUnavailableReason.SIGNAL_PROCESSING_DISABLED,
                ),
            )
        if source_supported and route_supported:
            return AriaResult(ok=True, data=CrossfadeCapabilityState(True, True, True, True, PlaybackCapabilityUnavailableReason.NONE))
        reason = PlaybackCapabilityUnavailableReason.SOURCE_UNSUPPORTED
        if source_supported and not route_supported:
            reason = PlaybackCapabilityUnavailableReason.ROUTE_UNSUPPORTED
        return AriaResult(ok=True, data=CrossfadeCapabilityState(False, True, source_supported, route_supported, reason))

    def evaluate_fade(
        self,
        *,
        mode: FadeMode = FadeMode.FADE_IN_OUT,
        requested: bool,
        source_supported: bool,
        route_supported: bool,
        timing: FadeTimingPreference | None = None,
        signal_processing_allowed: bool = True,
    ) -> AriaResult[FadeCapabilityState]:
        timing = timing or FadeTimingPreference()
        if timing.fade_in_ms < 0 or timing.fade_out_ms < 0:
            return AriaResult(
                ok=False,
                error=AriaError(code="INVALID_FADE_TIMING", message="Fade timing values must not be negative"),
            )
        if not requested:
            return AriaResult(
                ok=True,
                data=FadeCapabilityState(
                    mode=mode,
                    requested=False,
                    source_supported=source_supported,
                    route_supported=route_supported,
                    timing=timing,
                ),
            )
        if not signal_processing_allowed:
            return AriaResult(
                ok=True,
                data=FadeCapabilityState(
                    mode=mode,
                    availability=FadeAvailabilityState.UNAVAILABLE,
                    requested=True,
                    source_supported=source_supported,
                    route_supported=route_supported,
                    timing=timing,
                    reason=FadeUnavailableReason.SIGNAL_PROCESSING_DISABLED,
                ),
            )
        if source_supported and route_supported:
            return AriaResult(
                ok=True,
                data=FadeCapabilityState(
                    mode=mode,
                    availability=FadeAvailabilityState.AVAILABLE,
                    requested=True,
                    source_supported=True,
                    route_supported=True,
                    timing=timing,
                    reason=FadeUnavailableReason.NONE,
                ),
            )
        reason = FadeUnavailableReason.SOURCE_UNSUPPORTED
        if source_supported and not route_supported:
            reason = FadeUnavailableReason.ROUTE_UNSUPPORTED
        return AriaResult(
            ok=True,
            data=FadeCapabilityState(
                mode=mode,
                availability=FadeAvailabilityState.UNAVAILABLE,
                requested=True,
                source_supported=source_supported,
                route_supported=route_supported,
                timing=timing,
                reason=reason,
            ),
        )

    def map_quality_preference(
        self,
        preference: PlaybackQualityPreference,
        *,
        bit_perfect_available: bool = False,
    ) -> AriaResult[PlaybackQualityPreference]:
        if preference == PlaybackQualityPreference.AUTOMATIC:
            mapped = PlaybackQualityPreference.HIGH_QUALITY if bit_perfect_available else PlaybackQualityPreference.BALANCED
            return AriaResult(ok=True, data=mapped)
        if preference == PlaybackQualityPreference.BIT_PERFECT and not bit_perfect_available:
            return AriaResult(ok=True, data=PlaybackQualityPreference.HIGH_QUALITY)
        return AriaResult(ok=True, data=preference)

    def build_summary(
        self,
        *,
        gapless: GaplessCapabilityState | None = None,
        loudness: LoudnessNormalizationCapabilityState | None = None,
        replay_gain: ReplayGainAwarenessState | None = None,
        crossfade: CrossfadeCapabilityState | None = None,
        fade: FadeCapabilityState | None = None,
        bit_perfect: BitPerfectCapabilityState | None = None,
        quality_preference: PlaybackQualityPreference = PlaybackQualityPreference.AUTOMATIC,
    ) -> AriaResult[PlaybackCapabilitySummary]:
        gapless = gapless or GaplessCapabilityState()
        loudness = loudness or LoudnessNormalizationCapabilityState()
        replay_gain = replay_gain or ReplayGainAwarenessState()
        crossfade = crossfade or CrossfadeCapabilityState()
        fade = fade or FadeCapabilityState()
        bit_perfect = bit_perfect or BitPerfectCapabilityState()
        warnings = []
        if not gapless.available:
            warnings.append(PlaybackCapabilityWarning("GAPLESS_UNAVAILABLE", gapless.reason.name))
        if crossfade.requested and not crossfade.available:
            warnings.append(PlaybackCapabilityWarning("CROSSFADE_UNAVAILABLE", crossfade.reason.name))
        if fade.requested and fade.availability != FadeAvailabilityState.AVAILABLE:
            warnings.append(PlaybackCapabilityWarning("FADE_UNAVAILABLE", fade.reason.name))
        if bit_perfect.desired and not bit_perfect.available:
            warnings.append(PlaybackCapabilityWarning("BIT_PERFECT_UNAVAILABLE", bit_perfect.reason.name))
        return AriaResult(
            ok=True,
            data=PlaybackCapabilitySummary(
                gapless=gapless,
                loudness_normalization=loudness,
                replay_gain=replay_gain,
                crossfade=crossfade,
                fade=fade,
                bit_perfect=bit_perfect,
                quality_preference=quality_preference,
                warnings=tuple(warnings),
            ),
        )


class FakePlaybackCapabilityScenarios:
    """Deterministic local scenarios for capability/readiness tests."""

    @staticmethod
    def normal_system_audio_route() -> AudioOutputRouteState:
        return AudioOutputRouteState(
            route_type=AudioOutputRouteType.SYSTEM_AUDIO,
            available=True,
            supports_gapless=True,
            supports_crossfade=True,
            supports_fade=True,
            supports_bit_perfect=False,
            sample_rate_support=SampleRateSupport(frozenset({44100, 48000})),
            bit_depth_support=BitDepthSupport(frozenset({16, 24})),
            format_support=AudioFormatSupport(frozenset({"flac", "mp3", "aac"})),
            exclusive_output=ExclusiveOutputCapabilityState(False),
        )

    @staticmethod
    def usb_dac_route() -> AudioOutputRouteState:
        return AudioOutputRouteState(
            route_type=AudioOutputRouteType.USB_DAC,
            available=True,
            supports_gapless=True,
            supports_crossfade=False,
            supports_fade=True,
            supports_bit_perfect=True,
            sample_rate_support=SampleRateSupport(frozenset({44100, 48000, 96000})),
            bit_depth_support=BitDepthSupport(frozenset({16, 24})),
            format_support=AudioFormatSupport(frozenset({"flac", "wav", "pcm"})),
            usb_dac=UsbDacCapabilityState(True),
            exclusive_output=ExclusiveOutputCapabilityState(True, False, AudioOutputBlockedReason.NONE),
        )

    @staticmethod
    def exclusive_output_unavailable_route() -> AudioOutputRouteState:
        route = FakePlaybackCapabilityScenarios.usb_dac_route()
        return AudioOutputRouteState(
            route_type=route.route_type,
            available=route.available,
            supports_gapless=route.supports_gapless,
            supports_crossfade=route.supports_crossfade,
            supports_fade=route.supports_fade,
            supports_bit_perfect=route.supports_bit_perfect,
            sample_rate_support=route.sample_rate_support,
            bit_depth_support=route.bit_depth_support,
            format_support=route.format_support,
            usb_dac=route.usb_dac,
            exclusive_output=ExclusiveOutputCapabilityState(False),
        )

    @staticmethod
    def available_device() -> AudioOutputDeviceState:
        return AudioOutputDeviceState(
            available=True,
            sample_rate_support=SampleRateSupport(frozenset({44100, 48000, 96000})),
            bit_depth_support=BitDepthSupport(frozenset({16, 24})),
            format_support=AudioFormatSupport(frozenset({"flac", "wav", "pcm", "mp3"})),
        )

    @staticmethod
    def degraded_route() -> AudioOutputRouteState:
        route = FakePlaybackCapabilityScenarios.normal_system_audio_route()
        return AudioOutputRouteState(route_type=route.route_type, available=True, degraded=True)

    @staticmethod
    def unavailable_route() -> AudioOutputRouteState:
        return AudioOutputRouteState(route_type=AudioOutputRouteType.UNAVAILABLE, available=False)


__all__ = [
    "AudioFormatSupport",
    "AudioOutputBlockedReason",
    "AudioOutputCapabilityService",
    "AudioOutputDeviceState",
    "AudioOutputReadinessState",
    "AudioOutputRouteState",
    "AudioOutputRouteType",
    "BitDepthSupport",
    "BitPerfectCapabilityState",
    "CrossfadeCapabilityState",
    "ExclusiveOutputCapabilityState",
    "FadeAvailabilityState",
    "FadeCapabilityState",
    "FadeMode",
    "FadeTimingPreference",
    "FadeUnavailableReason",
    "FakePlaybackCapabilityScenarios",
    "GaplessCapabilityState",
    "LoudnessNormalizationCapabilityState",
    "PlaybackCapabilityService",
    "PlaybackCapabilitySummary",
    "PlaybackCapabilityUnavailableReason",
    "PlaybackCapabilityWarning",
    "PlaybackQualityPreference",
    "ReplayGainAwarenessState",
    "SampleRateSupport",
    "UsbDacCapabilityState",
]
