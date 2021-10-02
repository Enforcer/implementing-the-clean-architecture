import abc

from itca.shipping.domain.aggregates.order import Order
from itca.shipping.domain.value_objects.order_id import OrderId


class OrdersRepository(abc.ABC):
    class NotFound(Exception):
        pass

    @abc.abstractmethod
    def get(self, order_id: OrderId) -> Order:
        pass

    @abc.abstractmethod
    def save(self, order: Order) -> None:
        pass
