from datetime import datetime

from attr import define

from itca.auctions import AuctionsRepository
from itca.auctions.app.repositories.auctions_descriptors import (
    AuctionsDescriptorsRepository,
)
from itca.auctions.domain.entities.auction import Auction
from itca.auctions.domain.entities.auction_descriptor import AuctionDescriptor
from itca.foundation.money import Money


@define(frozen=True)
class StartingAuctionInputDto:
    stating_price: Money
    end_time: datetime
    title: str
    description: str


@define
class StartingAuction:
    _auctions_repo: AuctionsRepository
    _auctions_descriptors_repo: AuctionsDescriptorsRepository

    def execute(self, dto: StartingAuctionInputDto) -> None:
        descriptor = AuctionDescriptor(
            title=dto.title,
            description=dto.description,
        )
        self._auctions_descriptors_repo.add(descriptor)
        self._auctions_repo.save(
            Auction(
                id=descriptor.id,
                starting_price=dto.stating_price,
                bids=[],
                ends_at=dto.end_time,
            )
        )
