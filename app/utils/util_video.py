from typing import List
from yt_dlp import YoutubeDL
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

from .util_functions import timecode_to_float, get_dir_from_video_id

from app.model import VideoSplitType


def get_youtube_video_title(youtube_url: str) -> str:
    try:
        yt = YouTube(youtube_url)

        title = yt.title

        return title
    except Exception as e:
        print(e)
        raise e


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


def download_youtube_audio(youtube_url: str, save_path: str) -> None:
    try:
        with YoutubeDL(
            {
                "extract_audio": True,
                "format": "bestaudio",
                "outtmpl": save_path,
            }
        ) as video:
            video.download(youtube_url)
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


def split_video_into_scenes(
    video_id: str, threshold: float = 40.0
) -> List[VideoSplitType]:
    dir = get_dir_from_video_id(video_id)
    video_path = f"{dir}/{video_id}.mp4"

    video = open_video(video_path)

    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video, show_progress=True)
    data = scene_manager.get_scene_list()

    scene_list: List[VideoSplitType] = []
    for item in data:
        start = timecode_to_float(item[0].get_timecode())
        end = timecode_to_float(item[1].get_timecode())
        scene_list.append(
            VideoSplitType(
                start="{:.2f}".format(start),
                end="{:.2f}".format(end),
                video_id=video_id,
            )
        )

    return scene_list
