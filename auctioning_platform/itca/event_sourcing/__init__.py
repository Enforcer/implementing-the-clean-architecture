import injector
from sqlalchemy.orm import Session

from itca.event_sourcing.event_store import EventStore
from itca.event_sourcing.sqlalchemy_event_store import SqlAlchemyEventStore

__all__ = [
    # Module
    "EventSourcing",
    # Interfaces
    "EventStore",
]


class EventSourcing(injector.Module):
    @injector.provider
    def event_store(self, session: Session) -> EventStore:
        return SqlAlchemyEventStore(session)
