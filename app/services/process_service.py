import subprocess


from app.services import IOService


class ProcessService:
    def __init__(self):
        self.io_service = IOService()

    def _ffmpeg_run(self, command: str) -> None:
        subprocess.run(command, stdout=subprocess.DEVNULL, shell=True)

    def extract_frames(self, file_path: str, save_path: str) -> None:
        command = f"ffmpeg -i {file_path} -vf 'fps=1' {save_path}/%04d.png"
        self._ffmpeg_run(command)
