import inspect
from decimal import Decimal, DecimalException
from functools import total_ordering
from typing import Any, ClassVar, Type


class Currency:
    decimal_precision: ClassVar[int]
    iso_code: ClassVar[str]
    __subclasses: ClassVar[dict[str, Type["Currency"]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        cls.__subclasses[cls.__name__] = cls

    @classmethod
    def from_name(cls, name: str) -> Type["Currency"]:
        return cls.__subclasses[name]


class USD(Currency):
    decimal_precision = 2
    iso_code = "USD"


class EUR(Currency):
    decimal_precision = 2
    iso_code = "EUR"


@total_ordering
class Money:
    def __init__(self, currency: Type[Currency], amount: Any) -> None:
        if not inspect.isclass(currency) or not issubclass(currency, Currency):
            raise ValueError(f"{currency} is not a subclass of Currency!")
        try:
            decimal_amount = Decimal(amount).normalize()
        except DecimalException:
            raise ValueError(f'"{amount}" is not a valid amount!')
        else:
            decimal_tuple = decimal_amount.as_tuple()
            if decimal_tuple.sign:
                raise ValueError("amount must not be negative!")
            elif -decimal_tuple.exponent > currency.decimal_precision:
                raise ValueError(
                    f"given amount has invalid precision! It should have "
                    f"no more than {currency.decimal_precision} decimal places!"
                )

            self._currency = currency
            self._amount = decimal_amount

    @property
    def currency(self) -> Type[Currency]:
        return self._currency

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError
        return self.currency == other.currency and self.amount == other.amount

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            raise TypeError(
                f"'<' not supported between instances "
                f"of 'Money' and '{other.__class__.__name__}'"
            )
        elif self.currency != other.currency:
            raise TypeError("Can not compare money in different currencies!")
        else:
            return self.amount < other.amount

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}"
            f"({self.currency.__name__}, '{self.amount}')>"
        )
