from sqlalchemy import BigInteger, Column, Integer

from itca.db import JSONB, Base


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    starting_price = Column(JSONB(), nullable=False)
