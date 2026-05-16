# Requirements

## Status

Approved for Bloco 18 implementation in this task.

## Problem

Aria Core needs app-facing profile, preference, backup and restore vocabulary so future UI and app layers can reason about configuration/state safely. Without these contracts, future layers may be tempted to touch files, providers, music libraries, or platform storage APIs directly.

## Goal

Add deterministic, local-only models and services for user profiles, preferences, in-memory backup bundles, and preview-first restore planning. Backups cover safe Aria Core config/state only. Restore validates and previews structured bundles without applying destructive changes.

## Non-goals

- No real filesystem persistence, file writing, file reading, path traversal, backup file export, or backup file import.
- No destructive restore or apply flow.
- No music library backup, music library mutation, or library file copying.
- No provider mutation, provider backup, provider restore, provider direct integration, Anchor provider internals, or Anchor CLI integration.
- No Android storage APIs, SAF, MediaStore, permissions, Kotlin, Java, Gradle, UI, screens, navigation, or player code.
- No secrets, credentials, raw personal paths, private logs, or local config exposure in backups or restore warnings.
- No state snapshots or end-to-end fake flows from Bloco 20.
- No smart playlist behavior from Bloco 19.
- No UI implementation.

## Actors

- Future UI/app layer consuming Aria Core profile and preference models.
- Aria Core services validating local profile/preference operations.
- Future backup/restore adapter consuming safe in-memory plans and bundles.
- Tests and fake scenarios verifying deterministic behavior.

## Functional requirements

- FR-01: Define profile contracts: `UserProfileId`, `UserProfileSummary`, `UserProfileState`, `ActiveProfileState`, `ProfileOperationIntent`, `ProfileOperationPreview`, and `ProfileValidationIssue`.
- FR-02: Validate profile names and ids deterministically, including empty/invalid names and duplicate ids.
- FR-03: Preview profile creation without writing files or mutating external state.
- FR-04: Select an active profile from provided state without side effects.
- FR-05: Define preference contracts: `UserPreferenceKey`, `UserPreferenceValue`, `UserPreferenceScope`, `UserPreferencesState`, `PreferenceValidationIssue`, `PreferenceUpdateIntent`, and `PreferenceUpdatePreview`.
- FR-06: Validate preference updates, including invalid keys, secret-like keys, raw personal path values, and missing profile ids for profile-scoped preferences.
- FR-07: Support global and profile preference scopes with deterministic profile-over-global lookup.
- FR-08: Serialize preferences into sanitized state that excludes or redacts unsafe values.
- FR-09: Define backup/restore contracts: `BackupScope`, `BackupManifest`, `BackupBundle`, `BackupPlan`, `BackupPreview`, `BackupResult`, `RestorePlan`, `RestorePreview`, `RestoreResult`, `RestoreConflict`, `RestoreSafetyCheck`, `BackupRestoreWarning`, and `BackupBlockedReason`.
- FR-10: Build in-memory backup manifests and bundles from caller-provided Aria profile/preference state only.
- FR-11: Block unsafe backup scopes such as music library files, provider data, raw paths, secrets, logs, Android storage, and state snapshots.
- FR-12: Exclude or redact secret-like keys and raw personal path values from backup bundles.
- FR-13: Preview restore from a structured bundle and return a restore plan without applying changes.
- FR-14: Detect restore conflicts against existing profiles and require a future explicit decision.
- FR-15: Return safety checks for valid, invalid, corrupt, unsafe, and conflicting bundles.
- FR-16: Provide deterministic local services: `ProfilesService`, `PreferencesService`, and `BackupRestoreService`.

## Non-functional requirements

- NFR-01: Use Python standard library only; no new dependencies.
- NFR-02: All service operations are deterministic and side-effect-free beyond returned values.
- NFR-03: All unsafe inputs return safe `AriaResult` errors, previews, issues, warnings, or blocked reasons.
- NFR-04: Public API expansion is intentional and limited to Bloco 18 names.
- NFR-05: Tests must prove no real filesystem, provider, library, Android, network, Bloco 19, or Bloco 20 behavior is added.
- NFR-06: Serialized/backup output must be JSON-compatible through existing safe serialization conventions.

## Canonical Examples

- CE-01: Given a new profile name is valid, When profile creation is previewed, Then Aria returns a safe profile state without writing files.
- CE-02: Given a profile name is empty or invalid, When profile creation is validated, Then Aria returns a validation issue.
- CE-03: Given preferences include safe UI/core options, When preferences are serialized, Then Aria returns a sanitized preferences state.
- CE-04: Given preferences include a secret-like key or raw personal path, When backup is built, Then Aria excludes or redacts that value.
- CE-05: Given a backup bundle is valid, When restore is previewed, Then Aria returns a restore plan without applying changes.
- CE-06: Given a restore bundle conflicts with an existing profile, When restore is previewed, Then Aria reports conflicts and requires an explicit future decision.
- CE-07: Given a backup requests music library files, When backup scope is evaluated, Then Aria blocks it because real music library backup is out of scope.
- CE-08: Given UI needs profile/preferences later, When it consumes state, Then it uses Aria Core models and does not touch files/providers directly.

## Edge cases

- Empty, whitespace-only, too-long, or punctuation-only profile names.
- Empty, whitespace-only, or duplicate profile ids.
- Empty preference keys, keys with spaces, unsupported value types, secret-like keys, and raw personal path values.
- Profile-scoped preferences without a profile id.
- Empty backup scope, unsafe scope requests, and mixed safe/unsafe scope requests.
- Missing manifest, missing payload, unsupported bundle version, invalid bundle type, or structurally corrupt bundle.
- Restore bundle with duplicate or existing profile ids.
- Restore preview with warnings must not apply changes.

## Acceptance criteria

- Spec files exist under `aria/specs/features/profiles-preferences-backup-restore/` and include Context package, Canonical Examples, Behavior Budget, Test Risk Matrix, and Delta update checklist.
- Profile, preference, backup, and restore contracts are implemented and publicly exported intentionally.
- Services are deterministic, in-memory, and return safe `AriaResult` values.
- Required tests cover validation, scope behavior, safe backup/restore previews, conflict detection, invalid/corrupt bundles, sanitization, and forbidden boundaries.
- No real file persistence, destructive restore/apply, music library mutation, provider mutation, Android storage/API/UI code, Bloco 19 behavior, or Bloco 20 behavior exists.
- Validation commands pass and evidence is recorded in `review.md` and context delta.

## Open questions

- Exact future encrypted backup format remains deferred.
- Exact future restore conflict resolution/apply workflow remains deferred.
- Exact future UI presentation for profile switching and backup warnings remains deferred.
