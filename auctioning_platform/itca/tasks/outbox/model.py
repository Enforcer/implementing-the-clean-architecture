from sqlalchemy import BigInteger, Column, Integer, String

from itca.db import JSONB, Base


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    listener = Column(String(), nullable=False)
    event = Column(String(), nullable=False)
    event_payload = Column(JSONB(), nullable=False)
