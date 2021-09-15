import abc

from itca.auctions.entities.auction import Auction
from itca.auctions.value_objects.auction_id import AuctionId


class AuctionsRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, auction_id: AuctionId) -> Auction:
        pass

    @abc.abstractmethod
    def save(self, auction: Auction) -> None:
        pass
