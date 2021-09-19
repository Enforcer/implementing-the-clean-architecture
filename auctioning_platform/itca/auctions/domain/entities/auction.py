from datetime import datetime
from typing import Optional

from attr import define

from itca.auctions.domain.events.bidder_has_been_overbid import (
    BidderHasBeenOverbid,
)
from itca.auctions.domain.exceptions.bid_on_ended_auction import (
    BidOnEndedAuction,
)
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions.domain.value_objects.bid_id import BidId
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.event import Event
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
    _ends_at: datetime

    def __attrs_post_init__(self) -> None:
        self._bids.sort(key=lambda bid: bid.amount)

    @property
    def id(self) -> AuctionId:
        return self._id

    def place_bid(self, bidder_id: BidderId, amount: Money) -> list[Event]:
        events: list[Event] = []
        self._ensure_not_ended()

        if amount > self.current_price:
            if self._bids:
                events.append(
                    BidderHasBeenOverbid(
                        auction_id=self.id,
                        bidder_id=self._highest_bid.bidder_id,
                        old_price=self._highest_bid.amount,
                        new_price=amount,
                    )
                )

            new_bid = Bid(
                id=None,
                bidder_id=bidder_id,
                amount=amount,
            )
            self._bids.append(new_bid)

        return events

    def _ensure_not_ended(self) -> None:
        if datetime.now() > self._ends_at:
            raise BidOnEndedAuction

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

    def finalize(self, bidder_id: BidderId) -> None:
        pass
