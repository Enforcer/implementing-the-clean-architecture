import injector

from itca.auctions.app.queries.auction_details import (
    AuctionDetails,
    AuctionDetailsDto,
)
from itca.auctions.app.repositories.auctions import AuctionsRepository
from itca.auctions.app.repositories.auctions_descriptors import (
    AuctionsDescriptorsRepository,
)
from itca.auctions.app.use_cases.finalizing_auction import (
    FinalizingAuction,
    FinalizingAuctionInputDto,
)
from itca.auctions.app.use_cases.placing_bid import (
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from itca.auctions.app.use_cases.starting_auction import (
    StartingAuction,
    StartingAuctionInputDto,
)
from itca.auctions.domain.events.auction_ended import AuctionEnded
from itca.auctions.domain.events.bidder_has_been_overbid import (
    BidderHasBeenOverbid,
)
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.foundation.event_bus import EventBus

__all__ = [
    # Module
    "Auctions",
    # Use Cases
    "PlacingBid",
    "FinalizingAuction",
    "StartingAuction",
    # Queries
    "AuctionDetails",
    # DTOs
    "PlacingBidInputDto",
    "PlacingBidOutputDto",
    "AuctionDetailsDto",
    "FinalizingAuctionInputDto",
    "StartingAuctionInputDto",
    # Output Boundaries
    "PlacingBidOutputBoundary",
    # Repositories
    "AuctionsRepository",
    "AuctionsDescriptorsRepository",
    # Types
    "AuctionId",
    # Events
    "BidderHasBeenOverbid",
    "AuctionEnded",
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

    @injector.provider
    def starting_auction(
        self,
        auctions_repo: AuctionsRepository,
        auctions_descriptors_repo: AuctionsDescriptorsRepository,
    ) -> StartingAuction:
        return StartingAuction(
            auctions_repo=auctions_repo,
            auctions_descriptors_repo=auctions_descriptors_repo,
        )
