# Design

## Summary

Bloco 12 adds local now-playing contracts and a deterministic `NowPlayingService`. Now playing is app/player-facing state only: it may reference queue and library/media summaries, but it does not play audio, resolve streams, call providers, mutate real providers, or depend on Android SDKs.

## Context package

Standard. See `aria/context/context-packages.md`.

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
- Bloco 8, 9, 10, and 11 review files
- `src/noqlen_aria/**`
- `tests/**`
- `aria/review/validation-checklist.md`

## Existing project context

Bloco 11 provides `QueueState`, `QueueItem`, `QueueAvailabilityState`, and deterministic queue scenarios. Blocos 8-10 provide media IDs, media source IDs, and library item summaries. Bloco 12 should consume those contracts and add a now-playing snapshot layer without provider or playback behavior.

## Files to create

- `src/noqlen_aria/now_playing.py`
- `tests/test_now_playing_foundation.py`
- `aria/specs/features/now-playing-foundation/requirements.md`
- `aria/specs/features/now-playing-foundation/design.md`
- `aria/specs/features/now-playing-foundation/tasks.md`
- `aria/specs/features/now-playing-foundation/review.md`

## Files to modify

- `src/noqlen_aria/__init__.py`
- `tests/test_mvp_hardening.py`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/specs/features/now-playing-foundation/tasks.md`
- `aria/specs/features/now-playing-foundation/review.md`

## Files that must not be touched

- Android, Kotlin, Java, Gradle, UI, screen, navigation, player, or media-session files.
- Provider adapter internals.
- Anchor provider internals or Anchor CLI integration.
- Offline/cache or smart playlist files.
- Private/local tooling files.

## Data flow

1. Caller passes no queue state, an empty queue, or a `QueueState` to `NowPlayingService`.
2. Service reads `QueueState.current_position` and `QueueState.items`.
3. If there is no active item, service returns idle `NowPlayingState`.
4. If there is an active `QueueItem`, service builds `NowPlayingItem` by copying queue item ID, library summary, media ID, source ID, display name, and availability reason.
5. Availability is derived locally from queue item availability and explicit caller input.
6. Optional position and resumable state are validated locally.
7. Caller receives `AriaResult[NowPlayingState]` or a safe `AriaResult` error.

## Error handling

- Invalid queue current position returns `INVALID_NOW_PLAYING_QUEUE_POSITION`.
- Negative position returns `INVALID_PLAYBACK_POSITION`.
- Position beyond known duration returns `PLAYBACK_POSITION_EXCEEDS_DURATION`.
- Resumable state without an item returns `RESUMABLE_ITEM_REQUIRED`.
- Blocked/unavailable availability without a concrete reason is normalized to a safe explicit reason.

## Security considerations

- All state is app-facing and uses existing sanitized `AriaError` behavior.
- No raw provider errors, local paths, tokens, credentials, or private library data are introduced.
- `safe_serialize` must serialize now-playing state into JSON-compatible values.

## Provider boundary considerations

Now-playing does not call `MediaSourceClient`, request stream handles, inspect provider capabilities, call Anchor provider internals, call direct provider integrations, or use provider brand-specific names. It only references Aria Core media IDs and summaries already present in queue/library state.

## Now-playing state transition rules

- No active queue item -> `NowPlayingStatus.IDLE`, `item=None`, safe default availability.
- Active available queue item -> `NowPlayingStatus.READY`, item present, availability available.
- Active unavailable queue item -> `NowPlayingStatus.UNAVAILABLE`, item present, explicit `UnavailableMediaState`, availability unavailable.
- Valid position snapshot may be attached to ready, paused, unavailable, or resumable state.
- Resumable state is explicit and requires an item plus a valid position snapshot.
- Bloco 12 never transitions through play, pause, seek, skip, renderer selection, or playback intent execution.

## Dependencies

None. Standard library and existing Aria Core modules only.

## Risks

- Naming playback vocabulary too broadly could imply playback intent behavior. Mitigation: status and availability are state only.
- Position validation could become playback-engine logic. Mitigation: validate only simple snapshot bounds.
- Queue relation could mutate queue state. Mitigation: consume `QueueState` as immutable input and return a separate now-playing state.

## Rollback strategy

Remove `src/noqlen_aria/now_playing.py`, its tests, top-level exports, and the Bloco 12 spec/context updates. No data migrations or external state exist.

## Validation plan

- `pwd`
- `git status --short --branch`
- `find src/noqlen_aria tests aria/specs/features/now-playing-foundation aria/context -maxdepth 6 -type f | sort`
- `git diff --check`
- `python3 -m py_compile src/noqlen_aria/*.py`
- `PYTHONPATH=src python3 -m noqlen_aria.cli --help`
- `PYTHONPATH=src python3 -m noqlen_aria.cli doctor`
- `python3 -m pytest`
- tracked forbidden-file contamination check
- provider/network/filesystem/Android/playback-intent/offline/smart-playlist search checks

## Behavior Budget

- New behaviors: add now-playing state/contracts; add playback availability state vocabulary; add resumable/unavailable media state; add local deterministic `NowPlayingService`; reference existing queue/media models without playback.
- Public API changes: expose only intentional now-playing foundation names.
- Files allowed: `src/noqlen_aria/**`, `tests/**`, `aria/specs/features/now-playing-foundation/**`, `aria/context/current.md`, `aria/context/delta.md`, and `docs/handoff.md` only if a tiny status note is needed.
- Tests required: empty/idle now-playing state; now-playing from queue item; unavailable media state; resumable state; playback position snapshot validation; availability states; no provider/playback/network/filesystem behavior.
- Dependencies: none.
- Stop if: real playback, playback intent execution, stream resolution, provider mutation, provider integration, or Android integration becomes necessary.
