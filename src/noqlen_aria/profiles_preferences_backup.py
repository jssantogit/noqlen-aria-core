"""Profiles, preferences, backup and restore foundations for Aria Core.

Bloco 18 — local-only state/config contracts, in-memory backup bundles, and
preview-first restore planning. No file, provider, music-library, Android, or
destructive restore behavior is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeAlias, NewType

from noqlen_aria.contracts import AriaError, AriaResult

UserProfileId = NewType("UserProfileId", str)
UserPreferenceKey = NewType("UserPreferenceKey", str)
UserPreferenceValue: TypeAlias = str | int | float | bool | None

_BACKUP_VERSION = "profiles-preferences-backup-v1"
_REDACTED_VALUE = "[redacted]"
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
)


class ProfileValidationIssue(Enum):
    EMPTY_NAME = auto()
    INVALID_NAME = auto()
    NAME_TOO_LONG = auto()
    EMPTY_ID = auto()
    INVALID_ID = auto()
    DUPLICATE_ID = auto()
    PROFILE_NOT_FOUND = auto()


class ProfileOperationType(Enum):
    CREATE_PROFILE = auto()
    SELECT_ACTIVE_PROFILE = auto()


class UserPreferenceScope(Enum):
    GLOBAL = auto()
    PROFILE = auto()


class PreferenceValidationIssue(Enum):
    EMPTY_KEY = auto()
    INVALID_KEY = auto()
    SECRET_LIKE_KEY = auto()
    RAW_PERSONAL_PATH = auto()
    UNSUPPORTED_VALUE_TYPE = auto()
    MISSING_PROFILE_ID = auto()


class BackupScope(Enum):
    PROFILES = auto()
    PREFERENCES = auto()
    APP_CONFIG = auto()
    MUSIC_LIBRARY_FILES = auto()
    PROVIDER_DATA = auto()
    SECRETS = auto()
    RAW_PATHS = auto()
    PRIVATE_LOGS = auto()
    ANDROID_STORAGE = auto()
    STATE_SNAPSHOTS = auto()


class BackupBlockedReason(Enum):
    NONE = auto()
    EMPTY_SCOPE = auto()
    MUSIC_LIBRARY_OUT_OF_SCOPE = auto()
    PROVIDER_MUTATION_OUT_OF_SCOPE = auto()
    SECRETS_OUT_OF_SCOPE = auto()
    RAW_PATHS_OUT_OF_SCOPE = auto()
    PRIVATE_LOGS_OUT_OF_SCOPE = auto()
    ANDROID_STORAGE_OUT_OF_SCOPE = auto()
    STATE_SNAPSHOTS_OUT_OF_SCOPE = auto()
    INVALID_BUNDLE = auto()
    UNSUPPORTED_VERSION = auto()


class BackupRestoreWarning(Enum):
    SECRET_LIKE_ENTRY_EXCLUDED = auto()
    RAW_PATH_ENTRY_REDACTED = auto()
    UNSAFE_SCOPE_BLOCKED = auto()
    RESTORE_REQUIRES_FUTURE_APPLY = auto()
    RESTORE_CONFLICTS_REQUIRE_DECISION = auto()
    EMPTY_BUNDLE = auto()


@dataclass(frozen=True)
class UserProfileSummary:
    profile_id: UserProfileId
    display_name: str
    is_active: bool = False


@dataclass(frozen=True)
class UserProfileState:
    profile_id: UserProfileId
    display_name: str
    created_by: str = "aria-core"
    preferences_count: int = 0


@dataclass(frozen=True)
class ActiveProfileState:
    active_profile_id: UserProfileId | None = None
    profiles: tuple[UserProfileSummary, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProfileOperationIntent:
    operation_type: ProfileOperationType
    display_name: str = ""
    profile_id: UserProfileId | None = None


@dataclass(frozen=True)
class ProfileOperationPreview:
    intent: ProfileOperationIntent
    allowed: bool
    profile_state: UserProfileState | None = None
    active_state: ActiveProfileState | None = None
    issues: tuple[ProfileValidationIssue, ...] = field(default_factory=tuple)
    summary: str = ""


@dataclass(frozen=True)
class UserPreferencesState:
    global_preferences: dict[UserPreferenceKey, UserPreferenceValue] = field(default_factory=dict)
    profile_preferences: dict[UserProfileId, dict[UserPreferenceKey, UserPreferenceValue]] = field(default_factory=dict)


@dataclass(frozen=True)
class PreferenceUpdateIntent:
    key: UserPreferenceKey
    value: UserPreferenceValue
    scope: UserPreferenceScope = UserPreferenceScope.GLOBAL
    profile_id: UserProfileId | None = None


@dataclass(frozen=True)
class PreferenceUpdatePreview:
    intent: PreferenceUpdateIntent
    allowed: bool
    issues: tuple[PreferenceValidationIssue, ...] = field(default_factory=tuple)
    sanitized_value: UserPreferenceValue = None
    summary: str = ""


@dataclass(frozen=True)
class BackupManifest:
    version: str = _BACKUP_VERSION
    scopes: tuple[BackupScope, ...] = field(default_factory=tuple)
    profile_count: int = 0
    preference_count: int = 0
    warnings: tuple[BackupRestoreWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BackupBundle:
    manifest: BackupManifest
    profiles: tuple[UserProfileState, ...] = field(default_factory=tuple)
    preferences: UserPreferencesState = field(default_factory=UserPreferencesState)


@dataclass(frozen=True)
class BackupPlan:
    requested_scopes: tuple[BackupScope, ...] = field(default_factory=tuple)
    allowed_scopes: tuple[BackupScope, ...] = field(default_factory=tuple)
    blocked_reasons: tuple[BackupBlockedReason, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BackupPreview:
    plan: BackupPlan
    allowed: bool
    warnings: tuple[BackupRestoreWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BackupResult:
    success: bool
    preview: BackupPreview
    bundle: BackupBundle | None = None
    blocked_reasons: tuple[BackupBlockedReason, ...] = field(default_factory=tuple)
    warnings: tuple[BackupRestoreWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RestoreConflict:
    profile_id: UserProfileId | None
    field: str
    summary: str


@dataclass(frozen=True)
class RestoreSafetyCheck:
    name: str
    passed: bool
    summary: str = ""


@dataclass(frozen=True)
class RestorePlan:
    manifest: BackupManifest
    profiles_to_import: tuple[UserProfileState, ...] = field(default_factory=tuple)
    preferences_to_import: UserPreferencesState = field(default_factory=UserPreferencesState)
    requires_explicit_decision: bool = True
    applied: bool = False


@dataclass(frozen=True)
class RestorePreview:
    valid: bool
    plan: RestorePlan | None = None
    conflicts: tuple[RestoreConflict, ...] = field(default_factory=tuple)
    safety_checks: tuple[RestoreSafetyCheck, ...] = field(default_factory=tuple)
    warnings: tuple[BackupRestoreWarning, ...] = field(default_factory=tuple)
    applied: bool = False


@dataclass(frozen=True)
class RestoreResult:
    success: bool
    preview: RestorePreview
    applied: bool = False


class ProfilesService:
    """Validate and preview profile state without persistence."""

    def preview_create_profile(
        self,
        intent: ProfileOperationIntent,
        *,
        existing_profiles: tuple[UserProfileState, ...] = (),
    ) -> AriaResult[ProfileOperationPreview]:
        issues = self.validate_profile_name(intent.display_name)
        profile_id = intent.profile_id or self.build_profile_id(intent.display_name)
        issues += self.validate_profile_id(profile_id)
        if any(profile.profile_id == profile_id for profile in existing_profiles):
            issues += (ProfileValidationIssue.DUPLICATE_ID,)
        if issues:
            return self._ok(ProfileOperationPreview(intent=intent, allowed=False, issues=issues, summary="Profile creation is invalid"))
        state = UserProfileState(profile_id=profile_id, display_name=intent.display_name.strip())
        return self._ok(ProfileOperationPreview(intent=intent, allowed=True, profile_state=state, summary="Profile creation can be previewed safely"))

    def select_active_profile(
        self,
        profile_id: UserProfileId,
        profiles: tuple[UserProfileState, ...],
    ) -> AriaResult[ProfileOperationPreview]:
        intent = ProfileOperationIntent(operation_type=ProfileOperationType.SELECT_ACTIVE_PROFILE, profile_id=profile_id)
        ids = {profile.profile_id for profile in profiles}
        if profile_id not in ids:
            return self._ok(ProfileOperationPreview(intent=intent, allowed=False, issues=(ProfileValidationIssue.PROFILE_NOT_FOUND,), summary="Profile was not found"))
        summaries = tuple(
            UserProfileSummary(profile_id=profile.profile_id, display_name=profile.display_name, is_active=profile.profile_id == profile_id)
            for profile in profiles
        )
        active = ActiveProfileState(active_profile_id=profile_id, profiles=summaries)
        return self._ok(ProfileOperationPreview(intent=intent, allowed=True, active_state=active, summary="Profile selection can be applied by a future layer"))

    def validate_profile_name(self, display_name: str) -> tuple[ProfileValidationIssue, ...]:
        trimmed = display_name.strip()
        if not trimmed:
            return (ProfileValidationIssue.EMPTY_NAME,)
        issues: tuple[ProfileValidationIssue, ...] = ()
        if len(trimmed) > 80:
            issues += (ProfileValidationIssue.NAME_TOO_LONG,)
        if not any(char.isalnum() for char in trimmed):
            issues += (ProfileValidationIssue.INVALID_NAME,)
        return issues

    def validate_profile_id(self, profile_id: UserProfileId | None) -> tuple[ProfileValidationIssue, ...]:
        text = "" if profile_id is None else str(profile_id).strip()
        if not text:
            return (ProfileValidationIssue.EMPTY_ID,)
        if not all(char.isalnum() or char in "_-." for char in text):
            return (ProfileValidationIssue.INVALID_ID,)
        return ()

    def build_profile_id(self, display_name: str) -> UserProfileId:
        slug = "-".join(display_name.strip().lower().split())
        slug = "".join(char for char in slug if char.isalnum() or char in "_-." )
        return UserProfileId(slug or "profile")

    def _ok(self, data: ProfileOperationPreview) -> AriaResult[ProfileOperationPreview]:
        return AriaResult(ok=True, data=data)


class PreferencesService:
    """Validate and sanitize preference state without external persistence."""

    def preview_update(self, intent: PreferenceUpdateIntent) -> AriaResult[PreferenceUpdatePreview]:
        issues = self.validate_update(intent)
        return AriaResult(
            ok=True,
            data=PreferenceUpdatePreview(
                intent=intent,
                allowed=not issues,
                issues=issues,
                sanitized_value=self.sanitize_value(intent.value),
                summary="Preference update is valid" if not issues else "Preference update is invalid",
            ),
        )

    def apply_to_state(self, state: UserPreferencesState, intent: PreferenceUpdateIntent) -> AriaResult[UserPreferencesState]:
        preview = self.preview_update(intent)
        if preview.data is None or not preview.data.allowed:
            return AriaResult(ok=False, error=AriaError(code="INVALID_PREFERENCE", message="Preference update is invalid"))
        global_preferences = dict(state.global_preferences)
        profile_preferences = {profile_id: dict(values) for profile_id, values in state.profile_preferences.items()}
        if intent.scope == UserPreferenceScope.GLOBAL:
            global_preferences[intent.key] = preview.data.sanitized_value
        else:
            profile_id = intent.profile_id or UserProfileId("")
            profile_values = dict(profile_preferences.get(profile_id, {}))
            profile_values[intent.key] = preview.data.sanitized_value
            profile_preferences[profile_id] = profile_values
        return AriaResult(ok=True, data=UserPreferencesState(global_preferences=global_preferences, profile_preferences=profile_preferences))

    def preference_value(
        self,
        state: UserPreferencesState,
        key: UserPreferenceKey,
        *,
        profile_id: UserProfileId | None = None,
    ) -> AriaResult[UserPreferenceValue]:
        if profile_id is not None and profile_id in state.profile_preferences and key in state.profile_preferences[profile_id]:
            return AriaResult(ok=True, data=state.profile_preferences[profile_id][key])
        return AriaResult(ok=True, data=state.global_preferences.get(key))

    def sanitized_state(self, state: UserPreferencesState) -> UserPreferencesState:
        global_preferences = {
            key: self.sanitize_value(value)
            for key, value in state.global_preferences.items()
            if not _is_secret_like_key(str(key))
        }
        profile_preferences: dict[UserProfileId, dict[UserPreferenceKey, UserPreferenceValue]] = {}
        for profile_id, values in state.profile_preferences.items():
            profile_preferences[profile_id] = {
                key: self.sanitize_value(value)
                for key, value in values.items()
                if not _is_secret_like_key(str(key))
            }
        return UserPreferencesState(global_preferences=global_preferences, profile_preferences=profile_preferences)

    def validate_update(self, intent: PreferenceUpdateIntent) -> tuple[PreferenceValidationIssue, ...]:
        issues = self.validate_key(intent.key)
        if intent.scope == UserPreferenceScope.PROFILE and not intent.profile_id:
            issues += (PreferenceValidationIssue.MISSING_PROFILE_ID,)
        if not _is_supported_preference_value(intent.value):
            issues += (PreferenceValidationIssue.UNSUPPORTED_VALUE_TYPE,)
        if isinstance(intent.value, str) and _looks_like_raw_path(intent.value):
            issues += (PreferenceValidationIssue.RAW_PERSONAL_PATH,)
        return issues

    def validate_key(self, key: UserPreferenceKey) -> tuple[PreferenceValidationIssue, ...]:
        text = str(key).strip()
        if not text:
            return (PreferenceValidationIssue.EMPTY_KEY,)
        if _is_secret_like_key(text):
            return (PreferenceValidationIssue.SECRET_LIKE_KEY,)
        if not all(char.isalnum() or char in "._-" for char in text) or ".." in text:
            return (PreferenceValidationIssue.INVALID_KEY,)
        return ()

    def sanitize_value(self, value: UserPreferenceValue) -> UserPreferenceValue:
        if isinstance(value, str) and _looks_like_raw_path(value):
            return _REDACTED_VALUE
        return value


class BackupRestoreService:
    """Build safe in-memory backup bundles and preview restore plans."""

    def evaluate_backup_scope(self, scopes: tuple[BackupScope, ...]) -> AriaResult[BackupPreview]:
        blocked = _blocked_reasons_for_scopes(scopes)
        allowed_scopes = tuple(scope for scope in scopes if scope not in _UNSAFE_SCOPES)
        if not scopes:
            blocked += (BackupBlockedReason.EMPTY_SCOPE,)
        plan = BackupPlan(requested_scopes=scopes, allowed_scopes=allowed_scopes, blocked_reasons=blocked)
        warnings = (BackupRestoreWarning.UNSAFE_SCOPE_BLOCKED,) if blocked else ()
        return AriaResult(ok=True, data=BackupPreview(plan=plan, allowed=not blocked, warnings=warnings))

    def build_backup_bundle(
        self,
        *,
        profiles: tuple[UserProfileState, ...] = (),
        preferences: UserPreferencesState | None = None,
        scopes: tuple[BackupScope, ...] = (BackupScope.PROFILES, BackupScope.PREFERENCES),
    ) -> AriaResult[BackupResult]:
        preview_result = self.evaluate_backup_scope(scopes)
        preview = preview_result.data
        if preview is None:
            return AriaResult(ok=False, error=AriaError(code="BACKUP_SCOPE_FAILED", message="Backup scope could not be evaluated"))
        if not preview.allowed:
            return AriaResult(ok=True, data=BackupResult(success=False, preview=preview, blocked_reasons=preview.plan.blocked_reasons, warnings=preview.warnings))

        safe_preferences, sanitization_warnings = self._backup_safe_preferences(preferences or UserPreferencesState())
        included_profiles = profiles if BackupScope.PROFILES in scopes else ()
        included_preferences = safe_preferences if BackupScope.PREFERENCES in scopes or BackupScope.APP_CONFIG in scopes else UserPreferencesState()
        preference_count = len(included_preferences.global_preferences) + sum(len(values) for values in included_preferences.profile_preferences.values())
        manifest = BackupManifest(
            scopes=preview.plan.allowed_scopes,
            profile_count=len(included_profiles),
            preference_count=preference_count,
            warnings=sanitization_warnings,
        )
        bundle = BackupBundle(manifest=manifest, profiles=included_profiles, preferences=included_preferences)
        return AriaResult(ok=True, data=BackupResult(success=True, preview=preview, bundle=bundle, warnings=sanitization_warnings))

    def preview_restore(
        self,
        bundle: object,
        *,
        existing_profiles: tuple[UserProfileState, ...] = (),
    ) -> AriaResult[RestorePreview]:
        validation = self._validate_bundle(bundle)
        if not validation.ok:
            return AriaResult(ok=False, error=validation.error)
        backup_bundle = validation.data
        if backup_bundle is None:
            return AriaResult(ok=False, error=AriaError(code="INVALID_BUNDLE", message="Backup bundle is invalid"))

        conflicts = self._restore_conflicts(backup_bundle.profiles, existing_profiles)
        warnings = (BackupRestoreWarning.RESTORE_REQUIRES_FUTURE_APPLY,)
        if conflicts:
            warnings += (BackupRestoreWarning.RESTORE_CONFLICTS_REQUIRE_DECISION,)
        safety_checks = (
            RestoreSafetyCheck(name="valid_bundle", passed=True, summary="Bundle is structured and version-compatible"),
            RestoreSafetyCheck(name="preview_only", passed=True, summary="Restore preview does not apply changes"),
            RestoreSafetyCheck(name="no_destructive_restore", passed=True, summary="No destructive restore path exists"),
            RestoreSafetyCheck(name="conflict_free", passed=not conflicts, summary="Conflicts require a future explicit decision" if conflicts else "No profile conflicts found"),
        )
        plan = RestorePlan(
            manifest=backup_bundle.manifest,
            profiles_to_import=backup_bundle.profiles,
            preferences_to_import=backup_bundle.preferences,
            requires_explicit_decision=True,
            applied=False,
        )
        return AriaResult(ok=True, data=RestorePreview(valid=True, plan=plan, conflicts=conflicts, safety_checks=safety_checks, warnings=warnings, applied=False))

    def restore_result_from_preview(self, preview: RestorePreview) -> RestoreResult:
        return RestoreResult(success=preview.valid and not preview.conflicts, preview=preview, applied=False)

    def _backup_safe_preferences(self, state: UserPreferencesState) -> tuple[UserPreferencesState, tuple[BackupRestoreWarning, ...]]:
        warnings: tuple[BackupRestoreWarning, ...] = ()

        def safe_values(values: dict[UserPreferenceKey, UserPreferenceValue]) -> dict[UserPreferenceKey, UserPreferenceValue]:
            nonlocal warnings
            output: dict[UserPreferenceKey, UserPreferenceValue] = {}
            for key, value in values.items():
                if _is_secret_like_key(str(key)):
                    warnings += (BackupRestoreWarning.SECRET_LIKE_ENTRY_EXCLUDED,)
                    continue
                if isinstance(value, str) and _looks_like_raw_path(value):
                    warnings += (BackupRestoreWarning.RAW_PATH_ENTRY_REDACTED,)
                    continue
                output[key] = value
            return output

        return (
            UserPreferencesState(
                global_preferences=safe_values(state.global_preferences),
                profile_preferences={profile_id: safe_values(values) for profile_id, values in state.profile_preferences.items()},
            ),
            _dedupe_warnings(warnings),
        )

    def _validate_bundle(self, bundle: object) -> AriaResult[BackupBundle]:
        if not isinstance(bundle, BackupBundle):
            return AriaResult(ok=False, error=AriaError(code="INVALID_BUNDLE", message="Backup bundle is invalid"))
        if bundle.manifest.version != _BACKUP_VERSION:
            return AriaResult(ok=False, error=AriaError(code="UNSUPPORTED_BUNDLE", message="Backup bundle version is unsupported"))
        unsafe_reasons = _blocked_reasons_for_scopes(bundle.manifest.scopes)
        if unsafe_reasons:
            return AriaResult(ok=False, error=AriaError(code="UNSAFE_BUNDLE_SCOPE", message="Backup bundle contains unsafe scope"))
        return AriaResult(ok=True, data=bundle)

    def _restore_conflicts(
        self,
        profiles: tuple[UserProfileState, ...],
        existing_profiles: tuple[UserProfileState, ...],
    ) -> tuple[RestoreConflict, ...]:
        conflicts: tuple[RestoreConflict, ...] = ()
        existing_by_id = {profile.profile_id: profile for profile in existing_profiles}
        existing_names = {profile.display_name.strip().lower(): profile for profile in existing_profiles}
        for profile in profiles:
            if profile.profile_id in existing_by_id:
                conflicts += (RestoreConflict(profile_id=profile.profile_id, field="profile_id", summary="Profile id already exists"),)
            existing = existing_names.get(profile.display_name.strip().lower())
            if existing is not None and existing.profile_id != profile.profile_id:
                conflicts += (RestoreConflict(profile_id=profile.profile_id, field="display_name", summary="Profile name already exists"),)
        return conflicts


_UNSAFE_SCOPES = {
    BackupScope.MUSIC_LIBRARY_FILES,
    BackupScope.PROVIDER_DATA,
    BackupScope.SECRETS,
    BackupScope.RAW_PATHS,
    BackupScope.PRIVATE_LOGS,
    BackupScope.ANDROID_STORAGE,
    BackupScope.STATE_SNAPSHOTS,
}


def _blocked_reasons_for_scopes(scopes: tuple[BackupScope, ...]) -> tuple[BackupBlockedReason, ...]:
    mapping = {
        BackupScope.MUSIC_LIBRARY_FILES: BackupBlockedReason.MUSIC_LIBRARY_OUT_OF_SCOPE,
        BackupScope.PROVIDER_DATA: BackupBlockedReason.PROVIDER_MUTATION_OUT_OF_SCOPE,
        BackupScope.SECRETS: BackupBlockedReason.SECRETS_OUT_OF_SCOPE,
        BackupScope.RAW_PATHS: BackupBlockedReason.RAW_PATHS_OUT_OF_SCOPE,
        BackupScope.PRIVATE_LOGS: BackupBlockedReason.PRIVATE_LOGS_OUT_OF_SCOPE,
        BackupScope.ANDROID_STORAGE: BackupBlockedReason.ANDROID_STORAGE_OUT_OF_SCOPE,
        BackupScope.STATE_SNAPSHOTS: BackupBlockedReason.STATE_SNAPSHOTS_OUT_OF_SCOPE,
    }
    blocked: tuple[BackupBlockedReason, ...] = ()
    for scope in scopes:
        reason = mapping.get(scope)
        if reason is not None and reason not in blocked:
            blocked += (reason,)
    return blocked


def _is_secret_like_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SECRET_KEY_MARKERS)


def _looks_like_raw_path(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in _RAW_PATH_MARKERS)


def _is_supported_preference_value(value: object) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _dedupe_warnings(warnings: tuple[BackupRestoreWarning, ...]) -> tuple[BackupRestoreWarning, ...]:
    output: tuple[BackupRestoreWarning, ...] = ()
    for warning in warnings:
        if warning not in output:
            output += (warning,)
    return output


__all__ = [
    "ActiveProfileState",
    "BackupBlockedReason",
    "BackupBundle",
    "BackupManifest",
    "BackupPlan",
    "BackupPreview",
    "BackupRestoreService",
    "BackupRestoreWarning",
    "BackupResult",
    "BackupScope",
    "PreferenceUpdateIntent",
    "PreferenceUpdatePreview",
    "PreferenceValidationIssue",
    "PreferencesService",
    "ProfileOperationIntent",
    "ProfileOperationPreview",
    "ProfileOperationType",
    "ProfileValidationIssue",
    "ProfilesService",
    "RestoreConflict",
    "RestorePlan",
    "RestorePreview",
    "RestoreResult",
    "RestoreSafetyCheck",
    "UserPreferenceKey",
    "UserPreferenceScope",
    "UserPreferenceValue",
    "UserPreferencesState",
    "UserProfileId",
    "UserProfileState",
    "UserProfileSummary",
]
