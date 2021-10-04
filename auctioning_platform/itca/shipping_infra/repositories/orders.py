from attr import define

from itca.event_sourcing import EventStore
from itca.shipping import OrdersRepository
from itca.shipping.domain.aggregates.order import Order
from itca.shipping.domain.value_objects.order_id import OrderId


@define
class EventStoreOrdersRepository(OrdersRepository):
    _event_store: EventStore

    def get(self, order_id: OrderId) -> Order:
        try:
            stream = self._event_store.load_stream(order_id)
        except EventStore.NotFound:
            raise OrdersRepository.NotFound
        return Order(stream)

    def save(self, order: Order) -> None:
        changes = order.changes
        self._event_store.append_to_stream(changes)
        if changes.expected_version % 100 == 0:
            snapshot = order.take_snapshot()
            self._event_store.save_snapshot(snapshot)
