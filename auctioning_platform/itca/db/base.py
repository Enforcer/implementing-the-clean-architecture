from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative

metadata = MetaData()


@as_declarative(metadata=metadata)
class Base:
    pass
