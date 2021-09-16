from unittest.mock import Mock

from itca.auctions.app.use_cases.placing_bid import (
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from itca.auctions.domain.entities.auction import Auction
from itca.foundation.money import USD, Money
from tests.doubles.in_memory_auctions_repo import InMemoryAuctionsRepository


def test_presents_winning_and_10_usd_price_when_higher_bid_placed() -> None:
    output_boundary_mock = Mock(spec_set=PlacingBidOutputBoundary)
    repo = InMemoryAuctionsRepository()
    repo.save(Auction(id=2, starting_price=Money(USD, "5.00"), bids=[]))
    use_case = PlacingBid(
        output_boundary=output_boundary_mock, auctions_repo=repo
    )

    price = Money(USD, "10.00")
    input_dto = PlacingBidInputDto(
        bidder_id=1,
        auction_id=2,
        amount=price,
    )
    use_case.execute(input_dto)

    expected_output_dto = PlacingBidOutputDto(
        is_winning=True, current_price=price
    )
    output_boundary_mock.present.assert_called_once_with(expected_output_dto)
