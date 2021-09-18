import pytest

from itca.auctions import AuctionsRepository
from tests.doubles.in_memory_auctions_repo import InMemoryAuctionsRepository


@pytest.fixture()
def repo() -> AuctionsRepository:
    return InMemoryAuctionsRepository()
