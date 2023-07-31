from typing import List
import os, json

import numpy as np

import faiss

from app.services import IOService, ProcessService
from app.utils import (
    download_youtube_video,
    extract_youtube_video_id,
    vectorize_image_by_clip,
    get_dir_from_video_id,
    split_video_into_scenes,
)

from app.model import VideoSplitType

from app.constants import FAISS_DIMENSION


class IndexService:
    def __init__(self):
        self.io_service = IOService()
        self.process_service = ProcessService()
        self.metadata = []
        self.vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)

        if os.path.isfile("./app/files/metadata.json"):
            with open("./app/files/metadata.json", "r") as f:
                self.metadata = json.load(f)
        if os.path.isfile("./app/files/faiss_index"):
            self.vectorstore = faiss.read_index("faiss_index")

    def index_youtube_videos(self, youtube_urls: List[str]):
        # TODO: Implement this
        video_ids: List[str] = [None for _ in youtube_urls]

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
        # 5. Vectorize Scenes

        for index, video_id in enumerate(video_ids):
            saved_vectors: List[np.ndarray] = []
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)

            self.process_service.extract_frames(
                file_path=f"{dir}/{video_id}.mp4", save_path=dir
            )

            i = 1
            while os.path.isfile(f"{dir}/{i:04}.png"):
                frame_vector = vectorize_image_by_clip(image_path=f"{dir}/{i:04}.png")
                saved_vectors.append(frame_vector)
                i += 1

            scene_list: List[VideoSplitType] = split_video_into_scenes(
                video_id=video_id
            )

            for min_length in [3, 5]:
                for start_index, scene in enumerate(scene_list):
                    end_index = None
                    for i in range(start_index + 1, len(scene_list)):
                        end_index = i
                        if (
                            scene_list[end_index].end - scene_list[start_index].start
                            >= min_length
                        ):
                            break

                    if (
                        end_index is None
                        or scene_list[end_index].end - scene_list[start_index].start
                        <= 0
                    ):
                        continue

                    init_emb = np.zeros((1, 512))
                    cnt = 0
                    start_sec = round(scene_list[start_index].start)
                    end_sec = round(scene_list[end_index].end)
                    for i in range(start_sec, end_sec + 1):
                        if i >= len(saved_vectors):
                            break
                        init_emb += saved_vectors[i - 1]
                        cnt += 1
                    if cnt == 0:
                        continue

                    init_emb /= cnt

                    current_index = self.vectorstore.ntotal
                    self.vectorstore.add(init_emb)
                    self.metadata.append(
                        {
                            "index": current_index,
                            "start": scene_list[start_index].start,
                            "end": scene_list[end_index].end,
                            "video_id": video_id,
                        }
                    )

        with open("./app/files/metadata.json", "w") as f:
            json.dump(self.metadata, f)

        faiss.write_index(self.vectorstore, "./app/files/faiss_index")

        # 6. Remove Assets
        for video_id in video_ids:
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)
            self.io_service.remove_directory(dir)
