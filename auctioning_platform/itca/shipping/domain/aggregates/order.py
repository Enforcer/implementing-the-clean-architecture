from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from attr import define, evolve

from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event import EsEvent
from itca.event_sourcing.event_stream import EventStream
from itca.foundation.money import Money
from itca.shipping.domain.value_objects.product_id import ProductId


@define(frozen=True)
class OrderDrafted(EsEvent):
    pass


@define(frozen=True)
class OrderPaid(EsEvent):
    pass


@define(frozen=True)
class ProductAdded(EsEvent):
    product_id: ProductId
    quantity: int
    unit_price: Money


@define(frozen=True)
class OrderLine:
    quantity: int
    unit_price: Money


class AlreadyPaid(Exception):
    pass


class CannotChangeOrderLinesOfPaidOrder(Exception):
    pass


class Order:
    def __init__(self, stream: EventStream) -> None:  # 1
        self._uuid = stream.uuid
        self._version = stream.version

        self._paid_at: Optional[datetime] = None  # 2
        self._lines: dict[ProductId, OrderLine] = {}

        for event in stream.events:  # 3
            self._apply(event)

        self._new_events: list[EsEvent] = []  # 4

    def _apply(self, event: EsEvent) -> None:  # 5
        if isinstance(event, OrderDrafted):
            pass
        elif isinstance(event, OrderPaid):
            self._paid_at = event.created_at
        elif isinstance(event, ProductAdded):
            try:
                line = self._lines[event.product_id]
                new_line = evolve(
                    line,
                    quantity=line.quantity + event.quantity,
                    unit_price=event.unit_price,
                )
            except KeyError:
                new_line = OrderLine(
                    quantity=event.quantity, unit_price=event.unit_price
                )

            self._lines[event.product_id] = new_line
        else:
            raise ValueError(f"Unknown event {type(event)}!")

    @classmethod
    def draft(cls, uuid: UUID) -> "Order":  # 6
        instance = Order(EventStream(uuid=uuid, version=0, events=[]))
        instance._new_events.append(
            OrderDrafted(
                uuid=uuid4(),
                created_at=datetime.now(tz=timezone.utc),
                aggregate_uuid=uuid,
                version=0,
            )
        )
        return instance

    def mark_as_paid(self) -> None:  # 1
        if self._paid_at is not None:
            raise AlreadyPaid

        event = OrderPaid(
            uuid=uuid4(),
            aggregate_uuid=self._uuid,
            created_at=datetime.now(tz=timezone.utc),
            version=self._next_version,
        )
        self._apply(event)
        self._new_events.append(event)

    @property
    def _next_version(self) -> int:  # 2
        try:
            last_event = self._new_events[-1]
            return last_event.version + 1
        except IndexError:
            return self._version + 1

    @property
    def changes(self) -> AggregateChanges:  # 3
        return AggregateChanges(
            aggregate_uuid=self._uuid,
            events=self._new_events[:],
            expected_version=self._version,
        )


if __name__ == "__main__":
    o = Order.draft(uuid4())
    o.mark_as_paid()
    print(o.changes)
