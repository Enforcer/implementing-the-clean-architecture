from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from itca.auctions import AuctionsRepository
from itca.auctions.app.use_cases.placing_bid import (
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from itca.auctions.domain.exceptions.bid_on_ended_auction import (
    BidOnEndedAuction,
)
from itca.foundation.money import USD, Money
from tests.auctions.factories import create_auction


def test_presents_winning_and_10_usd_price_when_higher_bid_placed(
    repo: AuctionsRepository,
) -> None:
    output_boundary_mock = Mock(spec_set=PlacingBidOutputBoundary)
    auction_id = create_auction(repo)
    use_case = PlacingBid(
        output_boundary=output_boundary_mock, auctions_repo=repo
    )

    price = Money(USD, "10.00")
    input_dto = PlacingBidInputDto(
        bidder_id=1,
        auction_id=auction_id,
        amount=price,
    )
    use_case.execute(input_dto)

    expected_output_dto = PlacingBidOutputDto(
        is_winning=True, current_price=price
    )
    output_boundary_mock.present.assert_called_once_with(expected_output_dto)


def test_bidding_on_ended_auction_raises_exception(
    repo: AuctionsRepository,
) -> None:
    yesterday = datetime.now() - timedelta(days=1)
    auction_id = create_auction(
        repo, starting_price=Money(USD, "1"), ends_at=yesterday
    )
    use_case = PlacingBid(
        output_boundary=Mock(PlacingBidOutputBoundary), auctions_repo=repo
    )

    with pytest.raises(BidOnEndedAuction):
        use_case.execute(
            PlacingBidInputDto(
                bidder_id=1, auction_id=auction_id, amount=Money(USD, "10")
            )
        )
