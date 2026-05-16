# Delta Summary

## What changed

- Bloco 20 implemented: state snapshot models (AriaStateSnapshot, AriaSnapshotId, AriaSnapshotScope, AriaSnapshotMetadata, AriaSnapshotSection, AriaSnapshotRedactionPolicy, AriaSnapshotValidationIssue, AriaSnapshotResult, AriaSnapshotDiff, AriaSnapshotDiffEntry, AriaSnapshotUnavailableReason), deterministic services (AriaSnapshotService, AriaSnapshotDiffService), fake flow models (FakeFlowId, FakeFlowScenario, FakeFlowStep, FakeFlowStepKind, FakeFlowStepResult, FakeFlowTrace, FakeFlowResult, FakeFlowValidationIssue, FakeFlowUnavailableReason), and FakeFlowRunner scenarios for source/library/queue/now-playing/diagnostics, profile/preferences/smart playlist/queue preview, radio unavailable/playback preview, offline/cache/quality/capability summary, and degraded source partial flow. Snapshots are sanitized and in-memory only; fake flows are deterministic and local-only. No real provider integration, network, filesystem persistence/traversal, real music library access, playback, stream resolution, Android/UI, background jobs, provider mutation, or Bloco 21 provider extension behavior added.

- Bloco 19 implemented: smart playlist models (SmartPlaylistId, SmartPlaylistSummary, SmartPlaylistDefinition, SmartPlaylistRule, SmartPlaylistRuleGroup, SmartPlaylistRuleOperator, SmartPlaylistSortRule, SmartPlaylistLimit, SmartPlaylistEvaluationContext, SmartPlaylistEvaluationResult, SmartPlaylistItemCandidate, SmartPlaylistPreview, SmartPlaylistValidationIssue, SmartPlaylistUnavailableReason), smart mix models (SmartMixDefinition, SmartMixStrategy, SmartMixPreview, SmartMixSeed), saved filter models (SavedFilterId, SavedFilterDefinition, SavedFilterPreview, SavedFilterValidationIssue), deterministic services (SmartPlaylistService, SavedFilterService), and FakeSmartPlaylistScenarios. Evaluation is local-only over provided app-facing candidates. No real provider playlist creation, provider mutation/internals, direct provider integration, queue mutation, playback, background jobs, filesystem scans, network behavior, Android/UI, or Bloco 20 state snapshot/e2e fake flows added.

- Bloco 18 implemented: profile state models (UserProfileId, UserProfileSummary, UserProfileState, ActiveProfileState, ProfileOperationIntent/Preview), preference state/validation models (UserPreferenceKey, UserPreferenceValue, UserPreferenceScope, UserPreferencesState, PreferenceUpdateIntent/Preview), backup/restore models (BackupScope, BackupManifest, BackupBundle, BackupPlan/Preview/Result, RestorePlan/Preview/Result, RestoreConflict, RestoreSafetyCheck, BackupRestoreWarning, BackupBlockedReason), and deterministic local services (ProfilesService, PreferencesService, BackupRestoreService). Backup is in-memory structured state only; restore is preview-first and `applied=False`. No real filesystem persistence, destructive restore/apply, music library backup/mutation, provider mutation/internals, Android storage/API/UI, Bloco 19 smart playlist behavior, Bloco 20 state snapshots/e2e fake flows, network behavior, or secrets/raw path exposure added.

- Audit 14-17 completed: formal audit for Bloco 14 Offline/Cache/Storage Policy, Bloco 15 Internet Radio Foundation, Bloco 16 Stream Quality/Transcoding/Network Policy, Bloco 17 Playback Capability Models, and the fade capability follow-up. Audit-scoped fixes applied: stale roadmap/context/spec status corrected, Bloco 14 task checklist completed, storage pressure inclusive-threshold wording aligned with implementation/tests, and bit-perfect system-audio readiness now reports non-exclusive output before generic unsupported state. No Bloco 18 behavior, profiles/preferences/backup/restore, smart playlists, snapshots/e2e fake flows, real cache mutation, filesystem/device behavior, network/radio streaming/transcoding, playback/audio driver/USB output, Android/JNI/NDK/AAudio/Oboe/Media3/ExoPlayer/MediaSession, DSP/EQ, or provider integration added.

- Bloco 17 implemented with fade follow-up: playback capability models (GaplessCapabilityState, LoudnessNormalizationCapabilityState, ReplayGainAwarenessState, CrossfadeCapabilityState, FadeCapabilityState, FadeMode, FadeTimingPreference, FadeAvailabilityState, FadeUnavailableReason, BitPerfectCapabilityState, PlaybackCapabilitySummary, PlaybackCapabilityWarning, PlaybackQualityPreference), audio output readiness models (AudioOutputRouteState, AudioOutputRouteType, AudioOutputDeviceState, UsbDacCapabilityState, ExclusiveOutputCapabilityState, SampleRateSupport, BitDepthSupport, AudioFormatSupport, AudioOutputReadinessState), deterministic services (PlaybackCapabilityService, AudioOutputCapabilityService), and FakePlaybackCapabilityScenarios. No real playback, fade/audio processing, volume automation, audio driver, USB driver, Android/JNI/NDK/AAudio/Oboe, Media3/ExoPlayer/MediaSession, real bit-perfect output, sample-rate switching, DAC control, DSP/EQ, provider integration, network behavior, filesystem/device traversal, Audit 14-17 work, or Bloco 18 behavior added.

- Bloco 16 implemented: stream quality policy models (StreamQualityPreference, StreamQualityPolicy, StreamQualityProfile, StreamQualityDecision, StreamQualityReason, BitrateLimit, BandwidthBudget, QualityFallbackPolicy, OfflineQualityPolicy), transcoding capability/policy models (TranscodingCapability, TranscodingPolicy, TranscodingDecision, TranscodingUnavailableReason, TranscodingRequirement, TranscodingPreference), network quality models (NetworkQualityState, NetworkQualityLevel, NetworkConditionSnapshot, NetworkPolicyDecision, NetworkPolicyReason), deterministic services (QualityPolicyService, TranscodingPolicyService, NetworkQualityPolicyService), and FakeQualityPolicyScenarios. No real transcoding, transcoder library, stream execution, network probing/calls, provider integration, playback engine/session, Android/UI code, filesystem traversal, offline download/cache mutation, audio driver/USB work, or Bloco 17 behavior added.

- Bloco 15 implemented: internet radio foundation models (RadioStationId, RadioStationRef, RadioStationSummary, RadioSourceCapability, RadioDirectoryRef, RadioImportSource, ManualRadioStationInput, RadioStreamHandle, RadioStreamKind, RadioPlaybackAvailability, RadioMetadataState, IcyMetadataState, RadioArtworkState, RadioFavoriteState, RadioUnavailableReason, RadioValidationIssue), deterministic InternetRadioService, and FakeRadioScenarios. No real radio streaming, HLS/DASH/Shoutcast client, ICY network parsing, network behavior, playback engine/session, provider integration/mutation, Anchor provider internals, Android/UI code, filesystem traversal, Bloco 16 behavior, or Bloco 17 behavior added.

- Bloco 14 implemented: offline/cache/storage policy models (OfflineAvailabilityState, OfflineAvailabilityReason, CachePolicyState, CachePolicyMode, CacheEligibilityState, CacheOperationIntent, CacheOperationType, CacheOperationPreview, CacheOperationResult, PendingCacheOperation, StoragePressureState, StoragePressureLevel, StorageBudget, CacheCleanupPolicy, CacheCleanupPreview, CacheConfirmationState, CacheBlockedReason) and three deterministic local services (OfflineCachePolicyService, StoragePressureService, CacheCleanupPreviewService). No real download, cache write/delete, destructive cleanup, filesystem traversal, Android storage APIs, provider mutation, stream resolution, playback engine, radio support, or Bloco 15 behavior added.

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
- Roadmap alignment update: Aria Core MVP is Blocos 0-7; post-core feature expansion is now explicit as Blocos 8-24. Advanced library/player features and Android real integration remain backlog.
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

- Bloco 20 implementation validation: `python3 -m pytest` 897/897 pass; targeted Bloco 20/export tests passed with 30 tests; `py_compile` clean; CLI help/doctor pass; `git diff --check` clean; tracked contamination clean. Required boundary searches show no forbidden implementation; expected matches are limited to historical boundary-test string literals, existing queue `_current_after_remove` substring false positives, explicit sanitization vocabulary, Bloco 20 redaction tests/spec text, and ignored generated `__pycache__` binary matches from validation before cleanup.

- Bloco 19 implementation validation: `python3 -m pytest` 877/877 pass; targeted smart playlist/export tests passed with 26 tests; `py_compile` clean; CLI help/doctor pass; `git diff --check` clean; tracked contamination clean. Required boundary searches show no forbidden implementation; expected matches are limited to historical boundary-test string literals, existing queue service tests, existing playback capability wording, and Bloco 19 explicit `queue_mutated=False` / `playback_started=False` safety fields/tests.

- Bloco 18 implementation validation: `python3 -m pytest` 861/861 pass; targeted compile/tests passed; `py_compile` clean; CLI help/doctor pass; `git diff --check` clean; tracked contamination clean. Required boundary searches show no forbidden implementation; expected matches are limited to sanitization vocabulary, explicit boundary tests/spec text, historical LibraryActivity/SAFE substrings, queue `_current_after_remove` false positives, and ignored `__pycache__` binary matches.

- Bloco 16 implementation validation: `python3 -m pytest` 815/815 pass; `py_compile` clean; CLI help/doctor pass; network/provider/filesystem/Android/audio-driver searches clean; transcoding search shows expected Bloco 16 spec/model/test vocabulary only, with no real transcoder implementation; tracked contamination clean.

- Audit 14-17 validation: `python3 -m pytest` 836/836 pass; `py_compile` clean; CLI help/doctor pass; `git diff --check` clean; tracked contamination clean; required boundary searches show no forbidden implementation. Expected matches are limited to data-only enum/test/spec vocabulary, ignored `__pycache__` binary matches, and substring false positives such as `REQUIRED` for the broad `DSP\|EQ` pattern; standalone `DSP`/`EQ` search is clean.

- Bloco 17 fade follow-up validation: `python3 -m pytest` 836/836 pass; `py_compile` clean; CLI help/doctor pass; `git diff --check` clean; contamination clean; Android/audio/provider/network/filesystem/DSP searches show no forbidden implementation, with expected Bloco 16 vocabulary, Bloco 17 boundary-test vocabulary, and ignored `__pycache__` binary matches.

- Bloco 15 implementation validation: `python3 -m pytest` 788/788 pass; `py_compile` clean; CLI help/doctor pass; network/provider/filesystem/Android/transcoding searches show no forbidden implementation, with expected test/spec/model vocabulary matches for unsupported HLS/DASH/Shoutcast and local boundary assertions; tracked contamination clean.

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

- Bloco 20 State Snapshots and End-to-End Fake Flows is implemented and validated.
- Do not start Audit 18-20 or Bloco 21 without explicit approval and a dedicated spec/task.
- Roadmap documentation update: Bloco 17 wording clarified to include bit-perfect capability, USB DAC capability, exclusive output capability, audio output route state, sample-rate support, bit-depth support, output/device readiness, playback quality preferences, and driver bridge vocabulary for a future Android player. Bloco 17 remains capability/readiness/preference models only; no real audio driver, USB driver, Android USB Host API, JNI/NDK, AAudio/Oboe, Media3/ExoPlayer, real bit-perfect output, real sample-rate switching, real DAC control, or DSP/EQ.
- Future Android Player audio output phase (phases A–E) added to `docs/aria-core-handoff.md` and `docs/post-core-backlog.md` as a future project outside Aria Core. Invariant added: Aria Core may model requirements for a future custom/exclusive audio output layer; Aria Core must not implement an audio driver; a future Android Player phase may research or implement an exclusive USB/audio output bridge if feasible.
- Blocos 14-20 are implemented and validated.

## Open decisions

- Whether/when to publish package artifacts.
- Whether to create a short ADR for the source-agnostic `ControlClient` boundary during a future architecture review.
