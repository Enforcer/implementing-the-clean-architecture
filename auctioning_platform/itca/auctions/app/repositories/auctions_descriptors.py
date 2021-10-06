import abc

from itca.auctions.domain.entities.auction_descriptor import AuctionDescriptor
from itca.auctions.domain.value_objects.auction_id import AuctionId


class AuctionsDescriptorsRepository(abc.ABC):
    class NotFound(Exception):
        pass

    @abc.abstractmethod
    def get(self, auction_id: AuctionId) -> AuctionDescriptor:
        pass

    @abc.abstractmethod
    def add(self, descriptor: AuctionDescriptor) -> None:
        pass

    @abc.abstractmethod
    def delete(self, descriptor: AuctionDescriptor) -> None:
        pass
