from uuid import UUID

from attr import define
from sqlalchemy.orm import Session

from itca.event_sourcing import models
from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event_store import EventStore
from itca.event_sourcing.event_stream import EventStream


@define
class SqlAlchemyEventStore(EventStore):
    _session: Session

    def load_stream(self, aggregate_uuid: UUID) -> EventStream:
        pass

    def append_to_stream(self, changes: AggregateChanges) -> None:
        raise NotImplementedError
