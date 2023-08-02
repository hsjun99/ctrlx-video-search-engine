from fastapi.encoders import jsonable_encoder
from supabase import Client, create_client

from app.model import VideoType, VideoMetaDataType

from typing import List

from app.constants import SUPABASE_URL, SUPABASE_KEY

TABLE_NAME = "search_videos"


class VideoRepository:
    supabase: Client
    table_name: str

    def __init__(self) -> None:
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table_name = TABLE_NAME

    def sb_get_video(self, video_uid: str) -> VideoType:
        res = (
            self.supabase.table(self.table_name)
            .select("*")
            .eq("uid", video_uid)
            .single()
            .execute()
        )

        ret = VideoType(**res.data)

        return ret

    def sb_update_video(
        self,
        video_uid: str,
        video_state: str = None,
        video_metadata: VideoMetaDataType = None,
    ):
        update_dict = {}
        if video_state is not None:
            update_dict["state"] = video_state
        if video_metadata is not None:
            update_dict["metadata"] = jsonable_encoder(video_metadata)

        res = (
            self.supabase.table(self.table_name)
            .update(update_dict)
            .eq("uid", video_uid)
            .execute()
        )

        return res
