from typing import Tuple, Type, TypeVar

import requests

from itca.foundation.money import Money
from itca.payments.api.exceptions import PaymentFailedError
from itca.payments.api.requests import CaptureRequest, ChargeRequest, Request
from itca.payments.api.responses import CaptureResponse, ChargeResponse

ResponseCls = TypeVar("ResponseCls")


class ApiConsumer:
    def __init__(self, login: str, password: str) -> None:
        self._basic_auth = login, password

    def charge(self, card_token: str, amount: Money) -> str:
        currency, converted_amount = self._get_iso_code_and_amount(amount)
        request = ChargeRequest(card_token, currency, str(converted_amount))
        response = self._execute_request(request, ChargeResponse)
        return response.charge_uuid

    def capture(self, charge_id: str) -> None:
        request = CaptureRequest(charge_id)
        self._execute_request(request, CaptureResponse)

    def _execute_request(
        self, request: Request, response_cls: Type[ResponseCls]
    ) -> ResponseCls:
        response = requests.post(
            request.url, auth=self._basic_auth, json=request.to_params()
        )
        if not response.ok:
            raise PaymentFailedError
        else:
            return response_cls.from_dict(response.json())  # type: ignore

    def _get_iso_code_and_amount(self, money_amount: Money) -> Tuple[str, int]:
        return money_amount.currency.iso_code, int(money_amount.amount * 100)
