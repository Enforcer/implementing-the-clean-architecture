from itca.auctions.domain.entities.auction import Auction, Bid
from itca.foundation.money import USD, Money
from tests.doubles.in_memory_auctions_repo import InMemoryAuctionsRepository


def test_should_get_back_saved_auction() -> None:
    bids = [
        Bid(
            id=1,
            bidder_id=1,
            amount=Money(USD, "15.99"),
        )
    ]
    auction = Auction(
        id=1,
        starting_price=Money(USD, "9.99"),
        bids=bids,
    )
    repo = InMemoryAuctionsRepository()

    repo.save(auction)

    assert repo.get(auction.id) == auction
