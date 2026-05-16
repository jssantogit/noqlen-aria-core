"""Tests for Bloco 16 stream quality, transcoding and network policy."""

from __future__ import annotations

import inspect
import json

import noqlen_aria.stream_quality as stream_quality
from noqlen_aria import safe_serialize
from noqlen_aria.stream_quality import (
    BandwidthBudget,
    BitrateLimit,
    FakeQualityPolicyScenarios,
    NetworkConditionSnapshot,
    NetworkPolicyReason,
    NetworkQualityLevel,
    NetworkQualityPolicyService,
    OfflineQualityPolicy,
    QualityFallbackPolicy,
    QualityPolicyService,
    StreamQualityPolicy,
    StreamQualityPreference,
    StreamQualityProfile,
    StreamQualityReason,
    TranscodingCapability,
    TranscodingDecision,
    TranscodingPolicy,
    TranscodingPolicyService,
    TranscodingPreference,
    TranscodingRequirement,
    TranscodingUnavailableReason,
)


def _quality_service() -> QualityPolicyService:
    return QualityPolicyService()


def test_high_quality_preference_with_sufficient_bandwidth_returns_high_without_stream() -> None:
    result = _quality_service().evaluate_stream_quality(
        FakeQualityPolicyScenarios.high_quality_with_sufficient_bandwidth()
    )

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.preference == StreamQualityPreference.HIGH
    assert result.data.reason == StreamQualityReason.PREFERRED_QUALITY
    assert "no stream was opened" in result.data.summary


def test_low_bandwidth_automatic_selects_safer_lower_quality() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(
            preference=StreamQualityPreference.AUTOMATIC,
            bandwidth_budget=BandwidthBudget(available_kbps=128),
        )
    )

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.preference == StreamQualityPreference.LOW
    assert result.data.reason == StreamQualityReason.BANDWIDTH_LIMITED


def test_medium_low_original_preferences_map_to_profiles() -> None:
    for preference in (
        StreamQualityPreference.LOW,
        StreamQualityPreference.MEDIUM,
        StreamQualityPreference.ORIGINAL,
    ):
        result = _quality_service().evaluate_stream_quality(StreamQualityPolicy(preference=preference))

        assert result.ok
        assert result.data is not None
        assert result.data.profile is not None
        assert result.data.profile.preference == preference


def test_automatic_without_bandwidth_defaults_to_medium() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.AUTOMATIC)
    )

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.preference == StreamQualityPreference.MEDIUM
    assert result.data.reason == StreamQualityReason.AUTOMATIC_BANDWIDTH


def test_bitrate_limit_clamps_selected_profile() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(
            preference=StreamQualityPreference.HIGH,
            bitrate_limit=BitrateLimit(max_kbps=192),
        )
    )

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.preference == StreamQualityPreference.MEDIUM
    assert result.data.reason == StreamQualityReason.BITRATE_LIMITED


def test_negative_bitrate_limit_returns_safe_error() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(bitrate_limit=BitrateLimit(max_kbps=-1))
    )

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_BITRATE"


def test_negative_bandwidth_budget_returns_safe_error() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(bandwidth_budget=BandwidthBudget(available_kbps=-1))
    )

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_BANDWIDTH"


def test_negative_reserved_bandwidth_returns_safe_error() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(bandwidth_budget=BandwidthBudget(available_kbps=100, reserved_kbps=-1))
    )

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_BANDWIDTH"


def test_invalid_profile_bitrate_returns_safe_error() -> None:
    result = _quality_service().evaluate_stream_quality(
        profiles=(StreamQualityProfile(StreamQualityPreference.LOW, "broken", -1),)
    )

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_BITRATE"


def test_network_snapshot_offline_poor_degraded_good_excellent_levels() -> None:
    service = NetworkQualityPolicyService()
    cases = (
        (NetworkConditionSnapshot(connected=False), NetworkQualityLevel.OFFLINE, NetworkPolicyReason.OFFLINE),
        (NetworkConditionSnapshot(available_bandwidth_kbps=64), NetworkQualityLevel.POOR, NetworkPolicyReason.LOW_BANDWIDTH),
        (NetworkConditionSnapshot(available_bandwidth_kbps=256), NetworkQualityLevel.DEGRADED, NetworkPolicyReason.LOW_BANDWIDTH),
        (NetworkConditionSnapshot(available_bandwidth_kbps=1000), NetworkQualityLevel.GOOD, NetworkPolicyReason.HEALTHY),
        (NetworkConditionSnapshot(available_bandwidth_kbps=3000), NetworkQualityLevel.EXCELLENT, NetworkPolicyReason.HEALTHY),
    )

    for snapshot, level, reason in cases:
        result = service.evaluate_network_quality(snapshot)

        assert result.ok
        assert result.data is not None
        assert result.data.state.level == level
        assert result.data.reason == reason
        assert "no network was probed" in result.data.summary


def test_network_quality_handles_latency_loss_metered_and_unknown() -> None:
    service = NetworkQualityPolicyService()

    high_latency = service.evaluate_network_quality(NetworkConditionSnapshot(latency_ms=400))
    high_loss = service.evaluate_network_quality(NetworkConditionSnapshot(packet_loss_percent=6))
    metered = service.evaluate_network_quality(NetworkConditionSnapshot(metered=True))
    unknown = service.evaluate_network_quality(None)

    assert high_latency.data is not None
    assert high_latency.data.state.level == NetworkQualityLevel.DEGRADED
    assert high_loss.data is not None
    assert high_loss.data.reason == NetworkPolicyReason.HIGH_PACKET_LOSS
    assert metered.data is not None
    assert metered.data.reason == NetworkPolicyReason.METERED_OR_ROAMING
    assert unknown.data is not None
    assert unknown.data.state.level == NetworkQualityLevel.UNKNOWN


def test_negative_network_snapshot_values_return_safe_errors() -> None:
    service = NetworkQualityPolicyService()

    assert service.evaluate_network_quality(NetworkConditionSnapshot(available_bandwidth_kbps=-1)).error.code == "INVALID_BANDWIDTH"
    assert service.evaluate_network_quality(NetworkConditionSnapshot(latency_ms=-1)).error.code == "INVALID_LATENCY"
    assert service.evaluate_network_quality(NetworkConditionSnapshot(packet_loss_percent=-1)).error.code == "INVALID_PACKET_LOSS"


def test_degraded_network_drives_degraded_quality_decision() -> None:
    network = NetworkQualityPolicyService().evaluate_network_quality(
        NetworkConditionSnapshot(available_bandwidth_kbps=256)
    )
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.AUTOMATIC),
        network_decision=network.data,
    )

    assert result.ok
    assert result.data is not None
    assert result.data.degraded
    assert result.data.reason == StreamQualityReason.NETWORK_DEGRADED
    assert result.data.warnings


def test_source_degraded_adds_warning_without_playback_behavior() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.HIGH),
        source_degraded=True,
    )

    assert result.ok
    assert result.data is not None
    assert result.data.degraded
    assert result.data.warnings[0].code == "SOURCE_DEGRADED"


def test_source_unavailable_returns_policy_decision_without_crashing() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.HIGH),
        source_available=False,
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.allowed
    assert result.data.reason == StreamQualityReason.SOURCE_UNAVAILABLE


def test_unsupported_format_recommends_transcoding_need_as_decision_only() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.HIGH),
        source_format="flac",
        renderer_supported_formats=frozenset({"mp3"}),
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.allowed
    assert result.data.needs_transcoding
    assert result.data.reason == StreamQualityReason.FORMAT_UNSUPPORTED


def test_supported_transcoding_decision_is_carried_as_policy_only() -> None:
    result = _quality_service().evaluate_stream_quality(
        StreamQualityPolicy(preference=StreamQualityPreference.HIGH),
        source_format="flac",
        renderer_supported_formats=frozenset({"mp3"}),
        transcoding_decision=TranscodingDecision(
            available=True,
            requirement=TranscodingRequirement.REQUIRED,
            target_format="mp3",
            target_bitrate_kbps=320,
        ),
    )

    assert result.ok
    assert result.data is not None
    assert result.data.allowed
    assert result.data.needs_transcoding
    assert result.data.reason == StreamQualityReason.TRANSCODING_NEEDED


def test_offline_mode_uses_offline_quality_without_download() -> None:
    result = _quality_service().evaluate_stream_quality(FakeQualityPolicyScenarios.offline_preferred())

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.label == "Offline Low"
    assert result.data.reason == StreamQualityReason.OFFLINE_PREFERRED
    assert "no stream was opened" in result.data.summary


def test_offline_quality_fallback_defaults_to_medium_profile() -> None:
    result = _quality_service().evaluate_offline_quality(OfflineQualityPolicy(prefer_offline=True))

    assert result.ok
    assert result.data is not None
    assert result.data.profile is not None
    assert result.data.profile.preference == StreamQualityPreference.MEDIUM
    assert result.data.reason == StreamQualityReason.OFFLINE_PREFERRED


def test_transcoding_available_from_declared_capability_only() -> None:
    result = TranscodingPolicyService().evaluate_transcoding(
        capability=TranscodingCapability(
            supported=True,
            input_formats=frozenset({"flac"}),
            output_formats=frozenset({"mp3"}),
            max_output_bitrate_kbps=320,
        ),
        policy=TranscodingPolicy(
            requirement=TranscodingRequirement.REQUIRED,
            target_format="mp3",
            target_bitrate_kbps=192,
        ),
        input_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert result.data.available
    assert "no transcoder was invoked" in result.data.summary


def test_transcoding_unsupported_source_returns_unavailable_without_crashing() -> None:
    result = TranscodingPolicyService().evaluate_transcoding(
        capability=TranscodingCapability(supported=False),
        policy=TranscodingPolicy(requirement=TranscodingRequirement.REQUIRED),
        input_format="flac",
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.reason == TranscodingUnavailableReason.UNSUPPORTED_SOURCE


def test_transcoding_disabled_by_policy_returns_unavailable() -> None:
    result = TranscodingPolicyService().evaluate_transcoding(
        capability=TranscodingCapability(supported=True),
        policy=TranscodingPolicy(preference=TranscodingPreference.NEVER),
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.available
    assert result.data.reason == TranscodingUnavailableReason.POLICY_DISABLED


def test_transcoding_source_input_output_and_bitrate_unavailable_reasons() -> None:
    service = TranscodingPolicyService()
    capability = TranscodingCapability(
        supported=True,
        input_formats=frozenset({"flac"}),
        output_formats=frozenset({"mp3"}),
        max_output_bitrate_kbps=192,
    )

    source = service.evaluate_transcoding(capability=capability, source_available=False)
    input_format = service.evaluate_transcoding(capability=capability, input_format="ogg")
    output_format = service.evaluate_transcoding(
        capability=capability,
        policy=TranscodingPolicy(target_format="aac"),
        input_format="flac",
    )
    bitrate = service.evaluate_transcoding(
        capability=capability,
        policy=TranscodingPolicy(target_format="mp3", target_bitrate_kbps=320),
        input_format="flac",
    )

    assert source.data.reason == TranscodingUnavailableReason.SOURCE_UNAVAILABLE
    assert input_format.data.reason == TranscodingUnavailableReason.INPUT_FORMAT_UNSUPPORTED
    assert output_format.data.reason == TranscodingUnavailableReason.OUTPUT_FORMAT_UNSUPPORTED
    assert bitrate.data.reason == TranscodingUnavailableReason.BITRATE_UNSUPPORTED


def test_transcoding_negative_bitrate_values_return_safe_errors() -> None:
    service = TranscodingPolicyService()

    invalid_policy = service.evaluate_transcoding(
        capability=TranscodingCapability(supported=True),
        policy=TranscodingPolicy(target_bitrate_kbps=-1),
    )
    invalid_capability = service.evaluate_transcoding(
        capability=TranscodingCapability(supported=True, max_output_bitrate_kbps=-1),
    )

    assert invalid_policy.is_err()
    assert invalid_policy.error.code == "INVALID_BITRATE"
    assert invalid_capability.is_err()
    assert invalid_capability.error.code == "INVALID_CAPABILITY"


def test_model_defaults_and_safe_serialization_are_deterministic() -> None:
    decision = _quality_service().evaluate_stream_quality().data

    serialized = safe_serialize(decision)

    assert serialized["profile"]["preference"] == "MEDIUM"
    assert serialized["reason"] == "AUTOMATIC_BANDWIDTH"
    json.dumps(serialized)


def test_stream_quality_module_exports_are_intentional() -> None:
    assert set(stream_quality.__all__) == {
        "BandwidthBudget",
        "BitrateLimit",
        "FakeQualityPolicyScenarios",
        "NetworkConditionSnapshot",
        "NetworkPolicyDecision",
        "NetworkPolicyReason",
        "NetworkQualityLevel",
        "NetworkQualityPolicyService",
        "NetworkQualityState",
        "OfflineQualityPolicy",
        "QualityFallbackPolicy",
        "QualityPolicyService",
        "StreamQualityDecision",
        "StreamQualityPolicy",
        "StreamQualityPreference",
        "StreamQualityProfile",
        "StreamQualityReason",
        "TranscodingCapability",
        "TranscodingDecision",
        "TranscodingPolicy",
        "TranscodingPolicyService",
        "TranscodingPreference",
        "TranscodingRequirement",
        "TranscodingUnavailableReason",
    }


def test_policy_module_has_no_forbidden_runtime_integration_imports() -> None:
    source = inspect.getsource(stream_quality)
    forbidden = (
        "requests" + ".",
        "httpx" + ".",
        "aiohttp" + ".",
        "urllib" + ".",
        "socket" + ".",
        "ff" + "mpeg",
        "m3" + "u8",
        "Navidrome" + "Provider",
        "Jelly" + "fin",
        "Em" + "by",
        "android" + ".",
        "Media" + "3",
        "Exo" + "Player",
        "os" + ".walk",
        "glob" + ".glob",
        "scandir",
        "Audio" + "Driver",
        "Usb" + "Dac",
        "Smart" + "Playlist",
    )

    assert not any(term in source for term in forbidden)
