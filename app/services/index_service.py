from typing import Dict, List

import math

from app.constants import (
    CREDIT_PER_TRANSCRIBE_MINUTE,
    CREDIT_PER_TRANSLATE_HUNDRED_CHAR,
)


class IndexService:
    def __init__(self):
        pass

    def index_youtube_video(self, youtube_urls: List[str]):
        # TODO: Implement this
        # 1. Download video
        # 2. Retrieve Frames
        # 3. Vectorize Frames Using CLIP
        # 4. Split Video By Scene
        # 5. Vectorize Scene
        pass

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
