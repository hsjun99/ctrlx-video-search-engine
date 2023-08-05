from typing import List

from app.model import SegmentType

from app.services import IOService

from app.utils import transcribe_audio, get_dir_from_video_uid


class TranscribeService:
    def __init__(self):
        pass

    def transcribe(self, video_uid: str) -> List[SegmentType]:
        dir = get_dir_from_video_uid(video_uid)

        segments: List[SegmentType] = transcribe_audio(
            file_path=f"{dir}/{video_uid}.mp3"
        )

        return segments
