from typing import List, Optional
from fastapi import APIRouter, Request, UploadFile, File

from celery import chain

from PIL import Image
from io import BytesIO

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

from app.worker import (
    index_plain_video,
    index_youtube_video_first_step,
    index_youtube_video_final_step,
    task_inference,
)
from app.model import APIResponse
from app.services import SearchService

from app.vectorstore import PineconeVectorStore


@router.post("/index/plain")
async def index_plain_video(req: Request, video_uid: str) -> APIResponse:
    index_plain_video.delay(video_uid)

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


@router.post("/index/youtube")
async def index_plain_video(
    req: Request, video_uid: str, youtube_url: str
) -> APIResponse:
    # youtube_urls: List[str] = (await req.json()).get("youtube_urls", [])

    task_chain = chain(
        index_youtube_video_first_step.s(video_uid, youtube_url)
        | task_inference
        | index_youtube_video_final_step.s()
    )

    task_chain.delay()

    # index_youtube_video.delay(video_uid, youtube_url)

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


# @router.post("/delete/vector/namespace")
# async def delete_vector(req: Request, namespace: str) -> APIResponse:
#     vectorstore = PineconeVectorStore()

#     vectorstore.delete_vectors_by_namespace(index_name="frame-768", namespace=namespace)
#     vectorstore.delete_vectors_by_namespace(index_name="scene-768", namespace=namespace)
#     vectorstore.delete_vectors_by_namespace(
#         index_name="transcript", namespace=namespace
#     )

#     return APIResponse(
#         success=True,
#         code=200,
#         message="Operation completed successfully",
#         data={},
#     )


@router.post("/delete/vector")
async def delete_vector_by_video_uid(
    req: Request, org_uid: str, video_uid: str
) -> APIResponse:
    vectorstore = PineconeVectorStore()

    print(org_uid, video_uid)

    vectorstore.delete_vectors_by_filter(
        index_name="frame-768", namespace=org_uid, filter={"video_uid": video_uid}
    )
    vectorstore.delete_vectors_by_filter(
        index_name="scene-768", namespace=org_uid, filter={"video_uid": video_uid}
    )
    vectorstore.delete_vectors_by_filter(
        index_name="transcript", namespace=org_uid, filter={"video_uid": video_uid}
    )

    return APIResponse(
        success=True,
        code=200,
        message="Operation completed successfully",
        data={},
    )


@router.post("/search")
async def search_video(
    req: Request,
    org_uid: str,
    video_uid: str = None,
    type: str = "scene",
    file: Optional[UploadFile] = File(None),
) -> APIResponse:
    search_service = SearchService()

    final_items = None
    if type == "scene":
        query: str = (await req.json()).get("query", "")

        final_items = search_service.search_video_by_text(org_uid=org_uid, query=query)
    elif type == "transcript":
        query: str = (await req.json()).get("query", "")

        final_items = search_service.search_video_by_transcript(
            query=query, org_uid=org_uid
        )
    elif type == "image":
        file_contents = await file.read()

        image = Image.open(BytesIO(file_contents))

        final_items = search_service.search_video_by_image(
            org_uid=org_uid, query_image=image
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
