import os
import shutil
import boto3
from boto3.s3.transfer import TransferConfig

from app.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    AWS_S3_BUCKET,
)


class IOService:
    def __init__(self):
        self.config = TransferConfig(
            multipart_threshold=1024 * 100,
            max_concurrency=20,
            multipart_chunksize=1024 * 100,
            use_threads=True,
        )

    def create_directory(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)

        if not os.path.exists(directory):
            os.makedirs(directory)

    def remove_directory(self, path: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path)

    def upload_file_to_s3(self, file_path: str, key: str) -> None:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        s3.upload_file(
            file_path,
            AWS_S3_BUCKET,
            key,
            Config=self.config,
        )

    def download_file_from_s3(self, key: str, file_path: str) -> None:
        self.create_directory(file_path)

        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        with open(file_path, "wb") as file:
            s3.download_fileobj(
                AWS_S3_BUCKET,
                key,
                file,
                Config=self.config,
            )
