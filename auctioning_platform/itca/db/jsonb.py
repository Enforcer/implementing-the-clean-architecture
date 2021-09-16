import json
from typing import Any, Optional

from sqlalchemy.dialects.postgresql import JSONB as PostgresJSONB
from sqlalchemy.types import Text, TypeDecorator


class JSONB(TypeDecorator):
    impl = Text

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PostgresJSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value: Any, dialect: Any) -> Optional[Any]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value: Any, dialect: Any) -> Optional[Any]:
        if value is None:
            return value
        else:
            return json.loads(value)
