from typing import List
import os, json

import numpy as np

import faiss

from pydantic import parse_obj_as

from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = "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"

from app.services import IOService, ProcessService, AudioService
from app.utils import (
    download_youtube_video,
    download_youtube_audio,
    get_youtube_video_title,
    extract_youtube_video_id,
    vectorize_image_by_clip,
    get_dir_from_video_id,
    split_video_into_scenes,
)

from app.model import (
    VideoSplitType,
    VideoType,
    FrameMetaDataType,
    SegmentType,
    WordType,
    TranscriptMetadataType,
)

from app.constants import FAISS_DIMENSION

from concurrent.futures import ThreadPoolExecutor


class IndexService:
    def __init__(self):
        self.io_service = IOService()
        self.process_service = ProcessService()
        self.audio_service = AudioService()
        self.metadata: List[VideoSplitType] = []
        self.frame_metadata: List[FrameMetaDataType] = []
        self.transcript_metadata: List[TranscriptMetadataType] = []
        self.video_list: List[VideoType] = []
        self.vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)
        self.frame_vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)
        self.transcript__vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)

        if os.path.isfile("./app/files/metadata.json"):
            with open("./app/files/metadata.json", "r") as f:
                self.metadata = parse_obj_as(List[VideoSplitType], json.load(f))
        if os.path.isfile("./app/files/frame_metadata.json"):
            with open("./app/files/frame_metadata.json", "r") as f:
                self.frame_metadata = parse_obj_as(
                    List[FrameMetaDataType], json.load(f)
                )
        if os.path.isfile("./app/files/transcript_metadata.json"):
            with open("./app/files/transcript_metadata.json", "r") as f:
                self.transcript_metadata = parse_obj_as(
                    List[TranscriptMetadataType], json.load(f)
                )
        if os.path.isfile("./app/files/video_list.json"):
            with open("./app/files/video_list.json", "r") as f:
                self.video_list = parse_obj_as(List[VideoType], json.load(f))
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
            current_index = self.frame_vectorstore.ntotal
            self.frame_vectorstore.add(frame_vector)
            self.frame_metadata.append(
                FrameMetaDataType(index=current_index, frame=i, video_id=video_id)
            )
            i += 1

        return saved_vectors

    def _split_video(self, video_id: str) -> List[VideoSplitType]:
        return split_video_into_scenes(video_id=video_id)

    def _transcribe_audio(self, video_id: str) -> List[TranscriptMetadataType]:
        transcript: List[SegmentType] = self.audio_service.transcribe(video_id=video_id)

        current_index = self.transcript__vectorstore.ntotal
        embeddings = OpenAIEmbeddings()
        doc_result = embeddings.embed_documents(
            [segment.text for segment in transcript]
        )
        # print(doc_result)

        for segment in transcript:
            self.transcript_metadata.append(
                TranscriptMetadataType(
                    index=current_index,
                    video_id=video_id,
                    start=segment.start,
                    end=segment.end,
                )
            )

    def index_youtube_videos(self, youtube_urls: List[str]):
        # TODO: Implement this
        video_ids: List[str] = [None for _ in youtube_urls]

        for index, youtube_url in enumerate(youtube_urls):
            try:
                video_id: str = extract_youtube_video_id(youtube_url=youtube_url)
                dir = get_dir_from_video_id(video_id)
                self.io_service.create_directory(dir)

                title = get_youtube_video_title(youtube_url=youtube_url)
                self.video_list.append(
                    VideoType(title=title, video_id=video_id, status="PENDING")
                )
            except Exception:
                continue

        with open("./app/files/video_list.json", "w") as f:
            json.dump([item.dict() for item in self.video_list], f)

        # 1. Download video
        for index, youtube_url in enumerate(youtube_urls):
            try:
                video_id: str = extract_youtube_video_id(youtube_url=youtube_url)
                video_ids[index] = video_id

                dir = get_dir_from_video_id(video_id)

                download_youtube_video(
                    youtube_url=youtube_url, save_path=f"{dir}/{video_id}.mp4"
                )
                # download_youtube_audio(
                #     youtube_url=youtube_url, save_pathf="{dir}/{video_id}.mp3"
                # )

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

        for item in self.video_list:
            item.status = "SUCCESS"

        with open("./app/files/metadata.json", "w") as f:
            json.dump([item.dict() for item in self.metadata], f)
        with open("./app/files/frame_metadata.json", "w") as f:
            json.dump([item.dict() for item in self.frame_metadata], f)
        with open("./app/files/video_list.json", "w") as f:
            json.dump([item.dict() for item in self.video_list], f)
        faiss.write_index(self.frame_vectorstore, "./app/files/frame_faiss_index")
        faiss.write_index(self.vectorstore, "./app/files/faiss_index")

        # 6. Remove Assets
        for video_id in video_ids:
            if video_id is None:
                continue
            dir = get_dir_from_video_id(video_id)
            self.io_service.remove_directory(dir)
