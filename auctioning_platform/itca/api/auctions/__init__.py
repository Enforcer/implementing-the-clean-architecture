import flask_injector
import injector

from itca.api.auctions.auction import auction  # noqa: F401
from itca.api.auctions.bid import PlacingBidWebPresenter
from itca.auctions import PlacingBidOutputBoundary


class AuctionsWeb(injector.Module):
    @flask_injector.request
    @injector.provider
    def placing_bid_output_boundary(self) -> PlacingBidOutputBoundary:
        return PlacingBidWebPresenter()
