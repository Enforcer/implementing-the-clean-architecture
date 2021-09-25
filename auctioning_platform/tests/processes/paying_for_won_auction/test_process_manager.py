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


def test_cannot_be_started_twice_for_the_same_auction(
    pm: PayingForWonAuctionProcess, auction_details: Mock
) -> None:
    auction_details.query.return_value = AuctionDetailsDto(
        auction_id=1,
        title="Test",
        current_price=Money(USD, "9.99"),
        starting_price=Money(USD, "1.00"),
        top_bidders=[],
    )
    event = AuctionEnded(auction_id=1, winner_id=2, price=Money(USD, "9.99"))
    pm(event)

    with pytest.raises(InvalidRequest):
        pm(event)


@pytest.fixture()
def pm(
    container: Injector, auction_details: Mock
) -> PayingForWonAuctionProcess:
    repo = container.get(PayingForWonAuctionStateRepository)  # type: ignore
    return PayingForWonAuctionProcess(
        payments=Mock(spec_set=PaymentsFacade),
        customer_relationship=Mock(spec_set=CustomerRelationshipFacade),
        auction_details=auction_details,
        repository=repo,
        locks=DummyLock(),
    )


@pytest.fixture()
def auction_details() -> Mock:
    return Mock(spec_set=AuctionDetails)


class DummyLock(Lock):
    @contextmanager
    def acquire(self, name: str, expires_after: int, wait_for: int) -> Iterator:
        yield
