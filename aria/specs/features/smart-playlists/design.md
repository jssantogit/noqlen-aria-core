# Design

## Summary

Bloco 19 adds a smart playlist foundation as local Aria Core contracts and deterministic services. It models rule-based playlists, reusable saved filters, and smart mixes over caller-provided `SmartPlaylistItemCandidate` values. It does not persist to providers, mutate queues, start playback, scan files, call network, or implement UI.

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
- Relevant prior review files for library, filters/activity/favorites, queue, and profiles/preferences/backup/restore
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Aria Core already has app-facing library item summaries, filters, activity/favorites read models, deterministic local services, queue contracts, playback intent contracts, and profile/preference/backup foundations. Smart playlist evaluation should align with the library models but should not depend on a source client or provider adapter.

## Files to create

- `src/noqlen_aria/smart_playlists.py`
- `tests/test_smart_playlists.py`
- `aria/specs/features/smart-playlists/requirements.md`
- `aria/specs/features/smart-playlists/design.md`
- `aria/specs/features/smart-playlists/tasks.md`
- `aria/specs/features/smart-playlists/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/specs/features/smart-playlists/tasks.md`
- `aria/specs/features/smart-playlists/review.md`

## Files that must not be touched

- Provider adapter implementations except public exports are not needed.
- Queue, now-playing, playback intent, offline/cache, radio, Android, and CLI behavior files unless validation discovers an unrelated hard failure.
- Android/Kotlin/Java/Gradle/UI files.
- Private/local tooling files.
- Bloco 20 snapshot/e2e-flow files or docs.

## Data flow

Caller supplies `SmartPlaylistDefinition` or `SavedFilterDefinition` plus a tuple of `SmartPlaylistItemCandidate` values. `SmartPlaylistService` validates the definition, evaluates the root rule group, records missing metadata as unavailable/partial issues, sorts matched candidates deterministically, applies any limit, and returns `SmartPlaylistPreview` or `SmartPlaylistEvaluationResult`. `SavedFilterService` follows the same evaluation path for reusable filters. `SmartPlaylistService.build_smart_mix_preview` orders candidates with deterministic seeded keys and returns `SmartMixPreview` only.

## Rule model design

- `SmartPlaylistRuleOperator`: `EQUALS`, `NOT_EQUALS`, `CONTAINS`, `NOT_CONTAINS`, `GREATER_THAN`, `LESS_THAN`, `IS_TRUE`, `IS_FALSE`, `IS_PRESENT`, `IS_MISSING`, and `UNSUPPORTED`.
- `SmartPlaylistRule`: a field, operator, optional value, and `required` flag.
- `SmartPlaylistRuleGroup`: `match_all` boolean plus rules and nested groups.
- `SmartPlaylistItemCandidate`: app-facing item summary, normalized metadata fields, boolean activity/favorite fields, numeric rating/play count/duration fields, and an `extras` mapping for future app-facing metadata.
- Unsupported fields/operators are validation issues; missing field values during evaluation produce unavailable/partial result state.

## Saved filter design

`SavedFilterDefinition` owns a reusable `SmartPlaylistRuleGroup` and optional summary fields. `SavedFilterService` validates the underlying rule group and previews filtered candidates. It may align with existing Bloco 10 filter semantics by using app-facing fields only, but it does not instantiate provider filters or UI widgets.

## Smart mix design

`SmartMixDefinition` owns a base `SmartPlaylistRuleGroup`, a `SmartMixStrategy`, a deterministic `SmartMixSeed`, and an optional limit. `SmartMixStrategy.DETERMINISTIC_SHUFFLE` provides random-like behavior by hashing seed plus candidate identity with `hashlib.sha256`. No global random state or wall-clock time is used.

## Error handling

Validation failures return `AriaResult(ok=True, data=preview/result)` with issues and unavailable reason for safe user-facing feedback unless the caller asks for a blocked unsupported provider creation operation, which returns `AriaResult(ok=False, error=AriaError(...))`. Services do not raise for invalid user definitions.

## Security considerations

Definitions and candidates are app-facing data only. Services must not include secrets, raw local paths, provider internals, stack traces, network details, or direct provider names in errors. Existing `AriaError` sanitization remains in effect.

## Provider boundary considerations

Evaluation accepts only provided candidates and never opens a `MediaSourceClient`, provider adapter, Anchor internals, or provider-specific client. Provider playlist creation is represented by `request_provider_playlist_creation`, which always returns unsupported and performs no side effect.

## Deterministic evaluation rules

- Candidate order is preserved unless a sort or smart mix strategy changes it.
- Sort keys are derived from explicit app-facing fields and stable original indexes.
- Limits slice deterministic results after sorting/mixing.
- Smart mix seeded shuffle uses a stable SHA-256 key from `seed`, `source_id`, `item_id`, `display_name`, and original index.
- Tests use fixed candidates and fixed seeds.

## Dependencies

None. Use Python standard library only.

## Risks

- Smart playlist models could accidentally imply provider writes; mitigated by explicit blocked method and boundary tests.
- Missing metadata could be mistaken for false; mitigated by unavailable/partial reason tests.
- Random-like mix could become nondeterministic; mitigated by seed/hash tests.
- Public exports could grow unintentionally; mitigated by hardening test update.

## Rollback strategy

Revert `src/noqlen_aria/smart_playlists.py`, its public exports, tests, spec directory, and concise context updates. No persisted data, provider state, queue state, files, or background jobs are created.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/smart-playlists aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- Repository contamination check
- Provider/network/filesystem/Android/queue/playback/Bloco 20 boundary searches

## Behavior Budget

- New behaviors: add smart playlist rule models; add smart playlist definition/preview/evaluation models; add smart mix definition/preview models; add saved filter definition/preview models; add deterministic local smart playlist evaluation service; add validation for unsupported fields/operators.
- Public API changes: expose only intentional smart playlist, smart mix, and saved filter names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/smart-playlists/**`, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: rule validation; unsupported operator behavior; saved filter preview; smart playlist preview; smart mix preview; deterministic sorting/limit behavior; empty library behavior; unavailable field behavior; no provider mutation; no queue mutation; no filesystem/network/UI behavior.
- Dependencies: none.
- Stop if: provider playlist creation, queue mutation, playback, background scheduling, filesystem scan, or UI implementation becomes necessary.
