from typing import List

# from pydantic import parse_obj_as

from .celery_app import celery_app

from app.services import IndexService


@celery_app.task()
def index_video(video_uid: str):
    index_service = IndexService()
    index_service.index_plain_videos(video_uid=video_uid)
    # index_service.index_youtube_videos(youtube_urls)
