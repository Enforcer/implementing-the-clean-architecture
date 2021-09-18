from itca.foundation.money import USD, Money
from tests.auctions.factories import build_auction


def test_new_auction_has_current_price_equal_to_starting() -> None:
    starting_price = Money(USD, "12.99")
    auction = build_auction(starting_price=starting_price)

    assert starting_price == auction.current_price
