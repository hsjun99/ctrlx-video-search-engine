from __future__ import annotations

from typing import Optional, List, Generic, TypeVar, Optional, Dict, Union

from pydantic import BaseModel, Field

import numpy as np


class OrgType(BaseModel):
    id: int
    uid: str
    name: str
    abbr: str
    created_at: str


class VideoMetaDataType(BaseModel):
    type: Optional[str]
    title: Optional[str]
    size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    fps: Optional[str]
    # youtube_id: Optional[str]


class VideoType(BaseModel):
    id: int
    uid: str
    key: str
    metadata: VideoMetaDataType
    status: str
    org_uid: str
    created_at: str
    is_deleted: str


class VectorMetaDataType(BaseModel):
    video_uid: str
    order: int
    start: Optional[float]
    end: Optional[float]
    text: Optional[str]


class VectorType(BaseModel):
    id: str
    vector: np.ndarray
    metadata: VectorMetaDataType


# class FrameMetaDataType(BaseModel):
#     index: int
#     frame: int
#     video_id: str


# class VideoSplitType(BaseModel):
#     index: Optional[int]
#     start: float
#     end: float
#     video_id: str
#     index_list: Optional[List[int]]


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    success: bool = Field(..., example=True)
    code: int = Field(..., example=200)
    message: str = Field(..., example="Operation completed successfully")
    data: Optional[DataT] = None


# class TranscriptMetadataType(BaseModel):
#     index: int
#     start: float
#     end: float
#     video_id: str


# class WordType(BaseModel):
#     word: str
#     start: Optional[float]
#     end: Optional[float]
#     score: Optional[float]


# class SegmentType(BaseModel):
#     start: float
#     end: float
#     text: str
#     translation: Optional[str]
#     words: Optional[List[WordType]]
