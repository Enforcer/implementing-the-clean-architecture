from flask import Response, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session

from itca.api.auctions.blueprint import auctions_blueprint
from itca.auctions import AuctionDetails
from itca.auctions_infra import auction_read_model
from itca.foundation.serde import converter


@auctions_blueprint.get("/<int:auction_id>")
def auction(
    auction_id: int,
    auction_details: AuctionDetails,
) -> Response:
    data = auction_details.query(auction_id=auction_id)
    return jsonify(converter.unstructure(data))


@auctions_blueprint.get("/read_model/<int:auction_id>")
def auction_via_read_model(
    auction_id: int,
    session: Session,
) -> Response:
    stmt = select(auction_read_model).filter(
        auction_read_model.c.id == auction_id
    )
    row = session.execute(stmt).first()
    return jsonify(dict(row))
