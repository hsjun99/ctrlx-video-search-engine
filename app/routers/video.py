from typing import List
from fastapi import APIRouter, Request

import os, json

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

from app.worker import index_video
from app.model import APIResponse
from app.services import SearchService

from app.vectorstore import PineconeVectorStore


# @router.post("/list")
# async def get_video_list(req: Request) -> APIResponse:
#     video_list = []

#     if os.path.isfile("./app/files/video_list.json"):
#         with open("./app/files/video_list.json", "r") as f:
#             video_list = json.load(f)

#     return APIResponse(
#         success=True,
#         code=200,
#         message="Operation completed successfully",
#         data=video_list,
#     )


@router.post("/index/plain")
async def index_plain_video(req: Request, video_uid: str) -> APIResponse:
    index_video.delay(video_uid)

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


@router.post("/delete/vector")
async def index_plain_video(req: Request, namespace) -> APIResponse:
    vectorstore = PineconeVectorStore()

    vectorstore.delete_vectors_by_namespace(index_name="frame", namespace=namespace)
    vectorstore.delete_vectors_by_namespace(index_name="scene", namespace=namespace)
    vectorstore.delete_vectors_by_namespace(
        index_name="transcript", namespace=namespace
    )

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


# @router.post("/index/youtube")
# async def index_youtube_video(req: Request) -> APIResponse:
#     youtube_urls: List[str] = (await req.json()).get("youtube_urls", [])

#     index_video.delay(youtube_urls)

#     return APIResponse(
#         success=True,
#         code=200,
#         message="Operation completed successfully",
#         data={},
#     )


@router.post("/search")
async def search_video(
    req: Request, org_uid: str, video_uid: str = None, type="scene"
) -> APIResponse:
    search_service = SearchService()

    query: str = (await req.json()).get("query", "")

    final_items = None
    if type == "scene":
        final_items = search_service.search_video(
            query=query, org_uid=org_uid, video_uid=video_uid
        )
    elif type == "transcript":
        final_items = search_service.search_video_by_transcript(
            query=query, org_uid=org_uid, video_uid=video_uid
        )

    final_items = [item.dict() for item in final_items]
    for item in final_items:
        del item["order"]

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data=final_items,
    )
