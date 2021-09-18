import abc

from attr import define

from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.foundation.money import Money


@define(frozen=True)
class AuctionDetailsDto:
    @define(frozen=True)
    class TopBidder:
        anonymized_name: str
        bid_amount: Money

    auction_id: AuctionId
    title: str
    current_price: Money
    starting_price: Money
    top_bidders: list[TopBidder]


class AuctionDetails(abc.ABC):
    class NotFound(Exception):
        pass

    @abc.abstractmethod
    def query(self, auction_id: AuctionId) -> AuctionDetailsDto:
        pass
