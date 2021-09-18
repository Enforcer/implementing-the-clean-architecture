from attr import define

from itca.auctions import AuctionsRepository
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions.domain.value_objects.bidder_id import BidderId


@define(frozen=True)
class FinalizingAuctionInputDto:
    auction_id: AuctionId
    bidder_id: BidderId


@define
class FinalizingAuction:
    _auctions_repo: AuctionsRepository

    def execute(self, input_dto: FinalizingAuctionInputDto) -> None:
        auction = self._auctions_repo.get(input_dto.auction_id)
        auction.finalize(input_dto.bidder_id)
        # self._payments. ?
        self._auctions_repo.save(auction)
