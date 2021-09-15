from dataclasses import dataclass
from typing import Any, Optional

from itca.auctions.value_objects.auction_id import AuctionId
from itca.auctions.value_objects.bid_id import BidId
from itca.auctions.value_objects.bidder_id import BidderId
from itca.foundation.money import Money


@dataclass
class Bid:
    id: Optional[BidId]
    bidder_id: BidderId
    amount: Money


class Auction:
    def __init__(
        self,
        id: AuctionId,
        starting_price: Money,
        bids: list[Bid],
    ) -> None:
        self._id = id
        self._starting_price = starting_price
        self._bids = sorted(bids, key=lambda bid: bid.amount)  # 1

    @property
    def id(self) -> AuctionId:
        return self._id

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:  # 2
        if amount > self.current_price:
            new_bid = Bid(
                id=None,
                bidder_id=bidder_id,
                amount=amount,
            )
            self._bids.append(new_bid)

    @property
    def current_price(self) -> Money:
        if not self._bids:  # 3
            return self._starting_price
        else:
            return self._highest_bid.amount

    @property
    def winner(self) -> Optional[BidderId]:
        if not self._bids:  # 4
            return None
        return self._highest_bid.bidder_id

    @property
    def _highest_bid(self) -> Bid:
        return self._bids[-1]  # 5

    def __eq__(self, other: Any) -> bool:
        # sprawdzamy typ i pola w klasie
        return isinstance(other, Auction) and vars(self) == vars(other)
