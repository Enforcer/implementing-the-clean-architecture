from celery import Celery

app = Celery("itca", broker="redis://localhost:6379/0")
