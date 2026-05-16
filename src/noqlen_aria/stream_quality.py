"""Aria Core stream quality, transcoding and network policy models.

Bloco 16 — Stream Quality, Transcoding and Network Policy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning


class StreamQualityPreference(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    AUTOMATIC = auto()
    ORIGINAL = auto()


class StreamQualityReason(Enum):
    PREFERRED_QUALITY = auto()
    AUTOMATIC_BANDWIDTH = auto()
    BANDWIDTH_LIMITED = auto()
    BITRATE_LIMITED = auto()
    NETWORK_DEGRADED = auto()
    SOURCE_UNAVAILABLE = auto()
    FORMAT_UNSUPPORTED = auto()
    TRANSCODING_NEEDED = auto()
    TRANSCODING_UNAVAILABLE = auto()
    OFFLINE_PREFERRED = auto()
    FALLBACK_SELECTED = auto()
    INVALID_POLICY = auto()


class TranscodingUnavailableReason(Enum):
    NONE = auto()
    UNSUPPORTED_SOURCE = auto()
    POLICY_DISABLED = auto()
    SOURCE_UNAVAILABLE = auto()
    INPUT_FORMAT_UNSUPPORTED = auto()
    OUTPUT_FORMAT_UNSUPPORTED = auto()
    BITRATE_UNSUPPORTED = auto()
    INVALID_POLICY = auto()


class TranscodingRequirement(Enum):
    NOT_REQUIRED = auto()
    REQUIRED = auto()
    OPTIONAL = auto()


class TranscodingPreference(Enum):
    NEVER = auto()
    WHEN_NEEDED = auto()
    PREFER_SOURCE = auto()
    PREFER_TRANSCODED = auto()


class NetworkQualityLevel(Enum):
    OFFLINE = auto()
    POOR = auto()
    DEGRADED = auto()
    GOOD = auto()
    EXCELLENT = auto()
    UNKNOWN = auto()


class NetworkPolicyReason(Enum):
    SNAPSHOT_UNAVAILABLE = auto()
    OFFLINE = auto()
    LOW_BANDWIDTH = auto()
    HIGH_LATENCY = auto()
    HIGH_PACKET_LOSS = auto()
    METERED_OR_ROAMING = auto()
    HEALTHY = auto()


@dataclass(frozen=True)
class BitrateLimit:
    max_kbps: int | None = None


@dataclass(frozen=True)
class BandwidthBudget:
    available_kbps: int | None = None
    reserved_kbps: int = 0

    @property
    def usable_kbps(self) -> int | None:
        if self.available_kbps is None:
            return None
        return max(0, self.available_kbps - self.reserved_kbps)


@dataclass(frozen=True)
class StreamQualityProfile:
    preference: StreamQualityPreference
    label: str
    bitrate_kbps: int | None = None
    format_hint: str = ""


@dataclass(frozen=True)
class QualityFallbackPolicy:
    allow_lower_quality: bool = True
    require_supported_format: bool = True
    allow_transcoding_decision: bool = True


@dataclass(frozen=True)
class OfflineQualityPolicy:
    prefer_offline: bool = False
    offline_profile: StreamQualityProfile | None = None
    allow_stream_fallback: bool = True


@dataclass(frozen=True)
class StreamQualityPolicy:
    preference: StreamQualityPreference = StreamQualityPreference.AUTOMATIC
    bitrate_limit: BitrateLimit | None = None
    bandwidth_budget: BandwidthBudget | None = None
    fallback_policy: QualityFallbackPolicy = field(default_factory=QualityFallbackPolicy)
    offline_policy: OfflineQualityPolicy = field(default_factory=OfflineQualityPolicy)


@dataclass(frozen=True)
class StreamQualityDecision:
    profile: StreamQualityProfile | None
    preference: StreamQualityPreference
    reason: StreamQualityReason
    allowed: bool = True
    degraded: bool = False
    needs_transcoding: bool = False
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    summary: str = "Policy decision only; no stream was opened"


@dataclass(frozen=True)
class TranscodingCapability:
    supported: bool = False
    input_formats: frozenset[str] = frozenset()
    output_formats: frozenset[str] = frozenset()
    max_output_bitrate_kbps: int | None = None


@dataclass(frozen=True)
class TranscodingPolicy:
    requirement: TranscodingRequirement = TranscodingRequirement.OPTIONAL
    preference: TranscodingPreference = TranscodingPreference.WHEN_NEEDED
    target_format: str = ""
    target_bitrate_kbps: int | None = None
    allowed: bool = True


@dataclass(frozen=True)
class TranscodingDecision:
    available: bool
    requirement: TranscodingRequirement
    reason: TranscodingUnavailableReason = TranscodingUnavailableReason.NONE
    target_format: str = ""
    target_bitrate_kbps: int | None = None
    summary: str = "Policy decision only; no transcoder was invoked"


@dataclass(frozen=True)
class NetworkConditionSnapshot:
    connected: bool = True
    available_bandwidth_kbps: int | None = None
    latency_ms: int | None = None
    packet_loss_percent: float | None = None
    metered: bool = False
    roaming: bool = False


@dataclass(frozen=True)
class NetworkQualityState:
    level: NetworkQualityLevel = NetworkQualityLevel.UNKNOWN
    metered: bool = False
    roaming: bool = False
    connected: bool = True


@dataclass(frozen=True)
class NetworkPolicyDecision:
    state: NetworkQualityState
    reason: NetworkPolicyReason
    recommended_max_bitrate_kbps: int | None = None
    warnings: tuple[AriaWarning, ...] = field(default_factory=tuple)
    summary: str = "Policy decision only; no network was probed"


class NetworkQualityPolicyService:
    """Evaluate network quality from caller-provided snapshots only."""

    def evaluate_network_quality(self, snapshot: NetworkConditionSnapshot | None) -> AriaResult[NetworkPolicyDecision]:
        if snapshot is None:
            return AriaResult(
                ok=True,
                data=NetworkPolicyDecision(
                    state=NetworkQualityState(level=NetworkQualityLevel.UNKNOWN),
                    reason=NetworkPolicyReason.SNAPSHOT_UNAVAILABLE,
                ),
            )
        if snapshot.available_bandwidth_kbps is not None and snapshot.available_bandwidth_kbps < 0:
            return self._invalid("INVALID_BANDWIDTH", "Network bandwidth must not be negative")
        if snapshot.latency_ms is not None and snapshot.latency_ms < 0:
            return self._invalid("INVALID_LATENCY", "Network latency must not be negative")
        if snapshot.packet_loss_percent is not None and snapshot.packet_loss_percent < 0:
            return self._invalid("INVALID_PACKET_LOSS", "Packet loss must not be negative")
        if not snapshot.connected:
            return self._decision(snapshot, NetworkQualityLevel.OFFLINE, NetworkPolicyReason.OFFLINE, 0)

        bandwidth = snapshot.available_bandwidth_kbps
        latency = snapshot.latency_ms
        loss = snapshot.packet_loss_percent
        if bandwidth is not None and bandwidth < 128:
            return self._decision(snapshot, NetworkQualityLevel.POOR, NetworkPolicyReason.LOW_BANDWIDTH, 64)
        if latency is not None and latency > 1000:
            return self._decision(snapshot, NetworkQualityLevel.POOR, NetworkPolicyReason.HIGH_LATENCY, 64)
        if loss is not None and loss > 15:
            return self._decision(snapshot, NetworkQualityLevel.POOR, NetworkPolicyReason.HIGH_PACKET_LOSS, 64)
        if bandwidth is not None and bandwidth < 512:
            return self._decision(snapshot, NetworkQualityLevel.DEGRADED, NetworkPolicyReason.LOW_BANDWIDTH, 128)
        if latency is not None and latency > 300:
            return self._decision(snapshot, NetworkQualityLevel.DEGRADED, NetworkPolicyReason.HIGH_LATENCY, 128)
        if loss is not None and loss > 5:
            return self._decision(snapshot, NetworkQualityLevel.DEGRADED, NetworkPolicyReason.HIGH_PACKET_LOSS, 128)
        if snapshot.metered or snapshot.roaming:
            return self._decision(snapshot, NetworkQualityLevel.DEGRADED, NetworkPolicyReason.METERED_OR_ROAMING, 192)
        if bandwidth is not None and bandwidth >= 2000:
            return self._decision(snapshot, NetworkQualityLevel.EXCELLENT, NetworkPolicyReason.HEALTHY, 320)
        return self._decision(snapshot, NetworkQualityLevel.GOOD, NetworkPolicyReason.HEALTHY, 256)

    def _decision(
        self,
        snapshot: NetworkConditionSnapshot,
        level: NetworkQualityLevel,
        reason: NetworkPolicyReason,
        recommended_max_bitrate_kbps: int | None,
    ) -> AriaResult[NetworkPolicyDecision]:
        warnings = ()
        if level in {NetworkQualityLevel.OFFLINE, NetworkQualityLevel.POOR, NetworkQualityLevel.DEGRADED}:
            warnings = (AriaWarning(code=reason.name, message="Network quality is limited by provided snapshot"),)
        return AriaResult(
            ok=True,
            data=NetworkPolicyDecision(
                state=NetworkQualityState(
                    level=level,
                    metered=snapshot.metered,
                    roaming=snapshot.roaming,
                    connected=snapshot.connected,
                ),
                reason=reason,
                recommended_max_bitrate_kbps=recommended_max_bitrate_kbps,
                warnings=warnings,
            ),
        )

    def _invalid(self, code: str, message: str) -> AriaResult[NetworkPolicyDecision]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


class TranscodingPolicyService:
    """Evaluate transcoding readiness from declared capabilities only."""

    def evaluate_transcoding(
        self,
        *,
        capability: TranscodingCapability,
        policy: TranscodingPolicy | None = None,
        input_format: str = "",
        source_available: bool = True,
    ) -> AriaResult[TranscodingDecision]:
        policy = policy or TranscodingPolicy()
        if policy.target_bitrate_kbps is not None and policy.target_bitrate_kbps < 0:
            return AriaResult(ok=False, error=AriaError(code="INVALID_BITRATE", message="Target bitrate must not be negative"))
        if capability.max_output_bitrate_kbps is not None and capability.max_output_bitrate_kbps < 0:
            return AriaResult(ok=False, error=AriaError(code="INVALID_CAPABILITY", message="Maximum output bitrate must not be negative"))
        if policy.requirement == TranscodingRequirement.NOT_REQUIRED:
            return AriaResult(ok=True, data=TranscodingDecision(available=False, requirement=policy.requirement))
        if not source_available:
            return self._unavailable(policy, TranscodingUnavailableReason.SOURCE_UNAVAILABLE)
        if not policy.allowed or policy.preference == TranscodingPreference.NEVER:
            return self._unavailable(policy, TranscodingUnavailableReason.POLICY_DISABLED)
        if not capability.supported:
            return self._unavailable(policy, TranscodingUnavailableReason.UNSUPPORTED_SOURCE)
        if input_format and capability.input_formats and input_format not in capability.input_formats:
            return self._unavailable(policy, TranscodingUnavailableReason.INPUT_FORMAT_UNSUPPORTED)
        if policy.target_format and capability.output_formats and policy.target_format not in capability.output_formats:
            return self._unavailable(policy, TranscodingUnavailableReason.OUTPUT_FORMAT_UNSUPPORTED)
        if (
            policy.target_bitrate_kbps is not None
            and capability.max_output_bitrate_kbps is not None
            and policy.target_bitrate_kbps > capability.max_output_bitrate_kbps
        ):
            return self._unavailable(policy, TranscodingUnavailableReason.BITRATE_UNSUPPORTED)
        return AriaResult(
            ok=True,
            data=TranscodingDecision(
                available=True,
                requirement=policy.requirement,
                target_format=policy.target_format,
                target_bitrate_kbps=policy.target_bitrate_kbps,
            ),
        )

    def _unavailable(self, policy: TranscodingPolicy, reason: TranscodingUnavailableReason) -> AriaResult[TranscodingDecision]:
        return AriaResult(
            ok=True,
            data=TranscodingDecision(
                available=False,
                requirement=policy.requirement,
                reason=reason,
                target_format=policy.target_format,
                target_bitrate_kbps=policy.target_bitrate_kbps,
            ),
        )


class QualityPolicyService:
    """Evaluate quality decisions from explicit policy and capability snapshots."""

    DEFAULT_PROFILES = (
        StreamQualityProfile(StreamQualityPreference.LOW, "Low", 96, "mp3"),
        StreamQualityProfile(StreamQualityPreference.MEDIUM, "Medium", 192, "mp3"),
        StreamQualityProfile(StreamQualityPreference.HIGH, "High", 320, "mp3"),
        StreamQualityProfile(StreamQualityPreference.ORIGINAL, "Original", None, ""),
    )

    def evaluate_stream_quality(
        self,
        policy: StreamQualityPolicy | None = None,
        *,
        profiles: tuple[StreamQualityProfile, ...] = DEFAULT_PROFILES,
        network_decision: NetworkPolicyDecision | None = None,
        source_available: bool = True,
        source_degraded: bool = False,
        source_format: str = "",
        renderer_supported_formats: frozenset[str] = frozenset(),
        transcoding_decision: TranscodingDecision | None = None,
    ) -> AriaResult[StreamQualityDecision]:
        policy = policy or StreamQualityPolicy()
        invalid = self._validate_policy(policy, profiles)
        if invalid is not None:
            return invalid
        if policy.offline_policy.prefer_offline:
            offline_profile = policy.offline_policy.offline_profile or self._profile_for(StreamQualityPreference.MEDIUM, profiles)
            return self._ok(offline_profile, offline_profile.preference, StreamQualityReason.OFFLINE_PREFERRED)
        if not source_available:
            return self._ok(None, policy.preference, StreamQualityReason.SOURCE_UNAVAILABLE, allowed=False, degraded=True)

        selected = self._select_profile(policy.preference, profiles, policy.bandwidth_budget, network_decision)
        reason = StreamQualityReason.PREFERRED_QUALITY
        if policy.preference == StreamQualityPreference.AUTOMATIC:
            reason = StreamQualityReason.AUTOMATIC_BANDWIDTH
        if policy.bandwidth_budget and policy.bandwidth_budget.usable_kbps is not None:
            if selected.bitrate_kbps is not None and selected.bitrate_kbps >= policy.bandwidth_budget.usable_kbps:
                reason = StreamQualityReason.BANDWIDTH_LIMITED
            elif policy.preference == StreamQualityPreference.AUTOMATIC and policy.bandwidth_budget.usable_kbps < 320:
                reason = StreamQualityReason.BANDWIDTH_LIMITED
        if policy.bitrate_limit and policy.bitrate_limit.max_kbps is not None:
            if selected.bitrate_kbps is not None and selected.bitrate_kbps > policy.bitrate_limit.max_kbps:
                selected = self._highest_profile_at_or_below(policy.bitrate_limit.max_kbps, profiles)
                reason = StreamQualityReason.BITRATE_LIMITED

        warnings = ()
        degraded = source_degraded
        if network_decision and network_decision.state.level in {NetworkQualityLevel.POOR, NetworkQualityLevel.DEGRADED, NetworkQualityLevel.OFFLINE}:
            degraded = True
            reason = StreamQualityReason.NETWORK_DEGRADED
            warnings = network_decision.warnings
        if source_degraded and not warnings:
            warnings = (AriaWarning(code="SOURCE_DEGRADED", message="Source is degraded by provided state"),)

        if source_format and renderer_supported_formats and source_format not in renderer_supported_formats:
            needs_transcoding = policy.fallback_policy.allow_transcoding_decision
            if transcoding_decision and transcoding_decision.available:
                return self._ok(selected, selected.preference, StreamQualityReason.TRANSCODING_NEEDED, degraded=degraded, needs_transcoding=needs_transcoding, warnings=warnings)
            return self._ok(
                selected if policy.fallback_policy.allow_lower_quality else None,
                selected.preference,
                StreamQualityReason.FORMAT_UNSUPPORTED if needs_transcoding else StreamQualityReason.FALLBACK_SELECTED,
                allowed=not policy.fallback_policy.require_supported_format,
                degraded=True,
                needs_transcoding=needs_transcoding,
                warnings=warnings + (AriaWarning(code="FORMAT_UNSUPPORTED", message="Format support requires a future layer decision"),),
            )

        return self._ok(selected, selected.preference, reason, degraded=degraded, warnings=warnings)

    def evaluate_offline_quality(
        self,
        offline_policy: OfflineQualityPolicy,
        *,
        profiles: tuple[StreamQualityProfile, ...] = DEFAULT_PROFILES,
    ) -> AriaResult[StreamQualityDecision]:
        invalid = self._validate_profiles(profiles)
        if invalid is not None:
            return invalid
        profile = offline_policy.offline_profile or self._profile_for(StreamQualityPreference.MEDIUM, profiles)
        if offline_policy.prefer_offline:
            return self._ok(profile, profile.preference, StreamQualityReason.OFFLINE_PREFERRED)
        return self._ok(profile, profile.preference, StreamQualityReason.FALLBACK_SELECTED)

    def _select_profile(
        self,
        preference: StreamQualityPreference,
        profiles: tuple[StreamQualityProfile, ...],
        bandwidth_budget: BandwidthBudget | None,
        network_decision: NetworkPolicyDecision | None,
    ) -> StreamQualityProfile:
        if preference != StreamQualityPreference.AUTOMATIC:
            return self._profile_for(preference, profiles)
        limit = None
        if bandwidth_budget and bandwidth_budget.usable_kbps is not None:
            limit = bandwidth_budget.usable_kbps
        if network_decision and network_decision.recommended_max_bitrate_kbps is not None:
            limit = min(limit, network_decision.recommended_max_bitrate_kbps) if limit is not None else network_decision.recommended_max_bitrate_kbps
        if limit is None:
            return self._profile_for(StreamQualityPreference.MEDIUM, profiles)
        return self._highest_profile_at_or_below(limit, profiles)

    def _profile_for(self, preference: StreamQualityPreference, profiles: tuple[StreamQualityProfile, ...]) -> StreamQualityProfile:
        for profile in profiles:
            if profile.preference == preference:
                return profile
        return profiles[0]

    def _highest_profile_at_or_below(self, max_kbps: int, profiles: tuple[StreamQualityProfile, ...]) -> StreamQualityProfile:
        candidates = [profile for profile in profiles if profile.bitrate_kbps is not None and profile.bitrate_kbps <= max_kbps]
        if not candidates:
            return self._profile_for(StreamQualityPreference.LOW, profiles)
        return max(candidates, key=lambda profile: profile.bitrate_kbps or 0)

    def _validate_policy(self, policy: StreamQualityPolicy, profiles: tuple[StreamQualityProfile, ...]) -> AriaResult[StreamQualityDecision] | None:
        invalid_profiles = self._validate_profiles(profiles)
        if invalid_profiles is not None:
            return invalid_profiles
        if policy.bitrate_limit and policy.bitrate_limit.max_kbps is not None and policy.bitrate_limit.max_kbps < 0:
            return AriaResult(ok=False, error=AriaError(code="INVALID_BITRATE", message="Bitrate limit must not be negative"))
        if policy.bandwidth_budget:
            if policy.bandwidth_budget.available_kbps is not None and policy.bandwidth_budget.available_kbps < 0:
                return AriaResult(ok=False, error=AriaError(code="INVALID_BANDWIDTH", message="Bandwidth budget must not be negative"))
            if policy.bandwidth_budget.reserved_kbps < 0:
                return AriaResult(ok=False, error=AriaError(code="INVALID_BANDWIDTH", message="Reserved bandwidth must not be negative"))
        return None

    def _validate_profiles(self, profiles: tuple[StreamQualityProfile, ...]) -> AriaResult[StreamQualityDecision] | None:
        if not profiles:
            return AriaResult(ok=False, error=AriaError(code="INVALID_POLICY", message="At least one quality profile is required"))
        for profile in profiles:
            if profile.bitrate_kbps is not None and profile.bitrate_kbps < 0:
                return AriaResult(ok=False, error=AriaError(code="INVALID_BITRATE", message="Profile bitrate must not be negative"))
        return None

    def _ok(
        self,
        profile: StreamQualityProfile | None,
        preference: StreamQualityPreference,
        reason: StreamQualityReason,
        *,
        allowed: bool = True,
        degraded: bool = False,
        needs_transcoding: bool = False,
        warnings: tuple[AriaWarning, ...] = (),
    ) -> AriaResult[StreamQualityDecision]:
        return AriaResult(
            ok=True,
            data=StreamQualityDecision(
                profile=profile,
                preference=preference,
                reason=reason,
                allowed=allowed,
                degraded=degraded,
                needs_transcoding=needs_transcoding,
                warnings=warnings,
            ),
        )


class FakeQualityPolicyScenarios:
    """Deterministic local scenarios for tests and future UI prototypes."""

    @staticmethod
    def high_quality_with_sufficient_bandwidth() -> StreamQualityPolicy:
        return StreamQualityPolicy(
            preference=StreamQualityPreference.HIGH,
            bandwidth_budget=BandwidthBudget(available_kbps=1000),
        )

    @staticmethod
    def low_bandwidth_automatic() -> StreamQualityPolicy:
        return StreamQualityPolicy(
            preference=StreamQualityPreference.AUTOMATIC,
            bandwidth_budget=BandwidthBudget(available_kbps=128),
        )

    @staticmethod
    def offline_preferred() -> StreamQualityPolicy:
        return StreamQualityPolicy(
            preference=StreamQualityPreference.AUTOMATIC,
            offline_policy=OfflineQualityPolicy(
                prefer_offline=True,
                offline_profile=StreamQualityProfile(StreamQualityPreference.LOW, "Offline Low", 96, "mp3"),
            ),
        )


__all__ = [
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
]
