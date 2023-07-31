def timecode_to_float(timecode: str) -> float:
    h, m, s = timecode.split(":")

    return int(h) * 3600 + int(m) * 60 + float(s)


def get_dir_from_video_id(video_id: str) -> str:
    return f"./app/files/video/{video_id}"
