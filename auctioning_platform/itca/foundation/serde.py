"""Serialization / Deserialization"""
from datetime import datetime
from uuid import UUID

import cattr

from itca.foundation.money import Currency, Money

converter = cattr.Converter()
converter.register_unstructure_hook(  # type: ignore
    Money,
    lambda money: {
        "currency": money.currency.__name__,  # type: ignore
        "amount": str(money.amount),  # type: ignore
    },
)
converter.register_unstructure_hook(UUID, str)

converter.register_structure_hook(
    Money,
    lambda money_dict, _: Money(
        Currency.from_code(money_dict["currency"]), money_dict["amount"]
    ),
)
converter.register_structure_hook(
    datetime, lambda datetime_raw, _: datetime_raw
)
converter.register_structure_hook(
    UUID,
    lambda uuid_raw, _: UUID(uuid_raw)
    if not isinstance(uuid_raw, UUID)
    else uuid_raw,
)
