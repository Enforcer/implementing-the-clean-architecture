import injector
from sqlalchemy.orm import Session

from itca.auctions import AuctionDetails, AuctionsRepository
from itca.auctions_infra.queries.auction_details import SqlAlchemyAuctionDetails
from itca.auctions_infra.read_models.auction_details import auction_read_model
from itca.auctions_infra.repositories.auctions import (
    SqlAlchemyAuctionsRepository,
)

__all__ = [
    # Module
    "AuctionsInfra",
    # Read models
    "auction_read_model",
]


class AuctionsInfra(injector.Module):
    @injector.provider
    def auctions_repo(self, session: Session) -> AuctionsRepository:
        return SqlAlchemyAuctionsRepository(session=session)

    @injector.provider
    def auction_details(self, session: Session) -> AuctionDetails:
        return SqlAlchemyAuctionDetails(session)
