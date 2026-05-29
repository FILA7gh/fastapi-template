from datetime import date
from pathlib import Path
from typing import Set
from uuid import uuid4

from fastapi import UploadFile
from src.application.exceptions import FileSizeTooLarge, UnsupportedImageFormat
from src.application.interfaces import FileStorage


class MediaURLBuilder:
    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def build(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"


class ImageService:
    ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(
        self,
        storage: FileStorage,
    ):
        self._storage = storage

    def _validate_file_size(self, file: UploadFile, max_size: int):
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > max_size:
            raise FileSizeTooLarge(extra=f"max: {max_size}MB")

    async def save_image(
        self,
        image: UploadFile,
        max_size: int,
        folder: str,
        allowed_exts: Set[str] | None = None,
    ) -> str:
        if not image.filename:
            raise UnsupportedImageFormat()

        ext = Path(image.filename).suffix.lower()
        if allowed_exts is not None:
            if ext not in allowed_exts:
                raise UnsupportedImageFormat()
        else:
            if ext not in self.ALLOWED_EXT:
                raise UnsupportedImageFormat()

        self._validate_file_size(image, max_size)

        today = date.today().strftime("%Y/%m/%d")
        filename = f"{uuid4()}{ext}"
        dated_folder = f"{folder}/{today}"

        return await self._storage.save(
            file=image,
            filename=filename,
            folder=dated_folder,
        )

    async def delete(self, image_path: str | None) -> None:
        if not image_path:
            return
        await self._storage.delete(image_path)
