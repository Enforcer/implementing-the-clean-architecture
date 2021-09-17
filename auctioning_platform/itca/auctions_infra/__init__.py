import injector
from sqlalchemy.orm import Session

from itca.auctions import AuctionsRepository
from itca.auctions_infra.repositories.auctions import (
    SqlAlchemyAuctionsRepository,
)


class AuctionsInfra(injector.Module):
    @injector.provider
    def auctions_repo(self, session: Session) -> AuctionsRepository:
        return SqlAlchemyAuctionsRepository(session=session)
