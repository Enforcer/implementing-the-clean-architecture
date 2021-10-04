from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from attr import define, evolve

from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event import EsEvent
from itca.event_sourcing.event_stream import EventStream
from itca.foundation.event import Event
from itca.foundation.money import Money
from itca.shipping.domain import events as domain_events
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


@define(frozen=True)
class OrderSent(EsEvent):
    pass


class AlreadyPaid(Exception):
    pass


class NotPaidYet(Exception):
    pass


class AlreadySent(Exception):
    pass


class CannotChangeOrderLinesOfPaidOrder(Exception):
    pass


@define(frozen=True)
class OrderSnapshot(EsEvent):
    paid_at: Optional[datetime]
    lines: dict[ProductId, OrderLine]


class Order:
    def __init__(self, stream: EventStream) -> None:
        self._uuid = stream.uuid
        self._version = stream.version

        self._paid_at: Optional[datetime] = None
        self._lines: dict[ProductId, OrderLine] = {}
        self._sent_at: Optional[datetime] = None

        for event in stream.events:
            self._apply(event)

        self._new_events: list[EsEvent] = []

    def _apply(self, event: EsEvent) -> None:
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
        elif isinstance(event, OrderSent):
            self._sent_at = event.created_at
        elif isinstance(event, OrderSnapshot):
            self._paid_at = event.paid_at
            self._lines = event.lines
        else:
            raise ValueError(f"Unknown event {type(event)}!")

    @classmethod
    def draft(cls, uuid: UUID) -> "Order":
        instance = Order(EventStream(uuid=uuid, version=0, events=[]))
        instance._new_events.append(
            OrderDrafted(
                uuid=uuid4(),
                created_at=datetime.now(tz=timezone.utc),
                aggregate_uuid=uuid,
                version=1,
            )
        )
        return instance

    def mark_as_paid(self) -> None:
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

    def mark_as_sent(self) -> list[Event]:
        if self._paid_at is None:
            raise NotPaidYet

        if self._sent_at is not None:
            raise AlreadySent

        event = OrderSent(
            uuid=uuid4(),
            aggregate_uuid=self._uuid,
            created_at=datetime.now(tz=timezone.utc),
            version=self._next_version,
        )
        self._apply(event)
        self._new_events.append(event)

        return [domain_events.ConsignmentShipped(uuid=self.uuid)]

    def add_product(
        self,
        product_id: ProductId,
        quantity: int,
        unit_price: Money,
    ) -> None:
        if self._paid_at is not None:
            raise CannotChangeOrderLinesOfPaidOrder

        event = ProductAdded(
            uuid=uuid4(),
            aggregate_uuid=self._uuid,
            created_at=datetime.now(tz=timezone.utc),
            version=self._next_version,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        self._apply(event)
        self._new_events.append(event)

    @property
    def _next_version(self) -> int:
        try:
            last_event = self._new_events[-1]
            return last_event.version + 1
        except IndexError:
            return self._version + 1

    @property
    def changes(self) -> AggregateChanges:
        return AggregateChanges(
            aggregate_uuid=self._uuid,
            events=self._new_events[:],
            expected_version=self._version,
        )

    @property
    def uuid(self) -> UUID:
        return self._uuid

    def take_snapshot(self) -> OrderSnapshot:
        if self._new_events:
            # For synchronous snapshot creation after saving latest changes
            version = self._next_version
        else:
            # for asynchronous background snapshot creation
            version = self._version

        return OrderSnapshot(
            uuid=uuid4(),
            aggregate_uuid=self._uuid,
            created_at=datetime.now(tz=timezone.utc),
            version=version,
            paid_at=self._paid_at,
            lines=self._lines.copy(),
        )


if __name__ == "__main__":
    o = Order.draft(uuid4())
    o.mark_as_paid()
    print(o.changes)
