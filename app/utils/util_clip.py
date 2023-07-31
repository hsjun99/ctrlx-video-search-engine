from PIL import Image
import faiss
from sentence_transformers import SentenceTransformer, util

import numpy as np

# Load CLIP model
model = SentenceTransformer("clip-ViT-B-16")


def vectorize_image_by_clip(image_path: str) -> np.ndarray:
    img_emb = model.encode(Image.open(image_path))
    img_emb = img_emb.reshape(1, -1)

    faiss.normalize_L2(img_emb)

    return img_emb
