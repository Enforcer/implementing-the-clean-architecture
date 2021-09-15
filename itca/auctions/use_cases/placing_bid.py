import abc
from dataclasses import dataclass

from itca.auctions.repositories.auctions import AuctionsRepository
from itca.auctions.value_objects.auction_id import AuctionId
from itca.auctions.value_objects.bidder_id import BidderId
from itca.foundation.money import Money


@dataclass(frozen=True)
class PlacingBidOutputDto:
    is_winning: bool
    current_price: Money


class PlacingBidOutputBoundary(abc.ABC):
    @abc.abstractmethod
    def present(self, dto: PlacingBidOutputDto) -> None:
        pass


@dataclass(frozen=True)
class PlacingBidInputDto:
    bidder_id: BidderId
    auction_id: AuctionId
    amount: Money


class PlacingBid:
    def __init__(
        self,
        output_boundary: PlacingBidOutputBoundary,
        auctions_repo: AuctionsRepository,
    ) -> None:
        self._output_boundary = output_boundary
        self._auctions_repo = auctions_repo

    def execute(self, input_dto: PlacingBidInputDto) -> None:
        auction = self._auctions_repo.get(input_dto.auction_id)
        auction.place_bid(
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
