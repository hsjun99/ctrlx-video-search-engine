from celery import Celery

from app.constants import RABBITMQ_SERVER

celery_app = Celery("worker", broker=RABBITMQ_SERVER)
