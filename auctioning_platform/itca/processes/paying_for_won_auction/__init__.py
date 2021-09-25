import injector
from sqlalchemy.orm import Session

from itca.auctions import AuctionDetails, AuctionEnded
from itca.customer_relationship import CustomerRelationshipFacade
from itca.foundation.event_bus import AsyncEventListenerProvider, AsyncListener
from itca.payments import PaymentCaptured, PaymentsFacade
from itca.processes.paying_for_won_auction.process_manager import (
    PayingForWonAuctionProcess,
)
from itca.processes.paying_for_won_auction.repository import (
    PayingForWonAuctionStateRepository,
)
from itca.processes.paying_for_won_auction.sql_alchemy_repository import (
    SqlAStateRepository,
)
from itca.shipping import ConsignmentShipped


class PayingForWonAuctionModule(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(
            AsyncListener[AuctionEnded],
            to=AsyncEventListenerProvider(PayingForWonAuctionProcess),
        )
        binder.multibind(
            AsyncListener[PaymentCaptured],
            to=AsyncEventListenerProvider(PayingForWonAuctionProcess),
        )
        binder.multibind(
            AsyncListener[ConsignmentShipped],
            to=AsyncEventListenerProvider(PayingForWonAuctionProcess),
        )

    @injector.provider
    def paying_for_won_auction_process(
        self,
        payments: PaymentsFacade,
        customer_relationship: CustomerRelationshipFacade,
        auction_details: AuctionDetails,
        repository: PayingForWonAuctionStateRepository,
    ) -> PayingForWonAuctionProcess:
        return PayingForWonAuctionProcess(
            payments=payments,
            customer_relationship=customer_relationship,
            auction_details=auction_details,
            repository=repository,
        )

    @injector.provider
    def repository(
        self, session: Session
    ) -> PayingForWonAuctionStateRepository:
        return SqlAStateRepository(session=session)
