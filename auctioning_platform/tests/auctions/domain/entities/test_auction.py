from datetime import datetime, timedelta

from itca.auctions.domain.entities.auction import Auction
from itca.foundation.money import USD, Money


def test_new_auction_has_current_price_equal_to_starting() -> None:
    starting_price = Money(USD, "12.99")
    auction = Auction(
        id=1,
        starting_price=starting_price,
        bids=[],
        ends_at=datetime.now() + timedelta(days=3),
    )

    assert starting_price == auction.current_price
