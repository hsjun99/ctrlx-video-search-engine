import subprocess

import json

from app.model import VideoType

from app.services import IOService, VideoService


class ProcessService:
    def __init__(self):
        self.io_service = IOService()
        self.video_service = VideoService()

    def _ffmpeg_run(self, command: str) -> None:
        try:
            print("ENTER")
            subprocess.run(command, stdout=subprocess.DEVNULL, shell=True)
        except Exception as e:
            print("Error running ffmpeg command")
            print(e)

    def extract_frames(self, file_path: str, save_path: str) -> None:
        command = f"ffmpeg -i {file_path} -vf 'fps=1' {save_path}/%04d.png"

        self._ffmpeg_run(command)

    def extract_audio(self, video: VideoType, file_path: str, save_path: str) -> None:
        command = f"ffmpeg -y -i {file_path} -vn -ab 128k {save_path}"

        self._ffmpeg_run(command)

        self.io_service.upload_file_to_s3(
            file_path=save_path, key=f"{video.key}/{video.uid}.mp3"
        )

    def extract_thumbnail(
        self, video: VideoType, file_path: str, save_path: str
    ) -> None:
        command = f"ffmpeg -y -i {file_path} -ss 00:00:02.000 -vframes 1 {save_path}"

        self._ffmpeg_run(command)

        self.io_service.upload_file_to_s3(
            file_path=save_path, key=f"{video.key}/{video.uid}.png"
        )

    def extract_metadata(
        self, video: VideoType, file_path: str, save_path: str
    ) -> VideoType:
        command = f"ffprobe -v quiet -print_format json -show_format -show_streams {file_path} > {save_path}"

        self._ffmpeg_run(command)

        try:
            with open(save_path) as f:
                metadata = json.load(f)
        except FileNotFoundError:
            print(f"File {save_path} not found.")
            return video

        streams = metadata.get("streams", [])
        video_stream = next(
            (stream for stream in streams if stream.get("codec_type") == "video"), None
        )

        if not video_stream:
            print("No video stream found in metadata.")
            return video

        try:
            video.metadata.width = video_stream["width"]
            video.metadata.height = video_stream["height"]
            video.metadata.fps = video_stream["avg_frame_rate"]
            video.metadata.duration = float(metadata["format"]["duration"])

            self.video_service.update(
                video_uid=video.uid, video_metadata=video.metadata
            )
        except KeyError as e:
            print(f"Key not found in metadata: {e}")
            return video

        return video
