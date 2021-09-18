from attr import define
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from itca.auctions import AuctionDetails, AuctionDetailsDto
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions_infra.models import Auction, AuctionDescriptor, Bid
from itca.foundation.money import Money
from itca.foundation.serde import converter


@define
class SqlAlchemyAuctionDetails(AuctionDetails):
    _session: Session

    def query(self, auction_id: AuctionId) -> AuctionDetailsDto:
        auction_stmt = (
            select(Auction, AuctionDescriptor)
            .join(AuctionDescriptor, AuctionDescriptor.id == Auction.id)
            .filter(Auction.id == auction_id)
        )
        try:
            auction, descriptor = self._session.execute(auction_stmt).one()
        except NoResultFound:
            raise AuctionDetails.NotFound

        top_bids_stmt = (
            select(Bid)
            .filter(Bid.auction_id == auction_id)
            .order_by(Bid.id.desc())
            .limit(3)
        )
        top_bids: list[Bid] = self._session.execute(top_bids_stmt).scalars()

        return AuctionDetailsDto(
            auction_id=auction.id,
            title=descriptor.title,
            current_price=converter.structure(auction.current_price, Money),
            starting_price=converter.structure(auction.starting_price, Money),
            top_bidders=[
                AuctionDetailsDto.TopBidder(
                    anonymized_name=f"Bidder #{bid.bidder_id}",
                    bid_amount=converter.structure(bid.amount, Money),
                )
                for bid in top_bids
            ],
        )
