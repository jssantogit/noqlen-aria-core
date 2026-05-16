# Handoff

Bloco 0 state: repository bootstrap, Aria Workflow context, spec templates, review templates, docs, minimal package, CLI doctor, and CLI tests.

Implemented scope:

- Repository structure and workflow contract.
- Public docs for architecture and safety boundaries.
- Aria context files for project, architecture, conventions, tools, forbidden patterns, context hygiene, and mistakes.
- Spec, agent, prompt, and review templates.
- Minimal safe local CLI with `doctor`.

Not implemented:

- Android UI or SDK code.
- Playback engine, queues, now playing, cache/offline/download, media controls, Android Auto, or real music-library access.
- Provider hard coupling or real provider integrations.

Bloco 1 status: complete. Aria Core contracts implemented in `src/noqlen_aria/contracts.py` with source-agnostic `ControlClient`/`FakeControlClient`, plus comprehensive tests in `tests/test_contracts.py`.

Bloco 1.5 status: complete. `ControlClient` is generic and source-agnostic; Anchor is one adapter, not the center of Aria.

Bloco 2 status: complete. Five services implemented in `src/noqlen_aria/services.py` (`ResultMappingService`, `StatusService`, `DiagnosticsService`, `LifecycleIntentService`, `ReadinessService`) plus `LifecycleIntentPreview`. `FakeControlClient` extended with failure-injection/value-override hooks.

Bloco 3 status: complete. `AnchorControlClient` adapter implemented in `src/noqlen_aria/anchor_adapter.py` with `AnchorResultMapper` mapping layer. Adapter uses lazy optional `noqlen_anchor` import and constructor dependency injection. `send_lifecycle_intent` uses dry-run helpers only; apply-mode is blocked.

Bloco 4 status: complete. Android/player boundary contracts implemented in `src/noqlen_aria/android_boundaries.py` with 9 bridge protocols, supporting types, `AndroidBoundarySnapshot`, and 9 deterministic fake implementations. 129 tests in `tests/test_android_boundaries.py`.

Bloco 5 status: planning artifacts complete. Minimal UI Shell boundary documentation created in `docs/ui-shell-boundary.md` and referenced from `docs/architecture.md` and `docs/android-boundary.md`. The docs define the future thin UI/app shell role, Aria Core role, platform adapter role, allowed state/intent flows, anti-coupling rules, and conceptual examples. No UI or source implementation exists.

Bloco 6 status: complete. Aria MVP hardening added explicit public exports, safe serialization/sanitization helpers, safer Anchor adapter error output, optional Anchor absence coverage, dry-run/apply safety tests, forbidden integration checks, and documentation updates. No Android/UI/playback/queue/cache/provider implementation exists.

Bloco 7 status: complete. Aria Core Release Preparation implemented. Release artifacts created: release checklist (`docs/release-checklist.md`), release notes (`docs/release-notes.md`), public API surface summary (`docs/api-surface.md`), safety summary (`docs/safety-summary.md`), and post-core backlog summary (`docs/post-core-backlog.md`). All validation commands pass (368 tests). Local tag `v0.1.0` exists; no package publish action is recorded in this handoff.

Roadmap status: Aria Core MVP scope is Blocos 0-7. Post-core feature expansion starts after `v0.1.0`, is now explicit as Blocos 8-23, and is documented in `docs/post-core-backlog.md`. Advanced library/player features, stream quality/transcoding policy, backup/restore, profiles/preferences, state snapshots, automation intents, Android real integration, and the Android app/UI shell are not MVP blockers and are not implemented.

Repository direction: Aria Core is the modular app/player-facing core of a music player. The canonical local handoff is `docs/aria-core-handoff.md`.

Workflow vNext status: future tasks should start from `aria/context/current.md`, `aria/context/delta.md`, and the context package policy before reading large handoff context.

Release artifacts:
- `docs/release-checklist.md` — release readiness checklist with pass/fail items and final stop conditions.
- `docs/release-notes.md` — release notes covering completed Blocos 0-7, safety boundaries, known limitations, and post-core backlog.
- `docs/api-surface.md` — public API surface summary with all stable exports.
- `docs/safety-summary.md` — verified safety boundaries.
- `docs/post-core-backlog.md` — post-core features roadmap and backlog.

Third-party names in research docs are factual references only. They do not imply Noqlen affiliation, endorsement, sponsorship, association, official support, or compatibility.

Bloco 8 status: implemented. `src/noqlen_aria/media_source.py` provides `MediaSourceClient` protocol, `FakeMediaSourceClient`, 11 supporting types (media source identity, abstract media IDs, source capabilities, stream handle, provider capability). `tests/test_media_source.py` adds 100 tests (468 total). No provider integration, streaming, playback, Android, UI, queue, now playing, or cache code exists.

Bloco 9 status: implemented. `src/noqlen_aria/library.py` provides browse/search models and services for artists, albums, tracks, playlists, genres, and safe folder metadata. `tests/test_library_browse_search.py` covers unsupported capabilities, empty/no-match search, degraded/unavailable sources, and boundary enforcement. No provider integration, filesystem traversal, playback, queue, now playing, or cache code exists.

Bloco 10 status: implemented. `src/noqlen_aria/library.py` extended with filter/sort services, recently added/recently played activity, favorites read state, and readiness/health badges. Favorites mutation is blocked as unsupported. No provider mutation, smart playlists, queue, playback, or cache code exists.

Bloco 11 status: implemented. `src/noqlen_aria/queue.py` provides queue state, repeat/shuffle contracts, deterministic `QueueService`, fake queue scenarios, and multiple queue collection state. `tests/test_queue_foundation.py` covers invalid operations, unavailable items, and deterministic shuffle. No playback, stream resolution, provider integration, or cache code exists.

Bloco 12 status: implemented. `src/noqlen_aria/now_playing.py` provides now-playing state, playback availability vocabulary, resumable state, position snapshots, and deterministic `NowPlayingService`. No playback intent execution, stream resolution, provider integration, or cache code exists.

Bloco 13 status: implemented. `src/noqlen_aria/playback_intents.py` provides playback intent models, renderer selection models, automation intent models, and three deterministic preview/validation services. No real playback, stream resolution, provider integration, Android/UI, or cache code exists.

Audit 8-13 status: the formal audit for Blocos 8-13 has been completed. All blocks pass architecture, safety, test, spec, docs, boundary, and repository hygiene checks.

Bloco 14 status: implemented. `src/noqlen_aria/offline_cache.py` provides offline/cache/storage policy models (OfflineAvailabilityState, CachePolicyState, CacheEligibilityState, CacheOperationIntent, CacheOperationPreview, PendingCacheOperation, StoragePressureState, StoragePressureLevel, StorageBudget, CacheCleanupPolicy, CacheCleanupPreview, CacheConfirmationState, CacheBlockedReason) and three deterministic local services (OfflineCachePolicyService, StoragePressureService, CacheCleanupPreviewService). `tests/test_offline_cache_storage_policy.py` adds 104 tests (746 total). No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage APIs, provider mutation, stream resolution, playback engine, or Bloco 15 behavior exists.

Next step: Bloco 15 spec after explicit approval. Do not implement post-core features or publish without dedicated scope.

Future Android Player audio output phases (A–E) are documented in `docs/aria-core-handoff.md` and `docs/post-core-backlog.md` as a future project outside Aria Core. Aria Core remains driver-free.
