from __future__ import annotations

from typing import Optional, List, Generic, TypeVar, Optional, Dict, Union

from pydantic import BaseModel, Field


class VideoSplitType(BaseModel):
    start: float
    end: float
    video_uid: str


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    success: bool = Field(..., example=True)
    code: int = Field(..., example=200)
    message: str = Field(..., example="Operation completed successfully")
    data: Optional[DataT] = None
