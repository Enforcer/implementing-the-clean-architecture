from unittest.mock import Mock

import pytest

from itca.auctions import (
    AuctionsRepository,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
)
from itca.auctions.app.ports.payments import Payments
from itca.auctions.app.use_cases.finalizing_auction import (
    FinalizingAuction,
    FinalizingAuctionInputDto,
)
from itca.foundation.money import USD, Money
from tests.auctions.factories import create_auction


def test_calls_payments_with_token_and_current_price(
    repo: AuctionsRepository, placing_bid: PlacingBid
):
    auction_id = create_auction(repo=repo, starting_price=Money(USD, "1.00"))
    placing_bid.execute(
        PlacingBidInputDto(
            auction_id=auction_id, bidder_id=1, amount=Money(USD, "2.00")
        )
    )
    payments_mock = Mock(Payments)

    uc = FinalizingAuction(payments=payments_mock, auctions_repo=repo)
    uc.execute(
        FinalizingAuctionInputDto(
            auction_id=auction_id, bidder_id=1, payment_token="TOKEN123"
        )
    )

    payments_mock.pay.assert_called_once_with(
        token="TOKEN123", amount=Money(USD, "2.00")
    )


@pytest.fixture
def placing_bid(repo: AuctionsRepository) -> PlacingBid:
    return PlacingBid(
        output_boundary=Mock(PlacingBidOutputBoundary),
        auctions_repo=repo,
    )
