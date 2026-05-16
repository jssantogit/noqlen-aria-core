# Design

## Summary

Bloco 18 adds safe app-facing foundations for profiles, preferences, backup and restore. The implementation will be a single local-only module with dataclass/enum contracts and three deterministic services. Backup produces an in-memory structured bundle. Restore validates and previews a bundle, reports conflicts and safety checks, and never applies changes.

## Context package

Standard.

## Context files read

- `AGENTS.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/future-product-context.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `docs/aria-core-handoff.md`
- `docs/post-core-backlog.md`
- `docs/architecture.md`
- `docs/safety.md`
- `aria/specs/_template/**`
- Prior review files for Blocos 14-17
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

- Aria Core MVP v0.1.0 is complete.
- Blocos 14-17 are implemented and audited.
- Current source style uses focused modules, frozen dataclasses, enums, `NewType` ids, deterministic services, and `AriaResult`.
- Existing safety helpers sanitize app-facing text. Bloco 18 needs stricter backup-specific exclusion/redaction for secret-like keys and raw personal paths.

## Files to create

- `src/noqlen_aria/profiles_preferences_backup.py`
- `tests/test_profiles_preferences_backup_restore.py`
- `aria/specs/features/profiles-preferences-backup-restore/requirements.md`
- `aria/specs/features/profiles-preferences-backup-restore/design.md`
- `aria/specs/features/profiles-preferences-backup-restore/tasks.md`
- `aria/specs/features/profiles-preferences-backup-restore/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`

## Files that must not be touched

- Android/Kotlin/Java/Gradle files.
- UI/screen/navigation/player files.
- Provider integration files beyond public exports.
- Private/local tooling files.
- Docs outside allowed files except `docs/handoff.md` if a tiny note becomes necessary.

## Data flow

1. Caller submits a profile or preference intent.
2. `ProfilesService` or `PreferencesService` validates and returns a preview/state derived only from the supplied inputs.
3. Caller provides profile/preference state and requested `BackupScope` values to `BackupRestoreService`.
4. Backup service evaluates scope, blocks unsafe scopes, sanitizes profile/preference payloads, creates `BackupManifest`, and returns an in-memory `BackupBundle`.
5. Restore service validates a supplied structured bundle, compares bundle profiles to provided existing profiles, returns `RestorePreview` with `RestorePlan`, conflicts, warnings, and safety checks, and sets `applied=False`.

## Error handling

- Invalid model inputs return validation issue enums inside previews where possible.
- Structurally invalid or corrupt restore bundles return `AriaResult(ok=False)` with sanitized `AriaError`.
- Unsafe backup scopes return `BackupResult(success=False)` with blocked reasons and no bundle.
- Restore conflicts do not fail parsing; they appear as `RestoreConflict` values and force `requires_explicit_decision=True`.

## Security considerations

- Backup payloads must never include secret-like keys, credential-like values, raw personal paths, private logs, provider internals, or raw filesystem locations.
- Restore warnings must not echo unsafe values.
- All services remain local and side-effect-free.

## Secret/path sanitization rules

- Secret-like keys include substrings such as `password`, `passwd`, `token`, `secret`, `credential`, `authorization`, `api_key`, and `apikey`.
- Raw personal paths include values containing `/home/`, `/Users/`, `C:\\Users`, drive-root style paths, `raw_path`, or `personal path` markers.
- Secret-like preference entries are excluded from backup bundles.
- Raw personal path values are redacted to a stable safe placeholder when included in serialized preference state and excluded from backup bundles.
- Warning messages identify the key only after sanitization and never echo the unsafe value.

## Backup scope rules

- Allowed scopes: profiles, preferences, and safe app configuration/state represented by Bloco 18 models.
- Blocked scopes: music library files, provider data, secrets/credentials, raw paths/logs, Android storage/platform state, state snapshots, and unknown destructive scopes.
- Mixed safe/unsafe requests are rejected for bundle creation so callers must make scope decisions explicit.

## Restore preview/conflict rules

- Restore always starts with bundle validation.
- Restore requires manifest version compatibility and structured profiles/preferences payloads.
- Existing profile id collisions are conflicts.
- Profile name collisions with different ids are conflicts.
- Conflict presence means a future explicit decision is required.
- Restore preview never mutates provided existing profiles/preferences and never applies changes.

## Profile/preference validation rules

- Profile names must be non-empty, trimmed, at most 80 characters, and contain at least one alphanumeric character.
- Profile ids must be non-empty trimmed strings and may contain letters, digits, `_`, `-`, and `.`.
- Preference keys must be non-empty trimmed dot-separated identifiers with letters, digits, `_`, and `-`.
- Preference values must be `str`, `int`, `float`, `bool`, or `None`.
- Profile-scoped preference updates require a profile id.
- Secret-like keys are invalid for normal preference updates and excluded from backup if already present in supplied state.

## Dependencies

None beyond Python standard library and existing `noqlen_aria.contracts`.

## Risks

- Future layers could treat preview as apply. Mitigation: model names and tests assert `applied=False` and future decision requirements.
- Sanitization rules could miss future sensitive values. Mitigation: conservative substring checks and explicit tests.
- Backup format could be mistaken as durable storage format. Mitigation: manifest states in-memory structured bundle only.

## Rollback strategy

Revert `src/noqlen_aria/profiles_preferences_backup.py`, its public exports, tests, spec directory, and context updates. No migration or persisted data cleanup is needed because no real persistence exists.

## Validation plan

- Run the requested shell validation commands.
- Run full pytest.
- Run boundary searches for filesystem, music library backup/restore, secrets, raw paths, Android, providers, smart playlists, state snapshots, and private tooling.
- Record evidence in `review.md` and `aria/context/delta.md`.

## Behavior Budget

- New behaviors:
  - add profile state models;
  - add preferences state/validation models;
  - add backup manifest/bundle models;
  - add restore preview/conflict/safety models;
  - add deterministic local profile/preference/backup services;
  - add secret/path sanitization checks for backup/restore payloads.
- Public API changes:
  - expose only intentional profile/preference/backup/restore names.
- Files allowed:
  - `src/noqlen_aria/**`
  - `tests/**`
  - `aria/specs/features/profiles-preferences-backup-restore/**`
  - `aria/context/current.md`
  - `aria/context/delta.md`
  - `docs/handoff.md`, only if a tiny status note is needed.
- Tests required:
  - profile creation/selection validation;
  - preference validation;
  - preference scope behavior;
  - backup manifest creation;
  - backup bundle excludes secrets/raw paths;
  - restore preview;
  - restore conflict detection;
  - restore safety checks;
  - invalid/corrupt bundle handling;
  - no real filesystem/provider/library/Android behavior.
- Dependencies:
  - none.
- Stop if:
  - real file persistence becomes necessary;
  - destructive restore/apply becomes necessary;
  - music library mutation becomes necessary;
  - provider mutation becomes necessary;
  - Android storage API becomes necessary;
  - state snapshot API from Bloco 20 becomes necessary;
  - smart playlist behavior becomes necessary.
