from contextlib import contextmanager
from typing import Iterator
from unittest.mock import Mock

import pytest
from injector import Injector

from itca.auctions import AuctionDetails, AuctionDetailsDto, AuctionEnded
from itca.customer_relationship import CustomerRelationshipFacade
from itca.foundation.money import USD, Money
from itca.payments import PaymentsFacade
from itca.processes.exceptions import InvalidRequest
from itca.processes.locking import Lock
from itca.processes.paying_for_won_auction import (
    PayingForWonAuctionProcess,
    PayingForWonAuctionStateRepository,
)


class AuctionDetailsStub(AuctionDetails):
    def query(self, auction_id: int) -> AuctionDetailsDto:
        return AuctionDetailsDto(
            auction_id=auction_id,
            title="Test",
            current_price=Money(USD, "9.99"),
            starting_price=Money(USD, "1.00"),
            top_bidders=[],
        )


def test_cannot_be_started_twice_for_the_same_auction(
    pm: PayingForWonAuctionProcess,
) -> None:
    event = AuctionEnded(auction_id=1, winner_id=2, price=Money(USD, "9.99"))
    pm(event)

    with pytest.raises(InvalidRequest):
        pm(event)


@pytest.fixture()
def pm(container: Injector) -> PayingForWonAuctionProcess:
    repo = container.get(PayingForWonAuctionStateRepository)  # type: ignore
    return PayingForWonAuctionProcess(
        payments=Mock(spec_set=PaymentsFacade),
        customer_relationship=Mock(spec_set=CustomerRelationshipFacade),
        auction_details=AuctionDetailsStub(),
        repository=repo,
        locks=DummyLock(),
    )


class DummyLock(Lock):
    @contextmanager
    def acquire(self, name: str, expires_after: int, wait_for: int) -> Iterator:
        yield
