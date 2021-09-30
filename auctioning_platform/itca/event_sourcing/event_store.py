import abc
from uuid import UUID

from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event_stream import EventStream


class EventStore(abc.ABC):
    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: UUID) -> EventStream:
        pass

    @abc.abstractmethod
    def append_to_stream(self, changes: AggregateChanges) -> None:
        pass
