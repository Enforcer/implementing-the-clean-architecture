from attr import define
from sqlalchemy import select
from sqlalchemy.orm import Session

from itca.auctions.app.repositories.auctions import AuctionsRepository
from itca.auctions.domain.entities.auction import Auction
from itca.auctions.domain.value_objects.auction_id import AuctionId
from itca.auctions_infra.models.auction import Auction as AuctionModel
from itca.auctions_infra.models.bid import Bid as BidModel
from itca.foundation.serde import converter


@define
class SqlAlchemyAuctionsRepository(AuctionsRepository):
    _session: Session

    def get(self, auction_id: AuctionId) -> Auction:
        bids = self._session.execute(
            select(BidModel.__table__).where(BidModel.auction_id == auction_id)
        )
        auction_row = self._session.execute(
            select(AuctionModel.__table__).where(AuctionModel.id == auction_id)
        ).one()

        auction_vars = {
            f"_{key}": value for key, value in dict(auction_row).items()
        }
        return converter.structure(
            {"_bids": bids, **auction_vars},
            Auction,
        )

    def save(self, auction: Auction) -> None:
        dict_repr = converter.unstructure(auction)
        self._session.merge(
            AuctionModel(
                id=auction.id,
                starting_price=dict_repr["_starting_price"],
                ends_at=dict_repr["_ends_at"],
            )
        )
        for bid in dict_repr["_bids"]:
            self._session.merge(
                BidModel(
                    id=bid["id"],
                    amount=bid["amount"],
                    bidder_id=bid["bidder_id"],
                    auction_id=auction.id,
                )
            )
        self._session.flush()
