import requests
from yarl import URL

from itca.auctions.app.ports.payments import PaymentFailed, Payments
from itca.foundation.money import Money


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
