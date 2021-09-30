from uuid import UUID

from attr import define
from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event import EsEvent
from itca.event_sourcing.event_store import EventStore
from itca.event_sourcing.event_stream import EventStream
from itca.event_sourcing.models import Aggregate as AggregateModel
from itca.event_sourcing.models import Event as EventModel
from itca.foundation.serde import converter


@define
class SqlAlchemyEventStore(EventStore):
    _session: Session

    def load_stream(self, aggregate_uuid: UUID) -> EventStream:
        stmt = (
            select(EventModel)
            .filter(EventModel.aggregate_uuid == aggregate_uuid)
            .order_by(EventModel.version)
        )
        events: list[EventModel] = self._session.execute(stmt).scalars().all()

        if not events:
            raise EventStore.NotFound

        version = events[-1].version
        deserialized_events = [
            self._deserialize_event(model) for model in events
        ]

        return EventStream(
            uuid=aggregate_uuid,
            events=deserialized_events,
            version=version,
        )

    def _deserialize_event(self, event: EventModel) -> EsEvent:
        event_cls = EsEvent.subclass_for_name(event.name)
        return converter.structure(
            {
                "uuid": event.uuid,
                "aggregate_uuid": event.aggregate_uuid,
                "created_at": event.created_at,
                "version": event.version,
                **event.data,
            },
            event_cls,
        )

    def append_to_stream(self, changes: AggregateChanges) -> None:
        if not changes.events:
            raise EventStore.NoEventsToAppend

        if changes.expected_version:
            self._perform_update(changes)
        else:
            self._perform_create(changes)

        self._insert_events(changes)

    def _perform_update(self, changes: AggregateChanges) -> None:
        last_event_version = changes.events[-1].version
        stmt = (
            update(AggregateModel)
            .where(
                AggregateModel.version == changes.expected_version,
                AggregateModel.uuid == changes.aggregate_uuid,
            )
            .values(version=last_event_version)
        )
        result = self._session.execute(stmt)

        if result.rowcount != 1:  # optimistic lock failed
            raise EventStore.ConcurrentStreamWriteError

    def _perform_create(self, changes: AggregateChanges) -> None:
        stmt = insert(AggregateModel).values(
            uuid=changes.aggregate_uuid,
            version=1,
        )
        self._session.execute(stmt)

    def _insert_events(self, changes: AggregateChanges) -> None:
        rows = []
        for event in changes.events:
            event_as_dict = converter.unstructure(event)
            rows.append(
                {
                    "uuid": event_as_dict.pop("uuid"),
                    "aggregate_uuid": event_as_dict.pop("aggregate_uuid"),
                    "created_at": event_as_dict.pop("created_at"),
                    "version": event_as_dict.pop("version"),
                    "name": event.__class__.__name__,
                    "data": event_as_dict,
                }
            )

        self._session.execute(insert(EventModel), rows)
