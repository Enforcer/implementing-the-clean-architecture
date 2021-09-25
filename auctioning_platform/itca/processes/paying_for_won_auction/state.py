from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

import attr

from itca.foundation.money import Money
from itca.processes.exceptions import InvalidRequest


@attr.s(auto_attribs=True)
class PayingForWonAuctionState:
    _auction_id: int
    _winner_id: int
    _winning_bid: Money
    _payment_uuid: Optional[UUID] = None
    _payment_finished_at: Optional[datetime] = None
    _shipment_started_at: Optional[datetime] = None
    _shipment_sent_at: Optional[datetime] = None

    def generate_payment_uuid(self) -> None:
        if self._payment_uuid is not None:
            raise InvalidRequest
        self._payment_uuid = uuid4()

    @property
    def auction_id(self) -> int:
        return self._auction_id

    @property
    def payment_uuid(self) -> UUID:
        assert self._payment_uuid, "Begin it first!"
        return self._payment_uuid

    def finish_payment(self) -> None:
        if self._payment_finished_at:
            raise InvalidRequest
        self._payment_finished_at = datetime.now(tz=timezone.utc)

    def ship_item(self) -> None:
        if self._shipment_started_at:
            raise InvalidRequest
        self._shipment_started_at = datetime.now(tz=timezone.utc)

    def shipment_complete(self) -> None:
        if self._shipment_sent_at:
            raise InvalidRequest
        self._shipment_sent_at = datetime.now(tz=timezone.utc)
