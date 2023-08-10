from typing import List

from pydantic import parse_obj_as

from app.model import VideoType, SegmentType, VideoState

from .celery_app import celery_app

from app.services import IndexService, VideoService


@celery_app.task()
def index_plain_video(video_uid: str):
    index_service = IndexService()
    index_service.index_plain_video(video_uid=video_uid)


@celery_app.task()
def index_youtube_video_first_step(video_uid: str, youtube_url: str):
    index_service = IndexService()

    video: VideoType = index_service.index_youtube_video(
        video_uid=video_uid, youtube_url=youtube_url
    )

    return {"video": video.dict()}


@celery_app.task()
def index_youtube_video_final_step(data):
    index_service = IndexService()
    video_service = VideoService()

    video: VideoType = parse_obj_as(VideoType, data["video"])
    error: str = data.get("error", None)

    try:
        if error is not None:
            print("ERROR")
            raise Exception(error)

        segments: List[SegmentType] = [
            parse_obj_as(SegmentType, item) for item in data["segments"]
        ]

        index_service.index_audio(video=video, transcript=segments)

    except Exception as e:
        print(e)
        video_service.update(
            video_uid=video.uid,
            video_state=VideoState.READY,
        )


task_inference = celery_app.signature("transcribe_audio", queue="queue_inference")
