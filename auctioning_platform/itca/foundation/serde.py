"""Serialization / Deserialization"""
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
converter.register_structure_hook(
    Money,
    lambda money_dict, _: Money(
        Currency.from_name(money_dict["currency"]), money_dict["amount"]
    ),
)
