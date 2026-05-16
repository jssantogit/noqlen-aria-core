"""Aria Core queue foundation models and deterministic local service."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum, auto
from hashlib import sha256
from typing import NewType

from noqlen_aria.contracts import AriaError, AriaResult
from noqlen_aria.library import LibraryItemSummary
from noqlen_aria.media_source import MediaId, MediaSourceId

QueueId = NewType("QueueId", str)
QueueItemId = NewType("QueueItemId", str)

DEFAULT_QUEUE_ID = QueueId("default-queue")


class QueueMode(Enum):
    STANDARD = auto()
    RADIO = auto()
    AUTOMATION = auto()


class QueueRepeatMode(Enum):
    OFF = auto()
    ONE = auto()
    ALL = auto()


class QueueAvailabilityState(Enum):
    AVAILABLE = auto()
    PARTIALLY_UNAVAILABLE = auto()
    UNAVAILABLE = auto()
    UNKNOWN = auto()


class QueueOperationType(Enum):
    CREATE_QUEUE = auto()
    ADD_ITEM = auto()
    REMOVE_ITEM = auto()
    CLEAR_QUEUE = auto()
    MOVE_ITEM = auto()
    SET_CURRENT_POSITION = auto()
    SET_REPEAT_MODE = auto()
    SET_SHUFFLE_STATE = auto()
    SELECT_QUEUE = auto()


@dataclass(frozen=True)
class QueueShuffleState:
    enabled: bool = False
    seed: int = 0


@dataclass(frozen=True)
class QueueItem:
    item_id: QueueItemId
    library_item: LibraryItemSummary | None = None
    media_id: MediaId | None = None
    source_id: MediaSourceId | None = None
    display_name: str = ""
    availability: QueueAvailabilityState = QueueAvailabilityState.AVAILABLE
    availability_reason: str = ""

    @classmethod
    def from_library_item(
        cls,
        item_id: QueueItemId,
        library_item: LibraryItemSummary,
        availability: QueueAvailabilityState = QueueAvailabilityState.AVAILABLE,
        availability_reason: str = "",
    ) -> QueueItem:
        return cls(
            item_id=item_id,
            library_item=library_item,
            media_id=library_item.item_id,
            source_id=library_item.source_id,
            display_name=library_item.display_name,
            availability=availability,
            availability_reason=availability_reason,
        )

    @classmethod
    def from_media_id(
        cls,
        item_id: QueueItemId,
        media_id: MediaId,
        source_id: MediaSourceId | None = None,
        display_name: str = "",
        availability: QueueAvailabilityState = QueueAvailabilityState.UNKNOWN,
        availability_reason: str = "",
    ) -> QueueItem:
        return cls(
            item_id=item_id,
            media_id=media_id,
            source_id=source_id,
            display_name=display_name,
            availability=availability,
            availability_reason=availability_reason,
        )


@dataclass(frozen=True)
class QueueState:
    queue_id: QueueId = DEFAULT_QUEUE_ID
    label: str = "Default Queue"
    mode: QueueMode = QueueMode.STANDARD
    items: tuple[QueueItem, ...] = field(default_factory=tuple)
    current_position: int | None = None
    repeat_mode: QueueRepeatMode = QueueRepeatMode.OFF
    shuffle: QueueShuffleState = field(default_factory=QueueShuffleState)
    availability: QueueAvailabilityState = QueueAvailabilityState.AVAILABLE


@dataclass(frozen=True)
class QueueCollectionState:
    queues: dict[QueueId, QueueState] = field(default_factory=dict)
    selected_queue_id: QueueId | None = None

    @property
    def selected_queue(self) -> QueueState | None:
        if self.selected_queue_id is None:
            return None
        return self.queues.get(self.selected_queue_id)


@dataclass(frozen=True)
class QueueOperation:
    operation_type: QueueOperationType
    queue_id: QueueId | None = None
    item: QueueItem | None = None
    item_id: QueueItemId | None = None
    target_index: int | None = None
    current_position: int | None = None
    repeat_mode: QueueRepeatMode | None = None
    shuffle: QueueShuffleState | None = None
    label: str = ""
    mode: QueueMode = QueueMode.STANDARD


@dataclass(frozen=True)
class QueueIntent:
    operation: QueueOperation
    reason: str = ""


@dataclass(frozen=True)
class QueueOperationResult:
    changed: bool
    queue_state: QueueState | None = None
    collection_state: QueueCollectionState | None = None
    message: str = ""


class QueueService:
    """Apply deterministic local queue transitions without playback side effects."""

    def create_queue(
        self,
        queue_id: QueueId = DEFAULT_QUEUE_ID,
        label: str = "Default Queue",
        mode: QueueMode = QueueMode.STANDARD,
    ) -> AriaResult[QueueOperationResult]:
        queue = QueueState(queue_id=queue_id, label=label, mode=mode)
        return self._ok(queue, changed=True, message="Queue created")

    def add_item(self, queue: QueueState, item: QueueItem) -> AriaResult[QueueOperationResult]:
        items = queue.items + (item,)
        current_position = 0 if queue.current_position is None and items else queue.current_position
        return self._ok(
            replace(
                queue,
                items=items,
                current_position=current_position,
                availability=self._queue_availability(items),
            ),
            changed=True,
            message="Item added",
        )

    def remove_item(self, queue: QueueState, item_id: QueueItemId) -> AriaResult[QueueOperationResult]:
        index = self._find_item_index(queue, item_id)
        if index is None:
            return self._err("QUEUE_ITEM_NOT_FOUND", f"Queue item {item_id} was not found")
        items = queue.items[:index] + queue.items[index + 1 :]
        current_position = self._current_after_remove(queue.current_position, index, len(items))
        return self._ok(
            replace(
                queue,
                items=items,
                current_position=current_position,
                availability=self._queue_availability(items),
            ),
            changed=True,
            message="Item removed",
        )

    def clear_queue(self, queue: QueueState) -> AriaResult[QueueOperationResult]:
        return self._ok(
            replace(queue, items=(), current_position=None, availability=QueueAvailabilityState.AVAILABLE),
            changed=bool(queue.items) or queue.current_position is not None,
            message="Queue cleared",
        )

    def move_item(
        self,
        queue: QueueState,
        item_id: QueueItemId,
        target_index: int,
    ) -> AriaResult[QueueOperationResult]:
        if target_index < 0 or target_index >= len(queue.items):
            return self._err("INVALID_QUEUE_INDEX", f"Queue target index {target_index} is out of bounds")
        source_index = self._find_item_index(queue, item_id)
        if source_index is None:
            return self._err("QUEUE_ITEM_NOT_FOUND", f"Queue item {item_id} was not found")

        items_list = list(queue.items)
        item = items_list.pop(source_index)
        items_list.insert(target_index, item)
        items = tuple(items_list)
        current_item_id = None
        if queue.current_position is not None and 0 <= queue.current_position < len(queue.items):
            current_item_id = queue.items[queue.current_position].item_id
        current_position = self._find_item_index_in_items(items, current_item_id) if current_item_id else None
        return self._ok(
            replace(queue, items=items, current_position=current_position),
            changed=source_index != target_index,
            message="Item moved",
        )

    def set_current_position(
        self,
        queue: QueueState,
        current_position: int,
    ) -> AriaResult[QueueOperationResult]:
        if current_position < 0 or current_position >= len(queue.items):
            return self._err("INVALID_QUEUE_POSITION", f"Queue position {current_position} is out of bounds")
        return self._ok(
            replace(queue, current_position=current_position),
            changed=queue.current_position != current_position,
            message="Current position updated",
        )

    def set_repeat_mode(
        self,
        queue: QueueState,
        repeat_mode: QueueRepeatMode,
    ) -> AriaResult[QueueOperationResult]:
        return self._ok(
            replace(queue, repeat_mode=repeat_mode),
            changed=queue.repeat_mode != repeat_mode,
            message="Repeat mode updated",
        )

    def set_shuffle_state(
        self,
        queue: QueueState,
        shuffle: QueueShuffleState,
    ) -> AriaResult[QueueOperationResult]:
        return self._ok(
            replace(queue, shuffle=shuffle),
            changed=queue.shuffle != shuffle,
            message="Shuffle state updated",
        )

    def get_ordered_items(self, queue: QueueState) -> tuple[QueueItem, ...]:
        if not queue.shuffle.enabled:
            return queue.items
        return tuple(
            sorted(
                queue.items,
                key=lambda item: self._shuffle_key(queue.shuffle.seed, item.item_id),
            )
        )

    def create_collection(self, queues: tuple[QueueState, ...]) -> AriaResult[QueueOperationResult]:
        if not queues:
            return self._err("NO_QUEUES", "At least one queue is required")
        queue_map = {queue.queue_id: queue for queue in queues}
        selected_queue_id = queues[0].queue_id
        return self._ok_collection(
            QueueCollectionState(queues=queue_map, selected_queue_id=selected_queue_id),
            changed=True,
            message="Queue collection created",
        )

    def select_queue(
        self,
        collection: QueueCollectionState,
        queue_id: QueueId,
    ) -> AriaResult[QueueOperationResult]:
        if queue_id not in collection.queues:
            return self._err("QUEUE_NOT_FOUND", f"Queue {queue_id} was not found")
        return self._ok_collection(
            replace(collection, selected_queue_id=queue_id),
            changed=collection.selected_queue_id != queue_id,
            message="Queue selected",
        )

    def add_item_to_queue(
        self,
        collection: QueueCollectionState,
        queue_id: QueueId,
        item: QueueItem,
    ) -> AriaResult[QueueOperationResult]:
        queue = collection.queues.get(queue_id)
        if queue is None:
            return self._err("QUEUE_NOT_FOUND", f"Queue {queue_id} was not found")
        result = self.add_item(queue, item)
        if result.is_err():
            return result
        assert result.data is not None and result.data.queue_state is not None
        return self._replace_collection_queue(collection, result.data.queue_state, "Item added")

    def apply_operation(
        self,
        queue: QueueState,
        operation: QueueOperation,
    ) -> AriaResult[QueueOperationResult]:
        if operation.operation_type == QueueOperationType.ADD_ITEM and operation.item is not None:
            return self.add_item(queue, operation.item)
        if operation.operation_type == QueueOperationType.REMOVE_ITEM and operation.item_id is not None:
            return self.remove_item(queue, operation.item_id)
        if operation.operation_type == QueueOperationType.CLEAR_QUEUE:
            return self.clear_queue(queue)
        if operation.operation_type == QueueOperationType.MOVE_ITEM and operation.item_id is not None and operation.target_index is not None:
            return self.move_item(queue, operation.item_id, operation.target_index)
        if operation.operation_type == QueueOperationType.SET_CURRENT_POSITION and operation.current_position is not None:
            return self.set_current_position(queue, operation.current_position)
        if operation.operation_type == QueueOperationType.SET_REPEAT_MODE and operation.repeat_mode is not None:
            return self.set_repeat_mode(queue, operation.repeat_mode)
        if operation.operation_type == QueueOperationType.SET_SHUFFLE_STATE and operation.shuffle is not None:
            return self.set_shuffle_state(queue, operation.shuffle)
        return self._err("INVALID_QUEUE_OPERATION", f"Queue operation {operation.operation_type.name} is incomplete")

    def _replace_collection_queue(
        self,
        collection: QueueCollectionState,
        queue: QueueState,
        message: str,
    ) -> AriaResult[QueueOperationResult]:
        queues = dict(collection.queues)
        queues[queue.queue_id] = queue
        return self._ok_collection(replace(collection, queues=queues), changed=True, message=message)

    def _queue_availability(self, items: tuple[QueueItem, ...]) -> QueueAvailabilityState:
        if not items:
            return QueueAvailabilityState.AVAILABLE
        unavailable_count = sum(1 for item in items if item.availability == QueueAvailabilityState.UNAVAILABLE)
        if unavailable_count == 0:
            return QueueAvailabilityState.AVAILABLE
        if unavailable_count == len(items):
            return QueueAvailabilityState.UNAVAILABLE
        return QueueAvailabilityState.PARTIALLY_UNAVAILABLE

    def _current_after_remove(self, current: int | None, removed_index: int, new_length: int) -> int | None:
        if current is None or new_length == 0:
            return None
        if removed_index < current:
            return current - 1
        if removed_index == current:
            return min(current, new_length - 1)
        return current

    def _find_item_index(self, queue: QueueState, item_id: QueueItemId) -> int | None:
        return self._find_item_index_in_items(queue.items, item_id)

    def _find_item_index_in_items(
        self,
        items: tuple[QueueItem, ...],
        item_id: QueueItemId | None,
    ) -> int | None:
        if item_id is None:
            return None
        for index, item in enumerate(items):
            if item.item_id == item_id:
                return index
        return None

    def _shuffle_key(self, seed: int, item_id: QueueItemId) -> str:
        return sha256(f"{seed}:{item_id}".encode("utf-8")).hexdigest()

    def _ok(
        self,
        queue: QueueState,
        changed: bool,
        message: str,
    ) -> AriaResult[QueueOperationResult]:
        return AriaResult(ok=True, data=QueueOperationResult(changed=changed, queue_state=queue, message=message))

    def _ok_collection(
        self,
        collection: QueueCollectionState,
        changed: bool,
        message: str,
    ) -> AriaResult[QueueOperationResult]:
        return AriaResult(
            ok=True,
            data=QueueOperationResult(changed=changed, collection_state=collection, message=message),
        )

    def _err(self, code: str, message: str) -> AriaResult[QueueOperationResult]:
        return AriaResult(ok=False, error=AriaError(code=code, message=message))


class FakeQueueScenarios:
    @staticmethod
    def empty_queue() -> QueueState:
        return QueueState()

    @staticmethod
    def three_track_queue() -> QueueState:
        service = QueueService()
        queue = QueueState()
        for index in range(3):
            result = service.add_item(
                queue,
                QueueItem.from_media_id(
                    QueueItemId(f"queue-item-{index + 1}"),
                    MediaId(f"track-{index + 1}"),
                    display_name=f"Track {index + 1}",
                    availability=QueueAvailabilityState.AVAILABLE,
                ),
            )
            assert result.data is not None and result.data.queue_state is not None
            queue = result.data.queue_state
        return queue

    @staticmethod
    def queue_with_unavailable_item() -> QueueState:
        result = QueueService().add_item(
            QueueState(),
            QueueItem.from_media_id(
                QueueItemId("queue-item-unavailable"),
                MediaId("track-unavailable"),
                display_name="Unavailable Track",
                availability=QueueAvailabilityState.UNAVAILABLE,
                availability_reason="Media unavailable from source state",
            ),
        )
        assert result.data is not None and result.data.queue_state is not None
        return result.data.queue_state


__all__ = [
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
]
