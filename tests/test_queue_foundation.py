"""Tests for Bloco 11 queue foundation."""

from __future__ import annotations

from dataclasses import asdict

import inspect
import json

import noqlen_aria.queue as queue
from noqlen_aria.contracts import safe_serialize
from noqlen_aria.library import LibraryItemSummary
from noqlen_aria.media_source import MediaId, MediaIdKind, MediaSourceId
from noqlen_aria.queue import (
    DEFAULT_QUEUE_ID,
    FakeQueueScenarios,
    QueueAvailabilityState,
    QueueId,
    QueueItem,
    QueueItemId,
    QueueMode,
    QueueOperation,
    QueueOperationType,
    QueueRepeatMode,
    QueueService,
    QueueShuffleState,
    QueueState,
)


def _track_summary(track_id: str = "track-1", name: str = "First Difference") -> LibraryItemSummary:
    return LibraryItemSummary(
        source_id=MediaSourceId("fake-source-1"),
        item_id=MediaId(track_id),
        item_kind=MediaIdKind.TRACK,
        display_name=name,
        subtitle="Ada Quartet",
    )


def _queue_item(item_id: str, track_id: str | None = None, name: str | None = None) -> QueueItem:
    index = item_id.rsplit("-", 1)[-1]
    return QueueItem.from_library_item(
        QueueItemId(item_id),
        _track_summary(track_id or f"track-{index}", name or f"Track {index}"),
    )


def _data(result):
    assert result.ok, result.error
    assert result.data is not None
    return result.data


def test_empty_queue_defaults_are_safe_and_app_facing() -> None:
    state = QueueState()

    assert state.queue_id == DEFAULT_QUEUE_ID
    assert state.items == ()
    assert state.current_position is None
    assert state.repeat_mode == QueueRepeatMode.OFF
    assert state.shuffle == QueueShuffleState()
    assert state.availability == QueueAvailabilityState.AVAILABLE
    json.dumps(safe_serialize(state))


def test_create_queue_returns_queue_state_contract() -> None:
    result = QueueService().create_queue(QueueId("queue-a"), label="Queue A", mode=QueueMode.RADIO)

    data = _data(result)
    assert data.changed is True
    assert data.queue_state.queue_id == "queue-a"
    assert data.queue_state.label == "Queue A"
    assert data.queue_state.mode == QueueMode.RADIO


def test_add_track_summary_to_empty_queue_creates_app_facing_queue_item() -> None:
    item = QueueItem.from_library_item(QueueItemId("queue-item-1"), _track_summary())

    result = QueueService().add_item(QueueState(), item)

    state = _data(result).queue_state
    assert state.items == (item,)
    assert state.items[0].library_item == _track_summary()
    assert state.items[0].media_id == "track-1"
    assert state.items[0].display_name == "First Difference"
    assert state.current_position == 0


def test_remove_item_updates_current_position_deterministically() -> None:
    service = QueueService()
    state = FakeQueueScenarios.three_track_queue()
    state = _data(service.set_current_position(state, 2)).queue_state

    result = service.remove_item(state, QueueItemId("queue-item-1"))

    updated = _data(result).queue_state
    assert [item.item_id for item in updated.items] == ["queue-item-2", "queue-item-3"]
    assert updated.current_position == 1


def test_remove_current_item_keeps_current_position_valid() -> None:
    service = QueueService()
    state = _data(service.set_current_position(FakeQueueScenarios.three_track_queue(), 1)).queue_state

    updated = _data(service.remove_item(state, QueueItemId("queue-item-2"))).queue_state

    assert [item.item_id for item in updated.items] == ["queue-item-1", "queue-item-3"]
    assert updated.current_position == 1


def test_remove_last_item_resets_current_position() -> None:
    service = QueueService()
    state = _data(service.add_item(QueueState(), _queue_item("queue-item-1"))).queue_state

    updated = _data(service.remove_item(state, QueueItemId("queue-item-1"))).queue_state

    assert updated.items == ()
    assert updated.current_position is None
    assert updated.availability == QueueAvailabilityState.AVAILABLE


def test_clear_queue_preserves_identity_and_settings() -> None:
    service = QueueService()
    state = FakeQueueScenarios.three_track_queue()
    state = _data(service.set_repeat_mode(state, QueueRepeatMode.ALL)).queue_state
    state = _data(service.set_shuffle_state(state, QueueShuffleState(enabled=True, seed=7))).queue_state

    cleared = _data(service.clear_queue(state)).queue_state
    assert cleared.queue_id == state.queue_id
    assert cleared.items == ()
    assert cleared.current_position is None
    assert cleared.repeat_mode == QueueRepeatMode.ALL
    assert cleared.shuffle == QueueShuffleState(enabled=True, seed=7)


def test_move_item_order_is_deterministic_and_current_position_remains_valid() -> None:
    service = QueueService()
    state = _data(service.set_current_position(FakeQueueScenarios.three_track_queue(), 1)).queue_state

    moved = _data(service.move_item(state, QueueItemId("queue-item-3"), 0)).queue_state
    assert [item.item_id for item in moved.items] == ["queue-item-3", "queue-item-1", "queue-item-2"]
    assert moved.current_position == 2


def test_invalid_remove_and_reorder_return_safe_errors_without_mutating_state() -> None:
    service = QueueService()
    state = FakeQueueScenarios.three_track_queue()

    missing_remove = service.remove_item(state, QueueItemId("missing"))
    invalid_move = service.move_item(state, QueueItemId("queue-item-1"), 99)
    missing_move = service.move_item(state, QueueItemId("missing"), 0)

    assert missing_remove.is_err()
    assert missing_remove.error.code == "QUEUE_ITEM_NOT_FOUND"
    assert invalid_move.is_err()
    assert invalid_move.error.code == "INVALID_QUEUE_INDEX"
    assert missing_move.is_err()
    assert missing_move.error.code == "QUEUE_ITEM_NOT_FOUND"
    assert state == FakeQueueScenarios.three_track_queue()


def test_current_position_bounds_are_safe() -> None:
    service = QueueService()
    state = FakeQueueScenarios.three_track_queue()

    valid = service.set_current_position(state, 2)
    low = service.set_current_position(state, -1)
    high = service.set_current_position(state, 3)
    empty = service.set_current_position(QueueState(), 0)

    assert _data(valid).queue_state.current_position == 2
    assert low.is_err() and low.error.code == "INVALID_QUEUE_POSITION"
    assert high.is_err() and high.error.code == "INVALID_QUEUE_POSITION"
    assert empty.is_err() and empty.error.code == "INVALID_QUEUE_POSITION"


def test_repeat_one_serializes_explicitly_without_playback() -> None:
    state = _data(QueueService().set_repeat_mode(QueueState(), QueueRepeatMode.ONE)).queue_state

    serialized = safe_serialize(state)
    assert serialized["repeat_mode"] == "ONE"
    assert "play" not in serialized
    json.dumps(serialized)


def test_repeat_modes_are_explicit() -> None:
    service = QueueService()
    state = QueueState()

    for mode in QueueRepeatMode:
        result = service.set_repeat_mode(state, mode)
        assert _data(result).queue_state.repeat_mode == mode


def test_shuffle_order_is_deterministic_when_enabled() -> None:
    service = QueueService()
    state = _data(service.set_shuffle_state(FakeQueueScenarios.three_track_queue(), QueueShuffleState(True, seed=42))).queue_state

    first = service.get_ordered_items(state)
    second = service.get_ordered_items(state)

    assert [item.item_id for item in first] == [item.item_id for item in second]
    assert set(first) == set(state.items)
    assert service.get_ordered_items(FakeQueueScenarios.three_track_queue()) == FakeQueueScenarios.three_track_queue().items


def test_unavailable_item_state_is_preserved_without_stream_resolution() -> None:
    unavailable = QueueItem.from_library_item(
        QueueItemId("queue-item-unavailable"),
        _track_summary("track-unavailable", "Missing Track"),
        availability=QueueAvailabilityState.UNAVAILABLE,
        availability_reason="Source reports unavailable",
    )

    state = _data(QueueService().add_item(QueueState(), unavailable)).queue_state

    assert state.items[0].availability == QueueAvailabilityState.UNAVAILABLE
    assert state.items[0].availability_reason == "Source reports unavailable"
    assert state.availability == QueueAvailabilityState.UNAVAILABLE
    assert not hasattr(QueueService, "request_stream")


def test_partially_unavailable_queue_reports_safe_availability() -> None:
    service = QueueService()
    state = _data(service.add_item(QueueState(), _queue_item("queue-item-1"))).queue_state
    unavailable = QueueItem.from_media_id(
        QueueItemId("queue-item-2"),
        MediaId("track-2"),
        availability=QueueAvailabilityState.UNAVAILABLE,
    )

    state = _data(service.add_item(state, unavailable)).queue_state
    assert state.availability == QueueAvailabilityState.PARTIALLY_UNAVAILABLE


def test_multiple_queues_can_be_selected_and_only_target_queue_changes() -> None:
    service = QueueService()
    queue_a = QueueState(queue_id=QueueId("queue-a"), label="A")
    queue_b = QueueState(queue_id=QueueId("queue-b"), label="B")
    collection = _data(service.create_collection((queue_a, queue_b))).collection_state

    selected = _data(service.select_queue(collection, QueueId("queue-b"))).collection_state
    changed = _data(service.add_item_to_queue(selected, QueueId("queue-b"), _queue_item("queue-item-1"))).collection_state

    assert selected.selected_queue_id == "queue-b"
    assert changed.queues[QueueId("queue-a")].items == ()
    assert [item.item_id for item in changed.queues[QueueId("queue-b")].items] == ["queue-item-1"]


def test_invalid_multiple_queue_operations_return_safe_errors() -> None:
    service = QueueService()
    collection = _data(service.create_collection((QueueState(queue_id=QueueId("queue-a")),))).collection_state

    empty = service.create_collection(())
    select_missing = service.select_queue(collection, QueueId("missing"))
    add_missing = service.add_item_to_queue(collection, QueueId("missing"), _queue_item("queue-item-1"))

    assert empty.is_err() and empty.error.code == "NO_QUEUES"
    assert select_missing.is_err() and select_missing.error.code == "QUEUE_NOT_FOUND"
    assert add_missing.is_err() and add_missing.error.code == "QUEUE_NOT_FOUND"
    assert collection.queues[QueueId("queue-a")].items == ()


def test_apply_operation_supports_intent_models_and_invalid_payloads() -> None:
    service = QueueService()
    item = _queue_item("queue-item-1")
    add_operation = QueueOperation(QueueOperationType.ADD_ITEM, item=item)
    invalid_operation = QueueOperation(QueueOperationType.ADD_ITEM)

    added = service.apply_operation(QueueState(), add_operation)
    invalid = service.apply_operation(QueueState(), invalid_operation)

    assert len(_data(added).queue_state.items) == 1
    assert invalid.is_err()
    assert invalid.error.code == "INVALID_QUEUE_OPERATION"


def test_fake_queue_scenarios_are_deterministic() -> None:
    first = FakeQueueScenarios.three_track_queue()
    second = FakeQueueScenarios.three_track_queue()
    unavailable = FakeQueueScenarios.queue_with_unavailable_item()

    assert first == second
    assert [item.item_id for item in first.items] == ["queue-item-1", "queue-item-2", "queue-item-3"]
    assert unavailable.availability == QueueAvailabilityState.UNAVAILABLE


def test_queue_models_do_not_expose_provider_internals() -> None:
    model = QueueItem.from_library_item(QueueItemId("queue-item-1"), _track_summary())
    names = set(asdict(model))

    for key in names:
        lowered = key.lower()
        assert "navidrome" not in lowered
        assert "jellyfin" not in lowered
        assert "emby" not in lowered
        assert "anchor" not in lowered


def test_queue_service_has_no_provider_network_filesystem_or_playback_dependency() -> None:
    members = dict(inspect.getmembers(QueueService))
    forbidden = (
        "provider",
        "media_source",
        "request_stream",
        "stream",
        "requests",
        "httpx",
        "aiohttp",
        "socket",
        "walk",
        "sc" + "andir",
        "playback",
        "now_playing",
        "offline",
        "cache",
        "smart_playlist",
    )

    for name in members:
        assert all(term not in name.lower() for term in forbidden)


def test_ui_consumes_queue_data_from_aria_core_models_only() -> None:
    state = _data(QueueService().add_item(QueueState(), _queue_item("queue-item-1"))).queue_state

    assert state.__class__.__module__ == "noqlen_aria.queue"
    assert state.items[0].__class__.__module__ == "noqlen_aria.queue"
    assert state.items[0].library_item.__class__.__module__ == "noqlen_aria.library"


def test_queue_module_exports_bloco_11_names_intentionally() -> None:
    expected = {
        "DEFAULT_QUEUE_ID",
        "FakeQueueScenarios",
        "QueueAvailabilityState",
        "QueueCollectionState",
        "QueueId",
        "QueueIntent",
        "QueueItem",
        "QueueItemId",
        "QueueMode",
        "QueueOperation",
        "QueueOperationResult",
        "QueueOperationType",
        "QueueRepeatMode",
        "QueueService",
        "QueueShuffleState",
        "QueueState",
    }

    assert set(queue.__all__) == expected
