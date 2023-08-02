from typing import List
import os, json

import numpy as np

import faiss

from pydantic import parse_obj_as

from app.model import VideoSplitType, FrameMetaDataType

from app.utils import search_video_by_clip

from app.constants import FAISS_DIMENSION


class SearchService:
    def __init__(self):
        self.metadata: List[VideoSplitType] = []
        self.frame_metadata: List[FrameMetaDataType] = []
        self.vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)
        self.frame_vectorstore = faiss.IndexFlatIP(FAISS_DIMENSION)

    def search_video(self, query: str) -> List[VideoSplitType]:
        if os.path.isfile("./app/files/metadata.json"):
            with open("./app/files/metadata.json", "r") as f:
                self.metadata = parse_obj_as(List[VideoSplitType], json.load(f))
        if os.path.isfile("./app/files/frame_metadata.json"):
            with open("./app/files/frame_metadata.json", "r") as f:
                self.frame_metadata = parse_obj_as(
                    List[FrameMetaDataType], json.load(f)
                )
        if os.path.isfile("./app/files/faiss_index"):
            self.vectorstore = faiss.read_index("./app/files/faiss_index")
        if os.path.isfile("./app/files/frame_faiss_index"):
            self.frame_vectorstore = faiss.read_index("./app/files/frame_faiss_index")

        final_items: List[VideoSplitType] = search_video_by_clip(
            query=query,
            vectorstore=self.vectorstore,
            frame_vectorsore=self.frame_vectorstore,
            metadata=self.metadata,
            frame_metadata=self.frame_metadata,
        )

        return final_items
