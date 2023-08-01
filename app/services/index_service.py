from typing import List
import os, json

import numpy as np

import faiss

from pydantic import parse_obj_as

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

from concurrent.futures import ThreadPoolExecutor


class IndexService:
    def __init__(self):
        self.io_service = IOService()
        self.process_service = ProcessService()
        self.metadata: List[VideoSplitType] = []
        self.vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)
        self.frame_vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)

        if os.path.isfile("./app/files/metadata.json"):
            with open("./app/files/metadata.json", "r") as f:
                self.metadata = parse_obj_as(List[VideoSplitType], json.load(f))
        if os.path.isfile("./app/files/faiss_index"):
            self.vectorstore = faiss.read_index("./app/files/faiss_index")
        if os.path.isfile("./app/files/frame_faiss_index"):
            self.frame_vectorstore = faiss.read_index("./app/files/frame_faiss_index")

    def _extract_frames_and_vectorize(self, video_id: str) -> List[np.ndarray]:
        saved_vectors: List[np.ndarray] = []
        dir = get_dir_from_video_id(video_id)

        self.process_service.extract_frames(
            file_path=f"{dir}/{video_id}.mp4", save_path=dir
        )

        i = 1
        while os.path.isfile(f"{dir}/{i:04}.png"):
            frame_vector = vectorize_image_by_clip(image_path=f"{dir}/{i:04}.png")
            saved_vectors.append(frame_vector)

            # faiss.normalize_L2(frame_vector)
            self.frame_vectorstore.add(frame_vector)
            i += 1

        return saved_vectors

    def _split_video(self, video_id: str) -> List[VideoSplitType]:
        return split_video_into_scenes(video_id=video_id)

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

            with ThreadPoolExecutor() as executor:
                frame_vector_future = executor.submit(
                    lambda: self._extract_frames_and_vectorize(video_id=video_id)
                )
                scene_list_future = executor.submit(
                    lambda: self._split_video(video_id=video_id)
                )
                saved_vectors = frame_vector_future.result()
                scene_list = scene_list_future.result()

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

                    init_emb = np.zeros((1, FAISS_DIMENSION))
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

                    # faiss.normalize_L2(init_emb.astype(np.float32))

                    current_index = self.vectorstore.ntotal
                    self.vectorstore.add(init_emb)
                    self.metadata.append(
                        VideoSplitType(
                            index=current_index,
                            start=scene_list[start_index].start,
                            end=scene_list[end_index].end,
                            video_id=video_id,
                        )
                    )

        with open("./app/files/metadata.json", "w") as f:
            json.dump([item.dict() for item in self.metadata], f)
        faiss.write_index(self.frame_vectorstore, "./app/files/frame_faiss_index")
        faiss.write_index(self.vectorstore, "./app/files/faiss_index")

        # 6. Remove Assets
        for video_id in video_ids:
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)
            self.io_service.remove_directory(dir)
