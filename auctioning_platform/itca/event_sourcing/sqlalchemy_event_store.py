from typing import Union
from uuid import UUID

from attr import define
from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from itca.event_sourcing.aggregate_changes import AggregateChanges
from itca.event_sourcing.event import EsEvent
from itca.event_sourcing.event_store import EventStore
from itca.event_sourcing.event_stream import EventStream
from itca.event_sourcing.models import Aggregate as AggregateModel
from itca.event_sourcing.models import Event as EventModel
from itca.event_sourcing.models import Snapshot as SnapshotModel
from itca.event_sourcing.projection import SynchronousProjection
from itca.foundation.serde import converter


@define
class SqlAlchemyEventStore(EventStore):
    _session: Session
    _projections_to_run_synchronously: list[SynchronousProjection]

    def load_stream(self, aggregate_uuid: UUID) -> EventStream:
        events_stmt = (
            select(EventModel)
            .filter(EventModel.aggregate_uuid == aggregate_uuid)
            .order_by(EventModel.version)
        )
        events: list[Union[EventModel, SnapshotModel]]

        try:
            snapshot_stmt = (
                select(SnapshotModel)
                .filter(SnapshotModel.aggregate_uuid == aggregate_uuid)
                .order_by(SnapshotModel.version.desc())
                .limit(1)
            )
            latest_snapshot: SnapshotModel = (
                self._session.execute(snapshot_stmt).scalars().one()
            )
        except NoResultFound:
            events = self._session.execute(events_stmt).scalars().all()
        else:
            events_stmt = events_stmt.filter(
                EventModel.version > latest_snapshot.version
            )
            events = [latest_snapshot] + self._session.execute(
                events_stmt
            ).scalars().all()

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

    def _deserialize_event(
        self, event: Union[EventModel, SnapshotModel]
    ) -> EsEvent:
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

        for projection in self._projections_to_run_synchronously:
            projection(changes.events)

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

    def save_snapshot(self, snapshot: EsEvent) -> None:
        snapshot_as_dict = converter.unstructure(snapshot)
        row = {
            "uuid": snapshot_as_dict.pop("uuid"),
            "aggregate_uuid": snapshot_as_dict.pop("aggregate_uuid"),
            "created_at": snapshot_as_dict.pop("created_at"),
            "version": snapshot_as_dict.pop("version"),
            "name": snapshot.__class__.__name__,
            "data": snapshot_as_dict,
        }
        self._session.execute(insert(SnapshotModel), [row])
