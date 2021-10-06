from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from freezegun import freeze_time

from itca.auctions import (
    AuctionId,
    AuctionsDescriptorsRepository,
    AuctionsRepository,
    BidderHasBeenOverbid,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
    StartingAuction,
    StartingAuctionInputDto,
)
from itca.auctions.domain.entities.auction_descriptor import AuctionDescriptor
from itca.auctions.domain.exceptions.bid_on_ended_auction import (
    BidOnEndedAuction,
)
from itca.foundation.event_bus import EventBus
from itca.foundation.money import USD, Money
from tests.doubles.in_memory_auctions_repo import InMemoryAuctionsRepository

AUCTION_ID = 1


class AuctionsDescriptorsRepositoryFake(AuctionsDescriptorsRepository):
    def get(self, auction_id: AuctionId) -> AuctionDescriptor:
        raise NotImplementedError

    def add(self, descriptor: AuctionDescriptor) -> None:
        descriptor.id = AUCTION_ID

    def delete(self, descriptor: AuctionDescriptor) -> None:
        raise NotImplementedError


@pytest.fixture()
def starting_auction(auctions_repo: AuctionsRepository) -> StartingAuction:
    return StartingAuction(
        auctions_repo=auctions_repo,
        auctions_descriptors_repo=AuctionsDescriptorsRepositoryFake(),
    )


def test_overbidding_emits_events_about_new_winner_and_overbid(
    starting_auction: StartingAuction,
    placing_bid: PlacingBid,
    event_bus: Mock,
) -> None:
    # Arrange
    starting_auction.execute(
        StartingAuctionInputDto(
            stating_price=Money(USD, "1.00"),
            end_time=datetime.now() + timedelta(days=3),
            title="Yellow Submarine",
            description="...",
        )
    )
    placing_bid.execute(
        PlacingBidInputDto(
            bidder_id=1,
            auction_id=AUCTION_ID,
            amount=Money(USD, "2.00"),
        )
    )

    # Act
    event_bus.reset_mock()
    placing_bid.execute(
        PlacingBidInputDto(
            bidder_id=2,
            auction_id=AUCTION_ID,
            amount=Money(USD, "3.00"),
        )
    )

    # Assert
    event_bus.publish.assert_called_once_with(
        BidderHasBeenOverbid(
            auction_id=AUCTION_ID,
            bidder_id=1,
            old_price=Money(USD, "2.00"),
            new_price=Money(USD, "3.00"),
        )
    )


def test_overbidding_returns_winner_and_new_price(
    starting_auction: StartingAuction,
    placing_bid: PlacingBid,
    placing_bid_output_boundary: Mock,
) -> None:
    # Arrange
    starting_auction.execute(
        StartingAuctionInputDto(
            stating_price=Money(USD, "1.00"),
            end_time=datetime.now() + timedelta(days=3),
            title="Yellow Submarine",
            description="...",
        )
    )
    placing_bid.execute(
        PlacingBidInputDto(
            bidder_id=1,
            auction_id=AUCTION_ID,
            amount=Money(USD, "2.00"),
        )
    )

    # Act
    placing_bid_output_boundary.reset_mock()
    placing_bid.execute(
        PlacingBidInputDto(
            bidder_id=2,
            auction_id=AUCTION_ID,
            amount=Money(USD, "3.00"),
        )
    )

    # Assert
    placing_bid_output_boundary.present.assert_called_once_with(
        PlacingBidOutputDto(
            is_winning=True,
            current_price=Money(USD, "3.00"),
        )
    )


def test_bidding_on_ended_auction_raises_exception(
    starting_auction: StartingAuction,
    placing_bid: PlacingBid,
) -> None:
    # Arrange
    with freeze_time(datetime.now() - timedelta(days=1)):
        starting_auction.execute(
            StartingAuctionInputDto(
                stating_price=Money(USD, "1.00"),
                end_time=datetime.now(),
                title="Yellow Submarine",
                description="...",
            )
        )

    # Act & Assert
    with pytest.raises(BidOnEndedAuction):
        placing_bid.execute(
            PlacingBidInputDto(
                bidder_id=1,
                auction_id=AUCTION_ID,
                amount=Money(USD, "2.00"),
            )
        )


@pytest.fixture()
def placing_bid(
    auctions_repo: AuctionsRepository,
    event_bus: EventBus,
    placing_bid_output_boundary: PlacingBidOutputBoundary,
) -> PlacingBid:
    return PlacingBid(
        output_boundary=placing_bid_output_boundary,
        auctions_repo=auctions_repo,
        event_bus=event_bus,
    )


@pytest.fixture()
def auctions_repo() -> AuctionsRepository:
    return InMemoryAuctionsRepository()


@pytest.fixture()
def event_bus() -> EventBus:
    return Mock(spec_set=EventBus)


@pytest.fixture()
def placing_bid_output_boundary() -> Mock:
    return Mock(spec_set=PlacingBidOutputBoundary)
