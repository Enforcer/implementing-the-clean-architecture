from uuid import UUID

from attr import define

from itca.foundation.event import Event


@define(frozen=True)
class PaymentCharged(Event):
    payment_uuid: UUID
    customer_id: int
