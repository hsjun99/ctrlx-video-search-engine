from app.supabase import VideoRepository
from app.model import (
    VideoType,
    VideoMetaDataType,
)

from typing import List


class VideoService:
    def __init__(self):
        self.video_repository: VideoRepository = VideoRepository()

    def get(self, video_uid: str) -> VideoType:
        video: VideoType = self.video_repository.sb_get_video(video_uid)

        return video

    def get_all_video_uids(self) -> List[str]:
        video_uids: List[str] = self.video_repository.sb_get_all_video_uids()

        return video_uids

    def update(
        self,
        video_uid: str,
        video_state: str = None,
        video_metadata: VideoMetaDataType = None,
    ) -> None:
        self.video_repository.sb_update_video(
            video_uid,
            video_state,
            video_metadata,
        )
