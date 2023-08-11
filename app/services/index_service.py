from typing import List

import numpy as np
from pathlib import Path


from app.vectorstore import PineconeVectorStore


from app.services import IOService, ProcessService, VideoService, TranscribeService
from app.utils import (
    vectorize_image_by_clip,
    get_dir_from_video_uid,
    get_video_file_path,
    split_video_into_scenes,
    get_s3_key_from_video,
    download_youtube_video,
    get_youtube_video_metadata,
)

from app.model import VideoType, VectorType, VectorMetaDataType, VideoState, SegmentType


from app.constants import CLIP_DIMENSION, MIME_TYPES
from app.constants import (
    FRAME_VECTORSTORE_INDEX,
    SCENE_VECTORSTORE_INDEX,
    TRANSCRIPT_VECTORSTORE_INDEX,
    FRAME768_VECTORSTORE_INDEX,
    SCENE768_VECTORSTORE_INDEX,
)

from concurrent.futures import ThreadPoolExecutor


class IndexService:
    def __init__(self):
        self.io_service = IOService()
        self.process_service = ProcessService()
        self.video_service = VideoService()
        self.transcribe_service = TranscribeService()

        self.pine_vectorstore = PineconeVectorStore()

    def _upload_video_to_s3(self, video: VideoType) -> None:
        self.io_service.upload_file_to_s3(
            file_path=get_video_file_path(video=video),
            key=f"{get_s3_key_from_video(video=video)}.mp4",
        )

    def _extract_audio(self, video: VideoType) -> None:
        save_dir = get_dir_from_video_uid(video_uid=video.uid)

        extracted = self.process_service.extract_audio(
            video=video,
            file_path=get_video_file_path(video=video),
            save_path=f"{save_dir}/{video.uid}.mp3",
        )

        # if not extracted:
        #     return []

        # transcript: List[SegmentType] = self.transcribe_service.transcribe(
        #     video_uid=video.uid
        # )
        # texts = [
        #     segment.text
        #     for segment in transcript
        #     if segment is not None and segment.text is not None
        # ]
        # self.pine_vectorstore.insert_vectors_from_texts(
        #     texts=texts,
        #     metadatas=[
        #         {
        #             "video_uid": video.uid,
        #             "order": i + 1,
        #             "start": segment.start,
        #             "end": segment.end,
        #             "text": segment.text,
        #         }
        #         for i, segment in enumerate(transcript)
        #     ],
        #     index_name=TRANSCRIPT_VECTORSTORE_INDEX,
        #     namespace=video.org_uid,
        # )

    def _extract_frames_and_vectorize(self, video: VideoType) -> List[VectorType]:
        save_dir = Path(get_dir_from_video_uid(video_uid=video.uid))

        saved_vectors: List[VectorType] = []

        self.process_service.extract_frames(
            file_path=get_video_file_path(video=video),
            save_path=save_dir,
        )

        for image_index, image_path in enumerate(
            sorted(save_dir.glob("*.png")), start=1
        ):
            if image_path.stem.isdigit():
                frame_vector = vectorize_image_by_clip(str(image_path))

                saved_vectors.append(
                    VectorType(
                        id=f"{video.uid}_{image_index}",
                        vector=frame_vector.tolist(),
                        metadata=VectorMetaDataType(
                            video_uid=video.uid, order=int(image_index)
                        ),
                    )
                )

        self.pine_vectorstore.insert_vectors(
            index_name=FRAME768_VECTORSTORE_INDEX,
            namespace=video.org_uid,
            vectors=saved_vectors,
        )

        return saved_vectors

    def _split_video(self, video: VideoType) -> List[VectorMetaDataType]:
        return split_video_into_scenes(video=video)

    def _index_video(self, video: VideoType, s3_uploaded: bool = False) -> None:
        save_dir = get_dir_from_video_uid(video_uid=video.uid)
        # 2.
        # 0) Extract audio, thumbnail, metadata
        # 1) Extract frames + Vectorize
        # 2) Split video into scenes
        with ThreadPoolExecutor() as executor:
            s3_upload_future = None
            if not s3_uploaded:
                s3_upload_future = executor.submit(
                    lambda: self._upload_video_to_s3(
                        video=video,
                    )
                )
            audio_future = executor.submit(lambda: self._extract_audio(video=video))
            thumbnail_future = executor.submit(
                lambda: self.process_service.extract_thumbnail(
                    video=video,
                    file_path=get_video_file_path(video=video),
                    save_path=f"{save_dir}/{video.uid}.png",
                )
            )
            metadata_future = executor.submit(
                lambda: self.process_service.extract_metadata(
                    video=video,
                    file_path=get_video_file_path(video=video),
                    save_path=f"{save_dir}/{video.uid}.json",
                )
            )
            frame_vector_future = executor.submit(
                lambda: self._extract_frames_and_vectorize(video=video)
            )
            s3_upload_future.result()
            scene_list_future = executor.submit(lambda: self._split_video(video=video))
            audio_future.result()
            thumbnail_future.result()
            metadata_future.result()
            saved_vectors: List[VectorType] = frame_vector_future.result()
            scene_list: List[VectorMetaDataType] = scene_list_future.result()

        # 3. Create Scene Vectors
        scene_vectors: List[VectorType] = []

        for min_length in [3, 5]:
            for start_index in range(len(scene_list)):
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
                    or scene_list[end_index].end - scene_list[start_index].start <= 0
                ):
                    continue

                scene_emb = np.zeros(CLIP_DIMENSION)

                start_sec = round(scene_list[start_index].start)
                end_sec = min(round(scene_list[end_index].end), len(saved_vectors))

                vectors = [
                    saved_vectors[max(0, i - 1)].vector
                    for i in range(start_sec, end_sec + 1)
                ]
                if not vectors:
                    continue

                for v in vectors:
                    scene_emb += v

                scene_emb /= len(vectors)

                scene_cnt = len(scene_vectors)
                scene_vectors.append(
                    VectorType(
                        id=f"{video.uid}_{scene_cnt+1}",
                        vector=scene_emb.tolist(),
                        metadata=VectorMetaDataType(
                            video_uid=video.uid,
                            order=scene_cnt + 1,
                            start=scene_list[start_index].start,
                            end=scene_list[end_index].end,
                        ),
                    )
                )

        # 4. Insert Scene Vectors And Update Video State
        with ThreadPoolExecutor() as executor:
            vector_insert_future = executor.submit(
                lambda: self.pine_vectorstore.insert_vectors(
                    index_name=SCENE768_VECTORSTORE_INDEX,
                    namespace=video.org_uid,
                    vectors=scene_vectors,
                )
            )
            state_update_future = executor.submit(
                lambda: self.video_service.update(
                    video_uid=video.uid, video_state=VideoState.READY
                )
            )
            vector_insert_future.result()
            state_update_future.result()

        self.video_service.update(video_uid=video.uid, video_state=VideoState.READY)

        # 5. Remove Assets
        self.io_service.remove_directory(save_dir)

    def index_plain_video(self, video_uid: str) -> VideoType:
        video: VideoType = self.video_service.get(video_uid=video_uid)

        # 0. Create directory
        save_dir = get_dir_from_video_uid(video_uid=video.uid)
        self.io_service.create_directory(save_dir)

        # 1. Download video
        self.io_service.download_file_from_s3(
            key=f"{get_s3_key_from_video(video=video)}.{MIME_TYPES[video.metadata.type]}",
            file_path=get_video_file_path(video=video),
        )

        self._index_video(video=video)

        return video

    def index_youtube_video(self, video_uid: str, youtube_url: str) -> VideoType:
        video: VideoType = self.video_service.get(video_uid=video_uid)

        # video = get_youtube_video_metadata(video=video, youtube_url=youtube_url)
        # video.metadata.type = "video/mp4"

        # # 0. Create directory
        # save_dir = get_dir_from_video_uid(video_uid=video.uid)
        # self.io_service.create_directory(save_dir)

        # # 1. Download Youtube Video
        # download_youtube_video(
        #     youtube_url=youtube_url,
        #     save_path=get_video_file_path(video=video),
        # )

        # self._index_video(video=video)

        return video

    def index_audio(self, video: VideoType, transcript: List[SegmentType]) -> None:
        if transcript is None:
            return

        segments = [
            segment
            for segment in transcript
            if segment is not None and segment.text is not None
        ]
        self.pine_vectorstore.insert_vectors_from_texts(
            texts=[segment.text for segment in segments],
            metadatas=[
                {
                    "video_uid": video.uid,
                    "order": i + 1,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                }
                for i, segment in enumerate(segments)
            ],
            index_name=TRANSCRIPT_VECTORSTORE_INDEX,
            namespace=video.org_uid,
        )
