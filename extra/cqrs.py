from typing import Generic, TypeVar, Any

import injector
from attr import define
from injector import Injector, Binder

from itca.auctions import AuctionId
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.money import Money, USD

T = TypeVar("T")


class PlacingBidOutputBoundary:
    pass


class AuctionsRepository:
    pass


TCommand = TypeVar("TCommand")  # 1


class Handler(Generic[TCommand]):  # 2
    def __call__(self, command: TCommand) -> None:
        pass


class CommandBus:
    def __init__(self, container: Injector) -> None:  # 3
        self._container = container

    def dispatch(self, command: Any) -> None:
        handler = self._container.get(Handler[type(command)])  # 4
        handler(command)  # 5


# PlacingBidInputDto staje się samodzielną Komendą
@define(frozen=True)
class PlaceBid:  # 1
    bidder_id: BidderId
    auction_id: AuctionId
    amount: Money


@define
class PlaceBidHandler:  # 2
    _boundary: PlacingBidOutputBoundary
    _repo: AuctionsRepository

    def __call__(self, command: PlaceBid) -> None:
        ...


class Auctions(injector.Module):
    @injector.provider
    def place_bid_handler(  # 3
        self,
        boundary: PlacingBidOutputBoundary,
        repo: AuctionsRepository,
    ) -> Handler[PlaceBid]:
        return PlaceBidHandler(boundary, repo)


c = Injector([Auctions()])
command_bus = CommandBus(c)
command_bus.dispatch(
    PlaceBid(auction_id=1, bidder_id=1, amount=Money(USD, "1"))
)
