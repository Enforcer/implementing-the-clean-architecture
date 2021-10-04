from datetime import datetime, timezone
from uuid import uuid4

import pytest
from freezegun import freeze_time

from itca.event_sourcing.event_stream import EventStream
from itca.foundation.money import USD, Money
from itca.shipping.domain import events as domain_events
from itca.shipping.domain.aggregates.order import (
    AlreadyPaid,
    Order,
    OrderLine,
    OrderPaid,
)


def test_order_cannot_be_marked_as_paid_twice(order: Order) -> None:
    order.mark_as_paid()

    with pytest.raises(AlreadyPaid):
        order.mark_as_paid()


def test_marking_as_paid_records_order_paid_event(order: Order) -> None:
    order.mark_as_paid()

    changes = order.changes
    assert len(changes.events) == 1
    assert isinstance(changes.events[0], OrderPaid)


@freeze_time("2021-07-05 15:00:00")
def test_snapshot_contains_products_and_paid_at(order: Order) -> None:
    order.add_product(product_id=1, quantity=1, unit_price=Money(USD, "1.99"))
    order.add_product(product_id=1, quantity=2, unit_price=Money(USD, "0.99"))
    order.add_product(product_id=2, quantity=1, unit_price=Money(USD, "7.99"))
    order.mark_as_paid()

    snapshot = order.take_snapshot()

    assert snapshot.aggregate_uuid == order.uuid
    assert snapshot.paid_at == datetime(2021, 7, 5, 15, tzinfo=timezone.utc)
    assert snapshot.lines == {
        1: OrderLine(quantity=3, unit_price=Money(USD, "0.99")),
        2: OrderLine(quantity=1, unit_price=Money(USD, "7.99")),
    }


def test_snapshot_remembers_changes(order: Order) -> None:
    order.mark_as_paid()
    snapshot = order.take_snapshot()

    order_from_snapshot = Order(
        EventStream(
            uuid=order.uuid, events=[snapshot], version=snapshot.version
        )
    )

    with pytest.raises(AlreadyPaid):
        order_from_snapshot.mark_as_paid()


def test_returns_domain_event_order_sent_upon_marking_as_sent(
    order: Order,
) -> None:
    order.mark_as_paid()

    returned_events = order.mark_as_sent()

    assert len(returned_events) == 1
    assert isinstance(returned_events[0], domain_events.ConsignmentShipped)


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
