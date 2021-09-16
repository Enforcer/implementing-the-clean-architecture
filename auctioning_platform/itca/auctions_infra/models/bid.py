from sqlalchemy import BigInteger, Column, ForeignKey

from itca.db import JSONB, Base


class Bid(Base):
    __tablename__ = "bids"

    id = Column(BigInteger(), primary_key=True)
    amount = Column(JSONB(), nullable=False)
    bidder_id = Column(BigInteger(), nullable=False)
    auction_id = Column(BigInteger(), ForeignKey("auctions.id"), nullable=False)
