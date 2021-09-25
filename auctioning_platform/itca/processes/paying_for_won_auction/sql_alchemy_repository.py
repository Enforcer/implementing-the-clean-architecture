from uuid import UUID

from attr import define
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.orm import Session, composite

from itca.db import GUID, mapper_registry
from itca.foundation.money import Currency, Money
from itca.processes.paying_for_won_auction import (
    PayingForWonAuctionStateRepository,
)
from itca.processes.paying_for_won_auction.state import PayingForWonAuctionState

paying_for_won_auction_pm_table = Table(
    "paying_for_won_auction_pm",
    mapper_registry.metadata,
    Column(
        "auction_id",
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
    ),
    Column("winner_id", BigInteger(), nullable=False),
    Column("winning_bid_currency", String(3), nullable=False),
    Column("winning_bid_amount", Numeric(), nullable=False),
    Column("payment_uuid", GUID(), nullable=False),
    Column("payment_finished_at", DateTime(timezone=True), nullable=True),
    Column("shipment_started_at", DateTime(timezone=True), nullable=True),
    Column("shipment_sent_at", DateTime(timezone=True), nullable=True),
)


mapper_registry.map_imperatively(
    PayingForWonAuctionState,
    paying_for_won_auction_pm_table,
    properties={
        "_winning_bid": composite(
            lambda currency_code, amount: Money(
                Currency.from_code(currency_code), amount
            ),
            paying_for_won_auction_pm_table.c.winning_bid_currency,
            paying_for_won_auction_pm_table.c.winning_bid_amount,
        ),
    },
    column_prefix="_",
)


@define
class SqlAStateRepository(PayingForWonAuctionStateRepository):
    _session: Session

    def get_by_auction(self, auction_id: int) -> PayingForWonAuctionState:
        return (
            self._session.query(PayingForWonAuctionState)
            .filter_by(_auction_id=auction_id)
            .first()
        )

    def get_by_payment(self, payment_uuid: UUID) -> PayingForWonAuctionState:
        pass

    def add(self, state: PayingForWonAuctionState) -> None:
        self._session.add(state)
