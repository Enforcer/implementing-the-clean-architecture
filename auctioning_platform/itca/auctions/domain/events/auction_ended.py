from attr import define

from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.event import Event
from itca.foundation.money import Money


@define(frozen=True)
class AuctionEnded(Event):
    auction_id: AuctionId
    winner_id: BidderId
    price: Money
