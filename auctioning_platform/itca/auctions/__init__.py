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

__all__ = [
    # module
    "Auctions",
    # Use Cases
    "PlacingBid",
    "PlacingBidInputDto",
    "PlacingBidOutputDto",
    "PlacingBidOutputBoundary",
    # Queries
    "AuctionDetails",
    "AuctionDetailsDto",
]


class Auctions(injector.Module):
    @injector.provider
    def placing_bid(
        self,
        output_boundary: PlacingBidOutputBoundary,
        auctions_repo: AuctionsRepository,
    ) -> PlacingBid:
        return PlacingBid(
            output_boundary=output_boundary, auctions_repo=auctions_repo
        )
