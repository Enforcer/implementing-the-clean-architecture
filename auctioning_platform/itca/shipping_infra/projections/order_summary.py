import enum
from functools import singledispatchmethod
from uuid import UUID

from attr import define
from sqlalchemy import BigInteger, Column, DateTime, Enum, Integer
from sqlalchemy.orm import Session

from itca.db import GUID, JSONB, Base
from itca.event_sourcing.event import EsEvent
from itca.event_sourcing.projection import SynchronousProjection
from itca.foundation.money import USD, Money
from itca.foundation.serde import converter
from itca.shipping.domain.aggregates.order import (
    OrderDrafted,
    OrderPaid,
    ProductAdded,
)


class OrderStatus(enum.Enum):
    DRAFT = "DRAFT"
    PAID = "PAID"


class OrderSummary(Base):
    __tablename__ = "order_summaries"

    uuid = Column(GUID(), primary_key=True)
    version = Column(BigInteger(), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    total_quantity = Column(Integer(), nullable=False)
    total_price = Column(JSONB(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    def set_updated_at_and_version_for(self, event: EsEvent) -> None:
        self.version = event.version
        self.updated_at = event.created_at


@define
class OrderSummaryProjection(SynchronousProjection):
    _session: Session

    def __call__(self, events: list[EsEvent]) -> None:
        if not events:
            return

        model = self._get_model(events[0].aggregate_uuid)

        for event in events:
            self._project(event, model)
            model.set_updated_at_and_version_for(event)

    def _get_model(self, aggregate_uuid: UUID) -> OrderSummary:
        model = self._session.query(OrderSummary).get(aggregate_uuid)
        if not model:
            model = OrderSummary(uuid=aggregate_uuid)
            self._session.add(model)

        return model

    @singledispatchmethod
    def _project(self, event: EsEvent, model: OrderSummary) -> None:
        pass

    @_project.register
    def _project_drafted(
        self, event: OrderDrafted, model: OrderSummary
    ) -> None:
        model.status = OrderStatus.DRAFT
        model.total_quantity = 0
        model.total_price = converter.unstructure(Money(USD, 0))

    @_project.register
    def _project_product_added(
        self, event: ProductAdded, model: OrderSummary
    ) -> None:
        model.total_quantity += event.quantity
        old_total = converter.structure(model.total_price, Money)
        new_total = old_total + (event.unit_price * event.quantity)
        model.total_price = converter.unstructure(new_total)

    @_project.register
    def _project_paid(self, event: OrderPaid, model: OrderSummary) -> None:
        model.status = OrderStatus.PAID
