from pathlib import Path

import pytest
import vcr

from itca.auctions.app.ports.payments import PaymentFailed
from itca.auctions_infra.adapters.payments import BripePayments
from itca.foundation.money import EUR, USD, Money


@vcr.use_cassette(str(Path(__file__).parent / "bripe_success.yml"))
def test_doesnt_raise_exception_if_payment_succeeds(
    payments: BripePayments,
) -> None:
    try:
        payments.pay(token="IRRELEVANT", amount=Money(USD, "10"))
    except PaymentFailed:
        pytest.fail("Failed when it should succeed!")


@vcr.use_cassette(str(Path(__file__).parent / "bripe_failure.yml"))
def test_raises_exception_when_request_fails(payments: BripePayments) -> None:
    with pytest.raises(PaymentFailed):
        payments.pay(token="", amount=Money(EUR, "5"))


@pytest.fixture()
def payments() -> BripePayments:
    return BripePayments(
        username="test", password="test", base_url="http://localhost:5050/"
    )
