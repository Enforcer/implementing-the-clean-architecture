from typing import Optional

from attr import define

from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions.domain.value_objects.bid_id import BidId
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.money import Money


@define
class Bid:
    id: Optional[BidId]
    bidder_id: BidderId
    amount: Money


@define
class Auction:
    _id: AuctionId
    _starting_price: Money
    _bids: list[Bid]

    def __attrs_post_init__(self) -> None:
        self._bids.sort(key=lambda bid: bid.amount)

    @property
    def id(self) -> AuctionId:
        return self._id

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:
        if amount > self.current_price:
            new_bid = Bid(
                id=None,
                bidder_id=bidder_id,
                amount=amount,
            )
            self._bids.append(new_bid)

    @property
    def current_price(self) -> Money:
        if not self._bids:
            return self._starting_price
        else:
            return self._highest_bid.amount

    @property
    def winner(self) -> Optional[BidderId]:
        if not self._bids:
            return None
        return self._highest_bid.bidder_id

    @property
    def _highest_bid(self) -> Bid:
        return self._bids[-1]
