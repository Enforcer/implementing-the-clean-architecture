from datetime import date
from uuid import UUID

from attr import define

from itca.foundation.event import Event


@define(frozen=True)
class PaymentOverdue(Event):
    payment_uuid: UUID
    customer_id: int
    due_date: date
    days: int
