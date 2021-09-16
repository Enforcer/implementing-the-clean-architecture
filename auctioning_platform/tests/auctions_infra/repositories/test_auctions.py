from sqlalchemy.orm import Session

from itca.auctions.domain.entities.auction import Auction, Bid
from itca.auctions_infra.repositories.auctions import SqlAlchemyAuctionsRepository
from itca.foundation.money import USD, Money


def test_should_get_back_saved_auction(session: Session) -> None:
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
    repo = SqlAlchemyAuctionsRepository(session)

    repo.save(auction)

    assert repo.get(auction.id) == auction
