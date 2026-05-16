"""Tests for Bloco 18 profiles, preferences, backup and restore foundations."""

from __future__ import annotations

import json

from noqlen_aria.contracts import safe_serialize
from noqlen_aria.profiles_preferences_backup import (
    ActiveProfileState,
    BackupBlockedReason,
    BackupBundle,
    BackupManifest,
    BackupRestoreService,
    BackupRestoreWarning,
    BackupScope,
    PreferenceUpdateIntent,
    PreferenceValidationIssue,
    PreferencesService,
    ProfileOperationIntent,
    ProfileOperationType,
    ProfileValidationIssue,
    ProfilesService,
    RestorePreview,
    UserPreferenceKey,
    UserPreferenceScope,
    UserPreferencesState,
    UserProfileId,
    UserProfileState,
)


def test_profile_defaults_are_safe_and_serializable() -> None:
    profile = UserProfileState(profile_id=UserProfileId("main"), display_name="Main")
    active = ActiveProfileState(active_profile_id=UserProfileId("main"))

    assert profile.created_by == "aria-core"
    assert profile.preferences_count == 0
    assert active.profiles == ()
    json.dumps(safe_serialize(profile))


def test_valid_profile_creation_preview_does_not_write_files() -> None:
    service = ProfilesService()
    result = service.preview_create_profile(
        ProfileOperationIntent(operation_type=ProfileOperationType.CREATE_PROFILE, display_name="Road Trip")
    )

    assert result.ok is True
    assert result.data is not None
    assert result.data.allowed is True
    assert result.data.profile_state == UserProfileState(profile_id=UserProfileId("road-trip"), display_name="Road Trip")


def test_invalid_profile_creation_reports_validation_issue() -> None:
    service = ProfilesService()
    result = service.preview_create_profile(
        ProfileOperationIntent(operation_type=ProfileOperationType.CREATE_PROFILE, display_name="   ")
    )

    assert result.ok is True
    assert result.data is not None
    assert result.data.allowed is False
    assert result.data.issues == (ProfileValidationIssue.EMPTY_NAME,)


def test_duplicate_profile_id_is_rejected() -> None:
    service = ProfilesService()
    existing = (UserProfileState(profile_id=UserProfileId("main"), display_name="Main"),)
    result = service.preview_create_profile(
        ProfileOperationIntent(
            operation_type=ProfileOperationType.CREATE_PROFILE,
            display_name="Main",
            profile_id=UserProfileId("main"),
        ),
        existing_profiles=existing,
    )

    assert result.data is not None
    assert ProfileValidationIssue.DUPLICATE_ID in result.data.issues


def test_active_profile_selection_marks_only_selected_profile() -> None:
    service = ProfilesService()
    profiles = (
        UserProfileState(profile_id=UserProfileId("one"), display_name="One"),
        UserProfileState(profile_id=UserProfileId("two"), display_name="Two"),
    )

    result = service.select_active_profile(UserProfileId("two"), profiles)

    assert result.ok is True
    assert result.data is not None
    assert result.data.allowed is True
    assert result.data.active_state is not None
    assert result.data.active_state.active_profile_id == UserProfileId("two")
    assert [summary.is_active for summary in result.data.active_state.profiles] == [False, True]


def test_missing_active_profile_selection_is_preview_error() -> None:
    service = ProfilesService()
    result = service.select_active_profile(UserProfileId("missing"), ())

    assert result.data is not None
    assert result.data.allowed is False
    assert result.data.issues == (ProfileValidationIssue.PROFILE_NOT_FOUND,)


def test_preference_validation_accepts_safe_global_option() -> None:
    service = PreferencesService()
    result = service.preview_update(
        PreferenceUpdateIntent(key=UserPreferenceKey("ui.theme"), value="dark")
    )

    assert result.ok is True
    assert result.data is not None
    assert result.data.allowed is True
    assert result.data.issues == ()


def test_preference_validation_rejects_invalid_and_secret_like_keys() -> None:
    service = PreferencesService()

    invalid = service.preview_update(PreferenceUpdateIntent(key=UserPreferenceKey("ui theme"), value="dark"))
    secret = service.preview_update(PreferenceUpdateIntent(key=UserPreferenceKey("provider.token"), value="abc"))

    assert invalid.data is not None
    assert PreferenceValidationIssue.INVALID_KEY in invalid.data.issues
    assert secret.data is not None
    assert secret.data.issues == (PreferenceValidationIssue.SECRET_LIKE_KEY,)


def test_preference_validation_rejects_raw_personal_path_value() -> None:
    service = PreferencesService()
    result = service.preview_update(
        PreferenceUpdateIntent(key=UserPreferenceKey("library.last_path"), value="/home/user/Music")
    )

    assert result.data is not None
    assert result.data.allowed is False
    assert PreferenceValidationIssue.RAW_PERSONAL_PATH in result.data.issues
    assert result.data.sanitized_value == "[redacted]"


def test_preference_scope_requires_profile_id_for_profile_updates() -> None:
    service = PreferencesService()
    result = service.preview_update(
        PreferenceUpdateIntent(
            key=UserPreferenceKey("playback.crossfade"),
            value=True,
            scope=UserPreferenceScope.PROFILE,
        )
    )

    assert result.data is not None
    assert result.data.allowed is False
    assert PreferenceValidationIssue.MISSING_PROFILE_ID in result.data.issues


def test_preference_scope_lookup_prefers_profile_value_then_global() -> None:
    service = PreferencesService()
    state = UserPreferencesState(global_preferences={UserPreferenceKey("ui.theme"): "light"})
    applied = service.apply_to_state(
        state,
        PreferenceUpdateIntent(
            key=UserPreferenceKey("ui.theme"),
            value="dark",
            scope=UserPreferenceScope.PROFILE,
            profile_id=UserProfileId("main"),
        ),
    )

    assert applied.ok is True
    assert applied.data is not None
    assert service.preference_value(applied.data, UserPreferenceKey("ui.theme"), profile_id=UserProfileId("main")).data == "dark"
    assert service.preference_value(applied.data, UserPreferenceKey("ui.theme"), profile_id=UserProfileId("other")).data == "light"


def test_sanitized_preferences_exclude_secrets_and_redact_paths() -> None:
    service = PreferencesService()
    state = UserPreferencesState(
        global_preferences={
            UserPreferenceKey("ui.theme"): "dark",
            UserPreferenceKey("provider.password"): "abc",
            UserPreferenceKey("library.raw_path_hint"): "/Users/person/Music",
        }
    )

    sanitized = service.sanitized_state(state)

    assert sanitized.global_preferences == {
        UserPreferenceKey("ui.theme"): "dark",
        UserPreferenceKey("library.raw_path_hint"): "[redacted]",
    }


def test_backup_manifest_creation_counts_safe_profiles_and_preferences() -> None:
    service = BackupRestoreService()
    result = service.build_backup_bundle(
        profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="Main"),),
        preferences=UserPreferencesState(global_preferences={UserPreferenceKey("ui.theme"): "dark"}),
    )

    assert result.ok is True
    assert result.data is not None
    assert result.data.success is True
    assert result.data.bundle is not None
    assert result.data.bundle.manifest.profile_count == 1
    assert result.data.bundle.manifest.preference_count == 1
    assert result.data.bundle.manifest.scopes == (BackupScope.PROFILES, BackupScope.PREFERENCES)


def test_backup_bundle_excludes_secret_like_keys_and_raw_personal_paths() -> None:
    service = BackupRestoreService()
    state = UserPreferencesState(
        global_preferences={
            UserPreferenceKey("ui.theme"): "dark",
            UserPreferenceKey("provider.api_key"): "abc",
            UserPreferenceKey("library.last_folder"): "C:\\Users\\person\\Music",
        }
    )

    result = service.build_backup_bundle(preferences=state)

    assert result.data is not None
    assert result.data.bundle is not None
    assert result.data.bundle.preferences.global_preferences == {UserPreferenceKey("ui.theme"): "dark"}
    assert BackupRestoreWarning.SECRET_LIKE_ENTRY_EXCLUDED in result.data.warnings
    assert BackupRestoreWarning.RAW_PATH_ENTRY_REDACTED in result.data.warnings


def test_backup_blocks_real_music_library_scope() -> None:
    service = BackupRestoreService()
    result = service.build_backup_bundle(scopes=(BackupScope.PROFILES, BackupScope.MUSIC_LIBRARY_FILES))

    assert result.ok is True
    assert result.data is not None
    assert result.data.success is False
    assert result.data.bundle is None
    assert BackupBlockedReason.MUSIC_LIBRARY_OUT_OF_SCOPE in result.data.blocked_reasons
    assert BackupRestoreWarning.UNSAFE_SCOPE_BLOCKED in result.data.warnings


def test_backup_blocks_provider_android_snapshot_and_secret_scopes() -> None:
    service = BackupRestoreService()
    result = service.evaluate_backup_scope(
        (BackupScope.PROVIDER_DATA, BackupScope.ANDROID_STORAGE, BackupScope.STATE_SNAPSHOTS, BackupScope.SECRETS)
    )

    assert result.data is not None
    assert result.data.allowed is False
    assert result.data.plan.allowed_scopes == ()
    assert result.data.plan.blocked_reasons == (
        BackupBlockedReason.PROVIDER_MUTATION_OUT_OF_SCOPE,
        BackupBlockedReason.ANDROID_STORAGE_OUT_OF_SCOPE,
        BackupBlockedReason.STATE_SNAPSHOTS_OUT_OF_SCOPE,
        BackupBlockedReason.SECRETS_OUT_OF_SCOPE,
    )


def test_valid_backup_bundle_restore_preview_returns_plan_without_applying() -> None:
    service = BackupRestoreService()
    backup = service.build_backup_bundle(
        profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="Main"),),
        preferences=UserPreferencesState(global_preferences={UserPreferenceKey("ui.theme"): "dark"}),
    )
    assert backup.data is not None and backup.data.bundle is not None

    preview = service.preview_restore(backup.data.bundle)

    assert preview.ok is True
    assert preview.data is not None
    assert isinstance(preview.data, RestorePreview)
    assert preview.data.valid is True
    assert preview.data.applied is False
    assert preview.data.plan is not None
    assert preview.data.plan.applied is False
    assert preview.data.plan.profiles_to_import[0].profile_id == UserProfileId("main")


def test_restore_conflict_detection_reports_existing_profile_id() -> None:
    service = BackupRestoreService()
    bundle = BackupBundle(
        manifest=BackupManifest(scopes=(BackupScope.PROFILES,), profile_count=1),
        profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="Imported"),),
    )

    preview = service.preview_restore(
        bundle,
        existing_profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="Existing"),),
    )

    assert preview.data is not None
    assert preview.data.conflicts
    assert preview.data.conflicts[0].field == "profile_id"
    assert BackupRestoreWarning.RESTORE_CONFLICTS_REQUIRE_DECISION in preview.data.warnings
    assert preview.data.plan is not None
    assert preview.data.plan.requires_explicit_decision is True


def test_restore_conflict_detection_reports_existing_profile_name() -> None:
    service = BackupRestoreService()
    bundle = BackupBundle(
        manifest=BackupManifest(scopes=(BackupScope.PROFILES,), profile_count=1),
        profiles=(UserProfileState(profile_id=UserProfileId("new"), display_name="Main"),),
    )

    preview = service.preview_restore(
        bundle,
        existing_profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="main"),),
    )

    assert preview.data is not None
    assert preview.data.conflicts[0].field == "display_name"


def test_restore_safety_checks_include_preview_only_and_no_destructive_restore() -> None:
    service = BackupRestoreService()
    bundle = BackupBundle(manifest=BackupManifest(scopes=(BackupScope.PROFILES,)))

    preview = service.preview_restore(bundle)

    assert preview.data is not None
    checks = {check.name: check for check in preview.data.safety_checks}
    assert checks["preview_only"].passed is True
    assert checks["no_destructive_restore"].passed is True
    assert preview.data.applied is False


def test_invalid_corrupt_backup_bundle_handling_is_safe() -> None:
    service = BackupRestoreService()

    result = service.preview_restore({"manifest": "not-a-bundle"})

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "INVALID_BUNDLE"


def test_unsupported_backup_bundle_version_is_rejected() -> None:
    service = BackupRestoreService()
    bundle = BackupBundle(manifest=BackupManifest(version="future-v2", scopes=(BackupScope.PROFILES,)))

    result = service.preview_restore(bundle)

    assert result.ok is False
    assert result.error is not None
    assert result.error.code == "UNSUPPORTED_BUNDLE"


def test_restore_result_from_preview_never_applies_changes() -> None:
    service = BackupRestoreService()
    bundle = BackupBundle(manifest=BackupManifest(scopes=(BackupScope.PROFILES,)))
    preview = service.preview_restore(bundle)

    assert preview.data is not None
    result = service.restore_result_from_preview(preview.data)

    assert result.applied is False
    assert result.preview.applied is False


def test_no_real_filesystem_provider_library_or_android_behavior_exists() -> None:
    profile_service = ProfilesService()
    preference_service = PreferencesService()
    backup_service = BackupRestoreService()

    for service in (profile_service, preference_service, backup_service):
        method_names = set(dir(service))
        assert "write_backup_file" not in method_names
        assert "read_backup_file" not in method_names
        assert "apply_restore" not in method_names
        assert "mutate_provider" not in method_names
        assert "mutate_music_library" not in method_names
        assert "android_storage_api" not in method_names


def test_safe_serialized_backup_bundle_is_json_compatible() -> None:
    service = BackupRestoreService()
    result = service.build_backup_bundle(
        profiles=(UserProfileState(profile_id=UserProfileId("main"), display_name="Main"),),
        preferences=UserPreferencesState(global_preferences={UserPreferenceKey("ui.compact"): True}),
    )

    assert result.data is not None
    assert result.data.bundle is not None
    json.dumps(safe_serialize(result.data.bundle))
