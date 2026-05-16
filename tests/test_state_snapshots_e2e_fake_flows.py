"""Tests for Bloco 20 state snapshots and deterministic fake flows."""

from __future__ import annotations

from noqlen_aria.contracts import DiagnosticsViewState
from noqlen_aria.library import LibraryItemSummary
from noqlen_aria.media_source import MediaId, MediaIdKind, MediaSourceId
from noqlen_aria.now_playing import FakeNowPlayingScenarios
from noqlen_aria.profiles_preferences_backup import UserPreferenceKey, UserPreferencesState, UserProfileId, UserProfileState
from noqlen_aria.queue import FakeQueueScenarios, QueueItem, QueueItemId, QueueService, QueueState
from noqlen_aria.state_snapshots import (
    AriaSnapshotDiffService,
    AriaSnapshotId,
    AriaSnapshotMetadata,
    AriaSnapshotScope,
    AriaSnapshotService,
    AriaSnapshotUnavailableReason,
    AriaSnapshotValidationIssue,
    FakeFlowRunner,
    FakeFlowStepKind,
    FakeFlowUnavailableReason,
    FakeFlowValidationIssue,
)


def _profile_state() -> UserProfileState:
    return UserProfileState(UserProfileId("default"), "Default Listener")


def _library_item(index: int = 1) -> LibraryItemSummary:
    return LibraryItemSummary(
        MediaSourceId("fake-source-1"),
        MediaId(f"track-{index}"),
        MediaIdKind.TRACK,
        f"Track {index}",
        "Ada Quartet",
    )


def test_snapshot_defaults_are_safe_and_serializable() -> None:
    result = AriaSnapshotService().build_snapshot({})

    assert result.is_ok()
    snapshot_result = result.data
    assert snapshot_result is not None
    assert snapshot_result.success is True
    assert snapshot_result.snapshot is not None
    assert snapshot_result.snapshot.metadata.snapshot_id == AriaSnapshotId("aria-snapshot")
    assert snapshot_result.snapshot.sections == ()
    assert snapshot_result.snapshot.sanitized is True


def test_snapshot_scope_selection_includes_only_requested_sections() -> None:
    queue = FakeQueueScenarios.three_track_queue()
    result = AriaSnapshotService().build_snapshot(
        {"profile": _profile_state(), "queue": queue, "diagnostics": DiagnosticsViewState()},
        scopes=(AriaSnapshotScope.PROFILE, AriaSnapshotScope.QUEUE),
    )

    snapshot = result.data.snapshot
    assert [section.name for section in snapshot.sections] == ["profile", "queue"]


def test_snapshot_creation_sanitizes_profile_library_queue_and_now_playing() -> None:
    queue = FakeQueueScenarios.three_track_queue()
    now_playing = FakeNowPlayingScenarios.from_queue(queue)

    result = AriaSnapshotService().build_snapshot(
        {
            "profile": _profile_state(),
            "library": {"items": [_library_item()]},
            "queue": queue,
            "now_playing": now_playing,
        }
    )

    snapshot = result.data.snapshot
    assert snapshot.section("profile").data["display_name"] == "Default Listener"
    assert snapshot.section("library").data["items"][0]["display_name"] == "Track 1"
    assert snapshot.section("queue").data["items"][0]["display_name"] == "Track 1"
    assert snapshot.section("now_playing").data["status"] == "READY"


def test_snapshot_redacts_secret_like_keys() -> None:
    result = AriaSnapshotService().build_snapshot(
        {"preferences": {"theme": "dark", "api_token": "abc123", "nested": {"password": "hidden"}}}
    )

    snapshot = result.data.snapshot
    preferences = snapshot.section("preferences").data
    assert preferences == {"theme": "dark", "nested": {}}
    assert AriaSnapshotValidationIssue.UNSAFE_VALUE_REDACTED in snapshot.issues


def test_snapshot_redacts_raw_personal_paths() -> None:
    result = AriaSnapshotService().build_snapshot(
        {"preferences": {"download_hint": "/home/example/Music/library", "windows_hint": "C:\\Users\\example\\Music"}}
    )

    preferences = result.data.snapshot.section("preferences").data
    assert preferences["download_hint"] == "[redacted]"
    assert preferences["windows_hint"] == "[redacted]"


def test_snapshot_excludes_raw_logs() -> None:
    result = AriaSnapshotService().build_snapshot(
        {"diagnostics": {"safe": "ok", "raw_log": "Traceback\nline 2"}}
    )

    diagnostics = result.data.snapshot.section("diagnostics").data
    assert diagnostics["safe"] == "ok"
    assert diagnostics["raw_log"] == "[redacted]"


def test_snapshot_validation_issue_behavior() -> None:
    result = AriaSnapshotService().build_snapshot(
        {"unknown-section": {"value": True}},
        metadata=AriaSnapshotMetadata(snapshot_id=AriaSnapshotId("snap-validation")),
    )

    snapshot = result.data.snapshot
    assert snapshot.sections == ()
    assert AriaSnapshotValidationIssue.UNKNOWN_SECTION in snapshot.issues
    assert AriaSnapshotUnavailableReason.SECTION_NOT_PROVIDED in snapshot.unavailable_reasons


def test_snapshot_invalid_scope_returns_safe_result() -> None:
    result = AriaSnapshotService().build_snapshot({"queue": QueueState()}, scopes=())

    assert result.is_ok()
    assert result.data.success is False
    assert result.data.snapshot is None
    assert AriaSnapshotValidationIssue.INVALID_SCOPE in result.data.issues


def test_snapshot_diff_no_change() -> None:
    service = AriaSnapshotService()
    before = service.build_snapshot({"queue": FakeQueueScenarios.three_track_queue()}).data.snapshot
    after = service.build_snapshot({"queue": FakeQueueScenarios.three_track_queue()}).data.snapshot

    diff = AriaSnapshotDiffService().diff(before, after).data

    assert diff.changed is False
    assert diff.entries == ()


def test_snapshot_diff_reports_queue_order_change() -> None:
    service = QueueService()
    before_queue = FakeQueueScenarios.three_track_queue()
    moved = service.move_item(before_queue, before_queue.items[0].item_id, 2).data.queue_state
    snapshot_service = AriaSnapshotService()
    before = snapshot_service.build_snapshot(
        {"queue": before_queue}, metadata=AriaSnapshotMetadata(AriaSnapshotId("before"))
    ).data.snapshot
    after = snapshot_service.build_snapshot(
        {"queue": moved}, metadata=AriaSnapshotMetadata(AriaSnapshotId("after"))
    ).data.snapshot

    diff = AriaSnapshotDiffService().diff(before, after).data

    assert diff.changed is True
    assert len(diff.entries) == 1
    assert diff.entries[0].section_name == "queue"
    assert diff.entries[0].change_type == "changed"


def test_fake_flow_trace_order_is_deterministic() -> None:
    runner = FakeFlowRunner()
    first = runner.run(FakeFlowRunner.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS).data.trace
    second = runner.run(FakeFlowRunner.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS).data.trace

    assert [step.step.kind for step in first.steps] == [
        FakeFlowStepKind.SOURCE,
        FakeFlowStepKind.LIBRARY,
        FakeFlowStepKind.QUEUE,
        FakeFlowStepKind.NOW_PLAYING,
        FakeFlowStepKind.PLAYBACK_INTENT,
        FakeFlowStepKind.DIAGNOSTICS,
    ]
    assert first == second


def test_source_library_queue_now_playing_diagnostics_fake_flow() -> None:
    result = FakeFlowRunner().run(FakeFlowRunner.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS).data

    assert result.success is True
    assert result.degraded is False
    assert result.trace.steps[2].payload["items"][0]["display_name"] == "First Difference"
    assert result.trace.steps[4].payload["allowed"] is True


def test_smart_playlist_queue_preview_fake_flow_does_not_mutate_real_queue_or_provider() -> None:
    result = FakeFlowRunner().run(FakeFlowRunner.PROFILE_PREFERENCES_SMART_PLAYLIST_QUEUE_PREVIEW).data

    assert result.success is True
    smart_preview = result.trace.steps[2].payload
    queue_preview = result.trace.steps[3]
    assert smart_preview["provider_playlist_created"] is False
    assert smart_preview["queue_mutated"] is False
    assert queue_preview.real_queue_mutated is False
    assert len(queue_preview.payload["items"]) == 2


def test_radio_unavailable_fake_flow_blocks_playback_intent_safely() -> None:
    result = FakeFlowRunner().run(FakeFlowRunner.RADIO_AVAILABILITY_PLAYBACK_INTENT_PREVIEW).data

    assert result.success is False
    assert result.degraded is True
    assert FakeFlowValidationIssue.RADIO_UNAVAILABLE in result.issues
    assert FakeFlowUnavailableReason.PLAYBACK_BLOCKED in result.unavailable_reasons
    assert result.trace.steps[1].payload["allowed"] is False


def test_offline_quality_capability_fake_flow_returns_policy_decisions_only() -> None:
    result = FakeFlowRunner().run(FakeFlowRunner.OFFLINE_CACHE_QUALITY_CAPABILITY_SUMMARY).data

    assert result.success is True
    quality_step = result.trace.steps[2]
    capability_step = result.trace.steps[4]
    assert "no stream was opened" in quality_step.payload["summary"]
    assert "no playback was started" in capability_step.payload["summary"]


def test_degraded_fake_flow_returns_safe_partial_trace() -> None:
    result = FakeFlowRunner().run(FakeFlowRunner.DEGRADED_SOURCE_PARTIAL_FLOW).data

    assert result.success is False
    assert result.degraded is True
    assert FakeFlowValidationIssue.SOURCE_UNAVAILABLE in result.issues
    assert result.trace.steps[2].payload["items"] == []


def test_unknown_fake_flow_returns_safe_error() -> None:
    result = FakeFlowRunner().run("not-a-flow")

    assert result.is_err()
    assert result.error.code == "UNKNOWN_FAKE_FLOW"
    assert result.data.issues == (FakeFlowValidationIssue.UNKNOWN_SCENARIO,)


def test_fake_flows_report_no_provider_network_filesystem_playback_or_android_behavior() -> None:
    runner = FakeFlowRunner()
    scenarios = (
        FakeFlowRunner.SOURCE_LIBRARY_QUEUE_NOW_PLAYING_DIAGNOSTICS,
        FakeFlowRunner.PROFILE_PREFERENCES_SMART_PLAYLIST_QUEUE_PREVIEW,
        FakeFlowRunner.RADIO_AVAILABILITY_PLAYBACK_INTENT_PREVIEW,
        FakeFlowRunner.OFFLINE_CACHE_QUALITY_CAPABILITY_SUMMARY,
        FakeFlowRunner.DEGRADED_SOURCE_PARTIAL_FLOW,
    )

    for scenario in scenarios:
        result = runner.run(scenario).data
        for step in result.trace.steps:
            assert step.provider_called is False
            assert step.network_called is False
            assert step.filesystem_touched is False
            assert step.playback_started is False
            assert step.android_api_used is False
            assert step.provider_mutated is False


def test_snapshot_redacts_unsupported_objects() -> None:
    class Unsupported:
        pass

    result = AriaSnapshotService().build_snapshot({"library": {"object": Unsupported()}})

    snapshot = result.data.snapshot
    assert snapshot.section("library").data["object"] == "[unavailable]"
    assert AriaSnapshotValidationIssue.UNSUPPORTED_VALUE_REDACTED in snapshot.issues


def test_snapshot_can_include_preference_state_without_secret_values() -> None:
    state = UserPreferencesState(
        global_preferences={UserPreferenceKey("theme"): "dark", UserPreferenceKey("credential.value"): "hidden"}
    )

    snapshot = AriaSnapshotService().build_snapshot({"preferences": state}).data.snapshot

    preferences = snapshot.section("preferences").data
    assert preferences["global_preferences"] == {"theme": "dark"}
