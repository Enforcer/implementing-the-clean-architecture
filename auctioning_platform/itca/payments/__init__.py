import injector
from sqlalchemy.engine import Connection

from itca.foundation.event_bus import (
    AsyncEventListenerProvider,
    AsyncListener,
    EventBus,
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
    "PaymentsConfig",
    # Facade
    "PaymentsFacade",
    # Events
    "PaymentStarted",
    "PaymentCharged",
    "PaymentCaptured",
    "PaymentFailed",
]


class Payments(injector.Module):
    @injector.provider
    def facade(
        self,
        config: PaymentsConfig,
        connection: Connection,
        event_bus: EventBus,
    ) -> PaymentsFacade:
        return PaymentsFacade(config, connection, event_bus)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(
            AsyncListener[PaymentCharged],
            to=AsyncEventListenerProvider(PaymentChargedHandler),
        )


class PaymentChargedHandler:
    @injector.inject
    def __init__(self, facade: PaymentsFacade) -> None:
        self._facade = facade

    def __call__(self, event: PaymentCharged) -> None:
        self._facade.capture(event.payment_uuid, event.customer_id)
