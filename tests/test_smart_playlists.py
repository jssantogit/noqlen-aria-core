"""Tests for Bloco 19 smart playlists, saved filters, and smart mixes."""

from __future__ import annotations

import inspect
from dataclasses import asdict

from noqlen_aria.contracts import safe_serialize
from noqlen_aria.smart_playlists import (
    FakeSmartPlaylistScenarios,
    SavedFilterDefinition,
    SavedFilterId,
    SavedFilterService,
    SavedFilterValidationIssue,
    SmartMixDefinition,
    SmartMixSeed,
    SmartMixStrategy,
    SmartPlaylistDefinition,
    SmartPlaylistEvaluationContext,
    SmartPlaylistId,
    SmartPlaylistLimit,
    SmartPlaylistPreview,
    SmartPlaylistRule,
    SmartPlaylistRuleGroup,
    SmartPlaylistRuleOperator,
    SmartPlaylistService,
    SmartPlaylistSortRule,
    SmartPlaylistUnavailableReason,
    SmartPlaylistValidationIssue,
)


def _context() -> SmartPlaylistEvaluationContext:
    return SmartPlaylistEvaluationContext(candidates=FakeSmartPlaylistScenarios.candidates())


def _definition(rule: SmartPlaylistRule) -> SmartPlaylistDefinition:
    return SmartPlaylistDefinition(
        playlist_id=SmartPlaylistId("test"),
        display_name="Test Playlist",
        root_group=SmartPlaylistRuleGroup((rule,)),
    )


def test_valid_favorite_rule_builds_preview_without_provider_mutation() -> None:
    definition = FakeSmartPlaylistScenarios.favorite_tracks_definition()
    preview = SmartPlaylistService().build_preview(definition, _context()).data

    assert [item.item_id for item in preview.items] == ["track-1", "track-3"]
    assert preview.available is True
    assert preview.provider_playlist_created is False
    assert preview.queue_mutated is False
    assert preview.playback_started is False


def test_unsupported_operator_returns_validation_issue() -> None:
    definition = _definition(SmartPlaylistRule("favorite", SmartPlaylistRuleOperator.UNSUPPORTED))

    issues = SmartPlaylistService().validate_definition(definition)
    preview = SmartPlaylistService().build_preview(definition, _context()).data

    assert SmartPlaylistValidationIssue.UNSUPPORTED_OPERATOR in issues
    assert preview.available is False
    assert preview.unavailable_reasons == (SmartPlaylistUnavailableReason.UNSUPPORTED_OPERATOR,)


def test_unsupported_field_returns_safe_unavailable_preview() -> None:
    definition = _definition(SmartPlaylistRule("provider_rating", SmartPlaylistRuleOperator.EQUALS, 5))

    preview = SmartPlaylistService().build_preview(definition, _context()).data

    assert preview.available is False
    assert SmartPlaylistValidationIssue.UNSUPPORTED_FIELD in preview.issues
    assert SmartPlaylistUnavailableReason.UNSUPPORTED_FIELD in preview.unavailable_reasons


def test_missing_recently_played_metadata_returns_partial_result() -> None:
    definition = _definition(SmartPlaylistRule("recently_played", SmartPlaylistRuleOperator.IS_TRUE))

    preview = SmartPlaylistService().build_preview(definition, _context()).data

    assert [item.item_id for item in preview.items] == ["track-1"]
    assert preview.available is False
    assert preview.partial is True
    assert SmartPlaylistValidationIssue.MISSING_METADATA in preview.issues
    assert SmartPlaylistUnavailableReason.MISSING_METADATA in preview.unavailable_reasons


def test_recently_added_artist_album_and_genre_rules_are_supported() -> None:
    definition = SmartPlaylistDefinition(
        SmartPlaylistId("recent-instrumental"),
        "Recent Instrumental Ada",
        SmartPlaylistRuleGroup((
            SmartPlaylistRule("recently_added", SmartPlaylistRuleOperator.IS_TRUE),
            SmartPlaylistRule("artist_name", SmartPlaylistRuleOperator.CONTAINS, "ada"),
            SmartPlaylistRule("album_name", SmartPlaylistRuleOperator.CONTAINS, "analytical"),
            SmartPlaylistRule("genre", SmartPlaylistRuleOperator.EQUALS, "Instrumental"),
        )),
    )

    preview = SmartPlaylistService().build_preview(definition, _context()).data
    assert [item.item_id for item in preview.items] == ["track-2"]


def test_saved_filter_preview_applies_to_app_facing_candidates_only() -> None:
    definition = SavedFilterDefinition(
        SavedFilterId("ambient"),
        "Ambient Filter",
        SmartPlaylistRuleGroup((SmartPlaylistRule("genre", SmartPlaylistRuleOperator.EQUALS, "Ambient"),)),
    )

    preview = SavedFilterService().build_preview(definition, FakeSmartPlaylistScenarios.candidates()).data
    assert preview.available is True
    assert preview.issues == ()
    assert [item.display_name for item in preview.items] == ["Quiet Validation"]


def test_saved_filter_validation_maps_unsupported_operator() -> None:
    definition = SavedFilterDefinition(
        SavedFilterId("bad"),
        "Bad Filter",
        SmartPlaylistRuleGroup((SmartPlaylistRule("genre", SmartPlaylistRuleOperator.UNSUPPORTED),)),
    )

    assert SavedFilterService().validate_definition(definition) == (SavedFilterValidationIssue.UNSUPPORTED_OPERATOR,)


def test_deterministic_sorting_and_limit_behavior() -> None:
    definition = SmartPlaylistDefinition(
        SmartPlaylistId("longest-two"),
        "Longest Two",
        SmartPlaylistRuleGroup((SmartPlaylistRule("item_kind", SmartPlaylistRuleOperator.EQUALS, "TRACK"),)),
        sort_rules=(SmartPlaylistSortRule("duration_seconds", descending=True),),
        limit=SmartPlaylistLimit(2),
    )

    preview = SmartPlaylistService().build_preview(definition, _context()).data
    assert [item.item_id for item in preview.items] == ["track-3", "track-2"]


def test_empty_library_returns_available_empty_preview() -> None:
    preview = SmartPlaylistService().build_preview(
        FakeSmartPlaylistScenarios.favorite_tracks_definition(),
        SmartPlaylistEvaluationContext(candidates=FakeSmartPlaylistScenarios.empty_candidates()),
    ).data

    assert preview.available is True
    assert preview.items == ()
    assert preview.issues == ()


def test_smart_mix_seeded_shuffle_is_deterministic() -> None:
    definition = SmartMixDefinition(
        "Seeded Mix",
        SmartPlaylistRuleGroup((SmartPlaylistRule("item_kind", SmartPlaylistRuleOperator.EQUALS, "TRACK"),)),
        strategy=SmartMixStrategy.DETERMINISTIC_SHUFFLE,
        seed=SmartMixSeed("fixed-seed"),
        limit=SmartPlaylistLimit(3),
    )

    service = SmartPlaylistService()
    first = service.build_smart_mix_preview(definition, _context()).data
    second = service.build_smart_mix_preview(definition, _context()).data
    different_seed = SmartMixDefinition(
        "Seeded Mix",
        definition.root_group,
        strategy=SmartMixStrategy.DETERMINISTIC_SHUFFLE,
        seed=SmartMixSeed("other-seed"),
        limit=SmartPlaylistLimit(3),
    )
    third = service.build_smart_mix_preview(different_seed, _context()).data

    assert [item.item_id for item in first.items] == [item.item_id for item in second.items]
    assert [item.item_id for item in first.items] != [item.item_id for item in third.items]
    assert first.queue_mutated is False
    assert first.playback_started is False


def test_provider_playlist_creation_is_blocked_and_side_effect_free() -> None:
    service = SmartPlaylistService()
    preview = service.build_preview(FakeSmartPlaylistScenarios.favorite_tracks_definition(), _context()).data

    result = service.request_provider_playlist_creation(preview)
    after = service.build_preview(FakeSmartPlaylistScenarios.favorite_tracks_definition(), _context()).data

    assert result.is_err()
    assert result.error.code == "PROVIDER_PLAYLIST_CREATION_UNSUPPORTED"
    assert after == preview


def test_playlist_summary_and_safe_serialization_are_app_facing() -> None:
    service = SmartPlaylistService()
    preview = service.build_preview(FakeSmartPlaylistScenarios.favorite_tracks_definition(), _context()).data
    summary = service.summary_from_preview(preview)
    serialized = safe_serialize(SmartPlaylistPreview(definition=preview.definition, items=preview.items))

    assert summary.rule_count == 1
    assert summary.preview_count == 2
    assert serialized["items"][0]["display_name"] == "First Difference"


def test_invalid_limit_and_empty_group_are_validation_issues() -> None:
    definition = SmartPlaylistDefinition(
        SmartPlaylistId("invalid"),
        "Invalid",
        SmartPlaylistRuleGroup(),
        limit=SmartPlaylistLimit(0),
    )

    issues = SmartPlaylistService().validate_definition(definition)
    assert SmartPlaylistValidationIssue.EMPTY_RULE_GROUP in issues
    assert SmartPlaylistValidationIssue.INVALID_LIMIT in issues


def test_models_do_not_expose_provider_internals() -> None:
    candidate = FakeSmartPlaylistScenarios.candidates()[0]
    keys = set(asdict(candidate)) | set(asdict(candidate.item))

    for key in keys:
        lowered = key.lower()
        assert "navidrome" not in lowered
        assert "jellyfin" not in lowered
        assert "emby" not in lowered
        assert "anchor" not in lowered


def test_services_do_not_expose_queue_playback_filesystem_network_or_ui_methods() -> None:
    service_names = {name for name in set(dir(SmartPlaylistService)) | set(dir(SavedFilterService)) if not name.startswith("_")}
    for forbidden in (
        "queue",
        "playback_start",
        "provider_create",
        "filesystem",
        "network",
        "android",
        "android_ui",
        "snapshot",
        "end_to_end",
    ):
        assert all(forbidden not in name.lower() for name in service_names)


def test_fake_scenarios_have_no_provider_or_filesystem_dependency() -> None:
    members = dict(inspect.getmembers(FakeSmartPlaylistScenarios))
    for name in members:
        lowered = name.lower()
        assert "provider_api" not in lowered
        assert "filesystem" not in lowered
        assert "walk" not in lowered
