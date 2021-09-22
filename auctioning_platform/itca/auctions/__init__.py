import injector

from itca.auctions.app.queries.auction_details import (
    AuctionDetails,
    AuctionDetailsDto,
)
from itca.auctions.app.repositories.auctions import AuctionsRepository
from itca.auctions.app.use_cases.placing_bid import (
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.foundation.event_bus import EventBus

__all__ = [
    # Module
    "Auctions",
    # Use Cases
    "PlacingBid",
    # Queries
    "AuctionDetails",
    # DTOs
    "PlacingBidInputDto",
    "PlacingBidOutputDto",
    "AuctionDetailsDto",
    # Output Boundaries
    "PlacingBidOutputBoundary",
    # Repositories
    "AuctionsRepository",
    # Types
    "AuctionId",
]


class Auctions(injector.Module):
    @injector.provider
    def placing_bid(
        self,
        output_boundary: PlacingBidOutputBoundary,
        auctions_repo: AuctionsRepository,
    ) -> PlacingBid:
        return PlacingBid(
            output_boundary=output_boundary,
            auctions_repo=auctions_repo,
            event_bus=EventBus(),
        )
