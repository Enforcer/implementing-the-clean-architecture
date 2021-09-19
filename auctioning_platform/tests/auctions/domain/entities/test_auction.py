from itca.auctions.domain.events.bidder_has_been_overbid import (
    BidderHasBeenOverbid,
)
from itca.foundation.money import USD, Money
from tests.auctions.factories import build_auction


def test_new_auction_has_current_price_equal_to_starting() -> None:
    starting_price = Money(USD, "12.99")
    auction = build_auction(starting_price=starting_price)

    assert starting_price == auction.current_price


def test_returns_event_upon_overbid() -> None:
    auction = build_auction(starting_price=Money(USD, "1.00"))

    auction.place_bid(bidder_id=1, amount=Money(USD, "2.00"))
    events = auction.place_bid(bidder_id=2, amount=Money(USD, "3.00"))

    assert (
        BidderHasBeenOverbid(
            auction_id=auction.id,
            bidder_id=1,
            old_price=Money(USD, "2.00"),
            new_price=Money(USD, "3.00"),
        )
        in events
    )
