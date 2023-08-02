from app.constants import MIME_TYPES
from app.model import VideoType


def timecode_to_float(timecode: str) -> float:
    h, m, s = timecode.split(":")

    return int(h) * 3600 + int(m) * 60 + float(s)


def get_dir_from_video_uid(video_uid: str) -> str:
    return f"./app/files/video/{video_uid}"


def get_video_file_path(video: VideoType) -> str:
    return f"{get_dir_from_video_uid(video_id=video.uid)}/{video.uid}.{MIME_TYPES[video.metadata.type]}"
