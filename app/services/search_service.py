from typing import List
import os, json

import numpy as np

import faiss


from app.model import VideoSplitType

from app.utils import search_video_by_clip

from app.constants import FAISS_DIMENSION


class SearchService:
    def __init__(self):
        self.metadata = []
        self.vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)

    def search_video(self, query: str) -> List[VideoSplitType]:
        if os.path.isfile("./app/files/metadata.json"):
            with open("./app/files/metadata.json", "r") as f:
                self.metadata = json.load(f)
        if os.path.isfile("./app/files/faiss_index"):
            self.vectorstore = faiss.read_index("faiss_index")

        final_items: List[VideoSplitType] = search_video_by_clip(
            query=query,
            vectorstore=self.vectorstore,
            metadata=self.metadata,
        )

        return final_items
