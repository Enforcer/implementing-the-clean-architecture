from celery import Celery
from injector import Injector

ATTRIBUTE = "__container__"


def install(app: Celery, container: Injector) -> None:
    setattr(app, ATTRIBUTE, container)
