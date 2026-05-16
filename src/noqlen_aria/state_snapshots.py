"""State snapshots and deterministic fake end-to-end flows for Aria Core.

Bloco 20 is in-memory and local-only. It never calls real providers, network,
filesystem persistence, Android APIs, playback, stream resolution, or provider
mutation paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass, fields
from enum import Enum, auto
from typing import Any, NewType

from noqlen_aria.contracts import AriaError, AriaResult, AriaWarning, FakeControlClient, safe_serialize, sanitize_text

AriaSnapshotId = NewType("AriaSnapshotId", str)
FakeFlowId = NewType("FakeFlowId", str)

_REDACTED = "[redacted]"
_UNAVAILABLE = "[unavailable]"
_DEFAULT_SNAPSHOT_VERSION = "aria-state-snapshot-v1"

_SECRET_KEY_MARKERS = (
    "password",
    "passwd",
    "token",
    "secret",
    "credential",
    "authorization",
    "api_key",
    "apikey",
)
_RAW_PATH_MARKERS = (
    "/home/",
    "/users/",
    "c:\\users",
    "raw_path",
    "personal path",
    "music library",
)
_RAW_LOG_MARKERS = (
    "traceback",
    "stacktrace",
    "exception:",
    "raw log",
    "provider exception",
)


class AriaSnapshotScope(Enum):
    PROFILE = auto()
    PREFERENCES = auto()
    LIBRARY = auto()
    QUEUE = auto()
    NOW_PLAYING = auto()
    DIAGNOSTICS = auto()
    SMART_PLAYLISTS = auto()
    RADIO = auto()
    OFFLINE_CACHE = auto()
    QUALITY = auto()
    CAPABILITIES = auto()
    ALL = auto()


class AriaSnapshotValidationIssue(Enum):
    EMPTY_SNAPSHOT_ID = auto()
    INVALID_SCOPE = auto()
    UNKNOWN_SECTION = auto()
    EMPTY_SECTION_NAME = auto()
    UNSAFE_VALUE_REDACTED = auto()
    UNSUPPORTED_VALUE_REDACTED = auto()


class AriaSnapshotUnavailableReason(Enum):
    NONE = auto()
    SECTION_NOT_PROVIDED = auto()
    INVALID_SCOPE = auto()
    UNSAFE_VALUE_REDACTED = auto()
    UNSUPPORTED_VALUE = auto()


@dataclass(frozen=True)
class AriaSnapshotMetadata:
    snapshot_id: AriaSnapshotId = AriaSnapshotId("aria-snapshot")
    version: str = _DEFAULT_SNAPSHOT_VERSION
    created_by: str = "aria-core"
    deterministic: bool = True
    description: str = "Sanitized Aria Core state snapshot"


@dataclass(frozen=True)
class AriaSnapshotRedactionPolicy:
    redact_secret_like_keys: bool = True
    redact_raw_paths: bool = True
    exclude_raw_logs: bool = True
    redact_unsupported_objects: bool = True
    redacted_value: str = _REDACTED


@dataclass(frozen=True)
class AriaSnapshotSection:
    name: str
    scope: AriaSnapshotScope
    data: Any = None
    unavailable_reason: AriaSnapshotUnavailableReason = AriaSnapshotUnavailableReason.NONE
    redacted: bool = False


@dataclass(frozen=True)
class AriaStateSnapshot:
    metadata: AriaSnapshotMetadata = field(default_factory=AriaSnapshotMetadata)
    sections: tuple[AriaSnapshotSection, ...] = field(default_factory=tuple)
    issues: tuple[AriaSnapshotValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[AriaSnapshotUnavailableReason, ...] = field(default_factory=tuple)
    sanitized: bool = True

    def section(self, name: str) -> AriaSnapshotSection | None:
        normalized = _normalize_section_name(name)
        for section in self.sections:
            if _normalize_section_name(section.name) == normalized:
                return section
        return None


@dataclass(frozen=True)
class AriaSnapshotResult:
    success: bool
    snapshot: AriaStateSnapshot | None = None
    issues: tuple[AriaSnapshotValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[AriaSnapshotUnavailableReason, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AriaSnapshotDiffEntry:
    section_name: str
    change_type: str
    before: Any = None
    after: Any = None


@dataclass(frozen=True)
class AriaSnapshotDiff:
    before_id: AriaSnapshotId
    after_id: AriaSnapshotId
    entries: tuple[AriaSnapshotDiffEntry, ...] = field(default_factory=tuple)

    @property
    def changed(self) -> bool:
        return bool(self.entries)


class FakeFlowStepKind(Enum):
    SOURCE = auto()
    LIBRARY = auto()
    QUEUE = auto()
    NOW_PLAYING = auto()
    PLAYBACK_INTENT = auto()
    DIAGNOSTICS = auto()
    PROFILE = auto()
    PREFERENCES = auto()
    SMART_PLAYLIST = auto()
    RADIO = auto()
    OFFLINE_CACHE = auto()
    QUALITY = auto()
    CAPABILITY = auto()
    SAFETY = auto()


class FakeFlowValidationIssue(Enum):
    UNKNOWN_SCENARIO = auto()
    SOURCE_UNAVAILABLE = auto()
    LIBRARY_UNAVAILABLE = auto()
    QUEUE_PREVIEW_FAILED = auto()
    PLAYBACK_PREVIEW_BLOCKED = auto()
    RADIO_UNAVAILABLE = auto()
    POLICY_DEGRADED = auto()
    UNSAFE_BOUNDARY_ATTEMPT = auto()


class FakeFlowUnavailableReason(Enum):
    NONE = auto()
    SOURCE_UNAVAILABLE = auto()
    LIBRARY_UNAVAILABLE = auto()
    RADIO_STATION_UNAVAILABLE = auto()
    PLAYBACK_BLOCKED = auto()
    POLICY_BLOCKED = auto()
    UNKNOWN_SCENARIO = auto()


@dataclass(frozen=True)
class FakeFlowStep:
    index: int
    kind: FakeFlowStepKind
    label: str


@dataclass(frozen=True)
class FakeFlowStepResult:
    step: FakeFlowStep
    ok: bool
    payload: Any = None
    issues: tuple[FakeFlowValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[FakeFlowUnavailableReason, ...] = field(default_factory=tuple)
    provider_called: bool = False
    network_called: bool = False
    filesystem_touched: bool = False
    playback_started: bool = False
    android_api_used: bool = False
    provider_mutated: bool = False
    real_queue_mutated: bool = False


@dataclass(frozen=True)
class FakeFlowTrace:
    flow_id: FakeFlowId
    steps: tuple[FakeFlowStepResult, ...] = field(default_factory=tuple)
    deterministic: bool = True
    local_only: bool = True


@dataclass(frozen=True)
class FakeFlowScenario:
    flow_id: FakeFlowId
    display_name: str
    description: str = ""


@dataclass(frozen=True)
class FakeFlowResult:
    success: bool
    scenario: FakeFlowScenario
    trace: FakeFlowTrace
    degraded: bool = False
    issues: tuple[FakeFlowValidationIssue, ...] = field(default_factory=tuple)
    unavailable_reasons: tuple[FakeFlowUnavailableReason, ...] = field(default_factory=tuple)


class AriaSnapshotService:
    _SECTION_SCOPES = {
        "profile": AriaSnapshotScope.PROFILE,
        "preferences": AriaSnapshotScope.PREFERENCES,
        "library": AriaSnapshotScope.LIBRARY,
        "queue": AriaSnapshotScope.QUEUE,
        "now_playing": AriaSnapshotScope.NOW_PLAYING,
        "diagnostics": AriaSnapshotScope.DIAGNOSTICS,
        "smart_playlists": AriaSnapshotScope.SMART_PLAYLISTS,
        "radio": AriaSnapshotScope.RADIO,
        "offline_cache": AriaSnapshotScope.OFFLINE_CACHE,
        "quality": AriaSnapshotScope.QUALITY,
        "capabilities": AriaSnapshotScope.CAPABILITIES,
    }

    def __init__(self, redaction_policy: AriaSnapshotRedactionPolicy | None = None) -> None:
        self._redaction_policy = redaction_policy or AriaSnapshotRedactionPolicy()

    def build_snapshot(
        self,
        state: dict[str, Any] | None = None,
        *,
        scopes: tuple[AriaSnapshotScope, ...] = (AriaSnapshotScope.ALL,),
        metadata: AriaSnapshotMetadata | None = None,
    ) -> AriaResult[AriaSnapshotResult]:
        metadata = metadata or AriaSnapshotMetadata()
        issues = self._validate_metadata(metadata) + self._validate_scopes(scopes)
        if any(issue in {AriaSnapshotValidationIssue.EMPTY_SNAPSHOT_ID, AriaSnapshotValidationIssue.INVALID_SCOPE} for issue in issues):
            return AriaResult(ok=True, data=AriaSnapshotResult(success=False, issues=_dedupe_snapshot_issues(issues), unavailable_reasons=(AriaSnapshotUnavailableReason.INVALID_SCOPE,)))

        selected_scopes = self._expand_scopes(scopes)
        sections: list[AriaSnapshotSection] = []
        unavailable: tuple[AriaSnapshotUnavailableReason, ...] = ()
        for raw_name, raw_value in (state or {}).items():
            section_name = _normalize_section_name(raw_name)
            section_scope = self._SECTION_SCOPES.get(section_name)
            if not section_name:
                issues += (AriaSnapshotValidationIssue.EMPTY_SECTION_NAME,)
                continue
            if section_scope is None:
                issues += (AriaSnapshotValidationIssue.UNKNOWN_SECTION,)
                unavailable += (AriaSnapshotUnavailableReason.SECTION_NOT_PROVIDED,)
                continue
            if section_scope not in selected_scopes:
                continue
            redacted = _RedactionTracker()
            data = self._redact(raw_value, self._redaction_policy, redacted, key_hint=section_name)
            if redacted.unsafe_redacted:
                issues += (AriaSnapshotValidationIssue.UNSAFE_VALUE_REDACTED,)
                unavailable += (AriaSnapshotUnavailableReason.UNSAFE_VALUE_REDACTED,)
            if redacted.unsupported_redacted:
                issues += (AriaSnapshotValidationIssue.UNSUPPORTED_VALUE_REDACTED,)
                unavailable += (AriaSnapshotUnavailableReason.UNSUPPORTED_VALUE,)
            sections.append(AriaSnapshotSection(section_name, section_scope, data, redacted=redacted.any_redacted))

        snapshot = AriaStateSnapshot(
            metadata=metadata,
            sections=tuple(sorted(sections, key=lambda section: section.name)),
            issues=_dedupe_snapshot_issues(issues),
            unavailable_reasons=_dedupe_unavailable(unavailable),
            sanitized=True,
        )
        return AriaResult(ok=True, data=AriaSnapshotResult(success=True, snapshot=snapshot, issues=snapshot.issues, unavailable_reasons=snapshot.unavailable_reasons))

    def validate_snapshot(self, snapshot: AriaStateSnapshot) -> AriaResult[tuple[AriaSnapshotValidationIssue, ...]]:
        issues = self._validate_metadata(snapshot.metadata)
        for section in snapshot.sections:
            if not section.name.strip():
                issues += (AriaSnapshotValidationIssue.EMPTY_SECTION_NAME,)
            if _normalize_section_name(section.name) not in self._SECTION_SCOPES:
                issues += (AriaSnapshotValidationIssue.UNKNOWN_SECTION,)
        return AriaResult(ok=True, data=_dedupe_snapshot_issues(issues + snapshot.issues))

    def redact_value(self, value: Any) -> AriaResult[Any]:
        tracker = _RedactionTracker()
        return AriaResult(ok=True, data=self._redact(value, self._redaction_policy, tracker))

    def _validate_metadata(self, metadata: AriaSnapshotMetadata) -> tuple[AriaSnapshotValidationIssue, ...]:
        if not str(metadata.snapshot_id).strip():
            return (AriaSnapshotValidationIssue.EMPTY_SNAPSHOT_ID,)
        return ()

    def _validate_scopes(self, scopes: tuple[AriaSnapshotScope, ...]) -> tuple[AriaSnapshotValidationIssue, ...]:
        if not scopes:
            return (AriaSnapshotValidationIssue.INVALID_SCOPE,)
        if any(not isinstance(scope, AriaSnapshotScope) for scope in scopes):
            return (AriaSnapshotValidationIssue.INVALID_SCOPE,)
        return ()

    def _expand_scopes(self, scopes: tuple[AriaSnapshotScope, ...]) -> frozenset[AriaSnapshotScope]:
        if AriaSnapshotScope.ALL in scopes:
            return frozenset(scope for scope in AriaSnapshotScope if scope != AriaSnapshotScope.ALL)
        return frozenset(scopes)

    def _redact(
        self,
        value: Any,
        policy: AriaSnapshotRedactionPolicy,
        tracker: "_RedactionTracker",
        *,
        key_hint: str = "",
    ) -> Any:
        if policy.redact_secret_like_keys and _is_secret_like_key(key_hint):
            tracker.unsafe_redacted = True
            return None
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, str):
            return self._redact_text(value, policy, tracker)
        if isinstance(value, (int, float, bool)) or value is None:
            return value
        if is_dataclass(value):
            return {
                item.name: self._redact(getattr(value, item.name), policy, tracker, key_hint=item.name)
                for item in fields(value)
                if not (policy.redact_secret_like_keys and _is_secret_like_key(item.name))
            }
        if isinstance(value, dict):
            output: dict[str, Any] = {}
            for raw_key, raw_item in value.items():
                key = str(raw_key)
                if policy.redact_secret_like_keys and _is_secret_like_key(key):
                    tracker.unsafe_redacted = True
                    continue
                output[key] = self._redact(raw_item, policy, tracker, key_hint=key)
            return output
        if isinstance(value, (list, tuple, frozenset, set)):
            return [self._redact(item, policy, tracker) for item in value]
        if policy.redact_unsupported_objects:
            tracker.unsupported_redacted = True
            return _UNAVAILABLE
        return safe_serialize(value)

    def _redact_text(self, value: str, policy: AriaSnapshotRedactionPolicy, tracker: "_RedactionTracker") -> str:
        safe = sanitize_text(value)
        lowered = value.lower()
        if safe != value:
            tracker.unsafe_redacted = True
            return policy.redacted_value
        if policy.redact_raw_paths and any(marker in lowered for marker in _RAW_PATH_MARKERS):
            tracker.unsafe_redacted = True
            return policy.redacted_value
        if policy.exclude_raw_logs and ("\n" in value or "\r" in value or any(marker in lowered for marker in _RAW_LOG_MARKERS)):
            tracker.unsafe_redacted = True
            return policy.redacted_value
        return value


class AriaSnapshotDiffService:
    def diff(self, before: AriaStateSnapshot, after: AriaStateSnapshot) -> AriaResult[AriaSnapshotDiff]:
        before_sections = {section.name: section.data for section in before.sections}
        after_sections = {section.name: section.data for section in after.sections}
        entries: list[AriaSnapshotDiffEntry] = []
        for section_name in sorted(set(before_sections) | set(after_sections)):
            if section_name not in before_sections:
                entries.append(AriaSnapshotDiffEntry(section_name, "added", after=after_sections[section_name]))
            elif section_name not in after_sections:
                entries.append(AriaSnapshotDiffEntry(section_name, "removed", before=before_sections[section_name]))
            elif before_sections[section_name] != after_sections[section_name]:
                entries.append(AriaSnapshotDiffEntry(section_name, "changed", before_sections[section_name], after_sections[section_name]))
        return AriaResult(ok=True, data=AriaSnapshotDiff(before.metadata.snapshot_id, after.metadata.snapshot_id, tuple(entries)))


class FakeFlowRunner:
    SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS = FakeFlowScenario(
        FakeFlowId("source-library-queue-now-playing-diagnostics"),
        "Source to diagnostics fake flow",
    )
    PROFILE_PREFERENCES_SMART_PLAYLIST_QUEUE_PREVIEW = FakeFlowScenario(
        FakeFlowId("profile-preferences-smart-playlist-queue-preview"),
        "Profile preferences to smart playlist queue preview fake flow",
    )
    RADIO_AVAILABILITY_PLAYBACK_INTENT_PREVIEW = FakeFlowScenario(
        FakeFlowId("radio-availability-playback-intent-preview"),
        "Radio availability to playback intent preview fake flow",
    )
    OFFLINE_CACHE_QUALITY_CAPABILITY_SUMMARY = FakeFlowScenario(
        FakeFlowId("offline-cache-quality-capability-summary"),
        "Offline cache to quality capability summary fake flow",
    )
    DEGRADED_SOURCE_PARTIAL_FLOW = FakeFlowScenario(
        FakeFlowId("degraded-source-partial-flow"),
        "Degraded source partial fake flow",
    )

    def run(self, scenario: FakeFlowScenario | FakeFlowId | str) -> AriaResult[FakeFlowResult]:
        scenario = self._scenario_for(scenario)
        if scenario is None:
            unknown = FakeFlowScenario(FakeFlowId("unknown"), "Unknown fake flow")
            trace = FakeFlowTrace(unknown.flow_id)
            return AriaResult(ok=False, error=AriaError("UNKNOWN_FAKE_FLOW", "Fake flow scenario is not supported"), data=FakeFlowResult(False, unknown, trace, issues=(FakeFlowValidationIssue.UNKNOWN_SCENARIO,), unavailable_reasons=(FakeFlowUnavailableReason.UNKNOWN_SCENARIO,)))
        if scenario.flow_id == self.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS.flow_id:
            return self._run_source_library_queue_now_playing_diagnostics(scenario)
        if scenario.flow_id == self.PROFILE_PREFERENCES_SMART_PLAYLIST_QUEUE_PREVIEW.flow_id:
            return self._run_profile_preferences_smart_playlist_queue_preview(scenario)
        if scenario.flow_id == self.RADIO_AVAILABILITY_PLAYBACK_INTENT_PREVIEW.flow_id:
            return self._run_radio_availability_playback_intent_preview(scenario)
        if scenario.flow_id == self.OFFLINE_CACHE_QUALITY_CAPABILITY_SUMMARY.flow_id:
            return self._run_offline_cache_quality_capability_summary(scenario)
        if scenario.flow_id == self.DEGRADED_SOURCE_PARTIAL_FLOW.flow_id:
            return self._run_degraded_source_partial_flow(scenario)
        return AriaResult(ok=False, error=AriaError("UNKNOWN_FAKE_FLOW", "Fake flow scenario is not supported"))

    def _run_source_library_queue_now_playing_diagnostics(self, scenario: FakeFlowScenario) -> AriaResult[FakeFlowResult]:
        from noqlen_aria.library import LibraryBrowseCategory, LibraryBrowseRequest, LibraryBrowseService
        from noqlen_aria.media_source import FakeMediaSourceClient
        from noqlen_aria.now_playing import NowPlayingService
        from noqlen_aria.playback_intents import PlaybackIntent, PlaybackIntentService, PlaybackIntentType
        from noqlen_aria.queue import QueueItem, QueueItemId, QueueService, QueueState
        from noqlen_aria.services import DiagnosticsService

        source = FakeMediaSourceClient.with_full_library()
        source_info = source.get_source_info().data
        browse = LibraryBrowseService(source).browse(LibraryBrowseRequest(LibraryBrowseCategory.TRACKS)).data
        queue = QueueState()
        queue_service = QueueService()
        for index, item in enumerate(browse.items if browse else ()):
            result = queue_service.add_item(queue, QueueItem.from_library_item(QueueItemId(f"flow-queue-item-{index + 1}"), item.as_library_item()))
            queue = result.data.queue_state
        now_playing = NowPlayingService().build_from_queue(queue).data
        playback = PlaybackIntentService().preview(PlaybackIntent(PlaybackIntentType.PLAY), now_playing, queue).data
        diagnostics = DiagnosticsService(FakeControlClient()).collect().data
        steps = (
            self._step(1, FakeFlowStepKind.SOURCE, "source", source_info),
            self._step(2, FakeFlowStepKind.LIBRARY, "library tracks", browse),
            self._step(3, FakeFlowStepKind.QUEUE, "queue preview", queue),
            self._step(4, FakeFlowStepKind.NOW_PLAYING, "now playing intent state", now_playing),
            self._step(5, FakeFlowStepKind.PLAYBACK_INTENT, "playback intent preview", playback),
            self._step(6, FakeFlowStepKind.DIAGNOSTICS, "diagnostics", diagnostics),
        )
        return self._result(scenario, steps)

    def _run_profile_preferences_smart_playlist_queue_preview(self, scenario: FakeFlowScenario) -> AriaResult[FakeFlowResult]:
        from noqlen_aria.profiles_preferences_backup import PreferenceUpdateIntent, PreferencesService, ProfileOperationIntent, ProfileOperationType, ProfilesService, UserPreferenceKey, UserPreferencesState
        from noqlen_aria.queue import QueueItem, QueueItemId, QueueService, QueueState
        from noqlen_aria.smart_playlists import FakeSmartPlaylistScenarios, SmartPlaylistEvaluationContext, SmartPlaylistService

        profile_preview = ProfilesService().preview_create_profile(ProfileOperationIntent(ProfileOperationType.CREATE_PROFILE, "Bloco 20 Listener")).data
        preference_state = PreferencesService().apply_to_state(UserPreferencesState(), PreferenceUpdateIntent(UserPreferenceKey("playback.quality"), "balanced")).data
        definition = FakeSmartPlaylistScenarios.favorite_tracks_definition()
        preview = SmartPlaylistService().build_preview(definition, SmartPlaylistEvaluationContext(FakeSmartPlaylistScenarios.candidates())).data
        queue = QueueState(label="Smart playlist queue preview")
        queue_service = QueueService()
        for index, item in enumerate(preview.items):
            result = queue_service.add_item(queue, QueueItem.from_library_item(QueueItemId(f"smart-preview-item-{index + 1}"), item))
            queue = result.data.queue_state
        steps = (
            self._step(1, FakeFlowStepKind.PROFILE, "profile preview", profile_preview),
            self._step(2, FakeFlowStepKind.PREFERENCES, "preferences preview", preference_state),
            self._step(3, FakeFlowStepKind.SMART_PLAYLIST, "smart playlist preview", preview),
            self._step(4, FakeFlowStepKind.QUEUE, "local queue preview", queue),
        )
        return self._result(scenario, steps)

    def _run_radio_availability_playback_intent_preview(self, scenario: FakeFlowScenario) -> AriaResult[FakeFlowResult]:
        from noqlen_aria.internet_radio import FakeRadioScenarios
        from noqlen_aria.now_playing import NowPlayingItem, NowPlayingService, PlaybackAvailabilityReason
        from noqlen_aria.playback_intents import PlaybackIntent, PlaybackIntentService, PlaybackIntentType
        from noqlen_aria.queue import QueueState

        station = FakeRadioScenarios.unavailable_station()
        item = NowPlayingItem(display_name=station.display_name)
        now_playing = NowPlayingService().build_unavailable_state(item, reason=PlaybackAvailabilityReason.SOURCE_UNAVAILABLE, message="Radio station unavailable").data
        playback = PlaybackIntentService().preview(PlaybackIntent(PlaybackIntentType.PLAY), now_playing, QueueState()).data
        steps = (
            self._step(1, FakeFlowStepKind.RADIO, "radio station", station, ok=False, issues=(FakeFlowValidationIssue.RADIO_UNAVAILABLE,), unavailable=(FakeFlowUnavailableReason.RADIO_STATION_UNAVAILABLE,)),
            self._step(2, FakeFlowStepKind.PLAYBACK_INTENT, "blocked playback intent preview", playback, ok=False, issues=(FakeFlowValidationIssue.PLAYBACK_PREVIEW_BLOCKED,), unavailable=(FakeFlowUnavailableReason.PLAYBACK_BLOCKED,)),
        )
        return self._result(scenario, steps, degraded=True)

    def _run_offline_cache_quality_capability_summary(self, scenario: FakeFlowScenario) -> AriaResult[FakeFlowResult]:
        from noqlen_aria.offline_cache import CacheItemId, CacheOperationIntent, CacheOperationType, CachePolicyMode, CacheSourceId, OfflineCachePolicyService, StorageBudget
        from noqlen_aria.playback_capabilities import AudioOutputCapabilityService, FakePlaybackCapabilityScenarios, PlaybackCapabilityService
        from noqlen_aria.stream_quality import BandwidthBudget, NetworkConditionSnapshot, NetworkQualityPolicyService, QualityPolicyService, StreamQualityPolicy, StreamQualityPreference

        cache_service = OfflineCachePolicyService()
        offline = cache_service.evaluate_offline_availability(source_supports_cache=True, item_is_cacheable=True, source_available=True).data
        cache = cache_service.preview_cache_operation(CacheOperationIntent(CacheOperationType.ADD_TO_CACHE, CacheItemId("cache-track-1"), CacheSourceId("fake-source-1"), 128), cache_policy_mode=CachePolicyMode.BALANCED, budget=StorageBudget(1024, used_bytes=256)).data
        network = NetworkQualityPolicyService().evaluate_network_quality(NetworkConditionSnapshot(available_bandwidth_kbps=512, latency_ms=30)).data
        quality = QualityPolicyService().evaluate_stream_quality(StreamQualityPolicy(preference=StreamQualityPreference.AUTOMATIC, bandwidth_budget=BandwidthBudget(available_kbps=512)), network_decision=network).data
        output = AudioOutputCapabilityService().evaluate_output_readiness(route=FakePlaybackCapabilityScenarios.normal_system_audio_route(), device=FakePlaybackCapabilityScenarios.available_device()).data
        summary = PlaybackCapabilityService().build_summary().data
        steps = (
            self._step(1, FakeFlowStepKind.OFFLINE_CACHE, "offline availability", offline),
            self._step(2, FakeFlowStepKind.OFFLINE_CACHE, "cache policy preview", cache),
            self._step(3, FakeFlowStepKind.QUALITY, "quality decision", quality),
            self._step(4, FakeFlowStepKind.CAPABILITY, "output readiness", output),
            self._step(5, FakeFlowStepKind.CAPABILITY, "capability summary", summary),
        )
        return self._result(scenario, steps)

    def _run_degraded_source_partial_flow(self, scenario: FakeFlowScenario) -> AriaResult[FakeFlowResult]:
        from noqlen_aria.library import LibraryBrowseCategory, LibraryBrowseRequest, LibraryBrowseService
        from noqlen_aria.media_source import FakeMediaSourceClient
        from noqlen_aria.queue import QueueState

        source = FakeMediaSourceClient.unavailable()
        source_info = source.get_source_info().data
        browse_result = LibraryBrowseService(source).browse(LibraryBrowseRequest(LibraryBrowseCategory.TRACKS))
        steps = (
            self._step(1, FakeFlowStepKind.SOURCE, "source unavailable", source_info, ok=False, issues=(FakeFlowValidationIssue.SOURCE_UNAVAILABLE,), unavailable=(FakeFlowUnavailableReason.SOURCE_UNAVAILABLE,)),
            self._step(2, FakeFlowStepKind.LIBRARY, "library unavailable", browse_result.error, ok=False, issues=(FakeFlowValidationIssue.LIBRARY_UNAVAILABLE,), unavailable=(FakeFlowUnavailableReason.LIBRARY_UNAVAILABLE,)),
            self._step(3, FakeFlowStepKind.QUEUE, "empty local queue preview", QueueState()),
        )
        return self._result(scenario, steps, degraded=True)

    def _scenario_for(self, scenario: FakeFlowScenario | FakeFlowId | str) -> FakeFlowScenario | None:
        if isinstance(scenario, FakeFlowScenario):
            return scenario
        flow_id = str(scenario)
        for candidate in (
            self.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS,
            self.PROFILE_PREFERENCES_SMART_PLAYLIST_QUEUE_PREVIEW,
            self.RADIO_AVAILABILITY_PLAYBACK_INTENT_PREVIEW,
            self.OFFLINE_CACHE_QUALITY_CAPABILITY_SUMMARY,
            self.DEGRADED_SOURCE_PARTIAL_FLOW,
        ):
            if str(candidate.flow_id) == flow_id:
                return candidate
        return None

    def _step(
        self,
        index: int,
        kind: FakeFlowStepKind,
        label: str,
        payload: Any,
        *,
        ok: bool = True,
        issues: tuple[FakeFlowValidationIssue, ...] = (),
        unavailable: tuple[FakeFlowUnavailableReason, ...] = (),
    ) -> FakeFlowStepResult:
        return FakeFlowStepResult(
            step=FakeFlowStep(index, kind, label),
            ok=ok,
            payload=safe_serialize(payload),
            issues=issues,
            unavailable_reasons=unavailable,
        )

    def _result(self, scenario: FakeFlowScenario, steps: tuple[FakeFlowStepResult, ...], *, degraded: bool = False) -> AriaResult[FakeFlowResult]:
        issues: tuple[FakeFlowValidationIssue, ...] = ()
        unavailable: tuple[FakeFlowUnavailableReason, ...] = ()
        for step in steps:
            issues += step.issues
            unavailable += step.unavailable_reasons
        trace = FakeFlowTrace(scenario.flow_id, steps)
        success = all(step.ok for step in steps) and not degraded
        return AriaResult(ok=True, data=FakeFlowResult(success, scenario, trace, degraded=degraded, issues=_dedupe_flow_issues(issues), unavailable_reasons=_dedupe_flow_unavailable(unavailable)))


@dataclass
class _RedactionTracker:
    unsafe_redacted: bool = False
    unsupported_redacted: bool = False

    @property
    def any_redacted(self) -> bool:
        return self.unsafe_redacted or self.unsupported_redacted


def _normalize_section_name(name: str) -> str:
    return "_".join(str(name).strip().lower().replace("-", "_").split())


def _is_secret_like_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SECRET_KEY_MARKERS)


def _dedupe_snapshot_issues(issues: tuple[AriaSnapshotValidationIssue, ...]) -> tuple[AriaSnapshotValidationIssue, ...]:
    output: tuple[AriaSnapshotValidationIssue, ...] = ()
    for issue in issues:
        if issue not in output:
            output += (issue,)
    return output


def _dedupe_unavailable(reasons: tuple[AriaSnapshotUnavailableReason, ...]) -> tuple[AriaSnapshotUnavailableReason, ...]:
    output: tuple[AriaSnapshotUnavailableReason, ...] = ()
    for reason in reasons:
        if reason not in output:
            output += (reason,)
    return output


def _dedupe_flow_issues(issues: tuple[FakeFlowValidationIssue, ...]) -> tuple[FakeFlowValidationIssue, ...]:
    output: tuple[FakeFlowValidationIssue, ...] = ()
    for issue in issues:
        if issue not in output:
            output += (issue,)
    return output


def _dedupe_flow_unavailable(reasons: tuple[FakeFlowUnavailableReason, ...]) -> tuple[FakeFlowUnavailableReason, ...]:
    output: tuple[FakeFlowUnavailableReason, ...] = ()
    for reason in reasons:
        if reason not in output:
            output += (reason,)
    return output


__all__ = [
    "AriaSnapshotDiff",
    "AriaSnapshotDiffEntry",
    "AriaSnapshotDiffService",
    "AriaSnapshotId",
    "AriaSnapshotMetadata",
    "AriaSnapshotRedactionPolicy",
    "AriaSnapshotResult",
    "AriaSnapshotScope",
    "AriaSnapshotSection",
    "AriaSnapshotService",
    "AriaSnapshotUnavailableReason",
    "AriaSnapshotValidationIssue",
    "AriaStateSnapshot",
    "FakeFlowId",
    "FakeFlowResult",
    "FakeFlowRunner",
    "FakeFlowScenario",
    "FakeFlowStep",
    "FakeFlowStepKind",
    "FakeFlowStepResult",
    "FakeFlowTrace",
    "FakeFlowUnavailableReason",
    "FakeFlowValidationIssue",
]
