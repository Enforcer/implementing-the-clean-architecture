from uuid import uuid4

import pytest

from itca.event_sourcing.event_stream import EventStream
from itca.shipping.domain.aggregates.order import AlreadyPaid, Order, OrderPaid


def test_order_cannot_be_marked_as_paid_twice(order: Order) -> None:
    order.mark_as_paid()

    with pytest.raises(AlreadyPaid):
        order.mark_as_paid()


def test_marking_as_paid_records_order_paid_event(order: Order) -> None:
    order.mark_as_paid()

    changes = order.changes
    assert len(changes.events) == 1
    assert isinstance(changes.events[0], OrderPaid)


@pytest.fixture()
def order() -> Order:
    new_order = Order.draft(uuid=uuid4())
    changes = new_order.changes
    return Order(
        EventStream(
            uuid=changes.aggregate_uuid,
            events=changes.events,
            version=1,
        )
    )
