from contextlib import contextmanager
from functools import singledispatchmethod
from typing import Iterator

from attr import define

from itca.auctions import AuctionDetails, AuctionEnded
from itca.customer_relationship import CustomerRelationshipFacade
from itca.foundation.event import Event
from itca.payments import PaymentCaptured, PaymentsFacade
from itca.processes.locking import Lock
from itca.processes.paying_for_won_auction.repository import (
    PayingForWonAuctionStateRepository,
)
from itca.processes.paying_for_won_auction.state import PayingForWonAuctionState
from itca.shipping import ConsignmentShipped


@define
class PayingForWonAuctionProcess:
    _payments: PaymentsFacade
    _customer_relationship: CustomerRelationshipFacade
    _auction_details: AuctionDetails
    _repository: PayingForWonAuctionStateRepository
    _locks: Lock

    @singledispatchmethod
    def __call__(self, event: Event) -> None:
        raise NotImplementedError(f"Unknown event - {event}")

    @__call__.register
    def _handle_auction_ended(self, event: AuctionEnded) -> None:
        if not (state := self._repository.get_by_auction(event.auction_id)):
            state = PayingForWonAuctionState(
                auction_id=event.auction_id,
                winner_id=event.winner_id,
                winning_bid=event.price,
            )
            self._repository.add(state)

        with self._lock(state) as locked_state:
            del state  # we should not operate on it anymore after lock
            locked_state.generate_payment_uuid()

            auction_dto = self._auction_details.query(
                auction_id=event.auction_id
            )
            self._customer_relationship.notify_about_winning_auction(
                customer_id=event.winner_id,
                auction_id=event.auction_id,
                auction_title=auction_dto.title,
                amount=event.price,
            )
            self._payments.start_new_payment(
                payment_uuid=locked_state.payment_uuid,
                customer_id=event.winner_id,
                amount=event.price,
                description=f"For item won at auction {auction_dto.title}",
            )

    @__call__.register
    def _handle_payment_captured(self, event: PaymentCaptured) -> None:
        state = self._repository.get_by_payment(event.payment_uuid)
        with self._lock(state) as locked_state:
            del state
            locked_state.finish_payment()
            ...

    @__call__.register
    def _handle_consignment_shipped(self, event: ConsignmentShipped) -> None:
        pass

    @contextmanager
    def _lock(
        self, state: PayingForWonAuctionState
    ) -> Iterator[PayingForWonAuctionState]:
        with self._locks.acquire(
            name=f"{self.__class__.__name__}_{state.auction_id}",
            expires_after=60,
            wait_for=1,
        ):
            yield self._repository.get_by_auction(state.auction_id)
