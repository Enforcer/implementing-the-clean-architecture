import importlib
import logging
from typing import Type

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from itca.foundation.serde import converter
from itca.tasks.app import app
from itca.tasks.outbox.model import OutboxMessage

logger = logging.getLogger(__name__)


@app.task()
def send_out_from_outbox() -> None:
    session: Session = app.__container__.get(Session)
    with session.begin():
        pending_stmt = select(OutboxMessage).limit(100)

        messages: list[OutboxMessage] = (
            session.execute(pending_stmt).scalars().all()
        )
        logger.error("Sending out %d messages", len(messages))
        for message in messages:
            execute_listener.delay(
                message.listener, message.event, message.event_payload
            )

        delete_stmt = delete(OutboxMessage).filter(
            OutboxMessage.id.in_([message.id for message in messages])
        )
        session.execute(delete_stmt)


@app.task()
def execute_listener(
    listener_class_name: str, event_cls_name: str, event_payload: str
) -> None:
    listener_cls = get_cls_by_qualified_name(listener_class_name)
    event_cls = get_cls_by_qualified_name(event_cls_name)
    event = converter.structure(event_payload, event_cls)

    listener = app.__container__.get(listener_cls)
    listener(event)


def get_cls_by_qualified_name(qualified_name: str) -> Type:
    mod_name, class_name = qualified_name.rsplit(".", maxsplit=1)
    module = importlib.import_module(mod_name)
    return getattr(module, class_name)
