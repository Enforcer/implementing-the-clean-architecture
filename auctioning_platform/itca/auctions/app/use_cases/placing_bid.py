import abc
from dataclasses import dataclass
from typing import Any

from attr import define

from itca.auctions.app.repositories.auctions import AuctionsRepository
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.event_bus import EventBus
from itca.foundation.money import Money


@dataclass(frozen=True)
class PlacingBidOutputDto:
    is_winning: bool
    current_price: Money


class PlacingBidOutputBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: PlacingBidOutputDto) -> None:
        pass

    @abc.abstractmethod
    def get_presented_value(self) -> Any:
        pass


@dataclass(frozen=True)
class PlacingBidInputDto:
    bidder_id: BidderId
    auction_id: AuctionId
    amount: Money


@define
class PlacingBid:
    _output_boundary: PlacingBidOutputBoundary
    _auctions_repo: AuctionsRepository
    _event_bus: EventBus

    def execute(self, input_dto: PlacingBidInputDto) -> None:
        auction = self._auctions_repo.get(input_dto.auction_id)
        events = auction.place_bid(
            bidder_id=input_dto.bidder_id, amount=input_dto.amount
        )
        self._auctions_repo.save(auction)

        is_winning = input_dto.bidder_id == auction.winner
        self._output_boundary.present(
            PlacingBidOutputDto(
                is_winning=is_winning,
                current_price=auction.current_price,
            )
        )

        for event in events:
            self._event_bus.publish(event)
