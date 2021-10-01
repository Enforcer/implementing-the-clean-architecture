from uuid import uuid4

import pytest
from injector import Injector

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


@pytest.fixture()
def event_store(container: Injector) -> EventStore:
    return container.get(EventStore)  # type: ignore
