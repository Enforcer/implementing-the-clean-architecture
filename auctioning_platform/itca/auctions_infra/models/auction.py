from sqlalchemy import BigInteger, Column

from itca.db import JSONB, Base


class Auction(Base):
    __tablename__ = "auctions"

    id = Column(BigInteger(), primary_key=True)
    starting_price = Column(JSONB(), nullable=False)
