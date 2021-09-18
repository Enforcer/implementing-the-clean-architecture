import requests
from attr import define
from yarl import URL

from itca.auctions.app.ports.payments import CardId, PaymentFailed, Payments
from itca.auctions.domain.value_objects.bidder_id import BidderId
from itca.foundation.money import Money


@define
class CardDto:
    id: CardId
    last_4_digits: str
    processing_network: str


CustomerId = int


class BripePayments(Payments):
    def __init__(self, username: str, password: str, base_url: str) -> None:
        self._basic_auth = (username, password)
        self._base_url = base_url

    def pay(self, token: str, amount: Money) -> None:
        response = requests.post(
            url=str(URL(self._base_url) / "api/v1/charge"),
            auth=self._basic_auth,
            json={
                "card_token": token,
                "currency": amount.currency.iso_code,
                "amount": int(amount.amount * 100),
            },
        )
        if not response.ok:
            raise PaymentFailed

    def pay_with_selected_card(
        self, bidder_id: BidderId, card_id: CardId, amount: Money
    ) -> None:
        ...

    def list_of_remembered_cards(
        self, customer_id: CustomerId
    ) -> list[CardDto]:
        ...

    def remember_card(self, token: str) -> None:
        ...
