from uuid import UUID

from attr import define

from itca.foundation.event import Event


@define(frozen=True)
class PaymentStarted(Event):
    payment_uuid: UUID
    customer_id: int


@define(frozen=True)
class PaymentCharged(Event):
    payment_uuid: UUID
    customer_id: int


@define(frozen=True)
class PaymentCaptured(Event):
    payment_uuid: UUID
    customer_id: int


@define(frozen=True)
class PaymentFailed(Event):
    payment_uuid: UUID
    customer_id: int
