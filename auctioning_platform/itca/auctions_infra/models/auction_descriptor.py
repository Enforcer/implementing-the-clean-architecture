from sqlalchemy import BigInteger, Column, Integer, String, Table

from itca.db import Base, metadata

auction_descriptors = Table(
    "auctions_descriptors",
    metadata,
    Column(
        "id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    ),
    Column("title", String(), nullable=False),
    Column("description", String(), nullable=False),
)


class AuctionDescriptor(Base):
    __table__ = auction_descriptors
