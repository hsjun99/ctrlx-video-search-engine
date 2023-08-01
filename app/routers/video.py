from typing import List
from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

from app.worker import index_video
from app.model import APIResponse, VideoSplitType
from app.services import SearchService


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
async def search_video(req: Request):
    search_service = SearchService()

    query: str = (await req.json()).get("query", "")

    final_items: List[VideoSplitType] = search_service.search_video(query=query)

    def convert(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return (int(hours), int(minutes), int(seconds))

    final_items = [item.dict() for item in final_items]
    for item in final_items:
        s_h, s_m, s_s = convert(item["start"])
        e_h, e_m, e_s = convert(item["end"])
        item["start"] = f"{s_h}:{s_m}:{s_s}"
        item["end"] = f"{e_h}:{e_m}:{e_s}"

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data=final_items,
    )
