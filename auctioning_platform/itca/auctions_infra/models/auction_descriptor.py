from sqlalchemy import BigInteger, Column, Integer, String

from itca.db import Base


class AuctionDescriptor(Base):
    __tablename__ = "auctions_descriptors"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
