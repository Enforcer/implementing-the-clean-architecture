from uuid import UUID

from attr import define

from itca.foundation.event import Event


@define(frozen=True)
class ConsignmentShipped(Event):
    uuid: UUID
