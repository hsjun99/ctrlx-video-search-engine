from typing import List
import os


from app.services import IOService, ProcessService
from app.utils import (
    download_youtube_video,
    extract_youtube_video_id,
    vectorize_image_by_clip,
    get_dir_from_video_id,
    split_video_into_scenes,
)

from app.model import VideoSplitType


class IndexService:
    def __init__(self):
        self.io_service = IOService()
        self.process_service = ProcessService()

    def index_youtube_video(self, youtube_urls: List[str]):
        # TODO: Implement this
        video_ids = List[str] = [None for _ in youtube_urls]

        # 1. Download video
        for index, youtube_url in enumerate(youtube_urls):
            try:
                video_id: str = extract_youtube_video_id(youtube_url=youtube_url)
                video_ids[index] = video_id

                dir = get_dir_from_video_id(video_id)
                self.io_service.create_directory(dir)

                download_youtube_video(
                    youtube_url=youtube_url, save_path=f"{dir}/{video_id}.mp4"
                )

            except Exception:
                video_ids[index] = None
                continue

        # 2. Retrieve Frames
        # 3. Vectorize Frames Using CLIP
        # 4. Split Video By Scene
        for index, video_id in enumerate(video_ids):
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)

            self.process_service.extract_frames(
                file_path=f"{dir}/{video_id}.mp4", save_path=dir
            )

            i = 1
            while os.path.isfile(f"{dir}/{i:04}.png"):
                vectorize_image_by_clip(image_path=f"{dir}/{i:04}.png")
                i += 1

            scene_list: List[VideoSplitType] = split_video_into_scenes(
                video_id=video_id
            )

        # 5. Vectorize Scenes

        # 6. Remove Assets
        for video_id in video_ids:
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)
            self.io_service.remove_directory(dir)
