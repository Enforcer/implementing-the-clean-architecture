from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from attr import attrib, define, evolve

from itca.foundation.money import Money
from itca.shipping.domain.value_objects.customer_id import CustomerId
from itca.shipping.domain.value_objects.product_id import ProductId


@define(frozen=True)
class OrderLine:
    quantity: int
    unit_price: Money


class AlreadyPaid(Exception):
    pass


class CannotChangeOrderLinesOfPaidOrder(Exception):
    pass


@define
class Order:
    _uuid: UUID
    _customer_id: CustomerId
    _lines: dict[ProductId, OrderLine] = attrib(factory=dict)
    _paid_at: Optional[datetime] = None
    _shipped_at: Optional[datetime] = None

    def mark_as_paid(self) -> None:
        if self._paid_at is not None:
            raise AlreadyPaid

        self._paid_at = datetime.now(tz=timezone.utc)

    def add_product(
        self, product_id: ProductId, quantity: int, unit_price: Money
    ) -> None:
        if self._paid_at:
            raise CannotChangeOrderLinesOfPaidOrder

        try:
            line = self._lines[product_id]
            new_line = evolve(
                line, quantity=line.quantity + quantity, unit_price=unit_price
            )
        except KeyError:
            new_line = OrderLine(quantity=quantity, unit_price=unit_price)

        self._lines[product_id] = new_line
