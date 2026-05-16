"""Provider extension readiness foundation for future public adapters.

Bloco 21 — descriptor/readiness modeling only. This module never calls
providers, opens network connections, handles sign-in data, streams media,
starts playback, or touches Android/UI behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import NewType

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning


ProviderExtensionId = NewType("ProviderExtensionId", str)


class ProviderExtensionKind(Enum):
    ANCHOR_BACKED = auto()
    PUBLIC_ADAPTER = auto()
    LOCAL_DECLARATION = auto()
    FUTURE_PROVIDER = auto()


class ProviderExtensionStatus(Enum):
    READY = auto()
    DEGRADED = auto()
    UNAVAILABLE = auto()
    UNSUPPORTED = auto()
    PLANNED = auto()


class ProviderExtensionRequirement(Enum):
    PUBLIC_BOUNDARY = auto()
    AUTHENTICATION = auto()
    NETWORK_DISCOVERY = auto()
    PROVIDER_MUTATION = auto()
    STREAMING = auto()
    PLAYBACK = auto()
    ANDROID_UI = auto()


class ProviderExtensionUnavailableReason(Enum):
    NONE = auto()
    INVALID_DESCRIPTOR = auto()
    MISSING_PUBLIC_BOUNDARY = auto()
    DIRECT_PROVIDER_ACCESS_BLOCKED = auto()
    PROVIDER_INTERNALS_BLOCKED = auto()
    ANCHOR_PROVIDER_INTERNALS_BLOCKED = auto()
    AUTHENTICATION_OUT_OF_SCOPE = auto()
    NETWORK_DISCOVERY_OUT_OF_SCOPE = auto()
    PROVIDER_MUTATION_OUT_OF_SCOPE = auto()
    STREAMING_OUT_OF_SCOPE = auto()
    PLAYBACK_OUT_OF_SCOPE = auto()
    ANDROID_UI_OUT_OF_SCOPE = auto()
    CAPABILITY_UNSUPPORTED = auto()
    ANCHOR_NOT_MULTI_PROVIDER = auto()


@dataclass(frozen=True)
class ProviderExtensionWarning:
    code: str
    message: str


@dataclass(frozen=True)
class ProviderExtensionRef:
    provider_id: ProviderExtensionId
    display_name: str


@dataclass(frozen=True)
class ProviderExtensionCapabilitySummary:
    supported: frozenset[str] = field(default_factory=frozenset)
    degraded: frozenset[str] = field(default_factory=frozenset)
    unsupported: frozenset[str] = field(default_factory=frozenset)
    future: frozenset[str] = field(default_factory=frozenset)
    summary: str = "Provider capabilities are declared only; no provider was called"

    def __post_init__(self) -> None:
        object.__setattr__(self, "supported", _normalize_capabilities(self.supported))
        object.__setattr__(self, "degraded", _normalize_capabilities(self.degraded))
        object.__setattr__(self, "unsupported", _normalize_capabilities(self.unsupported))
        object.__setattr__(self, "future", _normalize_capabilities(self.future))

    def supports(self, capability: str) -> bool:
        return _normalize_capability(capability) in self.supported

    def is_degraded(self, capability: str) -> bool:
        return _normalize_capability(capability) in self.degraded


@dataclass(frozen=True)
class ProviderBoundaryPolicy:
    public_boundary_contract: str = ""
    ui_must_use_core_models: bool = True
    direct_provider_calls_allowed: bool = False
    provider_internals_allowed: bool = False
    anchor_provider_internals_allowed: bool = False
    network_discovery_allowed: bool = False
    handles_authentication: bool = False
    provider_mutation_allowed: bool = False
    streaming_allowed: bool = False
    playback_allowed: bool = False
    android_ui_allowed: bool = False
    anchor_multi_provider_claim: bool = False


@dataclass(frozen=True)
class ProviderAdapterDescriptor:
    provider_ref: ProviderExtensionRef
    kind: ProviderExtensionKind
    adapter_name: str
    boundary_policy: ProviderBoundaryPolicy = field(default_factory=ProviderBoundaryPolicy)
    declared_capabilities: frozenset[str] = field(default_factory=frozenset)
    degraded_capabilities: frozenset[str] = field(default_factory=frozenset)
    unsupported_capabilities: frozenset[str] = field(default_factory=frozenset)
    future_capabilities: frozenset[str] = field(default_factory=frozenset)
    requirements: frozenset[ProviderExtensionRequirement] = field(default_factory=frozenset)
    status_hint: ProviderExtensionStatus = ProviderExtensionStatus.PLANNED
    notes: str = ""

    def capability_summary(self) -> ProviderExtensionCapabilitySummary:
        return ProviderExtensionCapabilitySummary(
            supported=self.declared_capabilities,
            degraded=self.degraded_capabilities,
            unsupported=self.unsupported_capabilities,
            future=self.future_capabilities,
        )


@dataclass(frozen=True)
class ProviderAdapterReadiness:
    ready: bool = False
    degraded: bool = False
    status: ProviderExtensionStatus = ProviderExtensionStatus.UNAVAILABLE
    reason: ProviderExtensionUnavailableReason = ProviderExtensionUnavailableReason.MISSING_PUBLIC_BOUNDARY
    warnings: tuple[ProviderExtensionWarning, ...] = field(default_factory=tuple)
    summary: str = "Provider adapter readiness is descriptor-only; no adapter was connected"


@dataclass(frozen=True)
class ProviderExtensionReadinessState:
    provider_ref: ProviderExtensionRef
    ready: bool = False
    degraded: bool = False
    status: ProviderExtensionStatus = ProviderExtensionStatus.UNAVAILABLE
    reason: ProviderExtensionUnavailableReason = ProviderExtensionUnavailableReason.MISSING_PUBLIC_BOUNDARY
    requirements: frozenset[ProviderExtensionRequirement] = field(default_factory=frozenset)
    warnings: tuple[ProviderExtensionWarning, ...] = field(default_factory=tuple)
    summary: str = "Provider readiness is descriptor-only; no provider was called"


@dataclass(frozen=True)
class ProviderExtensionCompatibilityState:
    provider_ref: ProviderExtensionRef
    compatible: bool = False
    requested_capabilities: frozenset[str] = field(default_factory=frozenset)
    supported_capabilities: frozenset[str] = field(default_factory=frozenset)
    missing_capabilities: frozenset[str] = field(default_factory=frozenset)
    degraded_capabilities: frozenset[str] = field(default_factory=frozenset)
    unsupported_capabilities: frozenset[str] = field(default_factory=frozenset)
    future_capabilities: frozenset[str] = field(default_factory=frozenset)
    warnings: tuple[ProviderExtensionWarning, ...] = field(default_factory=tuple)
    summary: str = "Compatibility is evaluated from declared capabilities only"


@dataclass(frozen=True)
class ProviderExtensionSummary:
    provider_ref: ProviderExtensionRef
    kind: ProviderExtensionKind
    status: ProviderExtensionStatus
    capabilities: ProviderExtensionCapabilitySummary = field(default_factory=ProviderExtensionCapabilitySummary)
    readiness: ProviderExtensionReadinessState | None = None
    adapter_readiness: ProviderAdapterReadiness = field(default_factory=ProviderAdapterReadiness)


@dataclass(frozen=True)
class ProviderCapabilityDiscoveryIssue:
    code: str
    message: str
    requirement: ProviderExtensionRequirement | None = None


@dataclass(frozen=True)
class ProviderCapabilityDiscoveryPreview:
    provider_ref: ProviderExtensionRef
    capabilities: ProviderExtensionCapabilitySummary = field(default_factory=ProviderExtensionCapabilitySummary)
    issues: tuple[ProviderCapabilityDiscoveryIssue, ...] = field(default_factory=tuple)
    warnings: tuple[ProviderExtensionWarning, ...] = field(default_factory=tuple)
    network_opened: bool = False
    provider_called: bool = False
    summary: str = "Capability discovery preview used descriptor data only"


@dataclass(frozen=True)
class ProviderExtensionRegistryState:
    providers: tuple[ProviderExtensionSummary, ...] = field(default_factory=tuple)
    duplicate_provider_ids: frozenset[ProviderExtensionId] = field(default_factory=frozenset)
    unavailable_provider_ids: frozenset[ProviderExtensionId] = field(default_factory=frozenset)
    warnings: tuple[ProviderExtensionWarning, ...] = field(default_factory=tuple)
    summary: str = "Provider registry is in-memory descriptor state only"


class ProviderExtensionReadinessService:
    """Evaluate provider readiness from declared descriptors only."""

    def validate_descriptor(self, descriptor: ProviderAdapterDescriptor) -> AriaResult[ProviderAdapterDescriptor]:
        if not str(descriptor.provider_ref.provider_id).strip():
            return self._invalid("INVALID_PROVIDER_ID", "Provider extension id is required")
        if not descriptor.provider_ref.display_name.strip():
            return self._invalid("INVALID_PROVIDER_NAME", "Provider display name is required")
        if not descriptor.adapter_name.strip():
            return self._invalid("INVALID_ADAPTER_NAME", "Provider adapter name is required")
        if "\n" in descriptor.adapter_name or "\r" in descriptor.adapter_name:
            return self._invalid("INVALID_ADAPTER_NAME", "Provider adapter name must be single-line text")
        if not descriptor.declared_capabilities:
            return self._invalid("NO_CAPABILITIES", "At least one declared capability is required")
        return AriaResult(ok=True, data=descriptor)

    def enforce_boundary_policy(self, descriptor: ProviderAdapterDescriptor) -> AriaResult[ProviderAdapterReadiness]:
        invalid = self.validate_descriptor(descriptor)
        if invalid.is_err():
            return AriaResult(ok=False, error=invalid.error)
        reason = self._policy_block_reason(descriptor)
        if reason is not None:
            return AriaResult(ok=True, data=self._adapter_readiness(False, False, ProviderExtensionStatus.UNAVAILABLE, reason))
        if descriptor.degraded_capabilities:
            return AriaResult(
                ok=True,
                data=self._adapter_readiness(True, True, ProviderExtensionStatus.DEGRADED, ProviderExtensionUnavailableReason.NONE),
            )
        return AriaResult(
            ok=True,
            data=self._adapter_readiness(True, False, ProviderExtensionStatus.READY, ProviderExtensionUnavailableReason.NONE),
        )

    def evaluate_readiness(self, descriptor: ProviderAdapterDescriptor) -> AriaResult[ProviderExtensionReadinessState]:
        invalid = self.validate_descriptor(descriptor)
        if invalid.is_err():
            return AriaResult(ok=False, error=invalid.error)
        policy = self.enforce_boundary_policy(descriptor)
        if policy.is_err():
            return AriaResult(ok=False, error=policy.error)
        adapter = policy.data or ProviderAdapterReadiness()
        warnings = list(adapter.warnings)
        if descriptor.kind == ProviderExtensionKind.ANCHOR_BACKED:
            warnings.append(
                ProviderExtensionWarning(
                    "ANCHOR_NAVIDROME_FOCUSED",
                    "Current Anchor-backed integration remains focused on one existing provider boundary",
                )
            )
        if descriptor.degraded_capabilities:
            warnings.append(ProviderExtensionWarning("CAPABILITY_DEGRADED", "One or more declared capabilities are degraded"))
        return AriaResult(
            ok=True,
            data=ProviderExtensionReadinessState(
                provider_ref=descriptor.provider_ref,
                ready=adapter.ready,
                degraded=adapter.degraded,
                status=adapter.status,
                reason=adapter.reason,
                requirements=descriptor.requirements,
                warnings=tuple(warnings),
            ),
        )

    def evaluate_compatibility(
        self,
        descriptor: ProviderAdapterDescriptor,
        required_capabilities: frozenset[str],
    ) -> AriaResult[ProviderExtensionCompatibilityState]:
        invalid = self.validate_descriptor(descriptor)
        if invalid.is_err():
            return AriaResult(ok=False, error=invalid.error)
        requested = _normalize_capabilities(required_capabilities)
        summary = descriptor.capability_summary()
        available = summary.supported | summary.degraded
        missing = requested - available - summary.unsupported - summary.future
        unsupported = requested & summary.unsupported
        future = requested & summary.future
        degraded = requested & summary.degraded
        compatible = not missing and not unsupported and not future
        warnings: list[ProviderExtensionWarning] = []
        if degraded:
            warnings.append(ProviderExtensionWarning("CAPABILITY_DEGRADED", "Compatible capability is degraded"))
        if unsupported:
            warnings.append(ProviderExtensionWarning("CAPABILITY_UNSUPPORTED", "Requested capability is unsupported"))
        if future:
            warnings.append(ProviderExtensionWarning("CAPABILITY_FUTURE", "Requested capability is future scope"))
        return AriaResult(
            ok=True,
            data=ProviderExtensionCompatibilityState(
                provider_ref=descriptor.provider_ref,
                compatible=compatible,
                requested_capabilities=requested,
                supported_capabilities=requested & summary.supported,
                missing_capabilities=missing,
                degraded_capabilities=degraded,
                unsupported_capabilities=unsupported,
                future_capabilities=future,
                warnings=tuple(warnings),
            ),
        )

    def build_summary(self, descriptor: ProviderAdapterDescriptor) -> AriaResult[ProviderExtensionSummary]:
        readiness = self.evaluate_readiness(descriptor)
        if readiness.is_err():
            return AriaResult(ok=False, error=readiness.error)
        adapter = self.enforce_boundary_policy(descriptor)
        if adapter.is_err():
            return AriaResult(ok=False, error=adapter.error)
        return AriaResult(
            ok=True,
            data=ProviderExtensionSummary(
                provider_ref=descriptor.provider_ref,
                kind=descriptor.kind,
                status=readiness.data.status if readiness.data else ProviderExtensionStatus.UNAVAILABLE,
                capabilities=descriptor.capability_summary(),
                readiness=readiness.data,
                adapter_readiness=adapter.data or ProviderAdapterReadiness(),
            ),
        )

    def build_registry(self, descriptors: tuple[ProviderAdapterDescriptor, ...]) -> AriaResult[ProviderExtensionRegistryState]:
        seen: set[ProviderExtensionId] = set()
        duplicates: set[ProviderExtensionId] = set()
        providers: list[ProviderExtensionSummary] = []
        unavailable: set[ProviderExtensionId] = set()
        warnings: list[ProviderExtensionWarning] = []
        for descriptor in descriptors:
            provider_id = descriptor.provider_ref.provider_id
            if provider_id in seen:
                duplicates.add(provider_id)
                warnings.append(ProviderExtensionWarning("DUPLICATE_PROVIDER_ID", f"Duplicate provider id {provider_id}"))
                continue
            seen.add(provider_id)
            summary = self.build_summary(descriptor)
            if summary.is_err():
                unavailable.add(provider_id)
                warnings.append(ProviderExtensionWarning(summary.error.code if summary.error else "INVALID_DESCRIPTOR", "Provider descriptor is invalid"))
                continue
            if summary.data is not None:
                providers.append(summary.data)
                if summary.data.status not in {ProviderExtensionStatus.READY, ProviderExtensionStatus.DEGRADED}:
                    unavailable.add(provider_id)
        return AriaResult(
            ok=True,
            data=ProviderExtensionRegistryState(
                providers=tuple(providers),
                duplicate_provider_ids=frozenset(duplicates),
                unavailable_provider_ids=frozenset(unavailable),
                warnings=tuple(warnings),
            ),
        )

    def _policy_block_reason(self, descriptor: ProviderAdapterDescriptor) -> ProviderExtensionUnavailableReason | None:
        policy = descriptor.boundary_policy
        requirements = descriptor.requirements
        if not policy.public_boundary_contract.strip() or ProviderExtensionRequirement.PUBLIC_BOUNDARY not in requirements:
            return ProviderExtensionUnavailableReason.MISSING_PUBLIC_BOUNDARY
        if policy.direct_provider_calls_allowed:
            return ProviderExtensionUnavailableReason.DIRECT_PROVIDER_ACCESS_BLOCKED
        if policy.provider_internals_allowed:
            return ProviderExtensionUnavailableReason.PROVIDER_INTERNALS_BLOCKED
        if policy.anchor_provider_internals_allowed:
            return ProviderExtensionUnavailableReason.ANCHOR_PROVIDER_INTERNALS_BLOCKED
        if policy.anchor_multi_provider_claim:
            return ProviderExtensionUnavailableReason.ANCHOR_NOT_MULTI_PROVIDER
        requirement_blocks = (
            (ProviderExtensionRequirement.AUTHENTICATION, ProviderExtensionUnavailableReason.AUTHENTICATION_OUT_OF_SCOPE),
            (ProviderExtensionRequirement.NETWORK_DISCOVERY, ProviderExtensionUnavailableReason.NETWORK_DISCOVERY_OUT_OF_SCOPE),
            (ProviderExtensionRequirement.PROVIDER_MUTATION, ProviderExtensionUnavailableReason.PROVIDER_MUTATION_OUT_OF_SCOPE),
            (ProviderExtensionRequirement.STREAMING, ProviderExtensionUnavailableReason.STREAMING_OUT_OF_SCOPE),
            (ProviderExtensionRequirement.PLAYBACK, ProviderExtensionUnavailableReason.PLAYBACK_OUT_OF_SCOPE),
            (ProviderExtensionRequirement.ANDROID_UI, ProviderExtensionUnavailableReason.ANDROID_UI_OUT_OF_SCOPE),
        )
        for requirement, reason in requirement_blocks:
            if requirement in requirements:
                return reason
        if policy.network_discovery_allowed:
            return ProviderExtensionUnavailableReason.NETWORK_DISCOVERY_OUT_OF_SCOPE
        if policy.handles_authentication:
            return ProviderExtensionUnavailableReason.AUTHENTICATION_OUT_OF_SCOPE
        if policy.provider_mutation_allowed:
            return ProviderExtensionUnavailableReason.PROVIDER_MUTATION_OUT_OF_SCOPE
        if policy.streaming_allowed:
            return ProviderExtensionUnavailableReason.STREAMING_OUT_OF_SCOPE
        if policy.playback_allowed:
            return ProviderExtensionUnavailableReason.PLAYBACK_OUT_OF_SCOPE
        if policy.android_ui_allowed:
            return ProviderExtensionUnavailableReason.ANDROID_UI_OUT_OF_SCOPE
        return None

    def _adapter_readiness(
        self,
        ready: bool,
        degraded: bool,
        status: ProviderExtensionStatus,
        reason: ProviderExtensionUnavailableReason,
    ) -> ProviderAdapterReadiness:
        warnings = ()
        if reason != ProviderExtensionUnavailableReason.NONE:
            warnings = (ProviderExtensionWarning(reason.name, "Provider boundary policy blocks readiness"),)
        return ProviderAdapterReadiness(ready=ready, degraded=degraded, status=status, reason=reason, warnings=warnings)

    def _invalid(self, code: str, message: str) -> AriaResult[ProviderAdapterDescriptor]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


class ProviderCapabilityDiscoveryService:
    """Build preview-only discovery output from declared descriptors."""

    def preview_discovery(self, descriptor: ProviderAdapterDescriptor) -> AriaResult[ProviderCapabilityDiscoveryPreview]:
        readiness_service = ProviderExtensionReadinessService()
        invalid = readiness_service.validate_descriptor(descriptor)
        if invalid.is_err():
            return AriaResult(ok=False, error=invalid.error)
        issues: list[ProviderCapabilityDiscoveryIssue] = []
        warnings: list[ProviderExtensionWarning] = []
        for requirement in sorted(descriptor.requirements, key=lambda item: item.name):
            if requirement == ProviderExtensionRequirement.PUBLIC_BOUNDARY:
                continue
            issues.append(
                ProviderCapabilityDiscoveryIssue(
                    code=f"{requirement.name}_FUTURE_SCOPE",
                    message="Requirement is recorded for a future provider adapter and was not executed",
                    requirement=requirement,
                )
            )
        for capability in sorted(descriptor.degraded_capabilities):
            warnings.append(ProviderExtensionWarning("CAPABILITY_DEGRADED", f"Capability {capability} is degraded"))
        return AriaResult(
            ok=True,
            data=ProviderCapabilityDiscoveryPreview(
                provider_ref=descriptor.provider_ref,
                capabilities=descriptor.capability_summary(),
                issues=tuple(issues),
                warnings=tuple(warnings),
            ),
        )


class FakeProviderExtensionScenarios:
    """Deterministic provider-extension descriptors for tests and examples."""

    @staticmethod
    def anchor_navidrome_focused_boundary() -> ProviderAdapterDescriptor:
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("anchor-current"), "Current Anchor boundary"),
            kind=ProviderExtensionKind.ANCHOR_BACKED,
            adapter_name="AnchorControlClient",
            boundary_policy=ProviderBoundaryPolicy(public_boundary_contract="ControlClient dry-run boundary"),
            declared_capabilities=frozenset({"control_readiness", "library_summary"}),
            requirements=frozenset({ProviderExtensionRequirement.PUBLIC_BOUNDARY}),
            notes="Current Anchor-backed integration remains focused on the existing Navidrome-oriented boundary.",
        )

    @staticmethod
    def future_public_boundary_provider() -> ProviderAdapterDescriptor:
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("future-public-provider"), "Future Public Provider"),
            kind=ProviderExtensionKind.PUBLIC_ADAPTER,
            adapter_name="FuturePublicProviderAdapter",
            boundary_policy=ProviderBoundaryPolicy(public_boundary_contract="MediaSourceClient + ProviderAdapterDescriptor"),
            declared_capabilities=frozenset({"library", "playlist"}),
            requirements=frozenset({ProviderExtensionRequirement.PUBLIC_BOUNDARY}),
        )

    @staticmethod
    def missing_public_boundary() -> ProviderAdapterDescriptor:
        descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("missing-boundary"), "Missing Boundary Provider"),
            kind=descriptor.kind,
            adapter_name=descriptor.adapter_name,
            boundary_policy=ProviderBoundaryPolicy(),
            declared_capabilities=descriptor.declared_capabilities,
            requirements=frozenset(),
        )

    @staticmethod
    def requires_authentication() -> ProviderAdapterDescriptor:
        descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("future-requirement"), "Future Requirement Provider"),
            kind=descriptor.kind,
            adapter_name=descriptor.adapter_name,
            boundary_policy=descriptor.boundary_policy,
            declared_capabilities=descriptor.declared_capabilities,
            requirements=frozenset({ProviderExtensionRequirement.PUBLIC_BOUNDARY, ProviderExtensionRequirement.AUTHENTICATION}),
        )

    @staticmethod
    def degraded_capability() -> ProviderAdapterDescriptor:
        descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("degraded-provider"), "Degraded Provider"),
            kind=descriptor.kind,
            adapter_name=descriptor.adapter_name,
            boundary_policy=descriptor.boundary_policy,
            declared_capabilities=frozenset({"library", "playlist"}),
            degraded_capabilities=frozenset({"playlist"}),
            requirements=descriptor.requirements,
        )

    @staticmethod
    def unsupported_media_capability() -> ProviderAdapterDescriptor:
        descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("unsupported-media-provider"), "Unsupported Media Provider"),
            kind=descriptor.kind,
            adapter_name=descriptor.adapter_name,
            boundary_policy=descriptor.boundary_policy,
            declared_capabilities=frozenset({"library"}),
            unsupported_capabilities=frozenset({"stream_resolution"}),
            future_capabilities=frozenset({"provider_playlist_write"}),
            requirements=descriptor.requirements,
        )

    @staticmethod
    def requires_network_discovery() -> ProviderAdapterDescriptor:
        descriptor = FakeProviderExtensionScenarios.future_public_boundary_provider()
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId("future-network-discovery"), "Future Discovery Provider"),
            kind=descriptor.kind,
            adapter_name=descriptor.adapter_name,
            boundary_policy=descriptor.boundary_policy,
            declared_capabilities=descriptor.declared_capabilities,
            requirements=frozenset({ProviderExtensionRequirement.PUBLIC_BOUNDARY, ProviderExtensionRequirement.NETWORK_DISCOVERY}),
        )

    @staticmethod
    def invalid_descriptor() -> ProviderAdapterDescriptor:
        return ProviderAdapterDescriptor(
            provider_ref=ProviderExtensionRef(ProviderExtensionId(""), ""),
            kind=ProviderExtensionKind.LOCAL_DECLARATION,
            adapter_name="",
            declared_capabilities=frozenset(),
        )


def _normalize_capability(capability: str) -> str:
    return capability.strip().lower().replace(" ", "_")


def _normalize_capabilities(capabilities: frozenset[str]) -> frozenset[str]:
    return frozenset(_normalize_capability(capability) for capability in capabilities if capability.strip())


__all__ = [
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
]
