from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs


def timecode_to_float(timecode: str) -> float:
    h, m, s = timecode.split(":")

    return int(h) * 3600 + int(m) * 60 + float(s)


def download_youtube_video(youtube_url: str, save_path: str) -> None:
    try:
        ydl_opts = {
            "format": "best",
            "outtmpl": save_path,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        print(e)
        raise e


def extract_youtube_video_id(youtube_url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(youtube_url)

    if parsed_url.netloc == "youtu.be":
        # If the URL is a 'youtu.be' URL, the video ID is the path
        return parsed_url.path[1:]

    if parsed_url.netloc in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            # If the URL is a regular YouTube watch URL,
            # the video ID is in the 'v' query parameter
            return parse_qs(parsed_url.query).get("v")[0]
        if parsed_url.path[:7] == "/embed/":
            # If the URL is an embed URL, the video ID is in the path
            return parsed_url.path.split("/")[2]
        if parsed_url.path[:3] == "/v/":
            # If the URL is a shortened /v/ URL, the video ID is in the path
            return parsed_url.path.split("/")[2]

    # If none of the above cases are met, raise an error
    raise ValueError("Invalid YouTube URL")
