# Delta Summary

## What changed

- Bloco 14 implemented: offline/cache/storage policy models (OfflineAvailabilityState, OfflineAvailabilityReason, CachePolicyState, CachePolicyMode, CacheEligibilityState, CacheOperationIntent, CacheOperationType, CacheOperationPreview, CacheOperationResult, PendingCacheOperation, StoragePressureState, StoragePressureLevel, StorageBudget, CacheCleanupPolicy, CacheCleanupPreview, CacheConfirmationState, CacheBlockedReason) and three deterministic local services (OfflineCachePolicyService, StoragePressureService, CacheCleanupPreviewService). No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage APIs, provider mutation, stream resolution, playback engine, or Bloco 15 behavior added.

- Audit 8-13 completed: formal audit of Blocos 8-13 post-core media/library/queue/now-playing/playback-intent foundation. Architecture, safety, tests, specs, docs, boundaries, and repository hygiene verified. No real playback, stream resolution, provider integration, Android/UI, offline/cache, smart playlist, network, or filesystem behavior found. Minor fixes: stale handoff/context references corrected, confusing test assertion simplified, unchecked spec task items marked complete.

- Bloco 13 implemented: playback intent models (PlaybackIntent, PlaybackIntentType, PlaybackIntentResult, PlaybackCommandPreview, PlaybackBlockedReason, SeekTarget, SkipDirection, PlaybackIntentValidationIssue), renderer intent models (RendererId, RendererRef, RendererType, RendererAvailabilityState, RendererCapabilitySummary, RendererSelectionIntent, RendererSelectionResult), automation intent models (AutomationIntent, AutomationIntentType, AutomationIntentSource, AutomationIntentResult, AutomationSafetyLevel), and three deterministic local services (PlaybackIntentService, RendererIntentService, AutomationIntentService). No real playback, stream resolution, provider integration, Android/UI, offline/cache, smart playlist, network, or filesystem behavior was added.

- Blocos 4-6 formal audit found stale context/handoff references and CLI/doc wording that still described earlier blocks; audit-scoped corrections were applied.
- Bloco 1 completed source-agnostic core contracts, safe result/state primitives, `ControlClient`, and `FakeControlClient`.
- Bloco 2 completed fake-first control services, result mapping, readiness, diagnostics, lifecycle preview, and deterministic failure/value overrides.
- Bloco 3 completed the dry-run/offline `AnchorControlClient` adapter and mapping layer while blocking apply-mode behavior.
- Workflow vNext added compact context files, context packages, Behavior Budget, Test Risk Matrix, fake-hostility checklist, minimal role prompts, spec-template updates, and ADR templates.
- Bloco 4 implemented: `src/noqlen_aria/android_boundaries.py` with 9 bridge protocols, supporting types, and 9 deterministic fake implementations.
- Bloco 5 Minimal UI Shell Planning artifacts created: `docs/ui-shell-boundary.md` and architecture/android boundary updates. Documentation only.
- Bloco 6 implemented: explicit package/module exports, safe serialization and sanitization helpers, safer Anchor adapter exception output, hardening tests. No Android/UI/playback/queue/cache/provider implementation.
- Bloco 7 implemented: release readiness checklist, release notes, public API surface summary, safety summary, post-core backlog summary, handoff update, and README refresh. Documentation only; no publish, source, version, or implementation changes.
- Roadmap alignment update: Aria Core MVP is Blocos 0-7; post-core feature expansion is being restored explicitly as Blocos 8-23. Advanced library/player features and Android real integration remain backlog.
- Bloco 20 wording update: provider extension readiness, not real multi-provider support through current Anchor.
- Local tag `v0.1.0` exists. No publish action is recorded in this delta.
- Release artifacts created: `docs/release-checklist.md`, `docs/release-notes.md`, `docs/api-surface.md`, `docs/safety-summary.md`, `docs/post-core-backlog.md`.
- Workflow improvements from Noqlen Playbook comparison added: broader repository hygiene categories, PR template, read-only local repository study prompt, clearer audit finding/status fields, and Workflow vNext references. Workflow/template changes only.
- Bloco 8 spec created: `aria/specs/features/media-source-foundation/` with `requirements.md`, `design.md`, `tasks.md`, `review.md`.
- Bloco 8 implemented: `src/noqlen_aria/media_source.py` with `MediaSourceClient` protocol, `FakeMediaSourceClient`, and 11 supporting types. `tests/test_media_source.py` adds 100 tests.
- Bloco 9 implemented: `src/noqlen_aria/library.py` with browse/search models and services. `tests/test_library_browse_search.py`.
- Bloco 10 implemented: library filter/sort contracts and service behavior, recently added/recently played/favorites models and services, readiness/health badges.
- Bloco 11 implemented: queue state/contracts, repeat/shuffle state, queue operation/intent/result models, deterministic `QueueService`, fake queue scenarios.
- Bloco 12 implemented: now-playing state/contracts, playback availability vocabulary, deterministic `NowPlayingService`, fake now-playing scenarios.

## Evidence

- Bloco 14 implementation validation: `python3 -m pytest` 746/746 pass (642 base + 104 new); `py_compile` clean; CLI help/doctor pass; provider/network/filesystem/Android/smart-playlist/transcoding checks clean; contamination clean.
- Bloco 13 implementation validation: `python3 -m pytest` 642/642 pass; `py_compile` clean; CLI help/doctor pass; provider/network/filesystem/playback-intent/offline/smart-playlist checks clean; Android search reports existing Android boundary/LibraryActivity vocabulary only; contamination clean.
- Audit 8-13 completed and validated.
- All prior Bloco validation records remain valid.

## Decisions

- Aria Core remains UI-independent.
- `ControlClient` is source-agnostic.
- Anchor is one `ControlClient` adapter, not the center of Aria.
- Context files carry standing rules; prompts should carry only task deltas.
- Local tag `v0.1.0` exists; publish still requires explicit approval.
- Cross-repository workflow study should be read-only and sanitized unless a separate task explicitly scopes retrofit work.
- Storage pressure thresholds use `<=` (inclusive) for defensive classification.

## Regressions found

- None.

## Next step

- Bloco 14 (Offline, Cache and Storage Policy) is implemented and validated.
- Do not start Bloco 15 without explicit approval and a dedicated spec.

## Open decisions

- Whether/when to publish package artifacts.
- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
