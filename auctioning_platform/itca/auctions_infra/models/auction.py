from sqlalchemy import BigInteger, Column, DateTime, Integer

from itca.db import JSONB, Base


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    starting_price = Column(JSONB(), nullable=False)
    current_price = Column(JSONB(), nullable=False)
    ends_at = Column(DateTime(), nullable=False)
