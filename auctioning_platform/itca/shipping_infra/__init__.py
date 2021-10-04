import injector
from sqlalchemy.orm import Session

from itca.event_sourcing import SynchronousProjection
from itca.shipping_infra.projections.order_summary import OrderSummaryProjection

__all__ = [
    # Module
    "ShippingInfra",
]


class ShippingInfra(injector.Module):
    @injector.multiprovider
    def sync_order_summary_projection(
        self, session: Session
    ) -> list[SynchronousProjection]:
        return [
            OrderSummaryProjection(session=session),
        ]
