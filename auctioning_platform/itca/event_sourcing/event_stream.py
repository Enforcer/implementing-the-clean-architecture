from uuid import UUID

from attr import define

from itca.event_sourcing.event import EsEvent


@define(frozen=True)
class EventStream:
    uuid: UUID
    events: list[EsEvent]
    version: int
