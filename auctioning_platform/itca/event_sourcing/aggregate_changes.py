from uuid import UUID

from attr import define

from itca.event_sourcing.event import EsEvent


@define(frozen=True)
class AggregateChanges:
    aggregate_uuid: UUID
    events: list[EsEvent]
    expected_version: int
