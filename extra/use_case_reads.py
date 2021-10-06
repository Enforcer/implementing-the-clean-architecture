from attr import define

from itca.auctions import AuctionsRepository
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.foundation.money import Money


@define(frozen=True)
class GettingAuctionDetailsInputDto:
    auction_id: AuctionId


@define(frozen=True)
class GettingAuctionDetailsOutputDto:
    @define(frozen=True)
    class TopBidder:
        anonymized_name: str
        bid_amount: Money

    auction_id: AuctionId
    title: str
    current_price: Money
    starting_price: Money
    top_bidders: list[TopBidder]


class GettingAuctionDetailsOutputBoundary:
    def present(self, dto: GettingAuctionDetailsOutputDto) -> None:
        pass


class Bidder:
    username: str


class BiddersRepository:
    def get(self, bidder_id) -> Bidder:
        pass


class AuctionDescriptor:
    title: str


class AuctionsDescriptorsRepository:
    def get(self, auction_id) -> AuctionDescriptor:
        pass


@define
class GettingAuctionDetails:
    _output_boundary: GettingAuctionDetailsOutputBoundary
    _auctions_repo: AuctionsRepository
    _auctions_descriptors_repo: AuctionsDescriptorsRepository
    _bidders_repo: BiddersRepository

    def execute(self, input_dto: GettingAuctionDetailsInputDto) -> None:
        auction = self._auctions_repo.get(input_dto.auction_id)  # 1
        descriptor = self._auctions_descriptors_repo.get(
            input_dto.auction_id
        )  # 2
        top_bids = auction.get_top_bids(count=3)  # 3

        top_bidders = []
        for bid in top_bids:
            bidder = self._bidders_repo.get(bid.bidder_id)  # 4
            anonymized_name = f"{bidder.username[0]}..."
            top_bidders.append(
                GettingAuctionDetailsOutputDto.TopBidder(
                    anonymized_name, bid.amount
                )
            )

        output_dto = GettingAuctionDetailsOutputDto(  # 5
            auction_id=auction.id,
            title=descriptor.title,
            current_price=auction.current_price,
            starting_price=auction.starting_price,
            top_bidders=top_bidders,
        )
        self._output_boundary.present(output_dto)
