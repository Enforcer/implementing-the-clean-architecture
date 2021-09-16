from typing import Any

from sqlalchemy import MetaData, Table
from sqlalchemy.orm import as_declarative

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    __table__: Table

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
