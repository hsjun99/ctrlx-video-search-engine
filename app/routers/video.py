from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

from app.worker import index_video
from app.model import APIResponse


@router.post("/index/youtube")
def index_youtube_video(req: Request, youtube_url: str) -> APIResponse:
    index_video.delay(youtube_url)

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


@router.post("/search")
def search_video(req: Request):
    pass
