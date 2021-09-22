import pytest

from itca.foundation.money import USD, Money
from itca.payments.api import ApiConsumer, PaymentFailedError


def test_charge_then_capture(
    api_consumer: ApiConsumer, card_token: str
) -> None:
    charge_id = api_consumer.charge(card_token, Money(USD, "15.00"))

    try:
        api_consumer.capture(charge_id)
    except PaymentFailedError:
        pytest.fail("Should not fail!")


@pytest.fixture()
def api_consumer() -> ApiConsumer:
    return ApiConsumer("test", "test")


@pytest.fixture()
def card_token() -> str:
    return "irrevelant"
