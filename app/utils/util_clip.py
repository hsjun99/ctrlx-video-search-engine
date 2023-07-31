from PIL import Image
from typing import List
import faiss
from sentence_transformers import SentenceTransformer, util

import numpy as np

from app.model import VideoSplitType


_model = None

N_NEIGHBORS = 50
MIN_NUM_RESULTS = 10


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("clip-ViT-B-16")
    return _model


def vectorize_image_by_clip(image_path: str) -> np.ndarray:
    _model = get_model()

    img_emb = _model.encode(Image.open(image_path))
    img_emb = img_emb.reshape(1, -1)

    faiss.normalize_L2(img_emb)

    return img_emb


def search_video_by_clip(
    query: str, vectorstore: any, metadata: List[VideoSplitType]
) -> List[VideoSplitType]:
    text_emb = _model.encode(query)
    distances, neighbor_ids = vectorstore.search(text_emb.reshape(1, -1), N_NEIGHBORS)
    distances, neighbor_ids = distances[0], neighbor_ids[0]

    zipped = list(zip(distances, neighbor_ids))  # Pair up the two lists
    zipped.sort(
        reverse=True, key=lambda x: x[0]
    )  # Sort by distances in descending order
    distances, neighbor_ids = zip(*zipped)  # Unpack the sorted pairs

    # Pre-calculate a dictionary for fast lookup
    metadata_dict: dict[int, VideoSplitType] = {item.index: item for item in metadata}

    # Initialize final_result with the first item
    first_item: VideoSplitType = metadata_dict[neighbor_ids[0]]
    final_items: List[VideoSplitType] = [
        VideoSplitType(start=first_item.start, end=first_item.end)
    ]

    # Iterate over the rest of neighbor_ids
    for neighbor_id in neighbor_ids[1:]:
        original_item: VideoSplitType = metadata_dict[neighbor_id]
        merged = False

        # Check if original_item overlaps with any of the existing ranges in final_result
        for item in final_items:
            if (
                original_item.start >= item.start and original_item.start <= item.end
            ) or (item.end >= original_item.end and item.start <= original_item.end):
                # Merge the overlapping ranges
                item.start = min(item.start, original_item.start)
                item.end = max(item.end, original_item.end)
                merged = True
                # break

        # If original_item did not overlap with any range, add it to final_result
        if not merged:
            final_items.append(original_item)

        # Stop if we have enough results
        if len(final_items) >= MIN_NUM_RESULTS:
            break

    return final_items
