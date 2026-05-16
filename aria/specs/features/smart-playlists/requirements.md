# Requirements

## Status

Approved for Bloco 19 implementation in this task. Context package: Standard.

## Problem

Aria Core has library browse/search, filters, activity, favorites, queue, now-playing, playback intent, offline/cache, radio, capability, profile, preference, backup, and restore foundations. It does not yet have source-agnostic smart playlist contracts for reusable rule definitions, saved filters, deterministic previews, or smart mixes. Future UI and provider adapters need a safe core model that can evaluate app-facing library summaries without writing to providers, mutating queues, starting playback, scanning files, or implementing Android/UI behavior.

## Goal

Add a local-only smart playlist foundation with rule models, definition/preview/evaluation models, saved filter models, smart mix preview models, deterministic services, fake/library scenarios, and tests. Evaluation must use caller-provided app-facing library item candidates only.

## Non-goals

- No real provider playlist creation.
- No provider mutation.
- No direct Navidrome, Jellyfin, or Emby integration.
- No Anchor provider internals.
- No Anchor CLI integration.
- No queue mutation.
- No playback or stream resolution.
- No background jobs, scheduler, or refresh worker.
- No filesystem scanning or real music-library traversal.
- No network behavior.
- No Android, Kotlin, Java, Gradle, UI, screens, navigation, or player code.
- No Bloco 20 state snapshot, API snapshot, or end-to-end fake flow behavior.

## Actors

- Future UI/app: displays definitions and previews through Aria Core models.
- Future provider adapter: may later persist provider playlists outside this block, through a future spec only.
- Aria Core service caller: supplies app-facing library item candidates and receives safe previews/results.
- Test suite: validates deterministic evaluation, unsupported behavior, and boundary preservation.

## Functional requirements

- FR-01 Define `SmartPlaylistId`, `SmartPlaylistSummary`, `SmartPlaylistDefinition`, `SmartPlaylistRule`, `SmartPlaylistRuleGroup`, `SmartPlaylistRuleOperator`, `SmartPlaylistSortRule`, `SmartPlaylistLimit`, `SmartPlaylistEvaluationContext`, `SmartPlaylistEvaluationResult`, `SmartPlaylistItemCandidate`, `SmartPlaylistPreview`, `SmartPlaylistValidationIssue`, and `SmartPlaylistUnavailableReason`.
- FR-02 Define `SmartMixDefinition`, `SmartMixStrategy`, `SmartMixPreview`, and `SmartMixSeed`.
- FR-03 Define `SavedFilterId`, `SavedFilterDefinition`, `SavedFilterPreview`, and `SavedFilterValidationIssue`.
- FR-04 Implement `SmartPlaylistService` to validate definitions, evaluate rule groups against provided item candidates, build playlist previews, build smart mix previews with deterministic seeded behavior, apply sort rules, apply limits, and block provider playlist creation as unsupported.
- FR-05 Implement `SavedFilterService` to validate saved filters and preview them against provided app-facing item candidates.
- FR-06 Rule evaluation must support app-facing fields: `display_name`, `subtitle`, `item_kind`, `artist_name`, `album_name`, `genre`, `favorite`, `recently_added`, `recently_played`, `play_count`, `rating`, and `duration_seconds` when present on `SmartPlaylistItemCandidate`.
- FR-07 Validation must return issues for unsupported fields, unsupported operators, empty rule groups, invalid limits, and invalid sort fields.
- FR-08 Missing metadata must not crash evaluation; it must produce a safe unavailable/partial result when a requested field is unavailable on at least one candidate.
- FR-09 Smart mix random-like behavior must be deterministic from a seed and candidate identity.
- FR-10 Empty libraries must return successful empty previews/results.
- FR-11 Provider write/persist operations must be represented as blocked/unsupported future intent, not performed.
- FR-12 Services must not call providers, queues, playback, filesystem, network, background jobs, or UI/platform APIs.

## Non-functional requirements

- Deterministic, local, offline, stdlib-only behavior.
- Source-agnostic and provider-agnostic model names.
- Safe app-facing errors and validation issues.
- No new dependencies.
- Public API expansion limited to intentional smart playlist, smart mix, and saved filter contracts/services.
- Tests must remain deterministic and not depend on wall-clock time, filesystem, network, providers, queues, playback, or Android/UI.

## Canonical Examples

- Given a smart playlist rule selects favorite tracks, When evaluated against provided library items, Then Aria returns a preview list without mutating providers.
- Given a smart playlist rule uses recently played metadata, When metadata is missing, Then Aria returns a safe unavailable or partial result.
- Given a rule uses an unsupported operator, When validation runs, Then Aria returns a validation issue.
- Given a saved filter is valid, When preview is requested, Then Aria applies it to app-facing items only.
- Given a smart mix requests random-like behavior, When evaluated in tests, Then Aria uses deterministic seeded behavior.
- Given a playlist preview is accepted later, When Bloco 19 runs, Then no real provider playlist is created.
- Given UI needs smart playlists later, When it consumes data, Then it uses Aria Core models and does not call providers directly.

## Edge cases

- Empty library candidates return empty available previews.
- Empty rule groups are invalid.
- Unsupported fields and operators return validation issues and unavailable previews.
- Missing metadata for requested fields returns partial/unavailable state and warnings/issues instead of crashing.
- Limits below one are invalid; limits above candidate count return all matched items.
- Sort ties are stable and deterministic by original order and candidate identity.
- Deterministic mix behavior is stable for the same seed and changes predictably for a different seed.
- Provider creation requests return an unsupported result and do not mutate provider state.

## Acceptance criteria

- Spec files exist under `aria/specs/features/smart-playlists/`.
- Behavior Budget, Test Risk Matrix, Canonical Examples, and Delta update checklist are present.
- Required models and services are implemented and intentionally exported.
- Tests cover validation, unsupported operator/field behavior, saved filter preview, smart playlist preview, smart mix preview, sorting/limit, empty library, unavailable field behavior, provider mutation blocking, queue/playback boundary, and no filesystem/network/UI behavior.
- Required validation commands pass.
- `aria/context/current.md` and `aria/context/delta.md` are concise and updated.
- No Bloco 20 behavior is implemented.

## Open questions

- Future provider persistence format is deferred to a later provider/playlist spec.
- Future UI editing workflow is deferred to a later UI/app spec.
- Future background refresh/scheduling is explicitly out of scope and requires a separate spec.
