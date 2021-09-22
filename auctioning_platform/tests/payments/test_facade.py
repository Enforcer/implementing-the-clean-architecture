import uuid
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from _pytest.fixtures import SubRequest
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import RowProxy

from itca.db import metadata
from itca.foundation.event_bus import EventBus
from itca.foundation.money import USD, Money
from itca.payments.api import ApiConsumer
from itca.payments.api.exceptions import PaymentFailedError
from itca.payments.config import PaymentsConfig
from itca.payments.dao import PaymentDto, PaymentStatus
from itca.payments.events import (
    PaymentCaptured,
    PaymentCharged,
    PaymentFailed,
    PaymentStarted,
)
from itca.payments.facade import PaymentsFacade
from itca.payments.models import payments


@pytest.fixture()
def connection() -> Connection:
    engine = create_engine("sqlite://", future=True, echo=True)
    metadata.create_all(bind=engine)
    return engine.connect()


@pytest.fixture()
def event_bus() -> Mock:
    return Mock(spec_set=EventBus)


@pytest.fixture()
def facade(connection: Connection, event_bus: Mock) -> PaymentsFacade:
    return PaymentsFacade(PaymentsConfig("", ""), connection, event_bus)


@pytest.fixture()
def inserted_payment(request: SubRequest, connection: Connection) -> dict:
    status = getattr(request, "param", None) or PaymentStatus.NEW.value
    charge_id = (
        None
        if status
        not in (PaymentStatus.CHARGED.value, PaymentStatus.CAPTURED.value)
        else "token"
    )
    data: Dict[str, Any] = {
        "uuid": str(uuid.uuid4()),
        "customer_id": 1,
        "amount": 100,
        "currency": "USD",
        "status": status,
        "description": "irrelevant",
        "charge_id": charge_id,
    }
    connection.execute(payments.insert(data))
    return data


def get_payment(connection: Connection, payment_uuid: str) -> RowProxy:
    row = connection.execute(
        payments.select(payments.c.uuid == payment_uuid)
    ).first()
    return row


def test_adding_new_payment_is_reflected_on_pending_payments_list(
    facade: PaymentsFacade, event_bus: Mock
) -> None:
    customer_id = 1
    assert facade.get_pending_payments(customer_id) == []

    payment_uuid = uuid.uuid4()
    amount = Money(USD, "15.00")
    description = "Example"
    facade.start_new_payment(payment_uuid, customer_id, amount, description)

    pending_payments = facade.get_pending_payments(customer_id)

    assert pending_payments == [
        PaymentDto(payment_uuid, amount, description, PaymentStatus.NEW.value)
    ]
    event_bus.publish.assert_called_once_with(
        PaymentStarted(payment_uuid, customer_id)
    )


@pytest.mark.parametrize(
    "inserted_payment",
    [status.value for status in PaymentStatus if status != PaymentStatus.NEW],
    indirect=["inserted_payment"],
)
def test_pending_payments_returns_only_new_payments(
    facade: PaymentsFacade, inserted_payment: dict
) -> None:
    assert facade.get_pending_payments(inserted_payment["customer_id"]) == []


def test_successful_charge_updates_status(
    facade: PaymentsFacade,
    inserted_payment: dict,
    connection: Connection,
    event_bus: Mock,
) -> None:
    payment_uuid = uuid.UUID(inserted_payment["uuid"])
    charge_id = "SOME_CHARGE_ID"

    with patch.object(
        ApiConsumer, "charge", return_value=charge_id
    ) as charge_mock:
        facade.charge(
            uuid.UUID(inserted_payment["uuid"]),
            inserted_payment["customer_id"],
            "token",
        )

    charge_mock.assert_called_once_with(
        "token", Money(USD, inserted_payment["amount"] / 100)
    )
    payment_row = get_payment(connection, inserted_payment["uuid"])
    assert payment_row.status == PaymentStatus.CHARGED.value
    assert payment_row.charge_id == charge_id
    event_bus.publish.assert_called_once_with(
        PaymentCharged(payment_uuid, inserted_payment["customer_id"])
    )


def test_unsuccessful_charge(
    facade: PaymentsFacade,
    inserted_payment: dict,
    connection: Connection,
    event_bus: Mock,
) -> None:
    payment_uuid = uuid.UUID(inserted_payment["uuid"])

    with patch.object(
        ApiConsumer, "charge", side_effect=PaymentFailedError
    ) as charge_mock:
        facade.charge(payment_uuid, inserted_payment["customer_id"], "token")

    charge_mock.assert_called_once_with(
        "token", Money(USD, inserted_payment["amount"] / 100)
    )
    assert (
        get_payment(connection, inserted_payment["uuid"]).status
        == PaymentStatus.FAILED.value
    )
    event_bus.publish.assert_called_once_with(
        PaymentFailed(payment_uuid, inserted_payment["customer_id"])
    )


@pytest.mark.parametrize(
    "inserted_payment",
    [PaymentStatus.CHARGED.value],
    indirect=["inserted_payment"],
)
def test_capture(
    facade: PaymentsFacade,
    inserted_payment: dict,
    connection: Connection,
    event_bus: Mock,
) -> None:
    payment_uuid = uuid.UUID(inserted_payment["uuid"])
    with patch.object(ApiConsumer, "capture") as capture_mock:
        facade.capture(payment_uuid, inserted_payment["customer_id"])

    capture_mock.assert_called_once_with(inserted_payment["charge_id"])
    assert (
        get_payment(connection, inserted_payment["uuid"]).status
        == PaymentStatus.CAPTURED.value
    )
    event_bus.publish.assert_called_once_with(
        PaymentCaptured(payment_uuid, inserted_payment["customer_id"])
    )
