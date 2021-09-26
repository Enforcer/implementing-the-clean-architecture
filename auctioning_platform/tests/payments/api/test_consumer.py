from pathlib import Path

import pytest
import vcr

from itca.foundation.money import USD, Money
from itca.payments.api import ApiConsumer, PaymentFailedError


@vcr.use_cassette(str(Path(__file__).parent / "bripe_charge_then_capture.yml"))
def test_capture_after_charge_succeeds(
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
