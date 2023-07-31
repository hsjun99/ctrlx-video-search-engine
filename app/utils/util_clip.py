from PIL import Image
import faiss
from sentence_transformers import SentenceTransformer, util

import numpy as np


_model = None


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
