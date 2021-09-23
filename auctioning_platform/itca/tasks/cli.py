import os
from typing import Any

from celery import Celery

from itca.main import assemble
from itca.tasks import celery_injector
from itca.tasks.app import app
from itca.tasks.outbox.tasks import send_out_from_outbox

config_path = os.environ.get("CONFIG_PATH", "config.ini")
container = assemble(config_path=config_path)
celery_injector.install(app, container)


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs: Any) -> None:
    sender.add_periodic_task(
        1.0, send_out_from_outbox.s(), name="Send out from outbox"
    )
