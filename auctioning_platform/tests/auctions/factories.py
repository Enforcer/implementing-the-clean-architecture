from datetime import datetime, timedelta

import factory

from itca.auctions import AuctionsRepository
from itca.auctions.domain.entities.auction import Auction
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.foundation.money import USD, Money


def create_auction(
    repo: AuctionsRepository,
    starting_price: Money = Money(USD, "5.00"),
    ends_at: datetime = datetime.now() + timedelta(days=3),
) -> AuctionId:
    auction = build_auction(starting_price=starting_price, ends_at=ends_at)
    repo.save(auction)
    return auction.id


def build_auction(
    starting_price: Money = Money(USD, "5.00"),
    ends_at: datetime = datetime.now() + timedelta(days=3),
) -> Auction:
    auction_id = 2
    return Auction(
        id=auction_id,
        starting_price=starting_price,
        bids=[],
        ends_at=ends_at,
    )


class AuctionFactory(factory.Factory):
    class Meta:
        model = Auction

    class Params:
        ended = False

    id = factory.Sequence(lambda n: n)
    bids = factory.List([])
    starting_price = Money(USD, "5.00")
    ends_at: datetime = factory.LazyAttribute(
        lambda o: datetime.now() + timedelta(days=3)
        if not o.ended
        else datetime.now() - timedelta(days=1)
    )
