from sqlalchemy import BigInteger, Column, DateTime, Index, String

from itca.db import GUID, JSONB, Base


class Aggregate(Base):
    __tablename__ = "aggregates"

    uuid = Column(GUID(), primary_key=True)
    version = Column(BigInteger(), nullable=False)


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index(
            "ix_events_aggregate_version",
            "aggregate_uuid",
            "version",
        ),
    )
    uuid = Column(GUID, primary_key=True)
    aggregate_uuid = Column(GUID(), nullable=False)
    name = Column(String(50), nullable=False)
    data = Column(JSONB(), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    version = Column(BigInteger(), nullable=False)
