from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import registry, relationship, sessionmaker

from itca.auctions import AuctionId
from itca.auctions.domain.value_objects.bidder_id import BidderId


from sqlalchemy import create_engine, MetaData


engine = create_engine("sqlite://", echo=True)
Session = sessionmaker(bind=engine)

metadata = MetaData()
mapper_registry = registry(metadata=metadata)


session = Session()


@mapper_registry.mapped
@dataclass
class Bid:
    __tablename__ = "bids"
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )
    bidder_id: BidderId = field(metadata={"sa": Column(Integer)})
    amount: Decimal = field(metadata={"sa": Column(Numeric)})
    auction_id: AuctionId = field(
        init=False, metadata={"sa": Column(ForeignKey("auctions.id"))}
    )


@mapper_registry.mapped
@dataclass
class Auction:
    __tablename__ = "auctions"
    __sa_dataclass_metadata_key__ = "sa"

    id: int = field(
        init=False, metadata={"sa": Column(Integer, primary_key=True)}
    )
    starting_price: Decimal = field(metadata={"sa": Column(Numeric)})
    bids: list[Bid] = field(
        default_factory=list, metadata={"sa": relationship("Bid")}
    )

    def place_bid(self, bidder_id: BidderId, amount: Decimal) -> None:
        ...
        self.bids.append(Bid(bidder_id=bidder_id, amount=amount))


metadata.create_all(bind=engine)

auction = Auction(starting_price=Decimal("10.00"))
session.add(auction)
session.flush()

auction.place_bid(bidder_id=1, amount=Decimal("15.00"))
session.flush()
