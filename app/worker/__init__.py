from .celery_app import celery_app
from .tasks import (
    index_plain_video,
    index_youtube_video_final_step,
    index_youtube_video_first_step,
    task_inference,
)
