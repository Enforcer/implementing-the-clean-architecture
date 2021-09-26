import pytest
from attr import define

from itca.auctions import AuctionId


class AuctionAlreadyEnded(Exception):
    pass


@define
class Auction:
    _id: AuctionId
    _ended: bool

    def end(self) -> None:
        if self._ended:
            raise AuctionAlreadyEnded
        self._ended = True


def test_ending_auction_changes_ended_flag():
    auction = Auction(id=1, ended=False)

    auction.end()

    assert auction._ended


def test_auction_cannot_be_ended_twice():
    auction = Auction(id=1, ended=False)

    auction.end()

    with pytest.raises(AuctionAlreadyEnded):
        auction.end()
