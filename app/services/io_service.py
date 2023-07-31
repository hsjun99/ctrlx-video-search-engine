import os
import shutil


class IOService:
    def __init__(self):
        pass

    def create_directory(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

    def remove_directory(self, path: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path)
