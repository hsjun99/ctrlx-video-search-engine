from typing import List
from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

from app.worker import index_video
from app.model import APIResponse


@router.post("/index/youtube")
async def index_youtube_video(req: Request) -> APIResponse:
    youtube_urls: List[str] = (await req.json()).get("youtube_urls", [])

    index_video.delay(youtube_urls)

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


@router.post("/search")
def search_video(req: Request):
    query = "TEMPORARY QUERY"

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data=[],
    )
