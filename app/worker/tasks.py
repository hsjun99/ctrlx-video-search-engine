from typing import List
from pydantic import parse_obj_as

from .celery_app import celery_app

from app.services import IndexService


@celery_app.task()
def index_video(youtube_urls: List[str]):
    index_service = IndexService()
