import abc

from itca.foundation.money import Money


class Payments(abc.ABC):
    @abc.abstractmethod
    def pay(self, token: str, amount: Money) -> None:
        pass
