# Requirements

## Status

Draft for Bloco 4 — Android/Player Boundary Contracts.

## Problem

Aria Core has no Android boundary contract vocabulary. Blocos 1-3 define source-agnostic `ControlClient` contracts and permission/storage state enums, but the boundary between Aria Core and a future thin Android player shell has no defined contracts for playback engine interaction, MediaSession bridging, storage permission boundaries, Android Auto browsing, foreground service lifecycle, app lifecycle constraints, or notification/lock-screen/headset controls.

Without these boundary contracts, future Android player implementation would couple directly to Aria Core internals, violating the architecture model where Aria Core is UI-independent and the Android player is a thin adapter.

## Goal

Define a comprehensive set of boundary contract vocabularies (Python protocols, dataclasses, enums) that describe the interface between Aria Core and a future Android player thin adapter. These contracts cover playback engine commands/state, MediaSession bridge vocabulary, Android storage bridge vocabulary, Android Auto browse model vocabulary, foreground service lifecycle constraints, app lifecycle constraints, and notification/lock-screen/headset control boundaries. All contracts are Android-platform-aware in vocabulary only — no Android SDK, Kotlin, Java, Gradle, or real Android API code is included.

## Non-goals

- No Android SDK implementation.
- No Kotlin, Java, or Gradle files.
- No real playback engine (Media3, ExoPlayer, or any audio engine).
- No real MediaSession implementation.
- No real Android Auto implementation.
- No real foreground service or notification channel implementation.
- No real lock-screen or headset control implementation.
- No UI, screens, navigation, or Android components (Activity, Fragment, Service, BroadcastReceiver, Compose).
- No queue engine implementation.
- No now playing engine implementation.
- No offline/cache/download implementation.
- No real storage access or permission request flows.
- No provider hard coupling or real provider integration.
- No mutation testing policy or Pact Broker setup.

## Actors

- Future thin Android player adapter (Kotlin/Java app).
- Future implementation agents.
- Aria Core services and control plane.
- Maintainer.

## Functional requirements

### FR-10: PlaybackEngine boundary vocabulary

- FR-10a: Define `PlaybackState` enum representing playback states (`IDLE`, `BUFFERING`, `READY`, `PLAYING`, `PAUSED`, `STOPPED`, `COMPLETED`, `ERROR`).
- FR-10b: Define `PlaybackCommand` enum representing commands that a player shell may issue (`PLAY`, `PAUSE`, `STOP`, `SKIP_NEXT`, `SKIP_PREVIOUS`, `SEEK`, `PLAY_INDEX`, `PLAY_ITEM`).
- FR-10c: Define `PlaybackPosition` dataclass with `elapsed_ms`, `duration_ms`, and `buffered_ms`.
- FR-10d: Define `TrackMetadata` dataclass with `track_id`, `title`, `artist`, `album`, `duration_ms`, `cover_art_uri`, and optional fields for `album_artist`, `track_number`, `disc_number`, `genre`, `year`, `bitrate_kbps`, `sample_rate_hz`, `bit_depth`, `format`.
- FR-10e: Define `PlaybackEngineSnapshot` dataclass compositing `PlaybackState`, current `TrackMetadata`, `PlaybackPosition`, and optional `error` for the current playback engine state.
- FR-10f: Define `PlaybackEngineBridge` as a `typing.Protocol` with methods for `get_snapshot() -> AriaResult[PlaybackEngineSnapshot]`, `send_command(command: PlaybackCommand, **kwargs) -> AriaResult[bool]`, and `register_state_callback(callback)`.

### FR-20: MediaSessionBridge boundary vocabulary

- FR-20a: Define `MediaSessionAction` enum representing standard media session actions (`PLAY`, `PAUSE`, `SKIP_TO_NEXT`, `SKIP_TO_PREVIOUS`, `SEEK_TO`, `STOP`, `FAST_FORWARD`, `REWIND`, `SKIP_TO_QUEUE_ITEM`, `SET_REPEAT_MODE`, `SET_SHUFFLE_MODE`, `SET_RATING`, `CUSTOM_ACTION`).
- FR-20b: Define `MediaSessionRepeatMode` enum (`NONE`, `ONE`, `ALL`, `GROUP`).
- FR-20c: Define `MediaSessionShuffleMode` enum (`NONE`, `ALL`, `GROUP`).
- FR-20d: Define `MediaSessionPlaybackState` dataclass mirroring `PlaybackState` plus Android MediaSession-specific fields: `actions` (bitmask as int or set of `MediaSessionAction`), `position`, `repeat_mode`, `shuffle_mode`.
- FR-20e: Define `MediaSessionMetadata` dataclass with MediaSession-compatible metadata fields: `media_id`, `title`, `artist`, `album`, `album_artist`, `display_title`, `display_subtitle`, `display_description`, `display_icon_uri`, `art_uri`, `duration_ms`, `track_number`, `disc_number`, `genre`, `year`, `rating`.
- FR-20f: Define `MediaSessionBridge` as a `typing.Protocol` with methods for `get_playback_state() -> AriaResult[MediaSessionPlaybackState]`, `get_metadata() -> AriaResult[MediaSessionMetadata]`, `handle_action(action: MediaSessionAction, extras: dict | None) -> AriaResult[bool]`, and `on_command_from_transport(callback)`.

### FR-30: AndroidStorageBridge boundary vocabulary

- FR-30a: Reuse and extend Bloco 1 `PermissionState` and `StorageAccessState` with Android-specific boundary context.
- FR-30b: Define `StorageType` enum representing storage classifications (`MUSIC_DIRECTORY`, `PLAYLIST_FILE`, `CACHE_DIRECTORY`, `DOWNLOAD_DIRECTORY`, `DATABASE`, `PREFERENCES`, `LOGS`).
- FR-30c: Define `StorageRequirement` dataclass pairing a `StorageType` with whether write access is needed (`requires_write: bool`) and whether it is critical for playback (`critical: bool`).
- FR-30d: Define `StorageStatus` enum for per-type storage status (`OK`, `MISSING`, `FULL`, `READ_ONLY`, `PERMISSION_DENIED`, `IO_ERROR`).
- FR-30e: Define `StorageStatusSnapshot` dataclass with a `dict[StorageType, StorageStatus]` map and overall `all_ok: bool`.
- FR-30f: Define `AndroidStorageBridge` as a `typing.Protocol` with methods for `get_storage_status() -> AriaResult[StorageStatusSnapshot]`, `check_requirement(requirement: StorageRequirement) -> AriaResult[bool]`, and `get_permission_state() -> AriaResult[PermissionState]`.

### FR-40: Android Auto boundary vocabulary

- FR-40a: Define `AutoBrowseNodeType` enum (`ROOT`, `ARTISTS`, `ALBUMS`, `TRACKS`, `PLAYLISTS`, `GENRES`, `FOLDERS`, `RECENTLY_PLAYED`, `FAVORITES`, `SEARCH`, `NOW_PLAYING`, `QUEUE`, `CUSTOM`).
- FR-40b: Define `AutoBrowseNode` dataclass representing a browse tree node with `node_id`, `node_type: AutoBrowseNodeType`, `title`, `subtitle`, `playable: bool`, `browsable: bool`, `icon_uri`, and optional `children: list[AutoBrowseNode]`.
- FR-40c: Define `AutoBrowseResult` dataclass with `parent_node_id`, `nodes: list[AutoBrowseNode]`, `total_count: int`, and `has_more: bool`.
- FR-40d: Define `AutoSearchResult` dataclass with `query: str`, `nodes: list[AutoBrowseNode]`, and `total_count: int`.
- FR-40e: Define `AndroidAutoBridge` as a `typing.Protocol` with methods for `get_root() -> AriaResult[AutoBrowseNode]`, `browse(node_id: str) -> AriaResult[AutoBrowseResult]`, `search(query: str) -> AriaResult[AutoSearchResult]`, and `play_from_node(node_id: str) -> AriaResult[bool]`.

### FR-50: Foreground service lifecycle constraints

- FR-50a: Define `ForegroundServiceState` enum (`NOT_STARTED`, `STARTING`, `RUNNING`, `PAUSING`, `PAUSED`, `STOPPING`, `STOPPED`, `ERROR`).
- FR-50b: Define `ForegroundServiceRequirement` dataclass capturing what the foreground service needs: `notification_channel_id: str`, `notification_title_template: str`, `requires_audio_focus: bool`, `requires_wifi_lock: bool`, `requires_wake_lock: bool`.
- FR-50c: Define `ForegroundServiceBridge` as a `typing.Protocol` with methods for `start(requirement: ForegroundServiceRequirement) -> AriaResult[bool]`, `stop() -> AriaResult[bool]`, `update_notification(metadata: TrackMetadata) -> AriaResult[bool]`, and `get_state() -> AriaResult[ForegroundServiceState]`.

### FR-60: App lifecycle constraints

- FR-60a: Define `AppLifecycleEvent` enum representing lifecycle events the player shell may experience (`ON_CREATE`, `ON_START`, `ON_RESUME`, `ON_PAUSE`, `ON_STOP`, `ON_DESTROY`, `ON_LOW_MEMORY`, `ON_CONFIGURATION_CHANGED`, `ON_ENTER_PICTURE_IN_PICTURE`, `ON_LEAVE_PICTURE_IN_PICTURE`).
- FR-60b: Define `AppLifecycleState` enum (`CREATED`, `STARTED`, `RESUMED`, `PAUSED`, `STOPPED`, `DESTROYED`, `BACKGROUNDED`, `FOREGROUNDED`).
- FR-60c: Define `AppLifecycleBridge` as a `typing.Protocol` with methods for `report_event(event: AppLifecycleEvent) -> AriaResult[bool]`, `get_state() -> AriaResult[AppLifecycleState]`, and `is_in_foreground() -> AriaResult[bool]`.

### FR-70: Notification / lock-screen / headset control boundaries

- FR-70a: Define `NotificationAction` enum (`PLAY_PAUSE`, `NEXT`, `PREVIOUS`, `STOP`, `SEEK_FORWARD`, `SEEK_BACKWARD`, `CUSTOM`).
- FR-70b: Define `NotificationControlBridge` as a `typing.Protocol` with methods for `handle_action(action: NotificationAction) -> AriaResult[bool]`, `update_content(metadata: TrackMetadata, state: PlaybackState) -> AriaResult[bool]`, and `dismiss() -> AriaResult[bool]`.
- FR-70c: Define `LockScreenControlState` dataclass with `enabled: bool`, `playback_state: PlaybackState`, `metadata: TrackMetadata`, and `available_actions: list[NotificationAction]`.
- FR-70d: Define `LockScreenBridge` as a `typing.Protocol` with methods for `update_state(state: LockScreenControlState) -> AriaResult[bool]` and `handle_action(action: NotificationAction) -> AriaResult[bool]`.
- FR-70e: Define `HeadsetEventType` enum (`CONNECTED`, `DISCONNECTED`, `BUTTON_PRESS`, `BUTTON_DOUBLE_PRESS`, `BUTTON_TRIPLE_PRESS`, `BUTTON_LONG_PRESS`, `PLAY_PAUSE`, `NEXT`, `PREVIOUS`, `STOP`, `VOLUME_UP`, `VOLUME_DOWN`).
- FR-70f: Define `HeadsetControlBridge` as a `typing.Protocol` with methods for `handle_event(event: HeadsetEventType) -> AriaResult[bool]` and `is_connected() -> AriaResult[bool]`.

### FR-80: Composite Android boundary snapshot

- FR-80a: Define `AndroidBoundarySnapshot` dataclass compositing all Android boundary states: `playback_engine: PlaybackEngineSnapshot`, `media_session: MediaSessionPlaybackState`, `storage_status: StorageStatusSnapshot`, `foreground_service: ForegroundServiceState`, `app_lifecycle: AppLifecycleState`, `headset_connected: bool`.
- FR-80b: This snapshot provides a single point of truth for a future Android player to consume all boundary state at once.

### FR-90: Contract module placement and no-dependency rule

- FR-90a: All contracts must be defined in a proposed future Python module `src/noqlen_aria/android_boundaries.py`.
- FR-90b: All contracts must be importable with zero external dependencies beyond Python 3.11+ standard library (`dataclasses`, `enum`, `typing`).
- FR-90c: All contracts must be UI-independent and Android-SDK-free in vocabulary only.

## Canonical Examples

### CE-01: Playback engine bridge — play a track

Given a `PlaybackEngineBridge` implementation (fake in tests, future real in Android shell)
And a `PlaybackCommand.PLAY` is sent via `send_command(command=PlaybackCommand.PLAY)`
When the call returns
Then the result is `AriaResult[bool]` with `ok=True` and `data=True`
And a subsequent `get_snapshot()` call returns a `PlaybackEngineSnapshot` with `state=PlaybackState.PLAYING`

### CE-02: Playback engine bridge — seek

Given a `PlaybackEngineBridge` implementation currently in `PlaybackState.PLAYING`
When `send_command(command=PlaybackCommand.SEEK, position_ms=30000)` is called
Then the result is `AriaResult[bool]` with `ok=True`
And a subsequent `get_snapshot()` returns `PlaybackPosition` with `elapsed_ms=30000`

### CE-03: MediaSession bridge — handle transport action

Given a `MediaSessionBridge` implementation
When `handle_action(action=MediaSessionAction.PLAY)` is called
Then the result is `AriaResult[bool]` with `ok=True`
And `get_playback_state()` returns a `MediaSessionPlaybackState` reflecting the play action

### CE-04: Storage bridge — check requirement

Given an `AndroidStorageBridge` implementation
And a `StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY, requires_write=False, critical=True)`
When `check_requirement(requirement)` is called
Then the result is `AriaResult[bool]` with `ok=True` and `data=True` when the storage is available

### CE-05: Storage bridge — permission denied

Given an `AndroidStorageBridge` implementation with `PermissionState.DENIED` for `StorageType.MUSIC_DIRECTORY`
When `check_requirement(requirement=StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY, critical=True))` is called
Then the result is `AriaResult[bool]` with `ok=True` and `data=False`
And `get_storage_status()` returns `StorageStatus.PERMISSION_DENIED` for that storage type

### CE-06: Android Auto bridge — browse artists

Given an `AndroidAutoBridge` implementation
When `browse(node_id="artists_root")` is called
Then the result is `AriaResult[AutoBrowseResult]` with `ok=True`
And the `AutoBrowseResult.nodes` list contains `AutoBrowseNode` items with `node_type=AutoBrowseNodeType.ARTISTS`
And each node is `playable=False` and `browsable=True`

### CE-07: Foreground service bridge — start and update

Given a `ForegroundServiceBridge` implementation
And a `ForegroundServiceRequirement(notification_channel_id="playback", ...)`
When `start(requirement)` is called
Then the result is `AriaResult[bool]` with `ok=True`
And `get_state()` returns `ForegroundServiceState.RUNNING`
When `update_notification(metadata=TrackMetadata(...))` is called
Then the result is `AriaResult[bool]` with `ok=True`

### CE-08: App lifecycle bridge — report event chain

Given an `AppLifecycleBridge` implementation
When `report_event(AppLifecycleEvent.ON_CREATE)` is called, then `report_event(AppLifecycleEvent.ON_START)`, then `report_event(AppLifecycleEvent.ON_RESUME)`
Then `get_state()` returns `AppLifecycleState.RESUMED`
And `is_in_foreground()` returns `True`

### CE-09: Notification control bridge — handle action

Given a `NotificationControlBridge` implementation
And `update_content(metadata=..., state=PlaybackState.PLAYING)` has been called
When `handle_action(action=NotificationAction.PLAY_PAUSE)` is called
Then the result is `AriaResult[bool]` with `ok=True`
(Note: the bridge translates this to the appropriate `PlaybackEngineBridge` command internally)

### CE-10: Headset control bridge — button press

Given a `HeadsetControlBridge` implementation
And `is_connected()` returns `True`
When `handle_event(event=HeadsetEventType.BUTTON_PRESS)` is called
Then the result is `AriaResult[bool]` with `ok=True`
And the bridge translates this to a PLAY_PAUSE action internally

### CE-11: Composite snapshot — full boundary state

Given a fully initialized set of Android boundary bridges
When an `AndroidBoundarySnapshot` is composed from all individual bridge states
Then the snapshot contains non-null values for `playback_engine`, `media_session`, `storage_status`, `foreground_service`, `app_lifecycle`, and `headset_connected`
And the snapshot can be serialized/deserialized without loss

### CE-12: Unknown command — safe error

Given any boundary bridge implementation
When an unsupported command or invalid action is sent
Then the result is `AriaResult` with `ok=False` and an `AriaError` with code `"UNSUPPORTED_ACTION"` or `"INVALID_COMMAND"`

## Non-functional requirements

- NFR01: All contracts are UI-independent types only; no framework-specific code.
- NFR02: All contracts use Python standard library only (`dataclasses`, `enum`, `typing`).
- NFR03: No runtime dependencies on Android SDK, Kotlin, Java, Gradle, Media3, ExoPlayer, or any third-party Android library.
- NFR04: All public names must be explicit, stable, and documented in English.
- NFR05: Contracts must not leak Android platform internals (no `android.*` imports, no `Context`, no `Intent`, no `Bundle`, no `MediaSessionCompat`).
- NFR06: Contracts must be fake-first: every `Protocol` must have a corresponding `Fake*` class for local testing.
- NFR07: All `Protocol` bridges must use `AriaResult[T]` return types consistently.
- NFR08: Enums must be exhaustive; unknown values must produce safe errors.
- NFR09: `PlaybackEngineSnapshot`, `AndroidBoundarySnapshot`, and all other snapshot types must be serialization-safe (no non-serializable fields).
- NFR10: All contracts must use domain-generic names (e.g., `MediaSessionPlaybackState`, not `AndroidMediaSessionPlaybackState`); Android context is provided by the module namespace and documentation.

## Edge cases

- EC01: `PlaybackEngineBridge` called before any media is loaded (state=`IDLE`, metadata and position are null/empty).
- EC02: `MediaSessionBridge.handle_action` with an action not in the current `actions` set (should return error or no-op).
- EC03: `AndroidStorageBridge.check_requirement` with no permissions ever requested (state=`UNKNOWN`).
- EC04: `AndroidAutoBridge.browse` with an invalid `node_id` (returns error).
- EC05: `AndroidAutoBridge.search` with an empty query string (returns empty result or validation error).
- EC06: `ForegroundServiceBridge.start` called when already running (idempotent or error).
- EC07: `AppLifecycleBridge.report_event` with events out of expected order (e.g., `ON_PAUSE` before `ON_CREATE`).
- EC08: `HeadsetControlBridge.handle_event` when no headset is connected (to play/pause actions: should be safe no-op or error).
- EC09: All `Protocol` methods that return `AriaResult[T]` must handle the case where the underlying implementation is unavailable.
- EC10: Composite `AndroidBoundarySnapshot` must handle partial unavailability (e.g., no Android Auto available on this device).
- EC11: Thread safety — contracts do not prescribe thread safety, but callers should be aware that real implementations may involve Android main-thread constraints.
- EC12: All fake implementations must be deterministic and must never call real Android APIs, filesystem, or network.

## Acceptance criteria

- AC01: `aria/specs/features/android-player-boundary-contracts/` contains `requirements.md`, `design.md`, `tasks.md`, and `review.md`.
- AC02: No source code, test code, `pyproject.toml`, Android files, Kotlin files, Java files, or Gradle files are created by this spec.
- AC03: Spec clearly states that Bloco 4 defines boundary contracts only — no Android SDK, UI, or real playback implementation.
- AC04: Spec defines the expected source file(s) and test file(s) for later implementation.
- AC05: Existing validation commands pass without regression.
- AC06: Repository contamination check is clean.
- AC07: Spec includes Canonical Examples using Given/When/Then format.
- AC08: Spec includes Behavior Budget.
- AC09: Spec includes Test Risk Matrix.
- AC10: Context package used is documented.
- AC11: Delta update checklist is present.
- AC12: Spec is committed with `docs(spec): add Android player boundary contracts spec`.

## Open questions

- OQ01: Should boundary bridge protocols use `@runtime_checkable` like `ControlClient` does? (Settled in design: yes, for structural typing consistency.)
- OQ02: Should `MediaSessionMetadata` reuse `TrackMetadata` fields or be independent? (Settled in design: independent; they serve different consumers with different field requirements.)
- OQ03: Should `AndroidBoundarySnapshot` be a single composite or should consumers query bridges individually? (Design: both; composite for convenience, individual bridges for granular updates.)
- OQ04: Should `HeadsetEventType` split `BUTTON_PRESS` by playback action inference or leave that to the bridge implementation? (Deferred to implementation: protocol defines raw events; mapping to playback commands is bridge-internal.)
- OQ05: Should `ForegroundServiceBridge` declare a notification builder API or leave notification construction to the Android shell? (Settled in design: bridge defines content requirements; actual Notification construction is the shell's responsibility.)
- OQ06: Exact field lists for `TrackMetadata` and `MediaSessionMetadata`. (Deferred to implementation: design will propose initial fields; fields are subject to expansion in later blocks.)
- OQ07: Should playback bridge distinguish between user-initiated commands and automation commands? (Deferred: current spec handles both uniformly; distinction may be added in a future block.)
