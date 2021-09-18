from typing import Any

from flask import Response, abort, jsonify, make_response, request

from itca.api.auctions.blueprint import auctions_blueprint
from itca.auctions import (
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from itca.foundation.serde import converter


class current_user:
    """Little fake until Flask-Login is in place"""

    is_authenticated: bool = True
    id = 44


class PlacingBidWebPresenter(PlacingBidOutputBoundary):
    _response: Response

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        if output_dto.is_winning:
            message = "Hooray! You are a winner"
        else:
            message = (
                f"Your bid is too low. "
                f"Current price is {output_dto.current_price}"
            )
        self._response = make_response(jsonify({"message": message}))

    def get_presented_value(self) -> Any:
        return self._response


@auctions_blueprint.post("/<int:auction_id>/bids")
def place_bid(
    auction_id: int,
    placing_bid_uc: PlacingBid,
    presenter: PlacingBidOutputBoundary,
) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    input_dto = converter.structure(
        {
            **request.json,  # type: ignore
            **{"auction_id": auction_id, "bidder_id": current_user.id},
        },
        PlacingBidInputDto,
    )
    placing_bid_uc.execute(input_dto)
    return presenter.get_presented_value()
