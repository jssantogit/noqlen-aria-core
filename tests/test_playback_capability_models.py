"""Tests for Bloco 17 playback capability models."""

from __future__ import annotations

import inspect
import json

import noqlen_aria.playback_capabilities as playback_capabilities
from noqlen_aria import safe_serialize
from noqlen_aria.playback_capabilities import (
    AudioFormatSupport,
    AudioOutputBlockedReason,
    AudioOutputCapabilityService,
    AudioOutputDeviceState,
    AudioOutputRouteState,
    AudioOutputRouteType,
    BitDepthSupport,
    ExclusiveOutputCapabilityState,
    FadeAvailabilityState,
    FadeMode,
    FadeTimingPreference,
    FadeUnavailableReason,
    FakePlaybackCapabilityScenarios,
    PlaybackCapabilityService,
    PlaybackCapabilityUnavailableReason,
    PlaybackQualityPreference,
    SampleRateSupport,
    UsbDacCapabilityState,
)


def _playback_service() -> PlaybackCapabilityService:
    return PlaybackCapabilityService()


def _output_service() -> AudioOutputCapabilityService:
    return AudioOutputCapabilityService()


def test_gapless_available_when_source_and_route_support_without_playing_audio() -> None:
    gapless = _playback_service().evaluate_gapless(source_supported=True, route_supported=True).data
    route = FakePlaybackCapabilityScenarios.usb_dac_route()
    bit_perfect = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=route,
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=96000,
        bit_depth=24,
        audio_format="flac",
    ).data
    summary = _playback_service().build_summary(gapless=gapless, bit_perfect=bit_perfect).data

    assert summary is not None
    assert summary.gapless.available
    assert "no playback was started" in summary.summary


def test_gapless_unavailable_has_safe_reason() -> None:
    result = _playback_service().evaluate_gapless(source_supported=True, route_supported=False)

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.reason == PlaybackCapabilityUnavailableReason.ROUTE_UNSUPPORTED


def test_loudness_and_replay_gain_awareness_never_apply_gain() -> None:
    loudness = _playback_service().evaluate_loudness(metadata_present=True).data
    replay_gain = _playback_service().evaluate_replay_gain(track_gain_present=True).data
    missing = _playback_service().evaluate_replay_gain().data

    assert loudness is not None
    assert loudness.available
    assert "no gain was applied" in loudness.summary
    assert replay_gain is not None
    assert replay_gain.aware
    assert missing is not None
    assert not missing.aware


def test_crossfade_available_and_unavailable_behaviors_are_state_only() -> None:
    available = _playback_service().evaluate_crossfade(
        requested=True,
        source_supported=True,
        route_supported=True,
    ).data
    unavailable = _playback_service().evaluate_crossfade(
        requested=True,
        source_supported=True,
        route_supported=False,
    ).data

    assert available is not None
    assert available.available
    assert unavailable is not None
    assert not unavailable.available
    assert unavailable.reason == PlaybackCapabilityUnavailableReason.ROUTE_UNSUPPORTED
    assert "no crossfade was performed" in unavailable.summary


def test_fade_in_and_fade_out_available_behaviors_are_state_only() -> None:
    fade_in = _playback_service().evaluate_fade(
        mode=FadeMode.FADE_IN,
        requested=True,
        source_supported=True,
        route_supported=True,
        timing=FadeTimingPreference(fade_in_ms=1500),
    ).data
    fade_out = _playback_service().evaluate_fade(
        mode=FadeMode.FADE_OUT,
        requested=True,
        source_supported=True,
        route_supported=True,
        timing=FadeTimingPreference(fade_out_ms=2000),
    ).data

    assert fade_in is not None
    assert fade_in.availability == FadeAvailabilityState.AVAILABLE
    assert fade_in.timing.fade_in_ms == 1500
    assert "no fade processing" in fade_in.summary
    assert fade_out is not None
    assert fade_out.availability == FadeAvailabilityState.AVAILABLE
    assert fade_out.timing.fade_out_ms == 2000


def test_fade_unavailable_and_invalid_timing_behavior() -> None:
    unavailable = _playback_service().evaluate_fade(
        requested=True,
        source_supported=True,
        route_supported=False,
        timing=FadeTimingPreference(fade_in_ms=500, fade_out_ms=500),
    ).data
    invalid = _playback_service().evaluate_fade(
        requested=True,
        source_supported=True,
        route_supported=True,
        timing=FadeTimingPreference(fade_in_ms=-1),
    )

    assert unavailable is not None
    assert unavailable.availability == FadeAvailabilityState.UNAVAILABLE
    assert unavailable.reason == FadeUnavailableReason.ROUTE_UNSUPPORTED
    assert invalid.is_err()
    assert invalid.error is not None
    assert invalid.error.code == "INVALID_FADE_TIMING"


def test_bit_perfect_preference_blocks_fade_and_crossfade_signal_processing() -> None:
    crossfade = _playback_service().evaluate_crossfade(
        requested=True,
        source_supported=True,
        route_supported=True,
        signal_processing_allowed=False,
    ).data
    fade = _playback_service().evaluate_fade(
        requested=True,
        source_supported=True,
        route_supported=True,
        timing=FadeTimingPreference(fade_in_ms=1000, fade_out_ms=1000),
        signal_processing_allowed=False,
    ).data

    assert crossfade is not None
    assert not crossfade.available
    assert crossfade.reason == PlaybackCapabilityUnavailableReason.SIGNAL_PROCESSING_DISABLED
    assert fade is not None
    assert fade.availability == FadeAvailabilityState.UNAVAILABLE
    assert fade.reason == FadeUnavailableReason.SIGNAL_PROCESSING_DISABLED


def test_bit_perfect_available_for_declared_usb_dac_exclusive_route() -> None:
    result = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=FakePlaybackCapabilityScenarios.usb_dac_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=96000,
        bit_depth=24,
        audio_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert result.data.available
    assert result.data.reason == PlaybackCapabilityUnavailableReason.NONE
    assert "no output was controlled" in result.data.summary


def test_bit_perfect_blocked_by_system_audio_non_exclusive_route() -> None:
    result = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=FakePlaybackCapabilityScenarios.normal_system_audio_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=48000,
        bit_depth=24,
        audio_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.degraded
    assert result.data.reason == PlaybackCapabilityUnavailableReason.BIT_PERFECT_UNSUPPORTED
    assert result.data.warnings


def test_bit_perfect_blocked_by_unsupported_sample_rate() -> None:
    result = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=FakePlaybackCapabilityScenarios.usb_dac_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=192000,
        bit_depth=24,
        audio_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.reason == PlaybackCapabilityUnavailableReason.UNSUPPORTED_SAMPLE_RATE


def test_bit_perfect_blocked_by_unsupported_bit_depth() -> None:
    result = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=FakePlaybackCapabilityScenarios.usb_dac_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=96000,
        bit_depth=32,
        audio_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.reason == PlaybackCapabilityUnavailableReason.UNSUPPORTED_BIT_DEPTH


def test_usb_dac_capability_state_and_compatible_format_support() -> None:
    route = FakePlaybackCapabilityScenarios.usb_dac_route()
    result = _output_service().check_format_support(
        route=route,
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=96000,
        bit_depth=24,
        audio_format="flac",
    )

    assert route.route_type == AudioOutputRouteType.USB_DAC
    assert route.usb_dac.available
    assert result.ok
    assert result.data is not None
    assert result.data.ready
    assert result.data.blocked_reason == AudioOutputBlockedReason.NONE


def test_exclusive_output_unavailable_degrades_bit_perfect_readiness() -> None:
    result = _output_service().evaluate_bit_perfect_readiness(
        desired=True,
        route=FakePlaybackCapabilityScenarios.exclusive_output_unavailable_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
        sample_rate_hz=96000,
        bit_depth=24,
        audio_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.degraded
    assert result.data.reason == PlaybackCapabilityUnavailableReason.EXCLUSIVE_OUTPUT_UNAVAILABLE


def test_sample_rate_and_bit_depth_support_matching() -> None:
    sample_rates = SampleRateSupport(frozenset({44100, 96000}))
    bit_depths = BitDepthSupport(frozenset({16, 24}))
    formats = AudioFormatSupport(frozenset({"flac"}))

    assert sample_rates.supports(96000)
    assert not sample_rates.supports(192000)
    assert bit_depths.supports(24)
    assert not bit_depths.supports(32)
    assert formats.supports("FLAC")
    assert not formats.supports("mp3")


def test_output_device_readiness_degraded_and_unavailable() -> None:
    degraded = _output_service().evaluate_output_readiness(
        route=FakePlaybackCapabilityScenarios.degraded_route(),
        device=AudioOutputDeviceState(available=True),
    ).data
    unavailable = _output_service().evaluate_output_readiness(
        route=FakePlaybackCapabilityScenarios.unavailable_route(),
        device=FakePlaybackCapabilityScenarios.available_device(),
    ).data
    unavailable_device = _output_service().evaluate_output_readiness(
        route=FakePlaybackCapabilityScenarios.normal_system_audio_route(),
        device=AudioOutputDeviceState(available=False),
    ).data

    assert degraded is not None
    assert degraded.ready
    assert degraded.degraded
    assert degraded.blocked_reason == AudioOutputBlockedReason.ROUTE_DEGRADED
    assert unavailable is not None
    assert not unavailable.ready
    assert unavailable.blocked_reason == AudioOutputBlockedReason.ROUTE_UNAVAILABLE
    assert unavailable_device is not None
    assert unavailable_device.blocked_reason == AudioOutputBlockedReason.DEVICE_UNAVAILABLE


def test_playback_quality_preference_mapping() -> None:
    service = _playback_service()

    assert service.map_quality_preference(PlaybackQualityPreference.AUTOMATIC, bit_perfect_available=True).data == PlaybackQualityPreference.HIGH_QUALITY
    assert service.map_quality_preference(PlaybackQualityPreference.AUTOMATIC, bit_perfect_available=False).data == PlaybackQualityPreference.BALANCED
    assert service.map_quality_preference(PlaybackQualityPreference.BIT_PERFECT, bit_perfect_available=False).data == PlaybackQualityPreference.HIGH_QUALITY
    assert service.map_quality_preference(PlaybackQualityPreference.DATA_SAVER).data == PlaybackQualityPreference.DATA_SAVER


def test_invalid_declared_values_return_safe_errors() -> None:
    service = _output_service()
    invalid_rate = service.check_format_support(sample_rate_hz=-1)
    invalid_depth = service.evaluate_bit_perfect_readiness(desired=True, bit_depth=-1)
    invalid_declared_rate = service.evaluate_output_readiness(
        route=AudioOutputRouteState(available=True, sample_rate_support=SampleRateSupport(frozenset({0}))),
        device=AudioOutputDeviceState(available=True),
    )

    assert invalid_rate.is_err()
    assert invalid_rate.error is not None
    assert invalid_rate.error.code == "INVALID_SAMPLE_RATE"
    assert invalid_depth.is_err()
    assert invalid_depth.error is not None
    assert invalid_depth.error.code == "INVALID_BIT_DEPTH"
    assert invalid_declared_rate.is_err()


def test_summary_and_serialization_are_deterministic() -> None:
    summary = _playback_service().build_summary(
        gapless=_playback_service().evaluate_gapless(source_supported=False, route_supported=True).data,
        crossfade=_playback_service().evaluate_crossfade(requested=True, source_supported=True, route_supported=False).data,
        fade=_playback_service().evaluate_fade(requested=True, source_supported=True, route_supported=False).data,
    ).data

    serialized = safe_serialize(summary)

    assert serialized["gapless"]["available"] is False
    assert serialized["crossfade"]["reason"] == "ROUTE_UNSUPPORTED"
    assert serialized["fade"]["reason"] == "ROUTE_UNSUPPORTED"
    assert serialized["warnings"]
    json.dumps(serialized)


def test_fake_scenarios_cover_declared_capability_states() -> None:
    system_route = FakePlaybackCapabilityScenarios.normal_system_audio_route()
    usb_route = FakePlaybackCapabilityScenarios.usb_dac_route()
    exclusive_unavailable = FakePlaybackCapabilityScenarios.exclusive_output_unavailable_route()

    assert system_route.route_type == AudioOutputRouteType.SYSTEM_AUDIO
    assert not system_route.exclusive_output.available
    assert usb_route.usb_dac == UsbDacCapabilityState(True)
    assert usb_route.exclusive_output == ExclusiveOutputCapabilityState(True, False, AudioOutputBlockedReason.NONE)
    assert not exclusive_unavailable.exclusive_output.available


def test_playback_capability_module_exports_are_intentional() -> None:
    assert set(playback_capabilities.__all__) == {
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
    }


def test_module_has_no_real_playback_or_platform_integration_imports() -> None:
    source = inspect.getsource(playback_capabilities)
    forbidden = (
        "requests" + ".",
        "httpx" + ".",
        "aiohttp" + ".",
        "urllib" + ".",
        "socket" + ".",
        "Media" + "3",
        "Exo" + "Player",
        "Media" + "Session",
        "android" + ".",
        "JNI",
        "NDK",
        "AA" + "udio",
        "Ob" + "oe",
        "Usb" + "Manager",
        "Audio" + "Track",
        "Audio" + "Manager",
        "os" + ".walk",
        "glob" + ".glob",
        "scandir",
        "/dev/snd",
        "/proc/asound",
        "subprocess",
        "open(",
    )

    assert not any(term in source for term in forbidden)
