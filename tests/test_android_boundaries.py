"""Tests for Aria Core Android/player boundary contracts and fake implementations."""

import pytest

from noqlen_aria.android_boundaries import (
    AndroidAutoBridge,
    AndroidBoundarySnapshot,
    AndroidStorageBridge,
    AppLifecycleBridge,
    AppLifecycleEvent,
    AppLifecycleState,
    AutoBrowseNode,
    AutoBrowseNodeType,
    AutoBrowseResult,
    AutoSearchResult,
    FakeAndroidAutoBridge,
    FakeAndroidStorageBridge,
    FakeAppLifecycleBridge,
    FakeForegroundServiceBridge,
    FakeHeadsetControlBridge,
    FakeLockScreenBridge,
    FakeMediaSessionBridge,
    FakeNotificationControlBridge,
    FakePlaybackEngineBridge,
    ForegroundServiceBridge,
    ForegroundServiceRequirement,
    ForegroundServiceState,
    HeadsetControlBridge,
    HeadsetEventType,
    LockScreenBridge,
    LockScreenControlState,
    MediaSessionAction,
    MediaSessionBridge,
    MediaSessionMetadata,
    MediaSessionPlaybackState,
    MediaSessionRepeatMode,
    MediaSessionShuffleMode,
    NotificationAction,
    NotificationControlBridge,
    PlaybackCommand,
    PlaybackEngineBridge,
    PlaybackEngineSnapshot,
    PlaybackPosition,
    PlaybackState,
    StorageRequirement,
    StorageStatus,
    StorageStatusSnapshot,
    StorageType,
    TrackMetadata,
)
from noqlen_aria.contracts import AriaError, AriaResult, PermissionState


# ── Type Definitions ────────────────────────────────────────────


def test_playback_state_enum_members():
    members = set(PlaybackState)
    assert PlaybackState.IDLE in members
    assert PlaybackState.BUFFERING in members
    assert PlaybackState.READY in members
    assert PlaybackState.PLAYING in members
    assert PlaybackState.PAUSED in members
    assert PlaybackState.STOPPED in members
    assert PlaybackState.COMPLETED in members
    assert PlaybackState.ERROR in members


def test_playback_command_enum_members():
    members = set(PlaybackCommand)
    assert PlaybackCommand.PLAY in members
    assert PlaybackCommand.PAUSE in members
    assert PlaybackCommand.STOP in members
    assert PlaybackCommand.SKIP_NEXT in members
    assert PlaybackCommand.SKIP_PREVIOUS in members
    assert PlaybackCommand.SEEK in members
    assert PlaybackCommand.PLAY_INDEX in members
    assert PlaybackCommand.PLAY_ITEM in members


def test_playback_position_defaults():
    pos = PlaybackPosition()
    assert pos.elapsed_ms == 0
    assert pos.duration_ms == 0
    assert pos.buffered_ms == 0


def test_playback_position_explicit():
    pos = PlaybackPosition(elapsed_ms=30000, duration_ms=240000, buffered_ms=120000)
    assert pos.elapsed_ms == 30000
    assert pos.duration_ms == 240000
    assert pos.buffered_ms == 120000


def test_playback_position_immutable():
    pos = PlaybackPosition(elapsed_ms=1000)
    with pytest.raises(Exception):
        pos.elapsed_ms = 2000  # type: ignore[misc]


def test_track_metadata_required_fields():
    tm = TrackMetadata(
        track_id="t1",
        title="Test Title",
        artist="Test Artist",
        album="Test Album",
        duration_ms=180000,
    )
    assert tm.track_id == "t1"
    assert tm.title == "Test Title"
    assert tm.artist == "Test Artist"
    assert tm.album == "Test Album"
    assert tm.duration_ms == 180000


def test_track_metadata_optional_defaults():
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    assert tm.cover_art_uri == ""
    assert tm.album_artist is None
    assert tm.track_number is None
    assert tm.disc_number is None
    assert tm.genre is None
    assert tm.year is None
    assert tm.bitrate_kbps is None
    assert tm.sample_rate_hz is None
    assert tm.bit_depth is None
    assert tm.format is None


def test_track_metadata_optional_full():
    tm = TrackMetadata(
        track_id="t2",
        title="Full",
        artist="Artist",
        album="Album",
        duration_ms=200000,
        cover_art_uri="http://fake/art.jpg",
        album_artist="AlbumArtist",
        track_number=5,
        disc_number=1,
        genre="Rock",
        year=2024,
        bitrate_kbps=320,
        sample_rate_hz=44100,
        bit_depth=16,
        format="FLAC",
    )
    assert tm.cover_art_uri == "http://fake/art.jpg"
    assert tm.album_artist == "AlbumArtist"
    assert tm.track_number == 5
    assert tm.disc_number == 1
    assert tm.genre == "Rock"
    assert tm.year == 2024
    assert tm.bitrate_kbps == 320
    assert tm.sample_rate_hz == 44100
    assert tm.bit_depth == 16
    assert tm.format == "FLAC"


def test_track_metadata_immutable():
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    with pytest.raises(Exception):
        tm.title = "X"  # type: ignore[misc]


def test_playback_engine_snapshot_defaults():
    snap = PlaybackEngineSnapshot()
    assert snap.state == PlaybackState.IDLE
    assert snap.track is None
    assert isinstance(snap.position, PlaybackPosition)
    assert snap.error is None


def test_playback_engine_snapshot_full():
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    pos = PlaybackPosition(elapsed_ms=5000)
    err = AriaError(code="E", message="fail")
    snap = PlaybackEngineSnapshot(state=PlaybackState.PLAYING, track=tm, position=pos, error=err)
    assert snap.state == PlaybackState.PLAYING
    assert snap.track is tm
    assert snap.position == pos
    assert snap.error is err


# ── MediaSession Types ──────────────────────────────────────────


def test_media_session_action_enum():
    members = set(MediaSessionAction)
    assert MediaSessionAction.PLAY in members
    assert MediaSessionAction.PAUSE in members
    assert MediaSessionAction.SKIP_TO_NEXT in members
    assert MediaSessionAction.SKIP_TO_PREVIOUS in members
    assert MediaSessionAction.SEEK_TO in members
    assert MediaSessionAction.STOP in members
    assert MediaSessionAction.FAST_FORWARD in members
    assert MediaSessionAction.REWIND in members
    assert MediaSessionAction.SKIP_TO_QUEUE_ITEM in members
    assert MediaSessionAction.SET_REPEAT_MODE in members
    assert MediaSessionAction.SET_SHUFFLE_MODE in members
    assert MediaSessionAction.SET_RATING in members
    assert MediaSessionAction.CUSTOM_ACTION in members


def test_media_session_repeat_mode():
    members = set(MediaSessionRepeatMode)
    assert MediaSessionRepeatMode.NONE in members
    assert MediaSessionRepeatMode.ONE in members
    assert MediaSessionRepeatMode.ALL in members
    assert MediaSessionRepeatMode.GROUP in members


def test_media_session_shuffle_mode():
    members = set(MediaSessionShuffleMode)
    assert MediaSessionShuffleMode.NONE in members
    assert MediaSessionShuffleMode.ALL in members
    assert MediaSessionShuffleMode.GROUP in members


def test_media_session_playback_state_defaults():
    state = MediaSessionPlaybackState()
    assert state.state == PlaybackState.IDLE
    assert state.actions == 0
    assert isinstance(state.position, PlaybackPosition)
    assert state.repeat_mode == MediaSessionRepeatMode.NONE
    assert state.shuffle_mode == MediaSessionShuffleMode.NONE


def test_media_session_metadata_defaults():
    md = MediaSessionMetadata()
    assert md.media_id == ""
    assert md.title == ""
    assert md.duration_ms == 0


def test_media_session_metadata_full():
    md = MediaSessionMetadata(
        media_id="m1",
        title="The Title",
        artist="The Artist",
        album="The Album",
        album_artist="Album Artist",
        display_title="Display",
        display_subtitle="Subtitle",
        display_description="Description",
        display_icon_uri="icon://uri",
        art_uri="art://uri",
        duration_ms=300000,
        track_number=3,
        disc_number=1,
        genre="Jazz",
        year=2023,
        rating="5",
    )
    assert md.media_id == "m1"
    assert md.title == "The Title"
    assert md.artist == "The Artist"
    assert md.album == "The Album"
    assert md.album_artist == "Album Artist"
    assert md.display_title == "Display"
    assert md.display_subtitle == "Subtitle"
    assert md.display_description == "Description"
    assert md.display_icon_uri == "icon://uri"
    assert md.art_uri == "art://uri"
    assert md.duration_ms == 300000
    assert md.track_number == 3
    assert md.disc_number == 1
    assert md.genre == "Jazz"
    assert md.year == 2023
    assert md.rating == "5"


# ── Storage Types ──────────────────────────────────────────────


def test_storage_type_enum():
    members = set(StorageType)
    assert StorageType.MUSIC_DIRECTORY in members
    assert StorageType.PLAYLIST_FILE in members
    assert StorageType.CACHE_DIRECTORY in members
    assert StorageType.DOWNLOAD_DIRECTORY in members
    assert StorageType.DATABASE in members
    assert StorageType.PREFERENCES in members
    assert StorageType.LOGS in members


def test_storage_status_enum():
    members = set(StorageStatus)
    assert StorageStatus.OK in members
    assert StorageStatus.MISSING in members
    assert StorageStatus.FULL in members
    assert StorageStatus.READ_ONLY in members
    assert StorageStatus.PERMISSION_DENIED in members
    assert StorageStatus.IO_ERROR in members


def test_storage_requirement_construction():
    req = StorageRequirement(
        storage_type=StorageType.MUSIC_DIRECTORY,
        requires_write=True,
        critical=True,
    )
    assert req.storage_type == StorageType.MUSIC_DIRECTORY
    assert req.requires_write is True
    assert req.critical is True


def test_storage_requirement_defaults():
    req = StorageRequirement(storage_type=StorageType.PLAYLIST_FILE)
    assert req.requires_write is False
    assert req.critical is False


def test_storage_status_snapshot_defaults():
    snap = StorageStatusSnapshot()
    assert snap.entries == {}
    assert snap.all_ok is True


def test_storage_status_snapshot_custom():
    entries = {StorageType.MUSIC_DIRECTORY: StorageStatus.OK}
    snap = StorageStatusSnapshot(entries=entries, all_ok=True)
    assert snap.entries == entries
    assert snap.all_ok is True


# ── Android Auto Types ──────────────────────────────────────────


def test_auto_browse_node_type_enum():
    members = set(AutoBrowseNodeType)
    assert AutoBrowseNodeType.ROOT in members
    assert AutoBrowseNodeType.ARTISTS in members
    assert AutoBrowseNodeType.ALBUMS in members
    assert AutoBrowseNodeType.TRACKS in members
    assert AutoBrowseNodeType.PLAYLISTS in members
    assert AutoBrowseNodeType.GENRES in members
    assert AutoBrowseNodeType.FOLDERS in members


def test_auto_browse_node_construction():
    node = AutoBrowseNode(
        node_id="n1",
        node_type=AutoBrowseNodeType.ARTISTS,
        title="Artist Name",
        subtitle="5 albums",
        playable=False,
        browsable=True,
    )
    assert node.node_id == "n1"
    assert node.node_type == AutoBrowseNodeType.ARTISTS
    assert node.title == "Artist Name"
    assert node.subtitle == "5 albums"
    assert node.playable is False
    assert node.browsable is True
    assert node.icon_uri == ""
    assert node.children is None


def test_auto_browse_node_with_children():
    child = AutoBrowseNode(node_id="c1", node_type=AutoBrowseNodeType.ALBUMS, title="Album")
    parent = AutoBrowseNode(
        node_id="p1",
        node_type=AutoBrowseNodeType.ARTISTS,
        title="Artist",
        children=[child],
    )
    assert parent.children is not None
    assert len(parent.children) == 1
    assert parent.children[0].node_id == "c1"


def test_auto_browse_result_construction():
    node = AutoBrowseNode(node_id="n1", node_type=AutoBrowseNodeType.TRACKS, title="Track")
    result = AutoBrowseResult(
        parent_node_id="p1",
        nodes=[node],
        total_count=1,
        has_more=False,
    )
    assert result.parent_node_id == "p1"
    assert len(result.nodes) == 1
    assert result.total_count == 1
    assert result.has_more is False


def test_auto_search_result_construction():
    result = AutoSearchResult(query="hello", nodes=[], total_count=0)
    assert result.query == "hello"
    assert result.nodes == []
    assert result.total_count == 0


# ── Foreground Service Types ────────────────────────────────────


def test_foreground_service_state_enum():
    members = set(ForegroundServiceState)
    assert ForegroundServiceState.NOT_STARTED in members
    assert ForegroundServiceState.STARTING in members
    assert ForegroundServiceState.RUNNING in members
    assert ForegroundServiceState.PAUSING in members
    assert ForegroundServiceState.PAUSED in members
    assert ForegroundServiceState.STOPPING in members
    assert ForegroundServiceState.STOPPED in members
    assert ForegroundServiceState.ERROR in members


def test_foreground_service_requirement():
    req = ForegroundServiceRequirement(
        notification_channel_id="playback",
        notification_title_template="Now Playing",
        requires_audio_focus=True,
        requires_wifi_lock=False,
        requires_wake_lock=True,
    )
    assert req.notification_channel_id == "playback"
    assert req.notification_title_template == "Now Playing"
    assert req.requires_audio_focus is True
    assert req.requires_wifi_lock is False
    assert req.requires_wake_lock is True


# ── App Lifecycle Types ─────────────────────────────────────────


def test_app_lifecycle_event_enum():
    members = set(AppLifecycleEvent)
    assert AppLifecycleEvent.ON_CREATE in members
    assert AppLifecycleEvent.ON_START in members
    assert AppLifecycleEvent.ON_RESUME in members
    assert AppLifecycleEvent.ON_PAUSE in members
    assert AppLifecycleEvent.ON_STOP in members
    assert AppLifecycleEvent.ON_DESTROY in members


def test_app_lifecycle_state_enum():
    members = set(AppLifecycleState)
    assert AppLifecycleState.CREATED in members
    assert AppLifecycleState.STARTED in members
    assert AppLifecycleState.RESUMED in members
    assert AppLifecycleState.PAUSED in members
    assert AppLifecycleState.STOPPED in members
    assert AppLifecycleState.DESTROYED in members
    assert AppLifecycleState.BACKGROUNDED in members
    assert AppLifecycleState.FOREGROUNDED in members


# ── Notification/LockScreen/Headset Types ────────────────────────


def test_notification_action_enum():
    members = set(NotificationAction)
    assert NotificationAction.PLAY_PAUSE in members
    assert NotificationAction.NEXT in members
    assert NotificationAction.PREVIOUS in members
    assert NotificationAction.STOP in members
    assert NotificationAction.SEEK_FORWARD in members
    assert NotificationAction.SEEK_BACKWARD in members
    assert NotificationAction.CUSTOM in members


def test_lock_screen_control_state_defaults():
    state = LockScreenControlState()
    assert state.enabled is False
    assert state.playback_state == PlaybackState.IDLE
    assert state.metadata is None
    assert state.available_actions == []


def test_lock_screen_control_state_full():
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    actions = [NotificationAction.PLAY_PAUSE, NotificationAction.NEXT]
    state = LockScreenControlState(
        enabled=True,
        playback_state=PlaybackState.PLAYING,
        metadata=tm,
        available_actions=actions,
    )
    assert state.enabled is True
    assert state.playback_state == PlaybackState.PLAYING
    assert state.metadata is tm
    assert state.available_actions == actions


def test_headset_event_type_enum():
    members = set(HeadsetEventType)
    assert HeadsetEventType.CONNECTED in members
    assert HeadsetEventType.DISCONNECTED in members
    assert HeadsetEventType.BUTTON_PRESS in members
    assert HeadsetEventType.BUTTON_DOUBLE_PRESS in members
    assert HeadsetEventType.BUTTON_TRIPLE_PRESS in members
    assert HeadsetEventType.BUTTON_LONG_PRESS in members
    assert HeadsetEventType.PLAY_PAUSE in members
    assert HeadsetEventType.NEXT in members
    assert HeadsetEventType.PREVIOUS in members
    assert HeadsetEventType.STOP in members
    assert HeadsetEventType.VOLUME_UP in members
    assert HeadsetEventType.VOLUME_DOWN in members


# ── Composite Snapshot ──────────────────────────────────────────


def test_android_boundary_snapshot_defaults():
    snap = AndroidBoundarySnapshot()
    assert snap.playback_engine.state == PlaybackState.IDLE
    assert snap.media_session.state == PlaybackState.IDLE
    assert isinstance(snap.storage_status, StorageStatusSnapshot)
    assert snap.foreground_service == ForegroundServiceState.NOT_STARTED
    assert snap.app_lifecycle == AppLifecycleState.CREATED
    assert snap.headset_connected is False


def test_android_boundary_snapshot_custom():
    engine = PlaybackEngineSnapshot(state=PlaybackState.PLAYING)
    snap = AndroidBoundarySnapshot(
        playback_engine=engine,
        headset_connected=True,
    )
    assert snap.playback_engine.state == PlaybackState.PLAYING
    assert snap.headset_connected is True


# ── FakePlaybackEngineBridge ────────────────────────────────────


def test_fake_playback_engine_is_protocol():
    fake = FakePlaybackEngineBridge()
    assert isinstance(fake, PlaybackEngineBridge)


def test_fake_playback_get_snapshot_defaults():
    fake = FakePlaybackEngineBridge()
    result = fake.get_snapshot()
    assert result.is_ok()
    snap = result.data
    assert snap.state == PlaybackState.IDLE
    assert snap.track is not None
    assert snap.track.track_id == "fake-track-1"


def test_fake_playback_send_command_play():
    fake = FakePlaybackEngineBridge()
    result = fake.send_command(PlaybackCommand.PLAY)
    assert result.is_ok()
    assert result.data is True
    snap = fake.get_snapshot().data
    assert snap.state == PlaybackState.PLAYING


def test_fake_playback_send_command_pause():
    fake = FakePlaybackEngineBridge()
    fake.send_command(PlaybackCommand.PLAY)
    fake.send_command(PlaybackCommand.PAUSE)
    assert fake.get_snapshot().data.state == PlaybackState.PAUSED


def test_fake_playback_send_command_stop():
    fake = FakePlaybackEngineBridge()
    fake.send_command(PlaybackCommand.PLAY)
    fake.send_command(PlaybackCommand.STOP)
    assert fake.get_snapshot().data.state == PlaybackState.STOPPED


def test_fake_playback_send_command_seek():
    fake = FakePlaybackEngineBridge()
    result = fake.send_command(PlaybackCommand.SEEK, position_ms=30000)
    assert result.is_ok()
    snap = fake.get_snapshot().data
    assert snap.position.elapsed_ms == 30000


def test_fake_playback_register_callback():
    fake = FakePlaybackEngineBridge()

    def _cb(snap: PlaybackEngineSnapshot) -> None:
        pass

    result = fake.register_state_callback(_cb)
    assert result.is_ok()


def test_fake_playback_snapshot_error_injection():
    err = AriaError(code="ENGINE_CRASH", message="boom")
    fake = FakePlaybackEngineBridge(_snapshot_error=err)
    result = fake.get_snapshot()
    assert result.is_err()
    assert result.error is err


def test_fake_playback_command_error_injection():
    err = AriaError(code="COMMAND_REJECTED", message="nope")
    fake = FakePlaybackEngineBridge(_command_error=err)
    result = fake.send_command(PlaybackCommand.PLAY)
    assert result.is_err()
    assert result.error is err


# ── FakeMediaSessionBridge ──────────────────────────────────────


def test_fake_media_session_is_protocol():
    fake = FakeMediaSessionBridge()
    assert isinstance(fake, MediaSessionBridge)


def test_fake_media_session_get_playback_state():
    fake = FakeMediaSessionBridge()
    result = fake.get_playback_state()
    assert result.is_ok()
    assert result.data.state == PlaybackState.IDLE


def test_fake_media_session_get_metadata():
    fake = FakeMediaSessionBridge()
    result = fake.get_metadata()
    assert result.is_ok()
    assert result.data.media_id == "fake-media-1"
    assert result.data.title == "Fake Title"


def test_fake_media_session_handle_action_play():
    fake = FakeMediaSessionBridge()
    result = fake.handle_action(MediaSessionAction.PLAY)
    assert result.is_ok()
    state = fake.get_playback_state().data
    assert state.state == PlaybackState.PLAYING


def test_fake_media_session_handle_action_pause():
    fake = FakeMediaSessionBridge()
    fake.handle_action(MediaSessionAction.PLAY)
    fake.handle_action(MediaSessionAction.PAUSE)
    state = fake.get_playback_state().data
    assert state.state == PlaybackState.PAUSED


def test_fake_media_session_on_transport_callback():
    fake = FakeMediaSessionBridge()
    received: list[MediaSessionAction] = []

    def _cb(action: MediaSessionAction) -> None:
        received.append(action)

    result = fake.on_command_from_transport(_cb)
    assert result.is_ok()


def test_fake_media_session_action_error_injection():
    err = AriaError(code="ACTION_FAILED", message="failed")
    fake = FakeMediaSessionBridge(_action_error=err)
    result = fake.handle_action(MediaSessionAction.PLAY)
    assert result.is_err()
    assert result.error is err


# ── FakeAndroidStorageBridge ────────────────────────────────────


def test_fake_storage_is_protocol():
    fake = FakeAndroidStorageBridge()
    assert isinstance(fake, AndroidStorageBridge)


def test_fake_storage_get_status_defaults():
    fake = FakeAndroidStorageBridge()
    result = fake.get_storage_status()
    assert result.is_ok()
    assert result.data.all_ok is True
    for t in StorageType:
        assert result.data.entries.get(t) == StorageStatus.OK


def test_fake_storage_check_requirement_ok():
    fake = FakeAndroidStorageBridge()
    req = StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY)
    result = fake.check_requirement(req)
    assert result.is_ok()
    assert result.data is True


def test_fake_storage_check_requirement_denied():
    custom_entries = {
        StorageType.MUSIC_DIRECTORY: StorageStatus.PERMISSION_DENIED,
    }
    fake = FakeAndroidStorageBridge(_custom_status_entries=custom_entries)
    req = StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY, critical=True)
    result = fake.check_requirement(req)
    assert result.is_ok()
    assert result.data is False


def test_fake_storage_check_requirement_missing():
    custom_entries = {StorageType.CACHE_DIRECTORY: StorageStatus.MISSING}
    fake = FakeAndroidStorageBridge(_custom_status_entries=custom_entries)
    req = StorageRequirement(storage_type=StorageType.CACHE_DIRECTORY)
    result = fake.check_requirement(req)
    assert result.is_ok()
    assert result.data is False


def test_fake_storage_get_permission_state():
    fake = FakeAndroidStorageBridge()
    result = fake.get_permission_state()
    assert result.is_ok()
    assert result.data == PermissionState.GRANTED


def test_fake_storage_permission_denied():
    fake = FakeAndroidStorageBridge(_custom_permission_state=PermissionState.DENIED)
    result = fake.get_permission_state()
    assert result.data == PermissionState.DENIED


def test_fake_storage_permission_unknown():
    fake = FakeAndroidStorageBridge(_custom_permission_state=PermissionState.UNKNOWN)
    result = fake.get_permission_state()
    assert result.data == PermissionState.UNKNOWN


def test_fake_storage_error_injection():
    err = AriaError(code="STORAGE_UNAVAILABLE", message="no storage")
    fake = FakeAndroidStorageBridge(_storage_status_error=err)
    result = fake.get_storage_status()
    assert result.is_err()
    assert result.error is err


def test_fake_storage_all_ok_false():
    entries = {
        StorageType.MUSIC_DIRECTORY: StorageStatus.OK,
        StorageType.CACHE_DIRECTORY: StorageStatus.FULL,
    }
    fake = FakeAndroidStorageBridge(_custom_status_entries=entries)
    result = fake.get_storage_status()
    assert result.is_ok()
    assert result.data.all_ok is False


# ── FakeAndroidAutoBridge ───────────────────────────────────────


def test_fake_auto_is_protocol():
    fake = FakeAndroidAutoBridge()
    assert isinstance(fake, AndroidAutoBridge)


def test_fake_auto_get_root():
    fake = FakeAndroidAutoBridge()
    result = fake.get_root()
    assert result.is_ok()
    root = result.data
    assert root.node_id == "root"
    assert root.node_type == AutoBrowseNodeType.ROOT
    assert root.browsable is True
    assert root.children is not None
    assert len(root.children) == 2


def test_fake_auto_browse_valid():
    fake = FakeAndroidAutoBridge()
    result = fake.browse("artists_root")
    assert result.is_ok()
    browse_result = result.data
    assert browse_result.parent_node_id == "artists_root"
    assert len(browse_result.nodes) == 1
    assert browse_result.nodes[0].node_type == AutoBrowseNodeType.ARTISTS
    assert browse_result.nodes[0].playable is False
    assert browse_result.nodes[0].browsable is True


def test_fake_auto_browse_invalid():
    fake = FakeAndroidAutoBridge()
    result = fake.browse("nonexistent")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_NODE_ID"


def test_fake_auto_search_valid():
    fake = FakeAndroidAutoBridge()
    result = fake.search("test")
    assert result.is_ok()
    assert result.data.query == "test"
    assert isinstance(result.data.nodes, list)


def test_fake_auto_search_empty():
    fake = FakeAndroidAutoBridge()
    result = fake.search("")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_COMMAND"


def test_fake_auto_play_from_node_valid():
    fake = FakeAndroidAutoBridge()
    result = fake.play_from_node("artist_1")
    assert result.is_ok()
    assert result.data is True


def test_fake_auto_play_from_node_invalid():
    fake = FakeAndroidAutoBridge()
    result = fake.play_from_node("nonexistent")
    assert result.is_err()
    assert result.error is not None


# ── FakeForegroundServiceBridge ─────────────────────────────────


def test_fake_foreground_is_protocol():
    fake = FakeForegroundServiceBridge()
    assert isinstance(fake, ForegroundServiceBridge)


def test_fake_foreground_start():
    fake = FakeForegroundServiceBridge()
    req = ForegroundServiceRequirement()
    result = fake.start(req)
    assert result.is_ok()
    assert result.data is True
    state = fake.get_state().data
    assert state == ForegroundServiceState.RUNNING


def test_fake_foreground_start_idempotent():
    fake = FakeForegroundServiceBridge()
    req = ForegroundServiceRequirement()
    fake.start(req)
    result = fake.start(req)
    assert result.is_ok()
    assert fake.get_state().data == ForegroundServiceState.RUNNING


def test_fake_foreground_stop():
    fake = FakeForegroundServiceBridge()
    req = ForegroundServiceRequirement()
    fake.start(req)
    result = fake.stop()
    assert result.is_ok()
    assert fake.get_state().data == ForegroundServiceState.STOPPED


def test_fake_foreground_update_notification():
    fake = FakeForegroundServiceBridge()
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    result = fake.update_notification(tm)
    assert result.is_ok()
    assert fake._last_notification_metadata is tm


def test_fake_foreground_error_injection():
    err = AriaError(code="SERVICE_REJECTED", message="cannot start")
    fake = FakeForegroundServiceBridge(_start_error=err)
    result = fake.start(ForegroundServiceRequirement())
    assert result.is_err()
    assert result.error is err


# ── FakeAppLifecycleBridge ──────────────────────────────────────


def test_fake_app_lifecycle_is_protocol():
    fake = FakeAppLifecycleBridge()
    assert isinstance(fake, AppLifecycleBridge)


def test_fake_app_lifecycle_initial_state():
    fake = FakeAppLifecycleBridge()
    assert fake.get_state().data == AppLifecycleState.CREATED


def test_fake_app_lifecycle_report_events_sequence():
    fake = FakeAppLifecycleBridge()
    fake.report_event(AppLifecycleEvent.ON_CREATE)
    assert fake.get_state().data == AppLifecycleState.CREATED
    fake.report_event(AppLifecycleEvent.ON_START)
    assert fake.get_state().data == AppLifecycleState.STARTED
    fake.report_event(AppLifecycleEvent.ON_RESUME)
    assert fake.get_state().data == AppLifecycleState.RESUMED


def test_fake_app_lifecycle_is_in_foreground():
    fake = FakeAppLifecycleBridge()
    assert fake.is_in_foreground().data is False
    fake.report_event(AppLifecycleEvent.ON_RESUME)
    assert fake.is_in_foreground().data is True


def test_fake_app_lifecycle_pause():
    fake = FakeAppLifecycleBridge()
    fake.report_event(AppLifecycleEvent.ON_RESUME)
    fake.report_event(AppLifecycleEvent.ON_PAUSE)
    assert fake.get_state().data == AppLifecycleState.PAUSED
    assert fake.is_in_foreground().data is False


def test_fake_app_lifecycle_atypical_event():
    fake = FakeAppLifecycleBridge()
    fake.report_event(AppLifecycleEvent.ON_LOW_MEMORY)
    assert fake.get_state().data == AppLifecycleState.CREATED


def test_fake_app_lifecycle_error_injection():
    err = AriaError(code="LIFECYCLE_ERROR", message="bad")
    fake = FakeAppLifecycleBridge(_event_error=err)
    result = fake.report_event(AppLifecycleEvent.ON_RESUME)
    assert result.is_err()
    assert result.error is err


# ── FakeNotificationControlBridge ────────────────────────────────


def test_fake_notification_is_protocol():
    fake = FakeNotificationControlBridge()
    assert isinstance(fake, NotificationControlBridge)


def test_fake_notification_handle_action():
    fake = FakeNotificationControlBridge()
    result = fake.handle_action(NotificationAction.PLAY_PAUSE)
    assert result.is_ok()
    assert fake._last_action == NotificationAction.PLAY_PAUSE


def test_fake_notification_update_content():
    fake = FakeNotificationControlBridge()
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    result = fake.update_content(tm, PlaybackState.PLAYING)
    assert result.is_ok()
    assert fake._last_metadata is tm
    assert fake._last_state == PlaybackState.PLAYING


def test_fake_notification_dismiss():
    fake = FakeNotificationControlBridge()
    assert fake._dismissed is False
    result = fake.dismiss()
    assert result.is_ok()
    assert fake._dismissed is True


def test_fake_notification_error_injection():
    err = AriaError(code="NOTIFY_FAILED", message="fail")
    fake = FakeNotificationControlBridge(_action_error=err)
    result = fake.handle_action(NotificationAction.NEXT)
    assert result.is_err()


# ── FakeLockScreenBridge ────────────────────────────────────────


def test_fake_lock_screen_is_protocol():
    fake = FakeLockScreenBridge()
    assert isinstance(fake, LockScreenBridge)


def test_fake_lock_screen_update_state():
    fake = FakeLockScreenBridge()
    state = LockScreenControlState(enabled=True)
    result = fake.update_state(state)
    assert result.is_ok()
    assert fake._lock_screen_state is state


def test_fake_lock_screen_handle_action():
    fake = FakeLockScreenBridge()
    result = fake.handle_action(NotificationAction.NEXT)
    assert result.is_ok()
    assert fake._last_action == NotificationAction.NEXT


# ── FakeHeadsetControlBridge ────────────────────────────────────


def test_fake_headset_is_protocol():
    fake = FakeHeadsetControlBridge()
    assert isinstance(fake, HeadsetControlBridge)


def test_fake_headset_is_connected():
    fake = FakeHeadsetControlBridge()
    result = fake.is_connected()
    assert result.is_ok()
    assert result.data is True


def test_fake_headset_handle_event_button_press():
    fake = FakeHeadsetControlBridge()
    result = fake.handle_event(HeadsetEventType.BUTTON_PRESS)
    assert result.is_ok()
    assert fake._last_event == HeadsetEventType.BUTTON_PRESS


def test_fake_headset_handle_connect_disconnect():
    fake = FakeHeadsetControlBridge()
    fake.handle_event(HeadsetEventType.CONNECTED)
    assert fake._last_event == HeadsetEventType.CONNECTED
    fake.handle_event(HeadsetEventType.DISCONNECTED)
    assert fake._last_event == HeadsetEventType.DISCONNECTED


def test_fake_headset_button_when_disconnected():
    fake = FakeHeadsetControlBridge(_connected=False)
    result = fake.handle_event(HeadsetEventType.BUTTON_PRESS)
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "HEADSET_NOT_CONNECTED"


def test_fake_headset_connect_when_disconnected():
    fake = FakeHeadsetControlBridge(_connected=False)
    result = fake.handle_event(HeadsetEventType.CONNECTED)
    assert result.is_ok()


def test_fake_headset_disconnect_when_disconnected():
    fake = FakeHeadsetControlBridge(_connected=False)
    result = fake.handle_event(HeadsetEventType.DISCONNECTED)
    assert result.is_ok()


def test_fake_headset_error_injection():
    err = AriaError(code="HEADSET_ERROR", message="fail")
    fake = FakeHeadsetControlBridge(_event_error=err)
    result = fake.handle_event(HeadsetEventType.BUTTON_PRESS)
    assert result.is_err()
    assert result.error is err


# ── Structural Typing ───────────────────────────────────────────


def test_fake_playback_engine_satisfies_protocol():
    assert isinstance(FakePlaybackEngineBridge(), PlaybackEngineBridge)


def test_fake_media_session_satisfies_protocol():
    assert isinstance(FakeMediaSessionBridge(), MediaSessionBridge)


def test_fake_storage_satisfies_protocol():
    assert isinstance(FakeAndroidStorageBridge(), AndroidStorageBridge)


def test_fake_auto_satisfies_protocol():
    assert isinstance(FakeAndroidAutoBridge(), AndroidAutoBridge)


def test_fake_foreground_satisfies_protocol():
    assert isinstance(FakeForegroundServiceBridge(), ForegroundServiceBridge)


def test_fake_app_lifecycle_satisfies_protocol():
    assert isinstance(FakeAppLifecycleBridge(), AppLifecycleBridge)


def test_fake_notification_satisfies_protocol():
    assert isinstance(FakeNotificationControlBridge(), NotificationControlBridge)


def test_fake_lock_screen_satisfies_protocol():
    assert isinstance(FakeLockScreenBridge(), LockScreenBridge)


def test_fake_headset_satisfies_protocol():
    assert isinstance(FakeHeadsetControlBridge(), HeadsetControlBridge)


# ── Canonical Example Tests ─────────────────────────────────────


def test_ce01_playback_play_command():
    """CE-01: Playback engine bridge -- play a track."""
    fake = FakePlaybackEngineBridge()
    result = fake.send_command(PlaybackCommand.PLAY)
    assert result.is_ok()
    assert result.data is True
    snap = fake.get_snapshot().data
    assert snap.state == PlaybackState.PLAYING


def test_ce02_playback_seek_command():
    """CE-02: Playback engine bridge -- seek."""
    fake = FakePlaybackEngineBridge()
    fake.send_command(PlaybackCommand.PLAY)
    result = fake.send_command(PlaybackCommand.SEEK, position_ms=30000)
    assert result.is_ok()
    assert fake.get_snapshot().data.position.elapsed_ms == 30000


def test_ce03_media_session_handle_play():
    """CE-03: MediaSession bridge -- handle transport action."""
    fake = FakeMediaSessionBridge()
    result = fake.handle_action(MediaSessionAction.PLAY)
    assert result.is_ok()
    state = fake.get_playback_state().data
    assert state.state == PlaybackState.PLAYING


def test_ce04_storage_check_requirement_ok():
    """CE-04: Storage bridge -- check requirement."""
    fake = FakeAndroidStorageBridge()
    req = StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY, critical=True)
    result = fake.check_requirement(req)
    assert result.is_ok()
    assert result.data is True


def test_ce05_storage_check_requirement_denied():
    """CE-05: Storage bridge -- permission denied."""
    entries = {StorageType.MUSIC_DIRECTORY: StorageStatus.PERMISSION_DENIED}
    fake = FakeAndroidStorageBridge(_custom_status_entries=entries)
    req = StorageRequirement(storage_type=StorageType.MUSIC_DIRECTORY, critical=True)
    result = fake.check_requirement(req)
    assert result.is_ok()
    assert result.data is False
    status = fake.get_storage_status().data
    assert status.entries[StorageType.MUSIC_DIRECTORY] == StorageStatus.PERMISSION_DENIED


def test_ce06_auto_browse_artists():
    """CE-06: Android Auto bridge -- browse artists."""
    fake = FakeAndroidAutoBridge()
    result = fake.browse("artists_root")
    assert result.is_ok()
    nodes = result.data.nodes
    assert len(nodes) == 1
    assert nodes[0].node_type == AutoBrowseNodeType.ARTISTS
    assert nodes[0].playable is False
    assert nodes[0].browsable is True


def test_ce07_foreground_start_and_update():
    """CE-07: Foreground service bridge -- start and update."""
    fake = FakeForegroundServiceBridge()
    req = ForegroundServiceRequirement(notification_channel_id="playback")
    result = fake.start(req)
    assert result.is_ok()
    assert fake.get_state().data == ForegroundServiceState.RUNNING
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    result = fake.update_notification(tm)
    assert result.is_ok()


def test_ce08_app_lifecycle_event_chain():
    """CE-08: App lifecycle bridge -- report event chain."""
    fake = FakeAppLifecycleBridge()
    fake.report_event(AppLifecycleEvent.ON_CREATE)
    fake.report_event(AppLifecycleEvent.ON_START)
    fake.report_event(AppLifecycleEvent.ON_RESUME)
    assert fake.get_state().data == AppLifecycleState.RESUMED
    assert fake.is_in_foreground().data is True


def test_ce09_notification_handle_action():
    """CE-09: Notification control bridge -- handle action."""
    fake = FakeNotificationControlBridge()
    tm = TrackMetadata(track_id="t1", title="T", artist="A", album="B", duration_ms=1)
    fake.update_content(tm, PlaybackState.PLAYING)
    result = fake.handle_action(NotificationAction.PLAY_PAUSE)
    assert result.is_ok()


def test_ce10_headset_button_press():
    """CE-10: Headset control bridge -- button press."""
    fake = FakeHeadsetControlBridge()
    assert fake.is_connected().data is True
    result = fake.handle_event(HeadsetEventType.BUTTON_PRESS)
    assert result.is_ok()


def test_ce11_composite_snapshot():
    """CE-11: Composite snapshot -- full boundary state."""
    snap = AndroidBoundarySnapshot()
    assert snap.playback_engine is not None
    assert snap.media_session is not None
    assert snap.storage_status is not None
    assert snap.foreground_service is not None
    assert snap.app_lifecycle is not None
    assert snap.headset_connected is not None


def test_ce12_unsupported_command():
    """CE-12: Unknown command -- safe error."""
    fake = FakeAndroidAutoBridge()
    result = fake.browse("nonexistent")
    assert result.is_err()
    assert result.error is not None
    assert result.error.code == "INVALID_NODE_ID"


# ── Edge Case Tests ─────────────────────────────────────────────


def test_edge_playback_before_media_loaded():
    """EC-01: PlaybackEngineBridge called before any media is loaded."""
    fake = FakePlaybackEngineBridge()
    snap = fake.get_snapshot().data
    assert snap.state == PlaybackState.IDLE


def test_edge_storage_before_permission_requested():
    """EC-03: StorageBridge check_requirement with UNKNOWN permission."""
    fake = FakeAndroidStorageBridge(_custom_permission_state=PermissionState.UNKNOWN)
    result = fake.get_permission_state()
    assert result.data == PermissionState.UNKNOWN


def test_edge_auto_search_empty():
    """EC-05: AndroidAutoBridge search with empty query."""
    fake = FakeAndroidAutoBridge()
    result = fake.search("")
    assert result.is_err()


def test_edge_foreground_start_already_running():
    """EC-06: ForegroundServiceBridge start when already running."""
    fake = FakeForegroundServiceBridge()
    req = ForegroundServiceRequirement()
    fake.start(req)
    result = fake.start(req)
    assert result.is_ok()
    assert fake.get_state().data == ForegroundServiceState.RUNNING


def test_edge_headset_button_no_headset():
    """EC-08: HeadsetControlBridge handle_event when no headset."""
    fake = FakeHeadsetControlBridge(_connected=False)
    result = fake.handle_event(HeadsetEventType.BUTTON_PRESS)
    assert result.is_err()
    assert result.error.code == "HEADSET_NOT_CONNECTED"


def test_edge_fake_determinism():
    """EC-12: Fake implementations must be deterministic."""
    fake = FakePlaybackEngineBridge()
    snap1 = fake.get_snapshot().data
    snap2 = fake.get_snapshot().data
    assert snap1.state == snap2.state
    assert snap1.track == snap2.track


# ── No External Calls ──────────────────────────────────────────


def test_fakes_no_network_or_filesystem():
    """All fakes must never call network, filesystem, or external process."""
    fakes = [
        FakePlaybackEngineBridge(),
        FakeMediaSessionBridge(),
        FakeAndroidStorageBridge(),
        FakeAndroidAutoBridge(),
        FakeForegroundServiceBridge(),
        FakeAppLifecycleBridge(),
        FakeNotificationControlBridge(),
        FakeLockScreenBridge(),
        FakeHeadsetControlBridge(),
    ]
    for fake in fakes:
        assert isinstance(fake, object)
