# https://docs.sqlalchemy.org/en/14/orm/mapping_styles.html#imperative-mapping-with-dataclasses-and-attrs
import attr

from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    create_engine,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import registry, sessionmaker, relationship, composite

from itca.foundation.money import Money, Currency, USD

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

AuctionId = int
BidderId = int

auctions = Table(
    "auctions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("starting_price_amount", Numeric()),
    Column("starting_price_currency", String(3)),
)


bids = Table(
    "bids",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("auction_id", Integer, ForeignKey("auctions.id")),
    Column("amount_amount", Numeric()),
    Column("amount_currency", String(3)),
)


@attr.s(auto_attribs=True)
class Bid:
    _id: int = attr.ib(init=False)
    _bidder_id: BidderId
    _amount: Money


@attr.s(auto_attribs=True)
class Auction:
    _id: int = attr.ib(init=False)
    _starting_price: Money
    _bids: list[Bid] = attr.ib(factory=list)

    def place_bid(self, bid: Bid) -> None:
        ...
        self._bids.append(bid)


mapper_registry.map_imperatively(
    Auction,
    auctions,
    properties={
        "_bids": relationship(Bid),
        "_starting_price": composite(
            lambda currency_code, amount: Money(
                Currency.from_code(currency_code), amount
            ),
            auctions.c.starting_price_currency,
            auctions.c.starting_price_amount,
        ),
    },
    column_prefix="_",
)
mapper_registry.map_imperatively(
    Bid,
    bids,
    properties={
        "_amount": composite(
            lambda currency_code, amount: Money(
                Currency.from_code(currency_code), amount
            ),
            bids.c.amount_currency,
            bids.c.amount_amount,
        ),
    },
    column_prefix="_",
)


engine = create_engine("sqlite:///db.sqlite", echo=True)
metadata.drop_all(bind=engine)
metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


session = Session()
session.query(Auction).all()
some_auction = Auction(starting_price=Money(USD, "0.99"))
some_auction.place_bid(Bid(bidder_id=1, amount=Money(USD, "10.99")))

session.add(some_auction)
session.commit()


def get_auction() -> Auction:
    # .options(raiseload('*'))
    user_instance: Auction = session.query(Auction).one()
    # assert user_instance.id  # i tak mypy sie czepia
    return user_instance


us_instance = get_auction()
# assert us_instance.id
print(us_instance, us_instance._id + 2)
