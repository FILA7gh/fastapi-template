import boto3
from botocore.config import Config
from fastapi import UploadFile
from src.application.interfaces import FileStorage
from src.infrastructure.logging import logging
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


class S3FileStorage(FileStorage):
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        bucket: str,
        endpoint_url: str,
        upload_dir: str,
    ) -> None:
        self._bucket = bucket
        self._upload_dir = upload_dir

        self._client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            endpoint_url=endpoint_url,
            config=Config(signature_version="s3v4"),
        )

    async def save(self, file: UploadFile, filename: str, folder: str) -> str:
        key = f"{self._upload_dir}/{folder}/{filename}"

        await run_in_threadpool(
            self._client.upload_fileobj,
            file.file,
            self._bucket,
            key,
            {
                "ContentType": file.content_type,
                "ACL": "public-read",
            },
        )
        logger.info("S3 key saved: %s", key)
        return key

    async def delete(self, key: str) -> None:
        await run_in_threadpool(
            self._client.delete_object,
            Bucket=self._bucket,
            Key=key,
        )
