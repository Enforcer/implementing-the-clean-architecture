import copy

from itca.auctions.domain.entities.auction import Auction
from itca.auctions.app.repositories.auctions import AuctionsRepository
from itca.auctions.domain.value_objects.auction_id import AuctionId


class InMemoryAuctionsRepository(AuctionsRepository):
    def __init__(self) -> None:
        self._storage: dict[AuctionId, Auction] = {}  # 1

    def get(self, auction_id: AuctionId) -> Auction:
        return copy.deepcopy(self._storage[auction_id])  # 2

    def save(self, auction: Auction) -> None:
        self._storage[auction.id] = copy.deepcopy(auction)  # 3
