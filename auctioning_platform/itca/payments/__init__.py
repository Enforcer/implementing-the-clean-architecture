import injector
from attr import define
from sqlalchemy.engine import Connection

from itca.foundation.event_bus import (
    AsyncEventListenerProvider,
    AsyncListener,
    EventBus,
    Listener,
)
from itca.payments.config import PaymentsConfig
from itca.payments.events import (
    PaymentCaptured,
    PaymentCharged,
    PaymentFailed,
    PaymentStarted,
)
from itca.payments.facade import PaymentsFacade

__all__ = [
    # Module
    "Payments",
    # Facade
    "PaymentsFacade",
    # Events
    "PaymentStarted",
    "PaymentCharged",
    "PaymentCaptured",
    "PaymentFailed",
]


@define
class OnPaymentCharged(Listener[PaymentCharged]):  # type: ignore
    _facade: PaymentsFacade

    def __call__(self, event: PaymentCharged) -> None:
        self._facade.capture(event.payment_uuid, event.customer_id)


class Payments(injector.Module):
    def __init__(self, username: str, password: str) -> None:
        self._config = PaymentsConfig(username, password)

    @injector.provider
    def facade(
        self,
        connection: Connection,
        event_bus: EventBus,
    ) -> PaymentsFacade:
        return PaymentsFacade(self._config, connection, event_bus)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(
            AsyncListener[PaymentCharged],
            to=AsyncEventListenerProvider(OnPaymentCharged),
        )

    @injector.provider
    def on_payment_charged(
        self, payments_facade: PaymentsFacade
    ) -> OnPaymentCharged:
        return OnPaymentCharged(facade=payments_facade)
