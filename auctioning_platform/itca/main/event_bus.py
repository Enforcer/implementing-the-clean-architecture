from typing import Type

import injector
from sqlalchemy.orm import Session

from itca.foundation.event_bus import AsyncListener, Event
from itca.foundation.event_bus import EventBus as EventBusInterface
from itca.foundation.event_bus import InjectorEventBus
from itca.foundation.serde import converter
from itca.tasks.outbox.model import OutboxMessage


class EventBus(injector.Module):
    @injector.provider
    def event_bus(self, container: injector.Injector) -> EventBusInterface:
        def run_async(listener: Type[AsyncListener], event: Event) -> None:
            session = container.get(Session)
            session.add(
                OutboxMessage(
                    listener=f"{listener.__module__}.{listener.__name__}",
                    event=f"{type(event).__module__}.{type(event).__name__}",
                    event_payload=converter.unstructure(event),
                )
            )

        return InjectorEventBus(container, run_async)
