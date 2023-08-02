from __future__ import annotations

from typing import Optional, List, Generic, TypeVar, Optional, Dict, Union

from pydantic import BaseModel, Field


class WordType(BaseModel):
    word: str
    start: Optional[float]
    end: Optional[float]
    score: Optional[float]


class SegmentType(BaseModel):
    start: float
    end: float
    text: str
    translation: Optional[str]
    words: Optional[List[WordType]]


class TranscriptMetadataType(BaseModel):
    index: int
    start: float
    end: float
    video_id: str


class FrameMetaDataType(BaseModel):
    index: int
    frame: int
    video_id: str


class VideoSplitType(BaseModel):
    index: Optional[int]
    start: float
    end: float
    video_id: str
    index_list: Optional[List[int]]


class VideoType(BaseModel):
    title: str
    video_id: str
    status: str


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    success: bool = Field(..., example=True)
    code: int = Field(..., example=200)
    message: str = Field(..., example="Operation completed successfully")
    data: Optional[DataT] = None
