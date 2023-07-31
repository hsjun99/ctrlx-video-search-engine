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

        # 5. Vectorize Scenes
        # 6. Remove Assets
        for dir in save_directories:
            if dir is not None:
                self.io_service.remove_directory(dir)

    # def create_transaction(self, video: VideoType, transaction_type: str):
    #     prev_transaction: TransactionType = (
    #         self.transaction_repository.sb_get_last_transaction(uid=video.created_by)
    #     )

    #     consume_amount = 0

    #     if transaction_type == TransactionSubType.TRANSCRIBE:
    #         consume_amount = (
    #             math.ceil(video.metadata.duration / 60) * CREDIT_PER_TRANSCRIBE_MINUTE
    #         )

    #     elif transaction_type == TransactionSubType.TRANSLATE:
    #         subtitles: Dict[str, TranscriptType] = next(
    #             (t for t in video.subtitles if t.structure == 4), None
    #         ).transcript
    #         consume_amount = (
    #             math.ceil(sum(len(value.text) for value in subtitles.values()) / 100)
    #             * CREDIT_PER_TRANSLATE_HUNDRED_CHAR
    #         )

    #     new_balance = prev_transaction.new_balance - consume_amount
    #     if new_balance < 0:
    #         new_balance = 0
    #     new_transaction = TransactionType(
    #         consume_amount=consume_amount,
    #         previous_balance=prev_transaction.new_balance,
    #         new_balance=new_balance,
    #         type=transaction_type,
    #         created_by=video.created_by,
    #     )

    #     self.transaction_repository.sb_post_transaction(new_transaction=new_transaction)
