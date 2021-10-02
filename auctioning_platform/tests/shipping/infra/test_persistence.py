from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from injector import Injector
from retrying import retry

from itca.event_sourcing import EventStore
from itca.shipping.domain.aggregates.order import AlreadyPaid, Order


def test_write_then_read(event_store: EventStore) -> None:
    uuid = uuid4()
    order = Order.draft(uuid=uuid)
    order.mark_as_paid()

    event_store.append_to_stream(order.changes)

    stream = event_store.load_stream(uuid)
    loaded_order = Order(stream)

    with pytest.raises(AlreadyPaid):
        loaded_order.mark_as_paid()


def test_raises_concurrent_error_if_detects_race_condition(
    event_store: EventStore,
) -> None:
    uuid = uuid4()
    order = Order.draft(uuid=uuid)
    event_store.append_to_stream(order.changes)

    stream = event_store.load_stream(uuid)
    loaded_order = Order(stream)
    loaded_order.mark_as_paid()
    event_store.append_to_stream(loaded_order.changes)

    with pytest.raises(EventStore.ConcurrentStreamWriteError):
        event_store.append_to_stream(loaded_order.changes)


def test_retrying_upon_concurrent_stream_write(event_store: EventStore) -> None:
    uuid = uuid4()
    order = Order.draft(uuid=uuid)
    event_store.append_to_stream(order.changes)

    @retry(
        retry_on_exception=lambda exc: isinstance(  # 1
            exc, EventStore.ConcurrentStreamWriteError
        ),
        stop_max_attempt_number=2,  # 2
    )
    def execute(aggregate_uuid: UUID) -> None:  # 3
        stream = event_store.load_stream(aggregate_uuid)
        order = Order(stream)
        order.mark_as_paid()
        event_store.append_to_stream(order.changes)

    with patch.object(
        event_store,
        "append_to_stream",
        wraps=event_store.append_to_stream,
        side_effect=[EventStore.ConcurrentStreamWriteError, None],
    ) as append_to_stream_mock:
        execute(uuid)

    assert len(append_to_stream_mock.mock_calls) == 2


@pytest.fixture()
def event_store(container: Injector) -> EventStore:
    return container.get(EventStore)  # type: ignore
