import os
from typing import List

from app.model import VideoType, SegmentType

from app.services import IOService

from app.utils import transcribe_audio, get_dir_from_video_id


class AudioService:
    def __init__(self):
        pass

    def transcribe(self, video_id: str) -> List[SegmentType]:
        dir = get_dir_from_video_id(video_id)

        segments: List[SegmentType] = transcribe_audio(
            file_path=f"{dir}/{video_id}.mp3"
        )

        return segments
