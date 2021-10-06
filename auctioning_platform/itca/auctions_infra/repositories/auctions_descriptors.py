from attr import define
from sqlalchemy.orm import Session

from itca.auctions import AuctionId, AuctionsDescriptorsRepository
from itca.auctions.domain.entities.auction_descriptor import AuctionDescriptor


@define
class SqlAlchemyAuctionsDescriptorsRepository(AuctionsDescriptorsRepository):
    _session: Session

    def get(self, auction_id: AuctionId) -> AuctionDescriptor:
        raise NotImplementedError

    def add(self, descriptor: AuctionDescriptor) -> None:
        self._session.add(descriptor)
        self._session.flush([descriptor])

    def delete(self, descriptor: AuctionDescriptor) -> None:
        raise NotImplementedError
