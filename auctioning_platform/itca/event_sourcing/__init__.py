import injector
from sqlalchemy.orm import Session

from itca.event_sourcing.event_store import EventStore
from itca.event_sourcing.projection import Projection, SynchronousProjection
from itca.event_sourcing.sqlalchemy_event_store import SqlAlchemyEventStore

__all__ = [
    # Module
    "EventSourcing",
    # Interfaces
    "EventStore",
    "Projection",
    "SynchronousProjection",
]


class EventSourcing(injector.Module):
    @injector.provider
    def event_store(
        self,
        session: Session,
        projections_to_run_synchronously: list[SynchronousProjection],
    ) -> EventStore:
        return SqlAlchemyEventStore(
            session=session,
            projections_to_run_synchronously=projections_to_run_synchronously,
        )
