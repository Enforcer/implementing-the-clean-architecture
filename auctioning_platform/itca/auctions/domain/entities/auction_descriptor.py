import attr

from itca.auctions.domain.value_objects.auction_id import AuctionId


@attr.s(auto_attribs=True)
class AuctionDescriptor:
    id: AuctionId = attr.ib(init=False)
    title: str
    description: str
