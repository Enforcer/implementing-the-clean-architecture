from flask import Response, jsonify

from itca.api.auctions.blueprint import auctions_blueprint
from itca.auctions import AuctionDetails
from itca.foundation.serde import converter


@auctions_blueprint.get("/<int:auction_id>")
def auction(
    auction_id: int,
    auction_details: AuctionDetails,
) -> Response:
    data = auction_details.query(auction_id=auction_id)
    return jsonify(converter.unstructure(data))
