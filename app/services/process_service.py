from app.model import VideoType

import subprocess
import json


from app.services import IOService


class ProcessService:
    def __init__(self):
        self.io_service = IOService()

    def _ffmpeg_run(self, command: str) -> None:
        subprocess.run(command, stdout=subprocess.DEVNULL, shell=True)

    def extract_frames(self, file_path: str, save_path: str) -> None:
        command = f"ffmpeg -i {file_path} -vf 'fps=1' {save_path}/%04d.png"
        self._ffmpeg_run(command)

    # def extract_audio(self, file_path: str, save_path: str) -> None:
    #     # self.io_service.create_directory(save_path)

    #     command = f"ffmpeg -y -i {file_path} -vn -ab 128k {save_path}"
    #     self._ffmpeg_run(command)

    # def extract_thumbnail(
    #     self, video: VideoType, file_path: str, save_path: str
    # ) -> VideoType:
    #     # self.io_service.create_directory(save_path)

    #     command = f"ffmpeg -y -i {file_path} -ss 00:00:02.000 -vframes 1 {save_path}"
    #     self._ffmpeg_run(command)

    #     video.thumbnail_key = f"{video.key}.png"

    #     return video

    # def extract_metadata(
    #     self, video: VideoType, file_path: str, save_path: str
    # ) -> VideoType:
    #     # self.io_service.create_directory(save_path)

    #     command = f"ffprobe -v quiet -print_format json -show_format -show_streams {file_path} > {save_path}"

    #     self._ffmpeg_run(command)

    #     try:
    #         with open(save_path) as f:
    #             metadata = json.load(f)
    #     except FileNotFoundError:
    #         print(f"File {save_path} not found.")
    #         return video

    #     streams = metadata.get("streams", [])
    #     video_stream = next(
    #         (stream for stream in streams if stream.get("codec_type") == "video"), None
    #     )

    #     if not video_stream:
    #         print("No video stream found in metadata.")
    #         return video

    #     try:
    #         video.metadata.width = video_stream["width"]
    #         video.metadata.height = video_stream["height"]
    #         video.metadata.fps = video_stream["avg_frame_rate"]
    #         video.metadata.duration = float(metadata["format"]["duration"])
    #     except KeyError as e:
    #         print(f"Key not found in metadata: {e}")
    #         return video

    #     return video
