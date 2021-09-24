import injector
from attr import define

from itca.auctions import AuctionDetails, BidderHasBeenOverbid
from itca.customer_relationship.facade import CustomerRelationshipFacade
from itca.foundation.event_bus import (
    AsyncEventListenerProvider,
    AsyncListener,
    Listener,
)


@define
class OnBidderHasBeenOverbid(Listener[BidderHasBeenOverbid]):  # type: ignore
    _facade: CustomerRelationshipFacade
    _auction_details: AuctionDetails

    def __call__(self, event: BidderHasBeenOverbid) -> None:
        auction_dto = self._auction_details.query(event.auction_id)
        self._facade.notify_about_overbid(
            customer_id=event.bidder_id,
            auction_id=event.auction_id,
            auction_title=auction_dto.title,
            new_price=event.new_price,
        )


class CustomerRelationship(injector.Module):
    @injector.provider
    def facade(self) -> CustomerRelationshipFacade:
        return CustomerRelationshipFacade()

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(
            AsyncListener[BidderHasBeenOverbid],
            to=AsyncEventListenerProvider(OnBidderHasBeenOverbid),
        )

    @injector.provider
    def on_bidder_has_been_overbid(
        self,
        customer_relationship_facade: CustomerRelationshipFacade,
        auction_details: AuctionDetails,
    ) -> OnBidderHasBeenOverbid:
        return OnBidderHasBeenOverbid(
            facade=customer_relationship_facade,
            auction_details=auction_details,
        )
