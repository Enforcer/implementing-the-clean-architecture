from datetime import datetime
from typing import ClassVar, Type
from uuid import UUID

from attr import define


@define(frozen=True)
class EsEvent:
    _subclasses: ClassVar[dict[str, Type]] = {}

    uuid: UUID
    aggregate_uuid: UUID
    created_at: datetime
    version: int

    def __init_subclass__(cls) -> None:
        cls._subclasses[cls.__name__] = cls

    @classmethod
    def subclass_for_name(cls, name: str) -> Type["EsEvent"]:
        return cls._subclasses[name]
