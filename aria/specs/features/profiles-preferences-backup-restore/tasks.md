# Tasks

## Preparation checklist

- [x] Read required Aria context, handoff, safety, backlog, templates, prior reviews, source, tests, and validation checklist.
- [x] Use Context package: Standard.
- [x] Define Behavior Budget before implementation.
- [x] Define Canonical Examples before implementation.
- [x] Define Test Risk Matrix before implementation.

## TDD classification

- Required for preference validation.
- Required for secret/path sanitization in backup bundles.
- Required for restore preview/conflict behavior.
- Required for invalid/corrupt bundle behavior.
- Required for blocking real music library backup scope.
- Recommended for model defaults and serialization.

## Test Risk Matrix

| Area | Risk | Required coverage |
|------|------|-------------------|
| Preference validation and scope behavior | High | Negative tests for invalid keys, secret-like keys, raw paths, missing profile id; success tests for global/profile lookup |
| Secret/path sanitization in backup bundles | High | Verify secret-like entries excluded and raw personal paths redacted/excluded without exposing values |
| Restore preview/conflict behavior | High | Verify valid bundle preview, existing id/name conflicts, future decision required, no apply |
| Invalid/corrupt bundle behavior | High | Verify missing manifest/payload, wrong type, unsupported version, unsafe payload fail safely |
| Blocking real music library backup scope | High | Verify unsafe scope blocked and no bundle produced |
| Profile creation/selection validation | Medium | Verify defaults, valid preview, invalid names/ids, duplicate selection |
| Backup manifest/bundle defaults | Medium | Verify deterministic counts, scopes, bundle id, warnings |
| Public exports and serialization | Medium | Verify intentional top-level exports and JSON-compatible safe serialization |
| Documentation/context updates | Low | Verify review/current/delta are concise and updated |

## Behavior Budget check

- [x] New behavior limited to Bloco 18 profile/preference/backup/restore models and deterministic services.
- [x] Public API additions are intentional and named in the spec.
- [x] Allowed files only.
- [x] No new dependencies.
- [x] Stop conditions reviewed.

## Implementation tasks

- [x] Create Bloco 18 spec files.
- [x] Implement profile contracts and `ProfilesService`.
- [x] Implement preference contracts and `PreferencesService`.
- [x] Implement backup/restore contracts and `BackupRestoreService`.
- [x] Add deterministic fake/in-memory profile/preference/backup scenarios through unit tests.
- [x] Export intentional public names from `noqlen_aria`.
- [x] Update export-surface tests.
- [x] Add deterministic unit tests for required behavior and boundaries.

## Validation checklist

- [x] `pwd`
- [x] `git status --short --branch`
- [x] `find src/noqlen_aria tests aria/specs/features/profiles-preferences-backup-restore aria/context -maxdepth 6 -type f | sort`
- [x] `git diff --check`
- [x] `python3 -m py_compile src/noqlen_aria/*.py`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- [x] `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- [x] `python3 -m pytest`
- [x] Repository contamination check.
- [x] Required boundary search checks.

## Review checklist

- [x] Spec was created.
- [x] Implementation matches the Bloco 18 spec.
- [x] No Bloco 19 behavior was implemented.
- [x] No Bloco 20 behavior was implemented.
- [x] No real file backup/restore exists.
- [x] No destructive restore/apply exists.
- [x] No real music library mutation exists.
- [x] No provider mutation or provider internals were added.
- [x] No Android storage/API/UI code was added.
- [x] Secrets/raw paths are excluded or redacted.
- [x] Behavior Budget and Test Risk Matrix are present.
- [x] Tests pass.
- [x] `current.md` and `delta.md` stayed concise.
- [x] No private/local/tooling files are tracked.

## Delta update checklist

- [x] Update `aria/context/current.md` with concise Bloco 18 status.
- [x] Update `aria/context/delta.md` with concise change and validation evidence.
- [x] Update this task checklist after implementation.
- [x] Update `review.md` after validation.
