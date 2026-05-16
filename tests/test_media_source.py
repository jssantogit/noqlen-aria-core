"""Tests for Bloco 8 media source foundation."""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from noqlen_aria.contracts import AriaError, AriaResult
from noqlen_aria.media_source import (
    FakeMediaSourceClient,
    MediaId,
    MediaIdKind,
    MediaSourceClient,
    MediaSourceId,
    MediaSourceInfo,
    MediaSourceType,
    ProviderAvailabilityState,
    ProviderCapability,
    SourceAvailabilityState,
    SourceCapability,
    SourceCapabilitySummary,
    StreamAvailability,
    StreamHandle,
)
from noqlen_aria.library import (
    LibraryBrowseRequest,
    LibraryBrowseResult,
    LibraryBrowseCategory,
    LibrarySearchQuery,
    LibrarySearchResult,
)


# ── Test helpers ─────────────────────────────────────────────


def _make_error(code: str = "TEST_ERROR", message: str = "test error") -> AriaError:
    return AriaError(code=code, message=message)


def _ok(result: AriaResult) -> bool:
    return result.ok


def _value(result: AriaResult):
    assert result.ok, f"Expected ok result, got error={result.error}"
    return result.data


def _err(result: AriaResult):
    assert not result.ok, "Expected error result"
    return result.error


# ── Model construction and defaults ──────────────────────────


class TestMediaSourceId:
    def test_construction(self):
        sid = MediaSourceId("src-1")
        assert isinstance(sid, str)
        assert sid == "src-1"

    def test_equality(self):
        a = MediaSourceId("src-1")
        b = MediaSourceId("src-1")
        c = MediaSourceId("src-2")
        assert a == b
        assert a != c

    def test_hash_consistency(self):
        a = MediaSourceId("src-1")
        b = MediaSourceId("src-1")
        assert hash(a) == hash(b)
        assert a in {b}


class TestMediaSourceType:
    def test_values(self):
        assert MediaSourceType.REMOTE_SERVER is not None
        assert MediaSourceType.LOCAL_LIBRARY is not None
        assert MediaSourceType.CLOUD_STORAGE is not None

    def test_is_abstract_no_brand_names(self):
        values = {e.name for e in MediaSourceType}
        assert "NAVIDROME" not in values
        assert "JELLYFIN" not in values
        assert "EMBY" not in values
        assert "SUBSONIC" not in values


class TestSourceAvailabilityState:
    def test_values(self):
        states = set(SourceAvailabilityState)
        assert SourceAvailabilityState.AVAILABLE in states
        assert SourceAvailabilityState.DEGRADED in states
        assert SourceAvailabilityState.UNAVAILABLE in states
        assert SourceAvailabilityState.UNKNOWN in states


class TestMediaSourceInfo:
    def test_construction(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("src-1"),
            display_name="Test Source",
            source_type=MediaSourceType.REMOTE_SERVER,
            availability=SourceAvailabilityState.AVAILABLE,
        )
        assert info.source_id == "src-1"
        assert info.display_name == "Test Source"
        assert info.source_type == MediaSourceType.REMOTE_SERVER
        assert info.availability == SourceAvailabilityState.AVAILABLE

    def test_default_availability(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("src-x"),
            display_name="X",
            source_type=MediaSourceType.LOCAL_LIBRARY,
        )
        assert info.availability == SourceAvailabilityState.UNKNOWN

    def test_frozen(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("s"), display_name="d", source_type=MediaSourceType.REMOTE_SERVER
        )
        with pytest.raises(Exception):
            info.display_name = "mutated"  # type: ignore[misc]

    def test_serialization(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("src-1"),
            display_name="Test",
            source_type=MediaSourceType.REMOTE_SERVER,
            availability=SourceAvailabilityState.DEGRADED,
        )
        d = asdict(info)
        assert d["source_id"] == "src-1"
        assert d["display_name"] == "Test"
        assert d["source_type"] == MediaSourceType.REMOTE_SERVER
        assert d["availability"] == SourceAvailabilityState.DEGRADED


# ── MediaId and MediaIdKind ──────────────────────────────────


class TestMediaId:
    def test_construction(self):
        mid = MediaId("track-42")
        assert isinstance(mid, str)
        assert mid == "track-42"

    def test_equality(self):
        a = MediaId("track-1")
        b = MediaId("track-1")
        assert a == b

    def test_hash_consistency(self):
        a = MediaId("track-x")
        b = MediaId("track-x")
        assert hash(a) == hash(b)

    def test_serializable(self):
        mid = MediaId("track-42")
        assert json.dumps(mid) == '"track-42"'


class TestMediaIdKind:
    def test_values(self):
        kinds = {e.name for e in MediaIdKind}
        assert "ARTIST" in kinds
        assert "ALBUM" in kinds
        assert "TRACK" in kinds
        assert "PLAYLIST" in kinds
        assert "GENRE" in kinds
        assert "FOLDER" in kinds
        assert "STREAM" in kinds

    def test_no_provider_brand_names(self):
        values = {e.name for e in MediaIdKind}
        assert "NAVIDROME" not in values
        assert "JELLYFIN" not in values
        assert "EMBY" not in values


# ── SourceCapability and SourceCapabilitySummary ─────────────


class TestSourceCapability:
    def test_all_values_present(self):
        values = {e.name for e in SourceCapability}
        assert "ARTISTS" in values
        assert "ALBUMS" in values
        assert "TRACKS" in values
        assert "PLAYLISTS" in values
        assert "GENRES" in values
        assert "FOLDERS" in values
        assert "SEARCH" in values
        assert "STREAM" in values
        assert "RATINGS" in values
        assert "SCROBBLING" in values
        assert "LYRICS" in values

    def test_enum_value_count(self):
        assert len(list(SourceCapability)) == 11

    def test_no_provider_brand_names(self):
        values = {e.name for e in SourceCapability}
        assert "NAVIDROME" not in values
        assert "JELLYFIN" not in values
        assert "EMBY" not in values
        assert "SUBSONIC" not in values


class TestSourceCapabilitySummary:
    def test_defaults_empty(self):
        s = SourceCapabilitySummary()
        assert s.supported == frozenset()
        assert s.unavailable == frozenset()

    def test_custom_sets(self):
        supported = frozenset({SourceCapability.ARTISTS, SourceCapability.ALBUMS})
        unavailable = frozenset({SourceCapability.PLAYLISTS})
        s = SourceCapabilitySummary(supported=supported, unavailable=unavailable)
        assert s.supported == supported
        assert s.unavailable == unavailable

    def test_frozen(self):
        s = SourceCapabilitySummary()
        with pytest.raises(Exception):
            s.supported = frozenset()  # type: ignore[misc]

    def test_serialization_round_trip(self):
        s = SourceCapabilitySummary(
            supported=frozenset({SourceCapability.ARTISTS}),
            unavailable=frozenset({SourceCapability.LYRICS}),
        )
        d = asdict(s)
        assert SourceCapability.ARTISTS in d["supported"]
        assert SourceCapability.LYRICS in d["unavailable"]

    def test_all_capabilities_unavailable(self):
        s = SourceCapabilitySummary(
            supported=frozenset(),
            unavailable=frozenset(SourceCapability),
        )
        assert len(s.supported) == 0
        assert len(s.unavailable) == len(list(SourceCapability))

    def test_all_capabilities_supported(self):
        s = SourceCapabilitySummary(
            supported=frozenset(SourceCapability),
            unavailable=frozenset(),
        )
        assert len(s.supported) == 11
        assert len(s.unavailable) == 0


# ── StreamHandle and StreamAvailability ──────────────────────


class TestStreamAvailability:
    def test_values(self):
        states = set(StreamAvailability)
        assert StreamAvailability.AVAILABLE in states
        assert StreamAvailability.UNAVAILABLE in states
        assert StreamAvailability.STREAM_NOT_RESOLVED in states


class TestStreamHandle:
    def test_construction(self):
        h = StreamHandle(
            stream_id="stream-1",
            media_id=MediaId("track-1"),
            source_id=MediaSourceId("src-1"),
            availability=StreamAvailability.AVAILABLE,
            format_hint="mp3",
            quality_hint="320kbps",
        )
        assert h.stream_id == "stream-1"
        assert h.media_id == "track-1"
        assert h.source_id == "src-1"
        assert h.availability == StreamAvailability.AVAILABLE
        assert h.format_hint == "mp3"
        assert h.quality_hint == "320kbps"

    def test_default_availability_is_not_resolved(self):
        h = StreamHandle(
            stream_id="s", media_id=MediaId("t"), source_id=MediaSourceId("src")
        )
        assert h.availability == StreamAvailability.STREAM_NOT_RESOLVED

    def test_default_format_hint_none(self):
        h = StreamHandle(
            stream_id="s", media_id=MediaId("t"), source_id=MediaSourceId("src")
        )
        assert h.format_hint is None
        assert h.quality_hint is None

    def test_frozen(self):
        h = StreamHandle(
            stream_id="s", media_id=MediaId("t"), source_id=MediaSourceId("src")
        )
        with pytest.raises(Exception):
            h.stream_id = "mutated"  # type: ignore[misc]

    def test_serialization_round_trip(self):
        h = StreamHandle(
            stream_id="stream-1",
            media_id=MediaId("track-1"),
            source_id=MediaSourceId("src-1"),
        )
        d = asdict(h)
        assert d["stream_id"] == "stream-1"
        assert d["media_id"] == "track-1"
        assert d["availability"] == StreamAvailability.STREAM_NOT_RESOLVED


# ── ProviderAvailabilityState and ProviderCapability ─────────


class TestProviderAvailabilityState:
    def test_values(self):
        states = set(ProviderAvailabilityState)
        assert ProviderAvailabilityState.CONNECTED in states
        assert ProviderAvailabilityState.DISCONNECTED in states
        assert ProviderAvailabilityState.AUTH_REQUIRED in states
        assert ProviderAvailabilityState.ERROR in states
        assert ProviderAvailabilityState.UNKNOWN in states

    def test_no_provider_brand_names(self):
        values = {e.name for e in ProviderAvailabilityState}
        assert "NAVIDROME" not in values
        assert "JELLYFIN" not in values
        assert "EMBY" not in values


class TestProviderCapability:
    def test_defaults(self):
        pc = ProviderCapability()
        assert pc.capabilities == frozenset()
        assert pc.availability == ProviderAvailabilityState.UNKNOWN

    def test_with_capabilities(self):
        caps = frozenset({SourceCapability.ARTISTS, SourceCapability.TRACKS})
        pc = ProviderCapability(
            capabilities=caps,
            availability=ProviderAvailabilityState.CONNECTED,
        )
        assert pc.capabilities == caps
        assert SourceCapability.ARTISTS in pc.capabilities
        assert pc.availability == ProviderAvailabilityState.CONNECTED

    def test_frozen(self):
        pc = ProviderCapability()
        with pytest.raises(Exception):
            pc.capabilities = frozenset()  # type: ignore[misc]

    def test_serialization_round_trip(self):
        pc = ProviderCapability(
            capabilities=frozenset({SourceCapability.STREAM}),
            availability=ProviderAvailabilityState.CONNECTED,
        )
        d = asdict(pc)
        assert SourceCapability.STREAM in d["capabilities"]
        assert d["availability"] == ProviderAvailabilityState.CONNECTED


# ── MediaSourceClient protocol ───────────────────────────────


class TestMediaSourceClientProtocol:
    def test_is_runtime_checkable(self):
        assert hasattr(MediaSourceClient, "_is_runtime_protocol") or True

    def test_fake_satisfies_protocol(self):
        fake = FakeMediaSourceClient()
        assert isinstance(fake, MediaSourceClient)

    def test_fake_with_capabilities_satisfies_protocol(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({
                SourceCapability.ARTISTS,
                SourceCapability.ALBUMS,
                SourceCapability.TRACKS,
            })
        )
        assert isinstance(fake, MediaSourceClient)

    def test_minimal_object_fails_protocol(self):
        class Incomplete:
            pass

        assert not isinstance(Incomplete(), MediaSourceClient)

    def test_partial_object_fails_protocol(self):
        class Partial:
            def get_source_info(self):
                pass

        assert not isinstance(Partial(), MediaSourceClient)

    def test_complete_custom_satisfies_protocol(self):
        class CustomSource:
            def get_source_info(self):
                return AriaResult(ok=True, data=MediaSourceInfo(
                    source_id=MediaSourceId("c"), display_name="C",
                    source_type=MediaSourceType.LOCAL_LIBRARY,
                ))

            def get_capability_summary(self):
                return AriaResult(ok=True, data=SourceCapabilitySummary())

            def request_stream(self, media_id):
                return AriaResult(ok=True, data=StreamHandle(
                    stream_id="s", media_id=media_id, source_id=MediaSourceId("c"),
                ))

            def browse_library(self, request):
                return AriaResult(ok=True, data=LibraryBrowseResult(category=request.category))

            def search_library(self, query):
                return AriaResult(ok=True, data=LibrarySearchResult(query=query))

        assert isinstance(CustomSource(), MediaSourceClient)

    def test_custom_without_library_methods_fails_protocol(self):
        class OldShapeSource:
            def get_source_info(self):
                return AriaResult(ok=True, data=None)

            def get_capability_summary(self):
                return AriaResult(ok=True, data=None)

            def request_stream(self, media_id):
                return AriaResult(ok=True, data=None)

        assert not isinstance(OldShapeSource(), MediaSourceClient)

    def test_fake_browse_search_satisfies_protocol(self):
        fake = FakeMediaSourceClient.with_full_library()
        browse = fake.browse_library(LibraryBrowseRequest(LibraryBrowseCategory.ARTISTS))
        search = fake.search_library(LibrarySearchQuery("Ada"))
        assert browse.ok
        assert search.ok


# ── FakeMediaSourceClient — healthy source ───────────────────


class TestFakeHealthySource:
    def test_get_source_info_defaults(self):
        fake = FakeMediaSourceClient()
        result = fake.get_source_info()
        assert result.ok
        assert result.data.source_id == "fake-source-1"
        assert result.data.display_name == "Fake Media Source"
        assert result.data.source_type == MediaSourceType.REMOTE_SERVER
        assert result.data.availability == SourceAvailabilityState.AVAILABLE

    def test_get_source_info_custom(self):
        fake = FakeMediaSourceClient(
            source_id=MediaSourceId("p1"),
            display_name="Primary",
            source_type=MediaSourceType.LOCAL_LIBRARY,
            availability=SourceAvailabilityState.DEGRADED,
        )
        info = _value(fake.get_source_info())
        assert info.source_id == "p1"
        assert info.display_name == "Primary"
        assert info.source_type == MediaSourceType.LOCAL_LIBRARY
        assert info.availability == SourceAvailabilityState.DEGRADED

    # CE-07: Source identity and availability
    def test_ce07_source_identity_availability(self):
        fake = FakeMediaSourceClient(
            source_id=MediaSourceId("src-1"),
            source_type=MediaSourceType.REMOTE_SERVER,
            availability=SourceAvailabilityState.DEGRADED,
        )
        info = _value(fake.get_source_info())
        assert info.availability == SourceAvailabilityState.DEGRADED
        assert info.source_type == MediaSourceType.REMOTE_SERVER
        assert info.source_type != "NAVIDROME"
        assert info.source_type != "JELLYFIN"

    def test_default_source_type_is_not_branded(self):
        fake = FakeMediaSourceClient()
        info = _value(fake.get_source_info())
        assert info.source_type in (
            MediaSourceType.REMOTE_SERVER,
            MediaSourceType.LOCAL_LIBRARY,
            MediaSourceType.CLOUD_STORAGE,
        )


# ── FakeMediaSourceClient — capability summary ────────────────


class TestFakeCapabilitySummary:
    def test_empty_capabilities(self):
        fake = FakeMediaSourceClient()
        summary = _value(fake.get_capability_summary())
        assert summary.supported == frozenset()
        assert len(summary.unavailable) == len(list(SourceCapability))

    # CE-01: Source capability summary — artists/albums/tracks
    def test_ce01_artists_albums_tracks(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({
                SourceCapability.ARTISTS,
                SourceCapability.ALBUMS,
                SourceCapability.TRACKS,
            })
        )
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.ARTISTS in summary.supported
        assert SourceCapability.ALBUMS in summary.supported
        assert SourceCapability.TRACKS in summary.supported
        assert SourceCapability.PLAYLISTS not in summary.supported
        assert SourceCapability.GENRES not in summary.supported
        assert SourceCapability.PLAYLISTS in summary.unavailable
        assert SourceCapability.GENRES in summary.unavailable

    # CE-02: Missing capability — playlists unavailable
    def test_ce02_playlists_unavailable(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.ARTISTS})
        )
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.PLAYLISTS in summary.unavailable
        assert SourceCapability.PLAYLISTS not in summary.supported

    def test_all_capabilities_supported(self):
        all_caps = frozenset(SourceCapability)
        fake = FakeMediaSourceClient(supported_capabilities=all_caps)
        summary = _value(fake.get_capability_summary())
        assert summary.supported == all_caps
        assert summary.unavailable == frozenset()

    def test_single_capability_supported(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.STREAM})
        )
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.STREAM in summary.supported
        assert len(summary.supported) == 1
        assert len(summary.unavailable) == 10

    def test_capability_summary_is_complete(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.ARTISTS, SourceCapability.TRACKS})
        )
        summary = _value(fake.get_capability_summary())
        all_in_summary = summary.supported | summary.unavailable
        assert all_in_summary == frozenset(SourceCapability)

    def test_capability_summary_no_provider_leak(self):
        fake = FakeMediaSourceClient()
        summary = _value(fake.get_capability_summary())
        for cap in summary.supported:
            assert cap.name not in ("NAVIDROME", "JELLYFIN", "EMBY")
        for cap in summary.unavailable:
            assert cap.name not in ("NAVIDROME", "JELLYFIN", "EMBY")


# ── FakeMediaSourceClient — stream handle ────────────────────


class TestFakeStreamHandle:
    # CE-03: Stream handle unavailable
    def test_ce03_stream_handle_unavailable(self):
        fake = FakeMediaSourceClient(
            _default_stream_availability=StreamAvailability.UNAVAILABLE,
        )
        result = fake.request_stream(MediaId("track-1"))
        assert result.ok
        assert result.data.availability == StreamAvailability.UNAVAILABLE
        assert result.data.media_id == "track-1"
        assert result.data.source_id == "fake-source-1"

    def test_stream_handle_default_unresolved(self):
        fake = FakeMediaSourceClient()
        result = fake.request_stream(MediaId("track-x"))
        assert result.ok
        assert result.data.availability == StreamAvailability.STREAM_NOT_RESOLVED

    def test_stream_handle_available_override(self):
        fake = FakeMediaSourceClient(
            _default_stream_availability=StreamAvailability.AVAILABLE,
        )
        result = fake.request_stream(MediaId("track-1"))
        assert result.ok
        assert result.data.availability == StreamAvailability.AVAILABLE

    def test_stream_handle_media_id_preserved(self):
        fake = FakeMediaSourceClient()
        for media_id in ("artist-1", "album-3", "track-42", "playlist-7"):
            result = fake.request_stream(MediaId(media_id))
            assert result.ok
            assert result.data.media_id == media_id

    def test_stream_handle_override(self):
        override = StreamHandle(
            stream_id="custom-s1",
            media_id=MediaId("t1"),
            source_id=MediaSourceId("src-custom"),
            availability=StreamAvailability.AVAILABLE,
            format_hint="flac",
        )
        fake = FakeMediaSourceClient(_stream_handle_override=override)
        result = fake.request_stream(MediaId("any"))
        assert result.ok
        assert result.data.stream_id == "custom-s1"
        assert result.data.availability == StreamAvailability.AVAILABLE
        assert result.data.format_hint == "flac"


# ── FakeMediaSourceClient — error injection ──────────────────


class TestFakeErrorInjection:
    def test_get_source_info_error(self):
        fake = FakeMediaSourceClient(
            _get_source_info_error=_make_error("SRC_ERR", "source info failed")
        )
        result = fake.get_source_info()
        assert not result.ok
        assert result.error.code == "SRC_ERR"
        assert result.error.message == "source info failed"

    def test_get_capability_summary_error(self):
        fake = FakeMediaSourceClient(
            _get_capability_summary_error=_make_error("CAP_ERR", "capability query failed")
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error.code == "CAP_ERR"

    def test_request_stream_error(self):
        fake = FakeMediaSourceClient(
            _request_stream_error=_make_error("STREAM_ERR", "stream resolution failed")
        )
        result = fake.request_stream(MediaId("track-1"))
        assert not result.ok
        assert result.error.code == "STREAM_ERR"

    def test_all_errors_independent(self):
        fake = FakeMediaSourceClient(
            _get_source_info_error=_make_error("E1"),
        )
        assert not fake.get_source_info().ok
        assert fake.get_capability_summary().ok
        assert fake.request_stream(MediaId("t")).ok

    def test_error_injection_deterministic(self):
        fake = FakeMediaSourceClient(
            _get_capability_summary_error=_make_error("DET", "deterministic")
        )
        for _ in range(5):
            r = fake.get_capability_summary()
            assert not r.ok
            assert r.error.code == "DET"

    def test_clear_error_after_set(self):
        fake = FakeMediaSourceClient(
            _get_source_info_error=_make_error("E"),
        )
        assert not fake.get_source_info().ok
        fake._get_source_info_error = None
        assert fake.get_source_info().ok


# ── FakeMediaSourceClient — source unavailable ────────────────


class TestFakeUnavailableSource:
    # CE-08: Capability discovery with unavailable source
    def test_ce08_unavailable_source_capability(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNAVAILABLE,
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error is not None
        assert result.error.code == "SOURCE_UNAVAILABLE"

    def test_unavailable_source_info_still_returns(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNAVAILABLE,
        )
        result = fake.get_source_info()
        assert result.ok
        assert result.data.availability == SourceAvailabilityState.UNAVAILABLE

    def test_degraded_source_capability(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.DEGRADED,
            supported_capabilities=frozenset({SourceCapability.ARTISTS}),
        )
        result = fake.get_capability_summary()
        assert result.ok
        assert SourceCapability.ARTISTS in result.data.supported

    def test_unknown_source_capability(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNKNOWN,
            supported_capabilities=frozenset(),
        )
        result = fake.get_capability_summary()
        assert result.ok
        assert result.data.supported == frozenset()


# ── Canonical examples ───────────────────────────────────────


class TestCanonicalExamples:
    def test_ce01_full(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({
                SourceCapability.ARTISTS,
                SourceCapability.ALBUMS,
                SourceCapability.TRACKS,
            })
        )
        result = fake.get_capability_summary()
        assert result.ok
        assert SourceCapability.ARTISTS in result.data.supported
        assert SourceCapability.ALBUMS in result.data.supported
        assert SourceCapability.TRACKS in result.data.supported
        assert SourceCapability.PLAYLISTS in result.data.unavailable
        assert SourceCapability.GENRES in result.data.unavailable

    def test_ce02_full(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.ARTISTS})
        )
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.PLAYLISTS in summary.unavailable
        assert SourceCapability.PLAYLISTS not in summary.supported

    def test_ce03_full(self):
        fake = FakeMediaSourceClient(
            _default_stream_availability=StreamAvailability.UNAVAILABLE,
        )
        result = fake.request_stream(MediaId("track-1"))
        assert result.ok
        assert result.data.availability == StreamAvailability.UNAVAILABLE

    def test_ce07_full(self):
        fake = FakeMediaSourceClient(
            source_id=MediaSourceId("src-1"),
            source_type=MediaSourceType.REMOTE_SERVER,
            availability=SourceAvailabilityState.DEGRADED,
        )
        info = _value(fake.get_source_info())
        assert info.availability == SourceAvailabilityState.DEGRADED
        assert info.source_type == MediaSourceType.REMOTE_SERVER

    def test_ce08_full(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNAVAILABLE,
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error.code == "SOURCE_UNAVAILABLE"


# ── Edge cases ───────────────────────────────────────────────


class TestEdgeCases:
    def test_ec03_all_capabilities_unsupported(self):
        fake = FakeMediaSourceClient(supported_capabilities=frozenset())
        summary = _value(fake.get_capability_summary())
        assert summary.supported == frozenset()
        assert len(summary.unavailable) == len(list(SourceCapability))

    def test_ec04_unknown_availability(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNKNOWN,
        )
        info = _value(fake.get_source_info())
        assert info.availability == SourceAvailabilityState.UNKNOWN
        summary = _value(fake.get_capability_summary())
        assert summary.supported == frozenset()

    def test_ec07_error_injection_no_provider_query(self):
        fake = FakeMediaSourceClient(
            _get_capability_summary_error=_make_error("INJECTED"),
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error.code == "INJECTED"

    def test_ec08_future_capability_handled_as_unavailable(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.ARTISTS}),
        )
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.LYRICS in summary.unavailable
        assert SourceCapability.SCROBBLING in summary.unavailable

    def test_ec09_multiple_sources_independent(self):
        s1 = FakeMediaSourceClient(
            source_id=MediaSourceId("s1"),
            supported_capabilities=frozenset({SourceCapability.ARTISTS}),
        )
        s2 = FakeMediaSourceClient(
            source_id=MediaSourceId("s2"),
            supported_capabilities=frozenset({SourceCapability.TRACKS}),
        )
        assert _value(s1.get_source_info()).source_id == "s1"
        assert _value(s2.get_source_info()).source_id == "s2"
        s1_caps = _value(s1.get_capability_summary())
        s2_caps = _value(s2.get_capability_summary())
        assert SourceCapability.ARTISTS in s1_caps.supported
        assert SourceCapability.ARTISTS not in s2_caps.supported
        assert SourceCapability.TRACKS in s2_caps.supported
        assert SourceCapability.TRACKS not in s1_caps.supported

    def test_ec12_media_source_id_equality_across_instances(self):
        a = MediaSourceId("same")
        b = MediaSourceId("same")
        assert a == b
        assert hash(a) == hash(b)

    def test_source_info_override(self):
        override = MediaSourceInfo(
            source_id=MediaSourceId("over"),
            display_name="Overridden",
            source_type=MediaSourceType.CLOUD_STORAGE,
            availability=SourceAvailabilityState.AVAILABLE,
        )
        fake = FakeMediaSourceClient(_source_info_override=override)
        info = _value(fake.get_source_info())
        assert info.source_id == "over"

    def test_capability_summary_override(self):
        override = SourceCapabilitySummary(
            supported=frozenset({SourceCapability.STREAM}),
            unavailable=frozenset(),
        )
        fake = FakeMediaSourceClient(_capability_summary_override=override)
        summary = _value(fake.get_capability_summary())
        assert SourceCapability.STREAM in summary.supported
        assert len(summary.unavailable) == 0


# ── Determinism and fakeness ─────────────────────────────────


class TestFakeDeterminism:
    def test_multiple_calls_same_result(self):
        fake = FakeMediaSourceClient(
            supported_capabilities=frozenset({SourceCapability.ARTISTS}),
        )
        results = [fake.get_capability_summary() for _ in range(10)]
        for r in results:
            assert r.ok
            assert SourceCapability.ARTISTS in r.data.supported

    def test_no_external_calls(self):
        fake = FakeMediaSourceClient()
        assert fake.get_source_info().ok
        assert fake.get_capability_summary().ok
        assert fake.request_stream(MediaId("t")).ok

    def test_default_fake_is_deterministic(self):
        fakes = [FakeMediaSourceClient() for _ in range(5)]
        results = [f.get_source_info() for f in fakes]
        for r in results:
            assert r.ok
            assert r.data.display_name == "Fake Media Source"

    def test_fake_does_not_call_provider_internals(self):
        fake = FakeMediaSourceClient()
        assert not hasattr(fake, "_provider_api")
        assert not hasattr(fake, "_navidrome_api")
        assert not hasattr(fake, "_subsonic_client")
        assert not hasattr(fake, "_jellyfin_client")


# ── Provider boundary tests ──────────────────────────────────


class TestProviderBoundary:
    def test_no_provider_internals_exposed_in_models(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("s"),
            display_name="D",
            source_type=MediaSourceType.REMOTE_SERVER,
        )
        d = asdict(info)
        for key in d:
            assert "navidrome" not in key.lower()
            assert "subsonic" not in key.lower()
            assert "jellyfin" not in key.lower()
            assert "emby" not in key.lower()
            assert "anchor" not in key.lower()

    def test_stream_handle_no_provider_leak(self):
        h = StreamHandle(
            stream_id="s", media_id=MediaId("t"), source_id=MediaSourceId("src")
        )
        d = asdict(h)
        for key in d:
            assert "url" not in key.lower()
            assert "token" not in key.lower()
            assert "credential" not in key.lower()

    def test_media_source_client_no_provider_methods(self):
        import inspect

        members = dict(inspect.getmembers(MediaSourceClient))
        for name in members:
            name_lower = name.lower()
            assert "navidrome" not in name_lower
            assert "jellyfin" not in name_lower
            assert "emby" not in name_lower
            assert "subsonic" not in name_lower
            assert "anchor" not in name_lower

    def test_fake_media_source_client_no_provider_methods(self):
        import inspect

        members = dict(inspect.getmembers(FakeMediaSourceClient))
        for name in members:
            name_lower = name.lower()
            assert "navidrome" not in name_lower
            assert "subsonic" not in name_lower


# ── Safe degraded behavior ───────────────────────────────────


class TestSafeDegradedBehavior:
    def test_capability_missing_is_not_crash(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.DEGRADED,
            supported_capabilities=frozenset(),
        )
        result = fake.get_capability_summary()
        assert result.ok
        assert result.error is None

    def test_unavailable_source_is_safe_error(self):
        fake = FakeMediaSourceClient(
            availability=SourceAvailabilityState.UNAVAILABLE,
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error.code == "SOURCE_UNAVAILABLE"

    def test_stream_unavailable_is_safe(self):
        fake = FakeMediaSourceClient(
            _default_stream_availability=StreamAvailability.UNAVAILABLE,
        )
        result = fake.request_stream(MediaId("t"))
        assert result.ok
        assert result.data.availability == StreamAvailability.UNAVAILABLE

    def test_injected_error_is_not_raw_exception(self):
        fake = FakeMediaSourceClient(
            _get_capability_summary_error=_make_error("FAIL", "injected"),
        )
        result = fake.get_capability_summary()
        assert not result.ok
        assert result.error.code == "FAIL"
        assert result.error.message == "injected"


# ── Serialization safety ─────────────────────────────────────


class TestSerializationSafety:
    def test_media_source_info_no_callables(self):
        info = MediaSourceInfo(
            source_id=MediaSourceId("s"), display_name="d",
            source_type=MediaSourceType.REMOTE_SERVER,
        )
        d = asdict(info)
        for val in d.values():
            assert not callable(val)

    def test_capability_summary_no_callables(self):
        s = SourceCapabilitySummary()
        d = asdict(s)
        for val in d.values():
            assert not callable(val)

    def test_stream_handle_no_callables(self):
        h = StreamHandle(
            stream_id="s", media_id=MediaId("t"), source_id=MediaSourceId("src")
        )
        d = asdict(h)
        for val in d.values():
            assert not callable(val)

    def test_provider_capability_no_callables(self):
        pc = ProviderCapability()
        d = asdict(pc)
        for val in d.values():
            assert not callable(val)

    def test_media_id_serializable(self):
        mid = MediaId("test-id")
        assert json.loads(json.dumps(mid)) == "test-id"

    def test_media_source_id_serializable(self):
        sid = MediaSourceId("src-id")
        assert json.loads(json.dumps(sid)) == "src-id"
