"""Tests for Bloco 15 internet radio foundation."""

from __future__ import annotations

from dataclasses import asdict
import inspect
import json

import noqlen_aria.internet_radio as radio
from noqlen_aria.contracts import AriaResult, safe_serialize
from noqlen_aria.internet_radio import (
    FakeRadioScenarios,
    IcyMetadataState,
    InternetRadioService,
    ManualRadioStationInput,
    RadioArtworkState,
    RadioDirectoryRef,
    RadioFavoriteState,
    RadioImportSource,
    RadioMetadataState,
    RadioPlaybackAvailability,
    RadioSourceCapability,
    RadioStationId,
    RadioStationRef,
    RadioStationSummary,
    RadioStreamHandle,
    RadioStreamKind,
    RadioUnavailableReason,
    RadioValidationIssue,
)


def _data(result: AriaResult):
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def _err(result: AriaResult):
    assert result.is_err()
    assert result.error is not None
    return result.error


_service = InternetRadioService()


def test_radio_station_id_identity_and_hash() -> None:
    a = RadioStationId("station-1")
    b = RadioStationId("station-1")
    c = RadioStationId("station-2")
    assert isinstance(a, str)
    assert a == b
    assert a != c
    assert hash(a) == hash(b)


def test_radio_station_ref_preserves_directory_reference() -> None:
    directory = RadioDirectoryRef("dir-1", "Directory")
    ref = RadioStationRef(RadioStationId("s1"), "Station", directory=directory, source_label="manual")
    assert ref.station_id == "s1"
    assert ref.directory == directory
    assert ref.source_label == "manual"


def test_radio_station_summary_as_ref_is_app_facing() -> None:
    summary = FakeRadioScenarios.valid_manual_station()
    ref = summary.as_ref()
    assert ref.station_id == summary.station_id
    assert ref.display_name == summary.display_name
    assert ref.__class__.__module__ == "noqlen_aria.internet_radio"


def test_model_defaults_are_safe() -> None:
    favorite = RadioFavoriteState()
    metadata = RadioMetadataState()
    artwork = RadioArtworkState()
    availability = RadioPlaybackAvailability()
    assert not favorite.is_favorite
    assert favorite.future_intent_only
    assert metadata.is_live
    assert artwork.artwork_uri == ""
    assert not availability.available
    assert availability.reason == RadioUnavailableReason.PLAYBACK_NOT_CONFIGURED


def test_models_safe_serialize_to_json_data() -> None:
    summary = FakeRadioScenarios.valid_manual_station()
    serialized = safe_serialize(summary)
    assert serialized["station_id"] == "radio.example.test-live.mp3"
    assert serialized["stream"]["declared_uri"] == "https://radio.example.test/live.mp3"
    json.dumps(serialized)


def test_public_module_exports_are_intentional() -> None:
    expected = {
        "FakeRadioScenarios",
        "IcyMetadataState",
        "InternetRadioService",
        "ManualRadioStationInput",
        "RadioArtworkState",
        "RadioDirectoryRef",
        "RadioFavoriteState",
        "RadioImportSource",
        "RadioMetadataState",
        "RadioPlaybackAvailability",
        "RadioSourceCapability",
        "RadioStationId",
        "RadioStationRef",
        "RadioStationSummary",
        "RadioStreamHandle",
        "RadioStreamKind",
        "RadioUnavailableReason",
        "RadioValidationIssue",
    }
    assert set(radio.__all__) == expected


def test_valid_manual_station_validation_returns_summary_without_network() -> None:
    summary, issues = _data(_service.validate_manual_station_input(ManualRadioStationInput(
        display_name=" Local Radio ",
        stream_url=" https://example.test/radio.mp3 ",
        stream_kind=RadioStreamKind.MP3,
    )))
    assert issues == ()
    assert summary.display_name == "Local Radio"
    assert summary.import_source == RadioImportSource.MANUAL
    assert summary.playback_availability.available
    assert summary.stream.declared_uri == "https://example.test/radio.mp3"


def test_invalid_manual_station_url_returns_issue_and_no_streaming() -> None:
    result = _service.validate_manual_station_input(ManualRadioStationInput(
        display_name="Broken",
        stream_url="not a stream",
        stream_kind=RadioStreamKind.MP3,
    ))
    error = _err(result)
    assert error.code == "INVALID_RADIO_STATION"
    summary, issues = result.data
    assert RadioValidationIssue.UNSUPPORTED_URL_SCHEME in issues
    assert RadioValidationIssue.MALFORMED_URL in issues
    assert summary.playback_availability.reason == RadioUnavailableReason.VALIDATION_FAILED


def test_manual_station_empty_name_is_invalid() -> None:
    result = _service.validate_manual_station_input(ManualRadioStationInput(
        display_name=" ",
        stream_url="https://example.test/radio.mp3",
        stream_kind=RadioStreamKind.MP3,
    ))
    assert RadioValidationIssue.EMPTY_NAME in result.data[1]


def test_manual_station_missing_url_is_invalid() -> None:
    result = _service.validate_manual_station_input(ManualRadioStationInput(
        display_name="Missing URL",
        stream_url=" ",
        stream_kind=RadioStreamKind.MP3,
    ))
    assert RadioValidationIssue.MISSING_STREAM_URL in result.data[1]


def test_manual_station_unsupported_scheme_is_invalid() -> None:
    result = _service.validate_manual_station_input(ManualRadioStationInput(
        display_name="File Radio",
        stream_url="file:///music/radio.mp3",
        stream_kind=RadioStreamKind.MP3,
    ))
    assert RadioValidationIssue.UNSUPPORTED_URL_SCHEME in result.data[1]


def test_manual_station_unsupported_kind_is_invalid() -> None:
    result = _service.validate_manual_station_input(ManualRadioStationInput(
        display_name="HLS Radio",
        stream_url="https://example.test/live.m3u8",
        stream_kind=RadioStreamKind.HLS,
    ))
    assert RadioValidationIssue.UNSUPPORTED_STREAM_KIND in result.data[1]


def test_stream_handle_is_abstract_data_only() -> None:
    handle = _data(_service.build_stream_handle(
        RadioStationId("s1"),
        "https://example.test/live.mp3",
        RadioStreamKind.MP3,
    ))
    assert handle == RadioStreamHandle(
        handle_id="radio-stream-s1",
        station_id=RadioStationId("s1"),
        stream_kind=RadioStreamKind.MP3,
        declared_uri="https://example.test/live.mp3",
        label="Declared radio stream handle",
        format_hint="mp3",
    )
    assert not hasattr(handle, "session")
    assert not hasattr(handle, "play")


def test_supported_stream_kind_available() -> None:
    for kind in (RadioStreamKind.MP3, RadioStreamKind.AAC, RadioStreamKind.OGG, RadioStreamKind.OPUS):
        availability = _data(_service.evaluate_playback_availability(
            stream_kind=kind,
            stream_url="https://example.test/live",
        ))
        assert availability.available
        assert availability.reason == RadioUnavailableReason.NONE


def test_unsupported_stream_kind_returns_unavailable_safe_reason() -> None:
    for kind in (RadioStreamKind.HLS, RadioStreamKind.DASH, RadioStreamKind.SHOUTCAST, RadioStreamKind.UNKNOWN):
        availability = _data(_service.evaluate_playback_availability(
            stream_kind=kind,
            stream_url="https://example.test/live",
        ))
        assert not availability.available
        assert availability.reason == RadioUnavailableReason.UNSUPPORTED_STREAM_KIND


def test_playback_availability_source_unavailable() -> None:
    availability = _data(_service.evaluate_playback_availability(
        stream_kind=RadioStreamKind.MP3,
        stream_url="https://example.test/live.mp3",
        source_available=False,
    ))
    assert availability.reason == RadioUnavailableReason.SOURCE_UNAVAILABLE


def test_playback_availability_station_unavailable() -> None:
    availability = _data(_service.evaluate_playback_availability(
        stream_kind=RadioStreamKind.MP3,
        stream_url="https://example.test/live.mp3",
        station_available=False,
    ))
    assert availability.reason == RadioUnavailableReason.STATION_UNAVAILABLE


def test_playback_availability_missing_stream() -> None:
    availability = _data(_service.evaluate_playback_availability(stream_kind=RadioStreamKind.MP3))
    assert availability.reason == RadioUnavailableReason.STREAM_MISSING


def test_playback_availability_missing_capability() -> None:
    availability = _data(_service.evaluate_playback_availability(
        stream_kind=RadioStreamKind.MP3,
        stream_url="https://example.test/live.mp3",
        capabilities=frozenset(),
    ))
    assert availability.reason == RadioUnavailableReason.SOURCE_UNAVAILABLE


def test_degraded_radio_preserves_warnings() -> None:
    summary = FakeRadioScenarios.degraded_station_with_warnings()
    assert summary.playback_availability.available
    assert summary.playback_availability.degraded
    assert summary.playback_availability.warnings[0].code == "RADIO_DEGRADED"


def test_unavailable_radio_scenario_is_safe() -> None:
    summary = FakeRadioScenarios.unavailable_station()
    assert not summary.playback_availability.available
    assert summary.playback_availability.reason == RadioUnavailableReason.STATION_UNAVAILABLE


def test_icy_metadata_state_is_data_only() -> None:
    icy = _data(_service.build_icy_metadata_state(
        stream_title="Artist - Title",
        icy_name="Station",
        icy_genre="Jazz",
        icy_url="https://example.test",
        bitrate_kbps=128,
        metadata_interval=16000,
    ))
    assert icy.stream_title == "Artist - Title"
    assert icy.bitrate_kbps == 128
    assert not hasattr(icy, "read")
    assert not hasattr(icy, "parse")


def test_icy_metadata_rejects_negative_values() -> None:
    assert _service.build_icy_metadata_state(bitrate_kbps=-1).is_err()
    assert _service.build_icy_metadata_state(metadata_interval=-1).is_err()


def test_radio_metadata_state_embeds_icy_as_optional_data() -> None:
    icy = IcyMetadataState(stream_title="Artist - Title")
    metadata = _data(_service.build_metadata_state(title="Title", artist="Artist", icy=icy))
    assert metadata.title == "Title"
    assert metadata.artist == "Artist"
    assert metadata.icy == icy


def test_artwork_metadata_state_is_optional_data_only() -> None:
    artwork = _data(_service.build_artwork_state(
        artwork_uri="https://example.test/art.jpg",
        thumbnail_uri="https://example.test/thumb.jpg",
        alt_text="Station art",
    ))
    summary = _data(_service.build_station_summary(
        station_id=RadioStationId("art"),
        display_name="Art Radio",
        stream_url="https://example.test/live.mp3",
        stream_kind=RadioStreamKind.MP3,
        artwork=artwork,
    ))
    assert summary.artwork == artwork
    assert summary.artwork.artwork_uri == "https://example.test/art.jpg"


def test_favorite_read_state_is_read_only_future_intent() -> None:
    favorite = _data(_service.build_favorite_state(is_favorite=True, source_supports_read=True))
    assert favorite.is_favorite
    assert favorite.source_supports_read
    assert not favorite.mutation_supported
    assert favorite.future_intent_only
    assert favorite.unavailable_reason == RadioUnavailableReason.FAVORITE_MUTATION_UNSUPPORTED


def test_favorite_mutation_preview_is_blocked() -> None:
    state = _data(_service.preview_favorite_mutation(RadioStationRef(RadioStationId("s1"), "Station")))
    assert not state.mutation_supported
    assert state.future_intent_only
    assert state.unavailable_reason == RadioUnavailableReason.FAVORITE_MUTATION_UNSUPPORTED


def test_favorite_mutation_preview_requires_station_id() -> None:
    result = _service.preview_favorite_mutation(RadioStationRef(RadioStationId(""), "Station"))
    assert result.is_err()
    assert result.error.code == "RADIO_STATION_ID_REQUIRED"


def test_station_summary_requires_id_and_display_name() -> None:
    assert _service.build_station_summary(
        station_id=RadioStationId(""),
        display_name="Station",
        stream_url="https://example.test/live.mp3",
        stream_kind=RadioStreamKind.MP3,
    ).is_err()
    assert _service.build_station_summary(
        station_id=RadioStationId("s1"),
        display_name=" ",
        stream_url="https://example.test/live.mp3",
        stream_kind=RadioStreamKind.MP3,
    ).is_err()


def test_directory_and_import_references_are_data_only() -> None:
    directory = RadioDirectoryRef("public-dir", "Public Directory", homepage_hint="https://example.test")
    summary = _data(_service.build_station_summary(
        station_id=RadioStationId("dir-station"),
        display_name="Directory Radio",
        stream_url="https://example.test/live.mp3",
        stream_kind=RadioStreamKind.MP3,
        import_source=RadioImportSource.DIRECTORY,
        directory=directory,
    ))
    assert summary.directory == directory
    assert summary.import_source == RadioImportSource.DIRECTORY


def test_fake_valid_manual_station_is_deterministic() -> None:
    assert FakeRadioScenarios.valid_manual_station() == FakeRadioScenarios.valid_manual_station()


def test_fake_invalid_manual_station_url_is_deterministic() -> None:
    r1 = FakeRadioScenarios.invalid_manual_station_url()
    r2 = FakeRadioScenarios.invalid_manual_station_url()
    assert r1 == r2
    assert r1.is_err()


def test_fake_station_with_icy_metadata() -> None:
    summary = FakeRadioScenarios.station_with_icy_metadata()
    assert summary.metadata.icy is not None
    assert summary.metadata.icy.stream_title == "Example Artist - Example Track"


def test_fake_station_with_artwork_metadata() -> None:
    summary = FakeRadioScenarios.station_with_artwork_metadata()
    assert summary.artwork is not None
    assert summary.artwork.thumbnail_uri.endswith("thumb.jpg")


def test_fake_unsupported_stream_kind() -> None:
    summary = FakeRadioScenarios.unsupported_stream_kind()
    assert summary.stream.stream_kind == RadioStreamKind.HLS
    assert summary.playback_availability.reason == RadioUnavailableReason.UNSUPPORTED_STREAM_KIND


def test_fake_favorite_states() -> None:
    read = FakeRadioScenarios.favorite_read_state()
    mutation = FakeRadioScenarios.favorite_mutation_unsupported()
    assert read.is_favorite
    assert mutation.future_intent_only
    assert not mutation.mutation_supported


def test_ui_consumes_radio_core_models_only() -> None:
    summary = FakeRadioScenarios.valid_manual_station()
    assert summary.__class__.__module__ == "noqlen_aria.internet_radio"
    assert summary.stream.__class__.__module__ == "noqlen_aria.internet_radio"
    assert summary.favorite.__class__.__module__ == "noqlen_aria.internet_radio"


def test_summary_no_provider_or_playback_session_fields() -> None:
    summary = FakeRadioScenarios.valid_manual_station()
    fields = set(asdict(summary)) | set(asdict(summary.stream))
    for field_name in fields:
        lowered = field_name.lower()
        assert "backend" not in lowered
        assert "session" not in lowered
        assert "token" not in lowered
        assert "credential" not in lowered


def test_internet_radio_service_has_no_streaming_or_playback_methods() -> None:
    members = dict(inspect.getmembers(InternetRadioService))
    forbidden = (
        "open",
        "connect",
        "download",
        "start_playback",
        "execute_playback",
        "pause_playback",
        "seek_to",
        "resolve_session",
        "provider_client",
        "android",
    )
    for name in members:
        assert all(term not in name.lower() for term in forbidden)


def test_module_source_has_no_network_filesystem_provider_playback_dependencies() -> None:
    source = inspect.getsource(radio)
    forbidden = (
        "requests.",
        "httpx.",
        "aiohttp.",
        "urllib.",
        "socket.",
        "os.walk",
        "glob.glob",
        "iterdir",
        "scandir",
        "subprocess",
        "NavidromeProvider",
        "Jellyfin",
        "Emby",
        "noqlen_anchor.cli",
        "Media3",
        "ExoPlayer",
        "Activity",
        "Fragment",
        "Compose",
        "Kotlin",
        "Gradle",
        "Transcode",
        "StreamQuality",
        "BitPerfect",
        "UsbDac",
        "SmartPlaylist",
    )
    for term in forbidden:
        assert term not in source, f"Found forbidden dependency/reference: {term}"


def test_service_methods_return_aria_result() -> None:
    assert isinstance(_service.build_metadata_state(title="x"), AriaResult)
    assert isinstance(_service.evaluate_playback_availability(stream_kind=RadioStreamKind.MP3), AriaResult)


def test_all_dataclass_models_are_frozen() -> None:
    classes = [v for v in vars(radio).values() if inspect.isclass(v) and hasattr(v, "__dataclass_fields__")]
    for cls in classes:
        assert cls.__dataclass_params__.frozen, f"{cls.__name__} is not frozen"
