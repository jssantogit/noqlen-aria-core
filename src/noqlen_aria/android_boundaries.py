"""Aria Core Android/player boundary contracts.

UI-independent boundary vocabulary for a future thin Android player adapter.
All contracts use Python standard library types only.
No Android SDK, Kotlin, Java, or Gradle imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Protocol, runtime_checkable

from noqlen_aria.contracts import AriaError, AriaResult, PermissionState


# ── Playback Engine Boundary ─────────────────────────────────────


class PlaybackState(Enum):
    """Playback states for the playback engine boundary."""

    IDLE = auto()
    BUFFERING = auto()
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    COMPLETED = auto()
    ERROR = auto()


class PlaybackCommand(Enum):
    """Commands that a player shell may issue to the playback engine."""

    PLAY = auto()
    PAUSE = auto()
    STOP = auto()
    SKIP_NEXT = auto()
    SKIP_PREVIOUS = auto()
    SEEK = auto()
    PLAY_INDEX = auto()
    PLAY_ITEM = auto()


@dataclass(frozen=True)
class PlaybackPosition:
    """Current playback position information."""

    elapsed_ms: int = 0
    duration_ms: int = 0
    buffered_ms: int = 0


@dataclass(frozen=True)
class TrackMetadata:
    """Metadata for a track, suitable for display and session metadata."""

    track_id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    cover_art_uri: str = ""
    album_artist: str | None = None
    track_number: int | None = None
    disc_number: int | None = None
    genre: str | None = None
    year: int | None = None
    bitrate_kbps: int | None = None
    sample_rate_hz: int | None = None
    bit_depth: int | None = None
    format: str | None = None


@dataclass(frozen=True)
class PlaybackEngineSnapshot:
    """Composite snapshot of the current playback engine state."""

    state: PlaybackState = PlaybackState.IDLE
    track: TrackMetadata | None = None
    position: PlaybackPosition = field(default_factory=PlaybackPosition)
    error: AriaError | None = None


@runtime_checkable
class PlaybackEngineBridge(Protocol):
    """Boundary protocol for the playback engine.

    Provides state snapshots, command dispatch, and state callbacks.
    The Android player shell interacts with playback through this boundary.
    """

    def get_snapshot(self) -> AriaResult[PlaybackEngineSnapshot]: ...

    def send_command(
        self, command: PlaybackCommand, **kwargs: object
    ) -> AriaResult[bool]: ...

    def register_state_callback(
        self, callback: Callable[[PlaybackEngineSnapshot], None]
    ) -> AriaResult[bool]: ...


# ── MediaSession Bridge Boundary ─────────────────────────────────


class MediaSessionAction(Enum):
    """Standard media session actions.

    Actions bitmask encoding is deferred to the Android shell;
    the boundary communicates actions as discrete values.
    """

    PLAY = auto()
    PAUSE = auto()
    SKIP_TO_NEXT = auto()
    SKIP_TO_PREVIOUS = auto()
    SEEK_TO = auto()
    STOP = auto()
    FAST_FORWARD = auto()
    REWIND = auto()
    SKIP_TO_QUEUE_ITEM = auto()
    SET_REPEAT_MODE = auto()
    SET_SHUFFLE_MODE = auto()
    SET_RATING = auto()
    CUSTOM_ACTION = auto()


class MediaSessionRepeatMode(Enum):
    """MediaSession repeat modes."""

    NONE = auto()
    ONE = auto()
    ALL = auto()
    GROUP = auto()


class MediaSessionShuffleMode(Enum):
    """MediaSession shuffle modes."""

    NONE = auto()
    ALL = auto()
    GROUP = auto()


@dataclass(frozen=True)
class MediaSessionPlaybackState:
    """MediaSession-compatible playback state.

    ``actions`` is a bitmask-like int; encoding of specific
    ``MediaSessionAction`` values into the bitmask is the Android
    shell's responsibility.
    """

    state: PlaybackState = PlaybackState.IDLE
    actions: int = 0
    position: PlaybackPosition = field(default_factory=PlaybackPosition)
    repeat_mode: MediaSessionRepeatMode = MediaSessionRepeatMode.NONE
    shuffle_mode: MediaSessionShuffleMode = MediaSessionShuffleMode.NONE


@dataclass(frozen=True)
class MediaSessionMetadata:
    """MediaSession-compatible metadata.

    Independent from ``TrackMetadata`` to serve different consumer requirements.
    """

    media_id: str = ""
    title: str = ""
    artist: str = ""
    album: str = ""
    album_artist: str = ""
    display_title: str = ""
    display_subtitle: str = ""
    display_description: str = ""
    display_icon_uri: str = ""
    art_uri: str = ""
    duration_ms: int = 0
    track_number: int | None = None
    disc_number: int | None = None
    genre: str | None = None
    year: int | None = None
    rating: str | None = None


@runtime_checkable
class MediaSessionBridge(Protocol):
    """Boundary protocol for MediaSession integration.

    Handles transport actions, state/metadata queries, and callbacks
    from external media session controllers.
    """

    def get_playback_state(self) -> AriaResult[MediaSessionPlaybackState]: ...

    def get_metadata(self) -> AriaResult[MediaSessionMetadata]: ...

    def handle_action(
        self, action: MediaSessionAction, extras: dict | None = None
    ) -> AriaResult[bool]: ...

    def on_command_from_transport(
        self, callback: Callable[[MediaSessionAction], None]
    ) -> AriaResult[bool]: ...


# ── Android Storage Bridge Boundary ──────────────────────────────


class StorageType(Enum):
    """Storage classifications for the Android storage boundary."""

    MUSIC_DIRECTORY = auto()
    PLAYLIST_FILE = auto()
    CACHE_DIRECTORY = auto()
    DOWNLOAD_DIRECTORY = auto()
    DATABASE = auto()
    PREFERENCES = auto()
    LOGS = auto()


class StorageStatus(Enum):
    """Per-type storage status values."""

    OK = auto()
    MISSING = auto()
    FULL = auto()
    READ_ONLY = auto()
    PERMISSION_DENIED = auto()
    IO_ERROR = auto()


@dataclass(frozen=True)
class StorageRequirement:
    """A storage requirement pairing type, write access, and criticality."""

    storage_type: StorageType
    requires_write: bool = False
    critical: bool = False


@dataclass(frozen=True)
class StorageStatusSnapshot:
    """Snapshot of storage status across all storage types."""

    entries: dict[StorageType, StorageStatus] = field(default_factory=dict)
    all_ok: bool = True


@runtime_checkable
class AndroidStorageBridge(Protocol):
    """Boundary protocol for Android storage/permission access.

    Reuses Bloco 1 ``PermissionState`` for the permission boundary.
    """

    def get_storage_status(self) -> AriaResult[StorageStatusSnapshot]: ...

    def check_requirement(
        self, requirement: StorageRequirement
    ) -> AriaResult[bool]: ...

    def get_permission_state(self) -> AriaResult[PermissionState]: ...


# ── Android Auto Bridge Boundary ─────────────────────────────────


class AutoBrowseNodeType(Enum):
    """Android Auto browse tree node types."""

    ROOT = auto()
    ARTISTS = auto()
    ALBUMS = auto()
    TRACKS = auto()
    PLAYLISTS = auto()
    GENRES = auto()
    FOLDERS = auto()
    RECENTLY_PLAYED = auto()
    FAVORITES = auto()
    SEARCH = auto()
    NOW_PLAYING = auto()
    QUEUE = auto()
    CUSTOM = auto()


@dataclass(frozen=True)
class AutoBrowseNode:
    """A node in the Android Auto browse tree."""

    node_id: str
    node_type: AutoBrowseNodeType
    title: str
    subtitle: str = ""
    playable: bool = False
    browsable: bool = True
    icon_uri: str = ""
    children: list[AutoBrowseNode] | None = None


@dataclass(frozen=True)
class AutoBrowseResult:
    """Result of browsing a node in the Android Auto browse tree."""

    parent_node_id: str
    nodes: list[AutoBrowseNode] = field(default_factory=list)
    total_count: int = 0
    has_more: bool = False


@dataclass(frozen=True)
class AutoSearchResult:
    """Result of searching via Android Auto."""

    query: str
    nodes: list[AutoBrowseNode] = field(default_factory=list)
    total_count: int = 0


@runtime_checkable
class AndroidAutoBridge(Protocol):
    """Boundary protocol for Android Auto integration.

    Provides browse tree navigation, search, and play-from-node operations.
    """

    def get_root(self) -> AriaResult[AutoBrowseNode]: ...

    def browse(self, node_id: str) -> AriaResult[AutoBrowseResult]: ...

    def search(self, query: str) -> AriaResult[AutoSearchResult]: ...

    def play_from_node(self, node_id: str) -> AriaResult[bool]: ...


# ── Foreground Service Lifecycle Boundary ────────────────────────


class ForegroundServiceState(Enum):
    """Foreground service lifecycle states."""

    NOT_STARTED = auto()
    STARTING = auto()
    RUNNING = auto()
    PAUSING = auto()
    PAUSED = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()


@dataclass(frozen=True)
class ForegroundServiceRequirement:
    """Requirements for starting a foreground service.

    Fields are templates/descriptors, not actual Android notification
    channel or intent configuration.
    """

    notification_channel_id: str = "playback"
    notification_title_template: str = "Now Playing"
    requires_audio_focus: bool = False
    requires_wifi_lock: bool = False
    requires_wake_lock: bool = False


@runtime_checkable
class ForegroundServiceBridge(Protocol):
    """Boundary protocol for foreground service lifecycle management."""

    def start(
        self, requirement: ForegroundServiceRequirement
    ) -> AriaResult[bool]: ...

    def stop(self) -> AriaResult[bool]: ...

    def update_notification(
        self, metadata: TrackMetadata
    ) -> AriaResult[bool]: ...

    def get_state(self) -> AriaResult[ForegroundServiceState]: ...


# ── App Lifecycle Boundary ───────────────────────────────────────


class AppLifecycleEvent(Enum):
    """Lifecycle events the player shell may experience."""

    ON_CREATE = auto()
    ON_START = auto()
    ON_RESUME = auto()
    ON_PAUSE = auto()
    ON_STOP = auto()
    ON_DESTROY = auto()
    ON_LOW_MEMORY = auto()
    ON_CONFIGURATION_CHANGED = auto()
    ON_ENTER_PICTURE_IN_PICTURE = auto()
    ON_LEAVE_PICTURE_IN_PICTURE = auto()


class AppLifecycleState(Enum):
    """App lifecycle derived states."""

    CREATED = auto()
    STARTED = auto()
    RESUMED = auto()
    PAUSED = auto()
    STOPPED = auto()
    DESTROYED = auto()
    BACKGROUNDED = auto()
    FOREGROUNDED = auto()


@runtime_checkable
class AppLifecycleBridge(Protocol):
    """Boundary protocol for app lifecycle event reporting."""

    def report_event(self, event: AppLifecycleEvent) -> AriaResult[bool]: ...

    def get_state(self) -> AriaResult[AppLifecycleState]: ...

    def is_in_foreground(self) -> AriaResult[bool]: ...


# ── Notification / Lock-Screen / Headset Boundaries ──────────────


class NotificationAction(Enum):
    """Actions available on notifications and lock-screen controls."""

    PLAY_PAUSE = auto()
    NEXT = auto()
    PREVIOUS = auto()
    STOP = auto()
    SEEK_FORWARD = auto()
    SEEK_BACKWARD = auto()
    CUSTOM = auto()


@runtime_checkable
class NotificationControlBridge(Protocol):
    """Boundary protocol for notification media controls."""

    def handle_action(self, action: NotificationAction) -> AriaResult[bool]: ...

    def update_content(
        self, metadata: TrackMetadata, state: PlaybackState
    ) -> AriaResult[bool]: ...

    def dismiss(self) -> AriaResult[bool]: ...


@dataclass(frozen=True)
class LockScreenControlState:
    """State for lock-screen media controls."""

    enabled: bool = False
    playback_state: PlaybackState = PlaybackState.IDLE
    metadata: TrackMetadata | None = None
    available_actions: list[NotificationAction] = field(default_factory=list)


@runtime_checkable
class LockScreenBridge(Protocol):
    """Boundary protocol for lock-screen media control integration."""

    def update_state(
        self, state: LockScreenControlState
    ) -> AriaResult[bool]: ...

    def handle_action(
        self, action: NotificationAction
    ) -> AriaResult[bool]: ...


class HeadsetEventType(Enum):
    """Headset and Bluetooth media button events."""

    CONNECTED = auto()
    DISCONNECTED = auto()
    BUTTON_PRESS = auto()
    BUTTON_DOUBLE_PRESS = auto()
    BUTTON_TRIPLE_PRESS = auto()
    BUTTON_LONG_PRESS = auto()
    PLAY_PAUSE = auto()
    NEXT = auto()
    PREVIOUS = auto()
    STOP = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()


@runtime_checkable
class HeadsetControlBridge(Protocol):
    """Boundary protocol for headset/Bluetooth media button events."""

    def handle_event(self, event: HeadsetEventType) -> AriaResult[bool]: ...

    def is_connected(self) -> AriaResult[bool]: ...


# ── Composite Android Boundary Snapshot ──────────────────────────


@dataclass(frozen=True)
class AndroidBoundarySnapshot:
    """Composite snapshot of all Android boundary states.

    Provides a single point of truth for a future Android player to
    consume all boundary state at once.
    """

    playback_engine: PlaybackEngineSnapshot = field(
        default_factory=PlaybackEngineSnapshot
    )
    media_session: MediaSessionPlaybackState = field(
        default_factory=MediaSessionPlaybackState
    )
    storage_status: StorageStatusSnapshot = field(
        default_factory=StorageStatusSnapshot
    )
    foreground_service: ForegroundServiceState = (
        ForegroundServiceState.NOT_STARTED
    )
    app_lifecycle: AppLifecycleState = AppLifecycleState.CREATED
    headset_connected: bool = False


# ── Fake Implementations ─────────────────────────────────────────


@dataclass
class FakePlaybackEngineBridge:
    """Deterministic fake for ``PlaybackEngineBridge``.

    Returns known fake data. Never calls network, filesystem, or
    external process.

    Failure-injection hooks (set to an ``AriaError`` to simulate failures):
        _snapshot_error, _command_error, _callback_error

    Optional state mutation for scenario testing:
        _custom_state, _custom_track, _custom_position
    """

    _snapshot_error: AriaError | None = field(default=None, repr=False)
    _command_error: AriaError | None = field(default=None, repr=False)
    _callback_error: AriaError | None = field(default=None, repr=False)

    _custom_state: PlaybackState | None = field(default=None, repr=False)
    _custom_track: TrackMetadata | None = field(default=None, repr=False)
    _custom_position: PlaybackPosition | None = field(default=None, repr=False)

    def get_snapshot(self) -> AriaResult[PlaybackEngineSnapshot]:
        if self._snapshot_error is not None:
            return AriaResult(ok=False, error=self._snapshot_error)
        state = self._custom_state or PlaybackState.IDLE
        track = self._custom_track or TrackMetadata(
            track_id="fake-track-1",
            title="Fake Title",
            artist="Fake Artist",
            album="Fake Album",
            duration_ms=240000,
        )
        position = self._custom_position or PlaybackPosition(
            elapsed_ms=0, duration_ms=240000, buffered_ms=240000
        )
        return AriaResult(
            ok=True,
            data=PlaybackEngineSnapshot(
                state=state, track=track, position=position
            ),
        )

    def send_command(
        self, command: PlaybackCommand, **kwargs: object
    ) -> AriaResult[bool]:
        if self._command_error is not None:
            return AriaResult(ok=False, error=self._command_error)
        if command == PlaybackCommand.SEEK and "position_ms" in kwargs:
            pos_ms = int(kwargs["position_ms"])
            self._custom_position = PlaybackPosition(
                elapsed_ms=pos_ms,
                duration_ms=self._custom_position.duration_ms
                if self._custom_position
                else 240000,
                buffered_ms=self._custom_position.buffered_ms
                if self._custom_position
                else 240000,
            )
        if command == PlaybackCommand.PLAY:
            self._custom_state = PlaybackState.PLAYING
        elif command == PlaybackCommand.PAUSE:
            self._custom_state = PlaybackState.PAUSED
        elif command == PlaybackCommand.STOP:
            self._custom_state = PlaybackState.STOPPED
        return AriaResult(ok=True, data=True)

    def register_state_callback(
        self, callback: Callable[[PlaybackEngineSnapshot], None]
    ) -> AriaResult[bool]:
        if self._callback_error is not None:
            return AriaResult(ok=False, error=self._callback_error)
        return AriaResult(ok=True, data=True)


@dataclass
class FakeMediaSessionBridge:
    """Deterministic fake for ``MediaSessionBridge``.

    Failure-injection hooks:
        _playback_state_error, _metadata_error, _action_error, _transport_error
    """

    _playback_state_error: AriaError | None = field(default=None, repr=False)
    _metadata_error: AriaError | None = field(default=None, repr=False)
    _action_error: AriaError | None = field(default=None, repr=False)
    _transport_error: AriaError | None = field(default=None, repr=False)

    _custom_playback_state: MediaSessionPlaybackState | None = field(
        default=None, repr=False
    )
    _custom_metadata: MediaSessionMetadata | None = field(
        default=None, repr=False
    )
    _last_handled_action: MediaSessionAction | None = field(
        default=None, repr=False
    )

    def get_playback_state(self) -> AriaResult[MediaSessionPlaybackState]:
        if self._playback_state_error is not None:
            return AriaResult(ok=False, error=self._playback_state_error)
        if self._custom_playback_state is not None:
            return AriaResult(ok=True, data=self._custom_playback_state)
        return AriaResult(ok=True, data=MediaSessionPlaybackState())

    def get_metadata(self) -> AriaResult[MediaSessionMetadata]:
        if self._metadata_error is not None:
            return AriaResult(ok=False, error=self._metadata_error)
        if self._custom_metadata is not None:
            return AriaResult(ok=True, data=self._custom_metadata)
        return AriaResult(
            ok=True,
            data=MediaSessionMetadata(
                media_id="fake-media-1",
                title="Fake Title",
                artist="Fake Artist",
                album="Fake Album",
                duration_ms=240000,
            ),
        )

    def handle_action(
        self, action: MediaSessionAction, extras: dict | None = None
    ) -> AriaResult[bool]:
        if self._action_error is not None:
            return AriaResult(ok=False, error=self._action_error)
        self._last_handled_action = action
        if action == MediaSessionAction.PLAY:
            if self._custom_playback_state is None:
                self._custom_playback_state = MediaSessionPlaybackState()
            self._custom_playback_state = MediaSessionPlaybackState(
                state=PlaybackState.PLAYING,
                actions=self._custom_playback_state.actions,
                position=self._custom_playback_state.position,
                repeat_mode=self._custom_playback_state.repeat_mode,
                shuffle_mode=self._custom_playback_state.shuffle_mode,
            )
        elif action == MediaSessionAction.PAUSE:
            if self._custom_playback_state is None:
                self._custom_playback_state = MediaSessionPlaybackState()
            self._custom_playback_state = MediaSessionPlaybackState(
                state=PlaybackState.PAUSED,
                actions=self._custom_playback_state.actions,
                position=self._custom_playback_state.position,
                repeat_mode=self._custom_playback_state.repeat_mode,
                shuffle_mode=self._custom_playback_state.shuffle_mode,
            )
        return AriaResult(ok=True, data=True)

    def on_command_from_transport(
        self, callback: Callable[[MediaSessionAction], None]
    ) -> AriaResult[bool]:
        if self._transport_error is not None:
            return AriaResult(ok=False, error=self._transport_error)
        return AriaResult(ok=True, data=True)


@dataclass
class FakeAndroidStorageBridge:
    """Deterministic fake for ``AndroidStorageBridge``.

    Failure-injection hooks:
        _storage_status_error, _check_error, _permission_error

    State overrides:
        _custom_status_entries, _custom_permission_state
    """

    _storage_status_error: AriaError | None = field(default=None, repr=False)
    _check_error: AriaError | None = field(default=None, repr=False)
    _permission_error: AriaError | None = field(default=None, repr=False)

    _custom_status_entries: dict[StorageType, StorageStatus] | None = field(
        default=None, repr=False
    )
    _custom_permission_state: PermissionState | None = field(
        default=None, repr=False
    )

    def get_storage_status(self) -> AriaResult[StorageStatusSnapshot]:
        if self._storage_status_error is not None:
            return AriaResult(ok=False, error=self._storage_status_error)
        entries = (
            self._custom_status_entries
            if self._custom_status_entries is not None
            else {t: StorageStatus.OK for t in StorageType}
        )
        all_ok = all(s == StorageStatus.OK for s in entries.values())
        return AriaResult(
            ok=True,
            data=StorageStatusSnapshot(entries=entries, all_ok=all_ok),
        )

    def check_requirement(
        self, requirement: StorageRequirement
    ) -> AriaResult[bool]:
        if self._check_error is not None:
            return AriaResult(ok=False, error=self._check_error)
        entries = (
            self._custom_status_entries
            if self._custom_status_entries is not None
            else {}
        )
        status = entries.get(requirement.storage_type, StorageStatus.OK)
        return AriaResult(ok=True, data=status == StorageStatus.OK)

    def get_permission_state(self) -> AriaResult[PermissionState]:
        if self._permission_error is not None:
            return AriaResult(ok=False, error=self._permission_error)
        state = self._custom_permission_state or PermissionState.GRANTED
        return AriaResult(ok=True, data=state)


@dataclass
class FakeAndroidAutoBridge:
    """Deterministic fake for ``AndroidAutoBridge``.

    Failure-injection hooks:
        _root_error, _browse_error, _search_error, _play_error

    State overrides:
        _custom_root, _custom_browse_map, _custom_search_results
    """

    _root_error: AriaError | None = field(default=None, repr=False)
    _browse_error: AriaError | None = field(default=None, repr=False)
    _search_error: AriaError | None = field(default=None, repr=False)
    _play_error: AriaError | None = field(default=None, repr=False)

    _custom_root: AutoBrowseNode | None = field(default=None, repr=False)
    _custom_browse_map: dict[str, AutoBrowseResult] | None = field(
        default=None, repr=False
    )
    _custom_search_results: dict[str, AutoSearchResult] | None = field(
        default=None, repr=False
    )

    def get_root(self) -> AriaResult[AutoBrowseNode]:
        if self._root_error is not None:
            return AriaResult(ok=False, error=self._root_error)
        if self._custom_root is not None:
            return AriaResult(ok=True, data=self._custom_root)
        return AriaResult(
            ok=True,
            data=AutoBrowseNode(
                node_id="root",
                node_type=AutoBrowseNodeType.ROOT,
                title="Aria Root",
                browsable=True,
                children=[
                    AutoBrowseNode(
                        node_id="artists_root",
                        node_type=AutoBrowseNodeType.ARTISTS,
                        title="Artists",
                        browsable=True,
                    ),
                    AutoBrowseNode(
                        node_id="albums_root",
                        node_type=AutoBrowseNodeType.ALBUMS,
                        title="Albums",
                        browsable=True,
                    ),
                ],
            ),
        )

    def browse(self, node_id: str) -> AriaResult[AutoBrowseResult]:
        if self._browse_error is not None:
            return AriaResult(ok=False, error=self._browse_error)
        if self._custom_browse_map and node_id in self._custom_browse_map:
            return AriaResult(
                ok=True, data=self._custom_browse_map[node_id]
            )
        if node_id == "artists_root":
            return AriaResult(
                ok=True,
                data=AutoBrowseResult(
                    parent_node_id=node_id,
                    nodes=[
                        AutoBrowseNode(
                            node_id="artist_1",
                            node_type=AutoBrowseNodeType.ARTISTS,
                            title="Fake Artist",
                            playable=False,
                            browsable=True,
                        )
                    ],
                    total_count=1,
                ),
            )
        return AriaResult(
            ok=False,
            error=AriaError(
                code="INVALID_NODE_ID", message=f"Unknown node: {node_id}"
            ),
        )

    def search(self, query: str) -> AriaResult[AutoSearchResult]:
        if self._search_error is not None:
            return AriaResult(ok=False, error=self._search_error)
        if self._custom_search_results and query in self._custom_search_results:
            return AriaResult(
                ok=True, data=self._custom_search_results[query]
            )
        if not query.strip():
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="INVALID_COMMAND", message="Empty search query"
                ),
            )
        return AriaResult(
            ok=True,
            data=AutoSearchResult(query=query, nodes=[], total_count=0),
        )

    def play_from_node(self, node_id: str) -> AriaResult[bool]:
        if self._play_error is not None:
            return AriaResult(ok=False, error=self._play_error)
        if node_id in ("artist_1", "album_1", "track_1"):
            return AriaResult(ok=True, data=True)
        return AriaResult(
            ok=False,
            error=AriaError(
                code="INVALID_NODE_ID",
                message=f"Cannot play node: {node_id}",
            ),
        )


@dataclass
class FakeForegroundServiceBridge:
    """Deterministic fake for ``ForegroundServiceBridge``.

    Failure-injection hooks:
        _start_error, _stop_error, _notification_error, _state_error

    State tracking:
        _current_state, _last_notification_metadata
    """

    _start_error: AriaError | None = field(default=None, repr=False)
    _stop_error: AriaError | None = field(default=None, repr=False)
    _notification_error: AriaError | None = field(default=None, repr=False)
    _state_error: AriaError | None = field(default=None, repr=False)

    _current_state: ForegroundServiceState = field(
        default=ForegroundServiceState.NOT_STARTED, repr=False
    )
    _last_notification_metadata: TrackMetadata | None = field(
        default=None, repr=False
    )

    def start(
        self, requirement: ForegroundServiceRequirement
    ) -> AriaResult[bool]:
        if self._start_error is not None:
            return AriaResult(ok=False, error=self._start_error)
        if self._current_state == ForegroundServiceState.RUNNING:
            return AriaResult(ok=True, data=True)
        self._current_state = ForegroundServiceState.RUNNING
        return AriaResult(ok=True, data=True)

    def stop(self) -> AriaResult[bool]:
        if self._stop_error is not None:
            return AriaResult(ok=False, error=self._stop_error)
        self._current_state = ForegroundServiceState.STOPPED
        return AriaResult(ok=True, data=True)

    def update_notification(
        self, metadata: TrackMetadata
    ) -> AriaResult[bool]:
        if self._notification_error is not None:
            return AriaResult(ok=False, error=self._notification_error)
        self._last_notification_metadata = metadata
        return AriaResult(ok=True, data=True)

    def get_state(self) -> AriaResult[ForegroundServiceState]:
        if self._state_error is not None:
            return AriaResult(ok=False, error=self._state_error)
        return AriaResult(ok=True, data=self._current_state)


@dataclass
class FakeAppLifecycleBridge:
    """Deterministic fake for ``AppLifecycleBridge``.

    Implements a derived state machine from reported events.

    Failure-injection hooks:
        _event_error, _state_error, _foreground_error
    """

    _event_error: AriaError | None = field(default=None, repr=False)
    _state_error: AriaError | None = field(default=None, repr=False)
    _foreground_error: AriaError | None = field(default=None, repr=False)

    _derived_state: AppLifecycleState = field(
        default=AppLifecycleState.CREATED, repr=False
    )

    _EVENT_TO_STATE: dict[AppLifecycleEvent, AppLifecycleState] = field(
        default_factory=lambda: {
            AppLifecycleEvent.ON_CREATE: AppLifecycleState.CREATED,
            AppLifecycleEvent.ON_START: AppLifecycleState.STARTED,
            AppLifecycleEvent.ON_RESUME: AppLifecycleState.RESUMED,
            AppLifecycleEvent.ON_PAUSE: AppLifecycleState.PAUSED,
            AppLifecycleEvent.ON_STOP: AppLifecycleState.STOPPED,
            AppLifecycleEvent.ON_DESTROY: AppLifecycleState.DESTROYED,
        },
        repr=False,
    )

    _FOREGROUND_STATES: set[AppLifecycleState] = field(
        default_factory=lambda: {
            AppLifecycleState.RESUMED,
            AppLifecycleState.FOREGROUNDED,
        },
        repr=False,
    )

    def report_event(self, event: AppLifecycleEvent) -> AriaResult[bool]:
        if self._event_error is not None:
            return AriaResult(ok=False, error=self._event_error)
        new_state = self._EVENT_TO_STATE.get(event)
        if new_state is not None:
            self._derived_state = new_state
        return AriaResult(ok=True, data=True)

    def get_state(self) -> AriaResult[AppLifecycleState]:
        if self._state_error is not None:
            return AriaResult(ok=False, error=self._state_error)
        return AriaResult(ok=True, data=self._derived_state)

    def is_in_foreground(self) -> AriaResult[bool]:
        if self._foreground_error is not None:
            return AriaResult(ok=False, error=self._foreground_error)
        return AriaResult(
            ok=True, data=self._derived_state in self._FOREGROUND_STATES
        )


@dataclass
class FakeNotificationControlBridge:
    """Deterministic fake for ``NotificationControlBridge``.

    Failure-injection hooks:
        _action_error, _content_error, _dismiss_error
    """

    _action_error: AriaError | None = field(default=None, repr=False)
    _content_error: AriaError | None = field(default=None, repr=False)
    _dismiss_error: AriaError | None = field(default=None, repr=False)

    _last_action: NotificationAction | None = field(default=None, repr=False)
    _last_metadata: TrackMetadata | None = field(default=None, repr=False)
    _last_state: PlaybackState | None = field(default=None, repr=False)
    _dismissed: bool = field(default=False, repr=False)

    def handle_action(
        self, action: NotificationAction
    ) -> AriaResult[bool]:
        if self._action_error is not None:
            return AriaResult(ok=False, error=self._action_error)
        self._last_action = action
        return AriaResult(ok=True, data=True)

    def update_content(
        self, metadata: TrackMetadata, state: PlaybackState
    ) -> AriaResult[bool]:
        if self._content_error is not None:
            return AriaResult(ok=False, error=self._content_error)
        self._last_metadata = metadata
        self._last_state = state
        return AriaResult(ok=True, data=True)

    def dismiss(self) -> AriaResult[bool]:
        if self._dismiss_error is not None:
            return AriaResult(ok=False, error=self._dismiss_error)
        self._dismissed = True
        return AriaResult(ok=True, data=True)


@dataclass
class FakeLockScreenBridge:
    """Deterministic fake for ``LockScreenBridge``.

    Failure-injection hooks:
        _state_error, _action_error
    """

    _state_error: AriaError | None = field(default=None, repr=False)
    _action_error: AriaError | None = field(default=None, repr=False)

    _lock_screen_state: LockScreenControlState | None = field(
        default=None, repr=False
    )
    _last_action: NotificationAction | None = field(default=None, repr=False)

    def update_state(
        self, state: LockScreenControlState
    ) -> AriaResult[bool]:
        if self._state_error is not None:
            return AriaResult(ok=False, error=self._state_error)
        self._lock_screen_state = state
        return AriaResult(ok=True, data=True)

    def handle_action(
        self, action: NotificationAction
    ) -> AriaResult[bool]:
        if self._action_error is not None:
            return AriaResult(ok=False, error=self._action_error)
        self._last_action = action
        return AriaResult(ok=True, data=True)


@dataclass
class FakeHeadsetControlBridge:
    """Deterministic fake for ``HeadsetControlBridge``.

    Failure-injection hooks:
        _event_error, _connected_error

    State:
        _connected: whether a headset is simulated as connected.
    """

    _event_error: AriaError | None = field(default=None, repr=False)
    _connected_error: AriaError | None = field(default=None, repr=False)

    _connected: bool = field(default=True, repr=False)
    _last_event: HeadsetEventType | None = field(default=None, repr=False)

    def handle_event(self, event: HeadsetEventType) -> AriaResult[bool]:
        if self._event_error is not None:
            return AriaResult(ok=False, error=self._event_error)
        if not self._connected and event in (
            HeadsetEventType.BUTTON_PRESS,
            HeadsetEventType.BUTTON_DOUBLE_PRESS,
            HeadsetEventType.BUTTON_TRIPLE_PRESS,
            HeadsetEventType.BUTTON_LONG_PRESS,
            HeadsetEventType.PLAY_PAUSE,
            HeadsetEventType.NEXT,
            HeadsetEventType.PREVIOUS,
            HeadsetEventType.STOP,
        ):
            return AriaResult(
                ok=False,
                error=AriaError(
                    code="HEADSET_NOT_CONNECTED",
                    message="No headset connected",
                ),
            )
        self._last_event = event
        return AriaResult(ok=True, data=True)

    def is_connected(self) -> AriaResult[bool]:
        if self._connected_error is not None:
            return AriaResult(ok=False, error=self._connected_error)
        return AriaResult(ok=True, data=self._connected)
