import abc

from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.money import Money


class PaymentFailed(Exception):
    pass


class NotEnoughFunds(PaymentFailed):
    pass


class PaymentsTemporarilyUnavailable(PaymentFailed):
    pass


CardId = int


class Payments(abc.ABC):
    @abc.abstractmethod
    def pay(self, token: str, amount: Money) -> None:
        pass

    @abc.abstractmethod
    def pay_with_selected_card(
        self, bidder_id: BidderId, card_id: CardId, amount: Money
    ) -> None:
        pass
