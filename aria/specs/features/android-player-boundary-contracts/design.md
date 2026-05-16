# Design

## Summary

Create eight boundary bridge protocols (`PlaybackEngineBridge`, `MediaSessionBridge`, `AndroidStorageBridge`, `AndroidAutoBridge`, `ForegroundServiceBridge`, `AppLifecycleBridge`, `NotificationControlBridge`, `LockScreenBridge`, `HeadsetControlBridge`), supporting dataclasses/enums for each, a composite `AndroidBoundarySnapshot`, and corresponding fake implementations — all in a single proposed future `src/noqlen_aria/android_boundaries.py` module. No source code is created by this spec. All contracts are Android-platform-aware in vocabulary only, using Python standard library types with zero Android SDK imports.

## Context files read

- `AGENTS.md`
- `docs/aria-core-handoff.md`
- `docs/handoff.md`
- `aria/context/project.md`
- `aria/context/scope-boundaries.md`
- `aria/context/repository-hygiene.md`
- `aria/context/current.md`
- `aria/context/delta.md`
- `aria/context/context-packages.md`
- `aria/context/behavior-budget.md`
- `aria/context/test-risk-matrix.md`
- `aria/review/validation-checklist.md`
- `aria/review/fake-hostility-checklist.md`
- `aria/specs/_template/requirements.md`
- `aria/specs/_template/design.md`
- `aria/specs/_template/tasks.md`
- `aria/specs/_template/review.md`
- `aria/specs/features/aria-core-contracts/requirements.md`
- `aria/specs/features/aria-core-contracts/design.md`
- `aria/specs/features/aria-core-contracts/tasks.md`
- `aria/specs/features/aria-core-contracts/review.md`
- `src/noqlen_aria/contracts.py`

## Context package

Standard. This is a non-trivial spec with multiple boundary vocabularies, edge cases, and planning concerns.

## Existing project context

Blocos 0-3 are complete. The repository has `AriaResult[T]`, `AriaError`, `AriaWarning`, `ControlClient`, `FakeControlClient`, `PermissionState`, `StorageAccessState`, and `LifecycleIntent` defined in `src/noqlen_aria/contracts.py`. The `AndroidStorageBridge` boundary reuses `PermissionState` from Bloco 1.

Architecture model: `Future Android Player (thin adapter) -> Aria Core Android Boundaries -> Aria Core Control Plane`.

Bloco 4 is the first block that defines Android-player-facing contracts. It stays strictly at the boundary vocabulary level — no Android SDK, no real playback, no UI.

## Files to create

Spec (created now):

- `aria/specs/features/android-player-boundary-contracts/requirements.md`
- `aria/specs/features/android-player-boundary-contracts/design.md`
- `aria/specs/features/android-player-boundary-contracts/tasks.md`
- `aria/specs/features/android-player-boundary-contracts/review.md`

Source (targeted for future implementation, not created now):

- `src/noqlen_aria/android_boundaries.py` — single module with all boundary contract definitions.

Tests (targeted for future implementation, not created now):

- `tests/test_android_boundaries.py` — tests for all boundary contracts and fake implementations.

## Files to modify

- `aria/context/current.md` — update to reflect Bloco 4 spec completion.
- `aria/context/delta.md` — record Bloco 4 spec creation.
- `docs/handoff.md` — add Bloco 4 spec status note if needed.

## Files that must not be touched

- `src/noqlen_aria/__init__.py`
- `src/noqlen_aria/cli.py`
- `src/noqlen_aria/contracts.py`
- `src/noqlen_aria/services.py`
- `src/noqlen_aria/anchor_adapter.py`
- `tests/*.py`
- `pyproject.toml`
- All Android, Kotlin, Java, Gradle files (none exist)
- Any secret, credential, log, cache, or temporary file

## Expected module layout (`src/noqlen_aria/android_boundaries.py`)

Proposed contents for future implementation (not created now):

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Protocol, runtime_checkable

from noqlen_aria.contracts import (
    AriaError,
    AriaResult,
    PermissionState,
    StorageAccessState,
)

# ── Playback Engine Boundary ─────────────────────────────────

class PlaybackState(Enum):
    IDLE = auto()
    BUFFERING = auto()
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    STOPPED = auto()
    COMPLETED = auto()
    ERROR = auto()

class PlaybackCommand(Enum):
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
    elapsed_ms: int = 0
    duration_ms: int = 0
    buffered_ms: int = 0

@dataclass(frozen=True)
class TrackMetadata:
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
    state: PlaybackState = PlaybackState.IDLE
    track: TrackMetadata | None = None
    position: PlaybackPosition = field(default_factory=PlaybackPosition)
    error: AriaError | None = None

@runtime_checkable
class PlaybackEngineBridge(Protocol):
    def get_snapshot(self) -> AriaResult[PlaybackEngineSnapshot]: ...
    def send_command(self, command: PlaybackCommand, **kwargs) -> AriaResult[bool]: ...
    def register_state_callback(self, callback: Callable[[PlaybackEngineSnapshot], None]) -> AriaResult[bool]: ...

# ── MediaSession Bridge Boundary ────────────────────────────

class MediaSessionAction(Enum):
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
    NONE = auto()
    ONE = auto()
    ALL = auto()
    GROUP = auto()

class MediaSessionShuffleMode(Enum):
    NONE = auto()
    ALL = auto()
    GROUP = auto()

@dataclass(frozen=True)
class MediaSessionPlaybackState:
    state: PlaybackState = PlaybackState.IDLE
    actions: int = 0
    position: PlaybackPosition = field(default_factory=PlaybackPosition)
    repeat_mode: MediaSessionRepeatMode = MediaSessionRepeatMode.NONE
    shuffle_mode: MediaSessionShuffleMode = MediaSessionShuffleMode.NONE

@dataclass(frozen=True)
class MediaSessionMetadata:
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
    def get_playback_state(self) -> AriaResult[MediaSessionPlaybackState]: ...
    def get_metadata(self) -> AriaResult[MediaSessionMetadata]: ...
    def handle_action(self, action: MediaSessionAction, extras: dict | None = None) -> AriaResult[bool]: ...
    def on_command_from_transport(self, callback: Callable[[MediaSessionAction], None]) -> AriaResult[bool]: ...

# ── Android Storage Bridge Boundary ─────────────────────────

class StorageType(Enum):
    MUSIC_DIRECTORY = auto()
    PLAYLIST_FILE = auto()
    CACHE_DIRECTORY = auto()
    DOWNLOAD_DIRECTORY = auto()
    DATABASE = auto()
    PREFERENCES = auto()
    LOGS = auto()

class StorageStatus(Enum):
    OK = auto()
    MISSING = auto()
    FULL = auto()
    READ_ONLY = auto()
    PERMISSION_DENIED = auto()
    IO_ERROR = auto()

@dataclass(frozen=True)
class StorageRequirement:
    storage_type: StorageType
    requires_write: bool = False
    critical: bool = False

@dataclass(frozen=True)
class StorageStatusSnapshot:
    entries: dict[StorageType, StorageStatus] = field(default_factory=dict)
    all_ok: bool = True

@runtime_checkable
class AndroidStorageBridge(Protocol):
    def get_storage_status(self) -> AriaResult[StorageStatusSnapshot]: ...
    def check_requirement(self, requirement: StorageRequirement) -> AriaResult[bool]: ...
    def get_permission_state(self) -> AriaResult[PermissionState]: ...

# ── Android Auto Bridge Boundary ────────────────────────────

class AutoBrowseNodeType(Enum):
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
    parent_node_id: str
    nodes: list[AutoBrowseNode] = field(default_factory=list)
    total_count: int = 0
    has_more: bool = False

@dataclass(frozen=True)
class AutoSearchResult:
    query: str
    nodes: list[AutoBrowseNode] = field(default_factory=list)
    total_count: int = 0

@runtime_checkable
class AndroidAutoBridge(Protocol):
    def get_root(self) -> AriaResult[AutoBrowseNode]: ...
    def browse(self, node_id: str) -> AriaResult[AutoBrowseResult]: ...
    def search(self, query: str) -> AriaResult[AutoSearchResult]: ...
    def play_from_node(self, node_id: str) -> AriaResult[bool]: ...

# ── Foreground Service Lifecycle Boundary ───────────────────

class ForegroundServiceState(Enum):
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
    notification_channel_id: str = "playback"
    notification_title_template: str = "Now Playing"
    requires_audio_focus: bool = False
    requires_wifi_lock: bool = False
    requires_wake_lock: bool = False

@runtime_checkable
class ForegroundServiceBridge(Protocol):
    def start(self, requirement: ForegroundServiceRequirement) -> AriaResult[bool]: ...
    def stop(self) -> AriaResult[bool]: ...
    def update_notification(self, metadata: TrackMetadata) -> AriaResult[bool]: ...
    def get_state(self) -> AriaResult[ForegroundServiceState]: ...

# ── App Lifecycle Boundary ──────────────────────────────────

class AppLifecycleEvent(Enum):
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
    def report_event(self, event: AppLifecycleEvent) -> AriaResult[bool]: ...
    def get_state(self) -> AriaResult[AppLifecycleState]: ...
    def is_in_foreground(self) -> AriaResult[bool]: ...

# ── Notification / Lock-Screen / Headset Boundaries ─────────

class NotificationAction(Enum):
    PLAY_PAUSE = auto()
    NEXT = auto()
    PREVIOUS = auto()
    STOP = auto()
    SEEK_FORWARD = auto()
    SEEK_BACKWARD = auto()
    CUSTOM = auto()

@runtime_checkable
class NotificationControlBridge(Protocol):
    def handle_action(self, action: NotificationAction) -> AriaResult[bool]: ...
    def update_content(self, metadata: TrackMetadata, state: PlaybackState) -> AriaResult[bool]: ...
    def dismiss(self) -> AriaResult[bool]: ...

@dataclass(frozen=True)
class LockScreenControlState:
    enabled: bool = False
    playback_state: PlaybackState = PlaybackState.IDLE
    metadata: TrackMetadata | None = None
    available_actions: list[NotificationAction] = field(default_factory=list)

@runtime_checkable
class LockScreenBridge(Protocol):
    def update_state(self, state: LockScreenControlState) -> AriaResult[bool]: ...
    def handle_action(self, action: NotificationAction) -> AriaResult[bool]: ...

class HeadsetEventType(Enum):
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
    def handle_event(self, event: HeadsetEventType) -> AriaResult[bool]: ...
    def is_connected(self) -> AriaResult[bool]: ...

# ── Composite Android Boundary Snapshot ─────────────────────

@dataclass(frozen=True)
class AndroidBoundarySnapshot:
    playback_engine: PlaybackEngineSnapshot = field(default_factory=PlaybackEngineSnapshot)
    media_session: MediaSessionPlaybackState = field(default_factory=MediaSessionPlaybackState)
    storage_status: StorageStatusSnapshot = field(default_factory=StorageStatusSnapshot)
    foreground_service: ForegroundServiceState = ForegroundServiceState.NOT_STARTED
    app_lifecycle: AppLifecycleState = AppLifecycleState.CREATED
    headset_connected: bool = False
```

Note: This is a design proposal. Exact field lists, method signatures, and defaults are subject to refinement during implementation. All fake implementations must be deterministic and must never call real Android APIs, filesystem, or network.

## Data flow

```
Future Android Player (thin Kotlin adapter)
    │
    ├── PlaybackEngineBridge ──────> Aria Core PlaybackEngine (future)
    ├── MediaSessionBridge ────────> Aria Core MediaSessionController (future)
    ├── AndroidStorageBridge ──────> Aria Core StorageManager (future)
    ├── AndroidAutoBridge ─────────> Aria Core AutoController (future)
    ├── ForegroundServiceBridge ───> Aria Core ServiceManager (future)
    ├── AppLifecycleBridge ────────> Aria Core LifecycleManager (future)
    ├── NotificationControlBridge ─> Aria Core NotificationController (future)
    ├── LockScreenBridge ──────────> Aria Core LockScreenController (future)
    └── HeadsetControlBridge ──────> Aria Core HeadsetController (future)
```

In Bloco 4 (spec):
1. Define all boundary protocols, data classes, and enums.
2. No implementation, no tests, no Android SDK.

In future implementation:
1. Tests instantiate fake implementations for each bridge.
2. Tests verify contract compliance (return types, edge cases, determinism).
3. Future Android shell consumes real implementations that satisfy these protocols.

## Error handling

- All bridge methods return `AriaResult[T]` for consistent error propagation.
- `PlaybackEngineSnapshot.error` carries a nullable `AriaError` for playback-specific errors.
- `StorageStatusSnapshot` uses `StorageStatus` enum to signal per-type storage issues.
- Unknown/invalid commands must return `AriaResult.ok=False` with `AriaError(code="UNSUPPORTED_ACTION" | "INVALID_COMMAND")`.
- Fake implementations return deterministic results; they do not throw exceptions except for intentionally invalid inputs in tests.
- `MediaSessionBridge.handle_action` with an unsupported action returns error; with a supported but not-currently-available action returns success with no-op.

## Security considerations

- No secrets, tokens, URLs, or credentials in contract definitions.
- No network calls in boundary contracts.
- No filesystem access in boundary contracts.
- No subprocess execution in boundary contracts.
- No real Android API access.
- No real storage access or permission requests.
- `ForegroundServiceRequirement` fields are templates, not actual Android notification channel or intent configuration.
- `AutoBrowseNode.icon_uri` and similar URI fields are abstract identifiers, not real file paths or content URIs.

## Dependencies

- No runtime dependencies beyond Python 3.11+ standard library (`dataclasses`, `enum`, `typing`).
- Internal dependency on `noqlen_aria.contracts` for `AriaResult`, `AriaError`, `PermissionState`, `StorageAccessState`.
- No additions to `pyproject.toml`.
- No Android SDK, no Kotlin, no Java, no Gradle.

## Behavior Budget

- New behaviors: documentation/spec only. Zero runtime behavior changes.
- Public API changes: proposed only via future module layout. No source code created.
- Files allowed: `aria/specs/features/android-player-boundary-contracts/**`, plus `aria/context/current.md`, `aria/context/delta.md`, `docs/handoff.md` if needed.
- Tests required: none in this task. Validation only (existing commands must pass).
- Dependencies: none added.
- Stop if: any implementation code, Android file, or source code change becomes necessary.
- All boundary contracts are vocabulary-level only. No Android SDK integration.
- All bridges are `typing.Protocol` definitions; no real bridge implementations.

## Risks

- R01: Boundary vocabulary may be incomplete for full Android MediaSession/Auto integration. Mitigation: protocols can be extended non-breakingly; `@runtime_checkable` supports graceful degradation.
- R02: Tight coupling risk between boundary contracts and Android platform APIs. Mitigation: use domain-generic names, no `android.*` imports, vocabulary-only design.
- R03: `TrackMetadata` and `MediaSessionMetadata` may diverge as Android platform requirements evolve. Mitigation: keep them independent; no shared inheritance.
- R04: Time gap between spec and implementation may cause vocabulary drift. Mitigation: keep spec files as living documents; update during implementation.
- R05: `AndroidBoundarySnapshot` may grow too large to be practical for frequent updates. Mitigation: individual bridges provide granular access; composite snapshot is for convenience/serialization.

## Risk classification

Per `aria/context/test-risk-matrix.md`:

- High risk: Permission/storage boundary vocabulary (FR-30). Integration adapter boundaries (all bridge protocols). These affect safety rules and dry-run/apply boundaries.
- Medium risk: Playback engine state vocabulary (FR-10). MediaSession action vocabulary (FR-20). These affect view-state defaults and public exports.
- Low risk: Spec documentation only (this task). No source code changes.

For this spec-only task, risk is inherently low since no behavior changes are made.

## Rollback strategy

Spec-only task: if the spec is found to be incorrect during review or later implementation, edit the spec files in a focused commit. If the boundary vocabulary is fundamentally wrong, the spec files may be updated or replaced. No source code rollback is needed.

## Validation plan

During this spec-only phase:
1. Run `pwd` to confirm working directory.
2. Run `git status --short --branch` to confirm clean or only expected changes.
3. Run `find aria/specs/features/android-player-boundary-contracts aria/context -maxdepth 5 -type f | sort` to confirm all spec files present.
4. Run `git diff --check` to confirm no whitespace issues.
5. Run `python3 -m py_compile src/noqlen_aria/*.py` to confirm no regression.
6. Run `PYTHONPATH=src python3 -m noqlen_aria.cli --help` to confirm CLI works.
7. Run `PYTHONPATH=src python3 -m noqlen_aria.cli doctor` to confirm doctor works.
8. Run `python3 -m pytest` to confirm all existing tests pass.
9. Run repository contamination check with `git ls-files` patterns.
10. Commit spec files only.

During later implementation phase:
1. Run `python3 -m py_compile src/noqlen_aria/android_boundaries.py`.
2. Run `PYTHONPATH=src python3 -c "import noqlen_aria.android_boundaries"`.
3. Run `python3 -m pytest tests/test_android_boundaries.py -v`.
4. Run full Bloco 0-4 validation suite including structural typing and fake hostility checks.
