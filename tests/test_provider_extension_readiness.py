"""Tests for Bloco 21 provider extension readiness."""

from __future__ import annotations

import inspect
import json

import noqlen_aria.provider_extensions as provider_extensions
from noqlen_aria import safe_serialize
from noqlen_aria.provider_extensions import (
    FakeProviderExtensionScenarios,
    ProviderBoundaryPolicy,
    ProviderCapabilityDiscoveryService,
    ProviderExtensionCapabilitySummary,
    ProviderExtensionKind,
    ProviderExtensionReadinessService,
    ProviderExtensionRequirement,
    ProviderExtensionStatus,
    ProviderExtensionUnavailableReason,
)


def _readiness_service() -> ProviderExtensionReadinessService:
    return ProviderExtensionReadinessService()


def _discovery_service() -> ProviderCapabilityDiscoveryService:
    return ProviderCapabilityDiscoveryService()


def test_valid_provider_descriptor_normalizes_capability_summary() -> None:
    descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()

    result = _readiness_service().build_summary(descriptor)

    assert result.ok
    assert result.data is not None
    assert result.data.status == ProviderExtensionStatus.READY
    assert result.data.capabilities.supports("Library")
    assert result.data.capabilities.supports("playlist")
    assert "no provider was called" in result.data.capabilities.summary


def test_invalid_provider_descriptor_returns_safe_error() -> None:
    result = _readiness_service().validate_descriptor(FakeProviderExtensionScenarios.invalid_descriptor())

    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_PROVIDER_ID"
    assert "/" not in result.error.message


def test_missing_public_boundary_is_unavailable_with_safe_reason() -> None:
    readiness = _readiness_service().evaluate_readiness(FakeProviderExtensionScenarios.missing_public_boundary()).data

    assert readiness is not None
    assert not readiness.ready
    assert readiness.status == ProviderExtensionStatus.UNAVAILABLE
    assert readiness.reason == ProviderExtensionUnavailableReason.MISSING_PUBLIC_BOUNDARY
    assert readiness.warnings


def test_current_anchor_boundary_is_not_treated_as_multi_provider() -> None:
    descriptor = FakeProviderExtensionScenarios.anchor_navidrome_focused_boundary()
    readiness = _readiness_service().evaluate_readiness(descriptor).data

    compatibility = _readiness_service().evaluate_compatibility(descriptor, frozenset({"library_summary"})).data


    assert descriptor.kind == ProviderExtensionKind.ANCHOR_BACKED
    assert descriptor.boundary_policy.anchor_multi_provider_claim is False
    assert descriptor.boundary_policy.anchor_provider_internals_allowed is False
    assert readiness is not None
    assert readiness.ready
    assert any(warning.code == "ANCHOR_NAVIDROME_FOCUSED" for warning in readiness.warnings)
    assert compatibility is not None
    assert compatibility.compatible


def test_future_provider_descriptor_readiness_does_not_call_provider_apis() -> None:
    descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
    readiness = _readiness_service().evaluate_readiness(descriptor).data
    preview = _discovery_service().preview_discovery(descriptor).data

    assert readiness is not None
    assert readiness.ready
    assert preview is not None
    assert preview.provider_called is False
    assert preview.network_opened is False


def test_authentication_requirement_is_blocked_as_future_scope() -> None:
    readiness = _readiness_service().evaluate_readiness(FakeProviderExtensionScenarios.requires_authentication()).data
    preview = _discovery_service().preview_discovery(FakeProviderExtensionScenarios.requires_authentication()).data

    assert readiness is not None
    assert not readiness.ready
    assert readiness.reason == ProviderExtensionUnavailableReason.AUTHENTICATION_OUT_OF_SCOPE
    assert ProviderExtensionRequirement.AUTHENTICATION in readiness.requirements
    assert preview is not None
    assert preview.issues[0].requirement == ProviderExtensionRequirement.AUTHENTICATION


def test_network_discovery_requirement_is_blocked_as_future_scope() -> None:
    readiness = _readiness_service().evaluate_readiness(FakeProviderExtensionScenarios.requires_network_discovery()).data
    preview = _discovery_service().preview_discovery(FakeProviderExtensionScenarios.requires_network_discovery()).data

    assert readiness is not None
    assert readiness.reason == ProviderExtensionUnavailableReason.NETWORK_DISCOVERY_OUT_OF_SCOPE
    assert preview is not None
    assert preview.network_opened is False
    assert any(issue.requirement == ProviderExtensionRequirement.NETWORK_DISCOVERY for issue in preview.issues)


def test_degraded_capability_warnings_without_network() -> None:
    descriptor = FakeProviderExtensionScenarios.degraded_capability()

    readiness = _readiness_service().evaluate_readiness(descriptor).data
    preview = _discovery_service().preview_discovery(descriptor).data

    assert readiness is not None
    assert readiness.status == ProviderExtensionStatus.DEGRADED
    assert readiness.degraded
    assert preview is not None
    assert preview.warnings
    assert preview.network_opened is False


def test_compatibility_reports_missing_unsupported_future_and_degraded_capabilities() -> None:
    descriptor = FakeProviderExtensionScenarios.unsupported_media_capability()

    result = _readiness_service().evaluate_compatibility(
        descriptor,
        frozenset({"library", "stream_resolution", "provider_playlist_write", "lyrics"}),
    )

    assert result.ok
    assert result.data is not None
    assert not result.data.compatible
    assert result.data.supported_capabilities == frozenset({"library"})
    assert result.data.unsupported_capabilities == frozenset({"stream_resolution"})
    assert result.data.future_capabilities == frozenset({"provider_playlist_write"})
    assert result.data.missing_capabilities == frozenset({"lyrics"})


def test_registry_state_is_deterministic_and_tracks_unavailable_and_duplicate_ids() -> None:
    valid = FakeProviderExtensionScenarios.future_public_boundary_provider()
    missing = FakeProviderExtensionScenarios.missing_public_boundary()
    duplicate = FakeProviderExtensionScenarios.future_public_boundary_provider()

    registry = _readiness_service().build_registry((valid, missing, duplicate)).data

    assert registry is not None
    assert [summary.provider_ref.provider_id for summary in registry.providers] == [
        valid.provider_ref.provider_id,
        missing.provider_ref.provider_id,
    ]
    assert registry.duplicate_provider_ids == frozenset({valid.provider_ref.provider_id})
    assert registry.unavailable_provider_ids == frozenset({missing.provider_ref.provider_id})
    assert registry.warnings


def test_boundary_policy_blocks_direct_provider_and_platform_behaviors() -> None:
    base = FakeProviderExtensionScenarios.future_public_boundary_provider()
    blocked_policies = (
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", direct_provider_calls_allowed=True), ProviderExtensionUnavailableReason.DIRECT_PROVIDER_ACCESS_BLOCKED),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", provider_internals_allowed=True), ProviderExtensionUnavailableReason.PROVIDER_INTERNALS_BLOCKED),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", anchor_provider_internals_allowed=True), ProviderExtensionUnavailableReason.ANCHOR_PROVIDER_INTERNALS_BLOCKED),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", network_discovery_allowed=True), ProviderExtensionUnavailableReason.NETWORK_DISCOVERY_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", handles_authentication=True), ProviderExtensionUnavailableReason.AUTHENTICATION_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", provider_mutation_allowed=True), ProviderExtensionUnavailableReason.PROVIDER_MUTATION_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", streaming_allowed=True), ProviderExtensionUnavailableReason.STREAMING_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", playback_allowed=True), ProviderExtensionUnavailableReason.PLAYBACK_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", android_ui_allowed=True), ProviderExtensionUnavailableReason.ANDROID_UI_OUT_OF_SCOPE),
        (ProviderBoundaryPolicy(public_boundary_contract="Boundary", anchor_multi_provider_claim=True), ProviderExtensionUnavailableReason.ANCHOR_NOT_MULTI_PROVIDER),
    )

    for policy, reason in blocked_policies:
        descriptor = type(base)(
            provider_ref=base.provider_ref,
            kind=base.kind,
            adapter_name=base.adapter_name,
            boundary_policy=policy,
            declared_capabilities=base.declared_capabilities,
            requirements=base.requirements,
        )
        readiness = _readiness_service().evaluate_readiness(descriptor).data
        assert readiness is not None
        assert readiness.reason == reason


def test_capability_summary_defaults_and_serialization_are_safe() -> None:
    summary = ProviderExtensionCapabilitySummary(
        supported=frozenset({" Library ", "PLAYLIST"}),
        degraded=frozenset({"Playlist"}),
    )

    serialized = safe_serialize(summary)

    assert summary.supports("library")
    assert summary.is_degraded("playlist")
    assert serialized["supported"] == ["library", "playlist"] or set(serialized["supported"]) == {"library", "playlist"}
    json.dumps(serialized)


def test_provider_extension_module_exports_are_intentional() -> None:
    assert set(provider_extensions.__all__) == {
        "FakeProviderExtensionScenarios",
        "ProviderAdapterDescriptor",
        "ProviderAdapterReadiness",
        "ProviderBoundaryPolicy",
        "ProviderCapabilityDiscoveryIssue",
        "ProviderCapabilityDiscoveryPreview",
        "ProviderCapabilityDiscoveryService",
        "ProviderExtensionCapabilitySummary",
        "ProviderExtensionCompatibilityState",
        "ProviderExtensionId",
        "ProviderExtensionKind",
        "ProviderExtensionReadinessService",
        "ProviderExtensionReadinessState",
        "ProviderExtensionRef",
        "ProviderExtensionRegistryState",
        "ProviderExtensionRequirement",
        "ProviderExtensionStatus",
        "ProviderExtensionSummary",
        "ProviderExtensionUnavailableReason",
        "ProviderExtensionWarning",
    }


def test_no_direct_provider_network_mutation_streaming_playback_or_android_behavior() -> None:
    source = inspect.getsource(provider_extensions)
    forbidden = (
        "requests" + ".",
        "httpx" + ".",
        "aiohttp" + ".",
        "urllib" + ".",
        "socket" + ".",
        "subprocess",
        "noqlen_anchor" + ".cli",
        "Provider" + "API",
        "connect(",
        "login(",
        "stream_resolve(",
        "start_playback(",
        "android" + ".",
        "androidx" + ".",
        "Activity",
        "Fragment",
        "Compose",
        "Kotlin",
        "Gradle",
    )

    assert not any(term in source for term in forbidden)
