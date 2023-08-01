from PIL import Image
from typing import List
import faiss
from sentence_transformers import SentenceTransformer, util

from multilingual_clip import pt_multilingual_clip
import transformers

import torch
import open_clip

import math

import numpy as np

from app.model import VideoSplitType

from app.constants import FAISS_DIMENSION

_model = None
_image_model = None
_text_model = None
_tokenizr = None

N_NEIGHBORS = 100
MIN_NUM_RESULTS = 10


# def _get_device():
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print("Using {} device".format(device))
#     return device


# def get_image_model_and_preprocess():
#     global _image_model, _preprocess
#     if _image_model is None:
#         _image_model, _, _preprocess = open_clip.create_model_and_transforms(
#             "ViT-B-16-plus-240", pretrained="laion400m_e32"
#         )
#         _image_model.to(_get_device())

#     return _image_model, _preprocess


# def get_text_model_and_tokenizer():
#     global _text_model, _tokenizer
#     if _text_model is None:
#         _text_model = pt_multilingual_clip.MultilingualCLIP.from_pretrained(
#             "M-CLIP/XLM-Roberta-Large-Vit-B-16Plus"
#         )
#         _tokenizer = transformers.AutoTokenizer.from_pretrained(
#             "M-CLIP/XLM-Roberta-Large-Vit-B-16Plus"
#         )

#     return _text_model, _tokenizer


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("clip-ViT-B-16")
        # _model = SentenceTransformer("clip-ViT-L-14")
    return _model


def vectorize_image_by_clip(image_path: str) -> np.ndarray:
    _model = get_model()
    img_emb = _model.encode(Image.open(image_path))
    img_emb = img_emb.reshape(1, -1)

    # _image_model, _preprocess = get_image_model_and_preprocess()
    # image = Image.open(image_path)
    # image = _preprocess(image).unsqueeze(0).to(_get_device())

    # img_emb = _image_model.encode_image(image).detach().cpu().numpy()
    # img_emb = img_emb.reshape(1, -1)

    # faiss.normalize_L2(img_emb)

    return img_emb


def search_video_by_clip(
    query: str, vectorstore: any, frame_vectorsore: any, metadata: List[VideoSplitType]
) -> List[VideoSplitType]:
    _model = get_model()
    # text_emb = _model.encode(query)
    # print(text_emb.shape)
    text_emb = _model.encode(query).reshape(1, -1)

    # _text_model, _tokenizer = get_text_model_and_tokenizer()
    # text_emb = _text_model.forward(query, _tokenizer).detach().cpu().numpy()

    faiss.normalize_L2(text_emb)

    distances, neighbor_ids = vectorstore.search(text_emb, N_NEIGHBORS)
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
    first_item.index_list = [first_item.index]
    final_items: List[VideoSplitType] = [first_item]

    # Iterate over the rest of neighbor_ids
    for neighbor_id in neighbor_ids[1:]:
        original_item: VideoSplitType = metadata_dict[neighbor_id]
        merged = False

        # Check if original_item overlaps with any of the existing ranges in final_result
        for item in final_items:
            if item.video_id != original_item.video_id:
                continue
            if (
                original_item.start >= item.start and original_item.start <= item.end
            ) or (item.end >= original_item.end and item.start <= original_item.end):
                # Merge the overlapping ranges
                item.start = min(item.start, original_item.start)
                item.end = max(item.end, original_item.end)
                item.index_list.append(original_item.index)
                merged = True
                break

        # If original_item did not overlap with any range, add it to final_result
        if not merged:
            original_item.index_list = [original_item.index]
            final_items.append(original_item)

        # Stop if we have enough results
        if len(final_items) >= MIN_NUM_RESULTS:
            break

    final_cosine_sims = [-1 for i in range(len(final_items))]
    for index, item in enumerate(final_items):
        start_sec, end_sec = round(item.start), round(item.end)

        for i in range(start_sec, end_sec + 1):
            v = frame_vectorsore.reconstruct(i)
            final_cosine_sims[index] = max(
                util.cos_sim(v, text_emb), final_cosine_sims[index]
            )

    # final_cosine_sims = [-1 for i in range(len(final_items))]
    # for index, item in enumerate(final_items):
    #     final_vector = np.zeros((1, FAISS_DIMENSION))
    #     for v_index in item.index_list:
    #         v = vectorstore.reconstruct(v_index)
    #         final_vector += v

    #     final_cosine_sims[index] = util.cos_sim(
    #         final_vector.astype("double"), text_emb.astype("double")
    #     )

    final_items_coss = list(zip(final_cosine_sims, final_items))
    list_sorted = sorted(final_items_coss, key=lambda x: x[0], reverse=True)

    final_cosine_sims, final_items = map(list, zip(*list_sorted))
    print(final_cosine_sims)

    for item in final_items:
        del item.index
        del item.index_list

    return final_items
