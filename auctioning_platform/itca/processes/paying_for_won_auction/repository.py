import abc
from uuid import UUID

from itca.processes.paying_for_won_auction.state import PayingForWonAuctionState


class PayingForWonAuctionStateRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_auction(self, auction_id: int) -> PayingForWonAuctionState:
        pass

    @abc.abstractmethod
    def get_by_payment(self, payment_uuid: UUID) -> PayingForWonAuctionState:
        pass

    @abc.abstractmethod
    def add(self, state: PayingForWonAuctionState) -> None:
        pass
