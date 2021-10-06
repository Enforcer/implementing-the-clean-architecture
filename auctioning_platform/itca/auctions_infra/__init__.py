import injector
from sqlalchemy.orm import Session

from itca.auctions import (
    AuctionDetails,
    AuctionsDescriptorsRepository,
    AuctionsRepository,
)
from itca.auctions.domain.entities.auction_descriptor import AuctionDescriptor
from itca.auctions_infra.models import auction_descriptors
from itca.auctions_infra.queries.auction_details import SqlAlchemyAuctionDetails
from itca.auctions_infra.read_models.auction_details import auction_read_model
from itca.auctions_infra.repositories.auctions import (
    SqlAlchemyAuctionsRepository,
)
from itca.auctions_infra.repositories.auctions_descriptors import (
    SqlAlchemyAuctionsDescriptorsRepository,
)
from itca.db import mapper_registry

__all__ = [
    # Module
    "AuctionsInfra",
    # Read models
    "auction_read_model",
]


class AuctionsInfra(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        mapper_registry.map_imperatively(
            AuctionDescriptor,
            auction_descriptors,
        )

    @injector.provider
    def auctions_repo(self, session: Session) -> AuctionsRepository:
        return SqlAlchemyAuctionsRepository(session=session)

    @injector.provider
    def auctions_descriptors_repo(
        self, session: Session
    ) -> AuctionsDescriptorsRepository:
        return SqlAlchemyAuctionsDescriptorsRepository(session=session)

    @injector.provider
    def auction_details(self, session: Session) -> AuctionDetails:
        return SqlAlchemyAuctionDetails(session)
