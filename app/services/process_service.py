import subprocess


class ProcessService:
    def __init__(self):
        pass

    def _ffmpeg_run(self, command: str) -> None:
        try:
            print("ENTER")
            subprocess.run(command, stdout=subprocess.DEVNULL, shell=True)
        except Exception as e:
            print("Error running ffmpeg command")
            print(e)

    def extract_frames(self, file_path: str, save_path: str) -> None:
        command = f"ffmpeg -i {file_path} -vf 'fps=1' {save_path}/%04d.png"
        print(command)
        self._ffmpeg_run(command)
