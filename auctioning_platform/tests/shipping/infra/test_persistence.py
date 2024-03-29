from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from injector import Injector
from retrying import retry
from sqlalchemy.orm import Session

from itca.event_sourcing import EventStore
from itca.foundation.money import USD, Money
from itca.foundation.serde import converter
from itca.shipping.domain.aggregates.order import AlreadyPaid, Order
from itca.shipping_infra.projections.order_summary import (
    OrderStatus,
    OrderSummary,
)


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


def test_loads_state_from_snapshot(event_store: EventStore) -> None:
    uuid = uuid4()
    order = Order.draft(uuid=uuid)
    order.add_product(product_id=1, quantity=2, unit_price=Money(USD, "2.99"))
    event_store.append_to_stream(order.changes)
    snapshot = order.take_snapshot()
    event_store.save_snapshot(snapshot)

    stream = event_store.load_stream(uuid)

    assert len(stream.events) == 1
    assert isinstance(stream.events[0], type(snapshot))


def test_projects_order(event_store: EventStore, session: Session) -> None:
    order = Order.draft(uuid=uuid4())
    order.add_product(product_id=1, quantity=1, unit_price=Money(USD, "13.99"))
    order.add_product(product_id=2, quantity=3, unit_price=Money(USD, "7.50"))
    order.mark_as_paid()

    event_store.append_to_stream(order.changes)

    events = order.changes.events
    summary: OrderSummary = session.query(OrderSummary).get(order.uuid)
    assert summary.version == events[-1].version
    assert summary.total_quantity == 4
    assert converter.structure(summary.total_price, Money) == Money(
        USD, "36.49"
    )
    assert summary.status == OrderStatus.PAID


@pytest.fixture()
def event_store(container: Injector) -> EventStore:
    return container.get(EventStore)  # type: ignore


@pytest.fixture()
def session(container: Injector) -> Session:
    return container.get(Session)
