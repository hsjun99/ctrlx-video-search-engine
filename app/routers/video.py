from celery import chain
from fastapi import APIRouter, Request

router = APIRouter(
    prefix="/video",
    tags=["video"],
)


@router.post("/index/youtube")
def index_youtube_video(req: Request, youtube_url: str):
    pass


@router.post("/search")
def search_video(req: Request):
    pass


# @router.post("/transcribe")
# def transcribe(req: Request, video_uid: str, lang: str = "en") -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         transcribe_video_first_step.s(video_uid, lang)
#         | task_inference
#         | transcribe_video_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/translate")
# def translate(req: Request, video_uid: str, target_lang: str = "en") -> APIResponse:
#     translate_subtitles.delay(video_uid, target_lang)

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/extract")
# def extract_video(req: Request, video_uid: str) -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         extract_video_first_step.s(video_uid)
#         | task_extract_video
#         | extract_video_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/extract/youtube")
# def extract_youtube_video(
#     req: Request, video_uid: str, youtube_url: str
# ) -> APIResponse:
#     video_service = VideoService()

#     available, msg = video_service.check_youtube_available(youtube_url)

#     if not available:
#         return APIResponse(
#             success=True,
#             code=200,
#             message="Operation incompleted",
#             data={"available": available, "message": msg},
#         )

#     # Chain tasks
#     task_chain = chain(
#         extract_video_first_step.s(video_uid, youtube_url)
#         | task_extract_video
#         | extract_video_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True,
#         code=200,
#         message="Operation completed successfully",
#         data={"available": available},
#     )


# @router.post("/export/srt")
# def export_srt(
#     req: Request,
#     video_uid: str,
#     first_lang: str,
#     second_lang: str = None,
# ) -> APIResponse:
#     video_service = VideoService()

#     video: VideoType = video_service.get(video_uid)

#     if second_lang == "undefined" or second_lang == "null":
#         second_lang = None

#     create_srt_file(
#         video=video,
#         first_lang=first_lang,
#         second_lang=second_lang,
#     )

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/export/video")
# def add_subtitles(req: Request, video_uid: str, structure: int) -> APIResponse:
#     video_service = VideoService()

#     video: VideoType = video_service.get(video_uid)

#     video_service.update(video_uid=video_uid, video_state=VideoState.ENCODING)

#     encoded_video: EncodedVideoType = video_service.create_encode(
#         video=video, structure=structure
#     )

#     # Chain tasks
#     task_chain = chain(
#         encode_video_first_step.s(encoded_video.dict())
#         | task_pre_encode_subtitled_video
#         | task_encode_subtitled_video
#         | task_post_encode_subtitled_video
#         | encode_video_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True,
#         code=200,
#         message="Operation completed successfully",
#         data={"encoded_video_id": encoded_video.id},
#     )


# @router.post("/split")
# def split(req: Request, video_uid: str, threshold: float = 27.0) -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         split_video_by_scenes_first_step.s(video_uid, threshold)
#         | task_split_video_by_scenes
#         | split_video_by_scenes_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/mask")
# def mask(req: Request, video_uid: str, scene_uid: str) -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         mask_scene_image_first_step.s(video_uid, scene_uid)
#         | task_mask_scene_image
#         | mask_scene_image_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/track")
# def track(req: Request, video_uid: str, scene_uid: str, mask_index: int) -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         track_scene_frames_first_step.s(video_uid, scene_uid, mask_index)
#         | task_track_scene_frames
#         | track_scene_frames_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/export/video/tracked")
# def add_subtitles(
#     req: Request, video_uid: str, scene_uid: str, zoom_scale: float
# ) -> APIResponse:
#     # Chain tasks
#     task_chain = chain(
#         encode_object_tracked_video_first_step.s(video_uid, scene_uid, zoom_scale)
#         | task_encode_object_tracked_video
#         | encode_object_tracked_video_final_step.s()
#     )

#     task_chain.delay()

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )


# @router.post("/mask/reset")
# def mask_reset(req: Request, video_uid: str, scene_uid: str) -> APIResponse:
#     video: VideoType = sb_get_video(video_uid)

#     target_scene_index = next(
#         (index for index, scene in enumerate(video.scenes) if scene.uid == scene_uid),
#         None,
#     )

#     video.scenes[target_scene_index].bounding_boxes = []
#     video.scenes[target_scene_index].click_state = None

#     sb_update_video_scenes(video_uid, video.scenes)

#     return APIResponse(
#         success=True, code=200, message="Operation completed successfully", data={}
#     )
