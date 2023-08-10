from app.constants import MIME_TYPES
from app.model import VideoType


def timecode_to_float(timecode: str) -> float:
    h, m, s = timecode.split(":")

    return int(h) * 3600 + int(m) * 60 + float(s)


def check_time_overlap(start1=float, end1=float, start2=float, end2=float) -> bool:
    # Calculate overlap
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    overlap = max(0, overlap_end - overlap_start)

    # Calculate lengths of intervals
    length1 = end1 - start1
    length2 = end2 - start2

    # Check if overlap is more than 60% of either interval
    if overlap >= 0.7 * length1 or overlap >= 0.7 * length2:
        return True
    else:
        return False


def get_s3_key_from_video(video: VideoType) -> str:
    return f"search/{video.org_uid}/{video.uid}/{video.uid}"


def get_dir_from_video_uid(video_uid: str) -> str:
    return f"./app/files/video/{video_uid}"


def get_video_file_path(video: VideoType) -> str:
    file_extension = "mp4"
    if video.metadata is not None and video.metadata.type is not None:
        file_extension = MIME_TYPES[video.metadata.type]
    return f"{get_dir_from_video_uid(video_uid=video.uid)}/{video.uid}.{file_extension}"
