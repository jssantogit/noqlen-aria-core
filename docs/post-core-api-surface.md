# Post-core Public API Surface

This summary describes existing public API groups after post-core foundation work. It is based on top-level exports in `src/noqlen_aria/__init__.py` and implemented modules. It does not list future-only Android app, real playback engine, real provider integration, real audio driver, or UI APIs as current API.

## Core Contracts

- `AriaResult`, `AriaError`, `AriaWarning`.
- `ControlClient`, `FakeControlClient`.
- `ServerViewState`, `LibraryViewState`, `DiagnosticsViewState`, `ReadinessViewState`.
- `LifecycleIntent`, `PermissionState`, `StorageAccessState`.
- `safe_serialize`, `sanitize_text`.
- `__version__`.

## Control Clients And Services

- `AnchorControlClient`: optional dry-run/offline `ControlClient` adapter.
- `StatusService`, `DiagnosticsService`, `ReadinessService`, `LifecycleIntentService`, `LifecycleIntentPreview`, `ResultMappingService`.

## Media Source Foundation

The media source foundation is implemented in `noqlen_aria.media_source`. The top-level package currently exports the broader media/library-facing models through later library and provider groups, while source-specific implementation remains module-scoped. It includes `MediaSourceClient`, `FakeMediaSourceClient`, media source identity, abstract media IDs, source capabilities, stream handles, and source result state.

## Library Browse/Search

- `ArtistSummary`, `AlbumSummary`, `TrackSummary`, `PlaylistSummary`, `GenreSummary`, `FolderSummary`, `LibraryItemSummary`.
- `LibraryBrowseCategory`, `LibraryBrowseRequest`, `LibraryBrowseResult`, `LibraryBrowseService`.
- `LibrarySearchQuery`, `LibrarySearchResult`, `LibrarySearchService`.

## Filters, Activity, And Favorites

- `LibraryFilter`, `LibraryFilterSet`, `LibraryFilterService`.
- `LibrarySortDirection`, `LibrarySortOption`.
- `LibraryActivityType`, `LibraryActivityRequest`, `LibraryActivityResult`, `LibraryActivityService`.
- `RecentlyAddedViewState`, `RecentlyPlayedViewState`.
- `FavoriteItemSummary`, `FavoritesViewState`, `LibraryFavoritesService`.
- `LibraryReadinessBadge`, `LibraryHealthBadge`.

## Queue

- `DEFAULT_QUEUE_ID`, `QueueId`, `QueueItemId`, `QueueItem`, `QueueState`, `QueueCollectionState`.
- `QueueAvailabilityState`, `QueueMode`, `QueueRepeatMode`, `QueueShuffleState`.
- `QueueIntent`, `QueueOperation`, `QueueOperationType`, `QueueOperationResult`, `QueueService`, `FakeQueueScenarios`.

## Now Playing

- `NowPlayingItem`, `NowPlayingState`, `NowPlayingStatus`, `NowPlayingService`, `FakeNowPlayingScenarios`.
- `PlaybackAvailabilityState`, `PlaybackAvailabilityReason`, `PlaybackPositionSnapshot`, `ResumablePlaybackState`, `UnavailableMediaState`.

## Playback, Renderer, And Automation Intents

- `PlaybackIntent`, `PlaybackIntentType`, `PlaybackIntentResult`, `PlaybackIntentService`.
- `PlaybackCommandPreview`, `PlaybackBlockedReason`, `PlaybackIntentValidationIssue`, `SeekTarget`, `SkipDirection`.
- `RendererId`, `RendererRef`, `RendererType`, `RendererAvailabilityState`, `RendererCapabilitySummary`, `RendererSelectionIntent`, `RendererSelectionResult`, `RendererIntentService`.
- `AutomationIntent`, `AutomationIntentType`, `AutomationIntentSource`, `AutomationIntentResult`, `AutomationIntentService`, `AutomationSafetyLevel`.

## Offline, Cache, And Storage

- `OfflineAvailabilityState`, `OfflineAvailabilityReason`, `OfflineCachePolicyService`.
- `CachePolicyState`, `CachePolicyMode`, `CacheEligibilityState`, `CacheBlockedReason`.
- `CacheItemId`, `CacheSourceId`, `CacheOperationIntent`, `CacheOperationType`, `CacheOperationPreview`, `CacheOperationResult`, `PendingOperationId`, `PendingCacheOperation`.
- `StorageBudget`, `StoragePressureLevel`, `StoragePressureState`, `StoragePressureService`.
- `CacheCleanupItem`, `CacheCleanupPolicy`, `CacheCleanupPreview`, `CacheCleanupPreviewService`, `CacheConfirmationState`.

## Internet Radio

- `RadioStationId`, `RadioStationRef`, `RadioStationSummary`.
- `RadioSourceCapability`, `RadioDirectoryRef`, `RadioImportSource`, `ManualRadioStationInput`.
- `RadioStreamHandle`, `RadioStreamKind`, `RadioPlaybackAvailability`, `RadioUnavailableReason`, `RadioValidationIssue`.
- `RadioMetadataState`, `IcyMetadataState`, `RadioArtworkState`, `RadioFavoriteState`.
- `InternetRadioService`, `FakeRadioScenarios`.

## Quality, Transcoding, And Network Policy

- `StreamQualityPreference`, `StreamQualityProfile`, `StreamQualityPolicy`, `StreamQualityDecision`, `StreamQualityReason`.
- `BitrateLimit`, `BandwidthBudget`, `QualityFallbackPolicy`, `OfflineQualityPolicy`, `QualityPolicyService`.
- `TranscodingCapability`, `TranscodingPolicy`, `TranscodingDecision`, `TranscodingUnavailableReason`, `TranscodingRequirement`, `TranscodingPreference`, `TranscodingPolicyService`.
- `NetworkQualityState`, `NetworkQualityLevel`, `NetworkConditionSnapshot`, `NetworkPolicyDecision`, `NetworkPolicyReason`, `NetworkQualityPolicyService`.
- `FakeQualityPolicyScenarios`.

## Playback Capabilities

- `GaplessCapabilityState`, `LoudnessNormalizationCapabilityState`, `ReplayGainAwarenessState`, `CrossfadeCapabilityState`.
- `FadeCapabilityState`, `FadeAvailabilityState`, `FadeMode`, `FadeTimingPreference`, `FadeUnavailableReason`.
- `BitPerfectCapabilityState`, `UsbDacCapabilityState`, `ExclusiveOutputCapabilityState`.
- `AudioOutputRouteState`, `AudioOutputRouteType`, `AudioOutputDeviceState`, `AudioOutputReadinessState`, `AudioOutputBlockedReason`.
- `SampleRateSupport`, `BitDepthSupport`, `AudioFormatSupport`.
- `PlaybackCapabilitySummary`, `PlaybackCapabilityWarning`, `PlaybackCapabilityUnavailableReason`, `PlaybackQualityPreference`.
- `PlaybackCapabilityService`, `AudioOutputCapabilityService`, `FakePlaybackCapabilityScenarios`.

## Profiles, Preferences, Backup, And Restore

- `UserProfileId`, `UserProfileSummary`, `UserProfileState`, `ActiveProfileState`, `ProfilesService`.
- `ProfileOperationIntent`, `ProfileOperationType`, `ProfileOperationPreview`, `ProfileValidationIssue`.
- `UserPreferenceKey`, `UserPreferenceValue`, `UserPreferenceScope`, `UserPreferencesState`, `PreferencesService`.
- `PreferenceUpdateIntent`, `PreferenceUpdatePreview`, `PreferenceValidationIssue`.
- `BackupScope`, `BackupManifest`, `BackupBundle`, `BackupPlan`, `BackupPreview`, `BackupResult`, `BackupBlockedReason`.
- `RestorePlan`, `RestorePreview`, `RestoreResult`, `RestoreConflict`, `RestoreSafetyCheck`.
- `BackupRestoreWarning`, `BackupRestoreService`.

## Smart Playlists

- `SmartPlaylistId`, `SmartPlaylistSummary`, `SmartPlaylistDefinition`, `SmartPlaylistRule`, `SmartPlaylistRuleGroup`, `SmartPlaylistRuleOperator`, `SmartPlaylistSortRule`, `SmartPlaylistLimit`.
- `SmartPlaylistEvaluationContext`, `SmartPlaylistEvaluationResult`, `SmartPlaylistItemCandidate`, `SmartPlaylistPreview`, `SmartPlaylistValidationIssue`, `SmartPlaylistUnavailableReason`, `SmartPlaylistService`.
- `SmartMixDefinition`, `SmartMixStrategy`, `SmartMixSeed`, `SmartMixPreview`.
- `SavedFilterId`, `SavedFilterDefinition`, `SavedFilterPreview`, `SavedFilterValidationIssue`, `SavedFilterService`.
- `FakeSmartPlaylistScenarios`.

## State Snapshots And Fake Flows

- `AriaStateSnapshot`, `AriaSnapshotId`, `AriaSnapshotScope`, `AriaSnapshotMetadata`, `AriaSnapshotSection`, `AriaSnapshotRedactionPolicy`.
- `AriaSnapshotValidationIssue`, `AriaSnapshotResult`, `AriaSnapshotUnavailableReason`, `AriaSnapshotService`.
- `AriaSnapshotDiff`, `AriaSnapshotDiffEntry`, `AriaSnapshotDiffService`.
- `FakeFlowId`, `FakeFlowScenario`, `FakeFlowStep`, `FakeFlowStepKind`, `FakeFlowStepResult`, `FakeFlowTrace`, `FakeFlowResult`, `FakeFlowValidationIssue`, `FakeFlowUnavailableReason`, `FakeFlowRunner`.

## Provider Extension Readiness

- `ProviderExtensionId`, `ProviderExtensionRef`, `ProviderExtensionSummary`, `ProviderExtensionKind`, `ProviderExtensionStatus`.
- `ProviderExtensionCapabilitySummary`, `ProviderExtensionReadinessState`, `ProviderExtensionCompatibilityState`, `ProviderExtensionRequirement`, `ProviderExtensionUnavailableReason`, `ProviderExtensionWarning`.
- `ProviderBoundaryPolicy`, `ProviderAdapterDescriptor`, `ProviderAdapterReadiness`, `ProviderCapabilityDiscoveryPreview`, `ProviderCapabilityDiscoveryIssue`, `ProviderExtensionRegistryState`.
- `ProviderExtensionReadinessService`, `ProviderCapabilityDiscoveryService`, `FakeProviderExtensionScenarios`.

## Android Boundary And Planning Docs

Android boundary code exists as abstract Python contracts and deterministic fakes in `noqlen_aria.android_boundaries`; the top-level package does not export these names. Planning/handoff docs exist at:

- `docs/android-boundary.md`
- `docs/android-real-integration-plan.md`
- `docs/android-shell-handoff.md`

These are not Android SDK implementation, MediaSession implementation, Android Auto implementation, app shell implementation, or playback engine implementation.

## CLI

- Entry point: `noqlen-aria`.
- Smoke commands: `noqlen-aria --help`, `noqlen-aria doctor`.
